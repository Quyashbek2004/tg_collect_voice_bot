import logging
import os
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, \
    ContextTypes
import sqlite3
import random
import csv
import zipfile
import io

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Load authorized users from config
def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

def load_localization(lang='ru'):
    locale_path = Path('locales') / f'{lang}.yaml'
    if not locale_path.exists():
        locale_path = Path('locales') / 'en.yaml'
    with open(locale_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def get_message(key, lang=None, **kwargs):
    config = load_config()
    if lang is None:
        lang = config.get('default_language', 'en')
    messages = load_localization(lang)
    message = messages.get(key, messages.get('message_not_found', 'Message not found'))
    return message.format(**kwargs) if kwargs else message

def load_authorized_users():
    config = load_config()
    return config.get('authorized_users', [])

# Insert sentences from text file
def insert_sentences_from_text(file_content):
    sentences = [s.strip() for s in file_content.split('\n') if s.strip()]
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    for sentence in sentences:
        cursor.execute('INSERT INTO sentences (sentence) VALUES (?)', (sentence,))
    conn.commit()
    conn.close()
    return len(sentences)

# Get all recorded sentences
def get_recorded_sentences():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sentence, audio_path, author, date 
        FROM sentences 
        WHERE audio_path IS NOT NULL
    ''')
    results = cursor.fetchall()
    conn.close()
    return results

async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    authorized_users = load_authorized_users()
    
    if user.username not in authorized_users:
        await update.message.reply_text(get_message("no_permission"))
        return

    # Get all recorded sentences
    sentences = get_recorded_sentences()
    if not sentences:
        await update.message.reply_text(get_message("no_recordings"))
        return

    # Create ZIP buffer
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        # Create and add metadata.csv
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerow(['Text', 'Audio File', 'Author', 'Date'])
        
        # Download each audio file and add to ZIP
        for i, (text, audio_path, author, date) in enumerate(sentences, 1):
            # Get audio file
            audio_file = await context.bot.get_file(audio_path)
            audio_data = await audio_file.download_as_bytearray()
            
            # Add audio to ZIP
            filename = f'audio_{i}.ogg'
            zip_file.writestr(filename, audio_data)
            
            # Add metadata row
            csv_writer.writerow([text, filename, author, date])
        
        # Add metadata.csv to ZIP
        zip_file.writestr('metadata.csv', csv_buffer.getvalue())

    # Send ZIP file
    zip_buffer.seek(0)
    await update.message.reply_document(
        document=zip_buffer,
        filename='voice_archive.zip',
        caption=get_message("archive_caption")
    )
    return len(sentences)

# Database initialization
def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentence TEXT NOT NULL,
            audio_path TEXT,
            author TEXT,
            author_id INTEGER,
            date TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            user_id INTEGER PRIMARY KEY,
            last_notification_time TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# Get random sentence that hasn't been voiced yet
def get_random_sentence():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, sentence FROM sentences 
        WHERE audio_path IS NULL 
        ORDER BY RANDOM() 
        LIMIT 1
    ''')
    result = cursor.fetchone()
    conn.close()
    return result


