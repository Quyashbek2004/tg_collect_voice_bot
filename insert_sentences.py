import sqlite3

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

init_db()
conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()
cursor.execute('INSERT INTO sentences (sentence) VALUES (?)', ('Текст для озвучки1',))
cursor.execute('INSERT INTO sentences (sentence) VALUES (?)', ('Текст для озвучки2',))
cursor.execute('INSERT INTO sentences (sentence) VALUES (?)', ('Текст для озвучки3',))
cursor.execute('INSERT INTO sentences (sentence) VALUES (?)', ('Текст для озвучки4',))
cursor.execute('INSERT INTO sentences (sentence) VALUES (?)', ('Текст для озвучки5',))
conn.commit()
conn.close()