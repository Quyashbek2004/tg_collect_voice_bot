import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, \
    ContextTypes
import sqlite3
import random

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


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
    await update.message.reply_text(
        "Привет! Я бот для озвучки текстов. Я буду отправлять вам тексты, а вы должны их озвучить."
    )

    # Send first task
    await send_new_task(update, context)


async def send_new_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sentence_data = get_random_sentence()
    if sentence_data:
        sentence_id, sentence_text = sentence_data
        # Store the current sentence ID in user data
        context.user_data['current_sentence_id'] = sentence_id
        message = f"<b>озвучьте этот текст и отправьте как аудиосообщение: </b>\n{sentence_text}"
        await update.message.reply_text(message, parse_mode='HTML')
    else:
        await update.message.reply_text("Извините, все тексты уже озвучены!")


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
            "Спасибо за аудио! Вот следующее задание:")
        await send_new_task(update, context)
    else:
        await update.message.reply_text("Пожалуйста, начните с команды /start")


def main():
    # Initialize database
    init_db()

    # Initialize bot
    application = Application.builder().token('').build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()