# Update sentence with audio information
def update_sentence(sentence_id, audio_path, author, author_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        UPDATE sentences 
        SET audio_path = ?, author = ?, author_id = ?, date = ? 
        WHERE id = ?
    ''', (audio_path, author, author_id, current_date, sentence_id))
    conn.commit()
    conn.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Send welcome message
    await update.message.reply_text(get_message('welcome'))

    # Send first task
    await send_new_task(update, context)


async def send_new_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sentence_data = get_random_sentence()
    if sentence_data:
        sentence_id, sentence_text = sentence_data
        # Store the current sentence ID in user data
        context.user_data['current_sentence_id'] = sentence_id
        message = get_message('voice_task', text=sentence_text)
        await update.message.reply_text(message, parse_mode='HTML')
    else:
        await update.message.reply_text(get_message('all_voiced'))


async def insert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    authorized_users = load_authorized_users()
    
    if user.username not in authorized_users:
        await update.message.reply_text(get_message("no_permission"))
        return
    
    await update.message.reply_text(get_message("send_text_file"))
    context.user_data['waiting_for_file'] = True

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('waiting_for_file'):
        return
    
    document = update.message.document
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text(get_message("wrong_file_format"))
        return
    
    file = await context.bot.get_file(document.file_id)
    file_content = await file.download_as_bytearray()
    text_content = file_content.decode('utf-8')
    
    try:
        sentences_count = insert_sentences_from_text(text_content)
        await update.message.reply_text(get_message("sentences_added", count= sentences_count))
    except Exception as e:
        await update.message.reply_text(get_message("sentences_error", error= str(e)))
    
    context.user_data['waiting_for_file'] = False

async def get_user_stats(user_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    # Get current date ranges
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = today_start.replace(day=1)
    
    # Get total count
    cursor.execute('SELECT COUNT(*) FROM sentences WHERE author_id = ?', (user_id,))
    total_count = cursor.fetchone()[0]
    
    # Get today's count
    cursor.execute('SELECT COUNT(*) FROM sentences WHERE author_id = ? AND date >= ?', 
                  (user_id, today_start.strftime('%Y-%m-%d %H:%M:%S')))
    today_count = cursor.fetchone()[0]
    
    # Get week count
    cursor.execute('SELECT COUNT(*) FROM sentences WHERE author_id = ? AND date >= ?', 
                  (user_id, week_start.strftime('%Y-%m-%d %H:%M:%S')))
    week_count = cursor.fetchone()[0]
    
    # Get month count
    cursor.execute('SELECT COUNT(*) FROM sentences WHERE author_id = ? AND date >= ?', 
                  (user_id, month_start.strftime('%Y-%m-%d %H:%M:%S')))
    month_count = cursor.fetchone()[0]
    
    conn.close()
    return total_count, today_count, week_count, month_count

async def mystat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    total, today, week, month = await get_user_stats(user.id)
    
    stats_message = (
        f'{get_message("stats_header")}'
        f'{get_message("stats_total", count= total)}\n'
        f'{get_message("stats_today", count= total)}\n'
        f'{get_message("stats_week", count= total)}\n'
        f'{get_message("stats_month", count= total)}'
    )
    
    await update.message.reply_text(stats_message)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    user = update.message.from_user

    # Get the current sentence ID from user data
    sentence_id = context.user_data.get('current_sentence_id')

    if sentence_id:
        # Update the database
        update_sentence(
            sentence_id,
            voice.file_id,
            user.username or user.first_name,
            user.id
        )

        # Send confirmation and new task
        await update.message.reply_text(
            get_message("thanks_next_task"))
        await send_new_task(update, context)
    else:
        await update.message.reply_text(get_message("please_start"))


async def get_total_recordings():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM sentences WHERE audio_path IS NOT NULL')
    total = cursor.fetchone()[0]
    conn.close()
    return total

async def send_notification(context):
    config = load_config()
    notifications = config.get('notifications', {})
    
    if not notifications.get('enabled', False):
        return
    
    interval_hours = notifications.get('interval_hours', 24)
    if interval_hours <= 0:
        return

    application = context.application
    current_time = datetime.now()
    notification_threshold = current_time - timedelta(hours=interval_hours)

    # Get all users who have recordings and haven't been notified recently
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        WITH user_recordings AS (
            SELECT DISTINCT author_id
            FROM sentences
            WHERE audio_path IS NOT NULL
        )
        SELECT ur.author_id
        FROM user_recordings ur
        LEFT JOIN notifications n ON ur.author_id = n.user_id
        WHERE n.last_notification_time IS NULL 
        OR n.last_notification_time <= ?
    ''', (notification_threshold,))
    users = cursor.fetchall()

    total_recordings = await get_total_recordings()

    # Send notification to each eligible user
    for (user_id,) in users:
        try:
            user_stats = await get_user_stats(user_id)
            # Get last notification time
            cursor.execute('SELECT last_notification_time FROM notifications WHERE user_id = ?', (user_id,))
            last_notif = cursor.fetchone()

            message = get_message('notification_message', 
                                total=total_recordings,
                                user_total=user_stats[0])
            await application.bot.send_message(chat_id=user_id, text=message)
            
            # Update last notification time
            cursor.execute('''
                INSERT OR REPLACE INTO notifications (user_id, last_notification_time)
                VALUES (?, ?)
            ''', (user_id, current_time))
            
        except Exception as e:
            logging.error(f"Failed to send notification to user {user_id}: {e}")
    
    conn.commit()
    conn.close()

def main():
    # Initialize database
    init_db()

    # Initialize bot with job queue
    application = (
        Application.builder()
        .token(os.getenv('BOT_TOKEN'))
        .build()
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("insert", insert_command))
    application.add_handler(CommandHandler("download", download_command))
    application.add_handler(CommandHandler("mystat", mystat_command))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Start notification task
    application.job_queue.run_repeating(send_notification, interval=timedelta(hours=0.5), first=10)

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
