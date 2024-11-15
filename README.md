# Voice Recording Telegram Bot

This is a Telegram bot that sends texts to users and collects voice recordings of these texts.

## Setup Instructions

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install required dependencies:
```bash
pip install python-telegram-bot
```

3. Set your Telegram bot token as environment variable:
```bash
export BOT_TOKEN='your_bot_token_here'
```

4. Initialize the database with sentences:
```bash
python insert_sentences.py
```

5. Start the bot:
```bash
python main.py
```

## Requirements
- Python 3.7+
- python-telegram-bot
- SQLite3 (included with Python)
