# Voice Recording Telegram Bot | Telegram-бот для записи голоса

[English](#english) | [Русский](#russian)

<a name="english"></a>
# English

This is a Telegram bot that sends texts to users and collects voice recordings of these texts.

## Available Commands

- `/start` - Begin interaction with the bot and receive your first text to record
- `/mystat` - View your personal recording statistics (total recordings, today's count, weekly count, monthly count)
- `/insert` - Upload new sentences from a text file (admin only)
- `/download` - Download archive of all recorded audio files with metadata (admin only)

## Setup Instructions

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the bot by editing `config.yaml`:
```yaml
service_name: "voice_bot"  # Service name for systemd
bot_token: "YOUR_BOT_TOKEN_HERE"  # Your Telegram bot token
authorized_users:  # List of admin usernames
  - username1
  - username2
default_language: "ba"  # Default bot language
notifications:
  enabled: true
  interval_hours: 24
```

4. You can start the bot in two ways:

Method 1 - Using Make (recommended):
```bash
make init    # First time setup
make start   # Start the bot
make stop    # Stop the bot
make restart # Restart the bot
make logs    # View bot logs
```

Method 2 - Manual start:
```bash
python main.py
```

## Requirements
- Python 3.7+
- python-telegram-bot
- SQLite3 (included with Python)
- PyYAML

## Configuration

Create a `config.yaml` file to configure:
- Authorized users who can use admin commands
- Default language for bot messages
- Notification settings

Example config.yaml:
```yaml
authorized_users:
  - username1
  - username2
default_language: "ba"  # Available: "ba", "en", "ru", "mhr"
notifications:
  enabled: true
  interval_hours: 24
```

## Localization

The bot supports multiple languages:
- Bashkir (ba)
- English (en)
- Russian (ru)
- Mari (mhr)

Language-specific messages are stored in YAML files in the `locales` directory. To add a new language:
1. Create a new YAML file in `locales` directory (e.g., `de.yaml` for German)
2. Copy the structure from an existing language file
3. Translate all messages to the new language

## Usage Instructions

1. Start the bot with `/start` command
2. The bot will send you a text to record
3. Record and send a voice message with your reading of the text
4. The bot will automatically send you the next text to record
5. Use `/mystat` to track your recording progress
6. Administrators can use `/insert` to add new texts and `/download` to get all recordings

---

<a name="russian"></a>
# Русский

Это Telegram-бот, который отправляет пользователям тексты и собирает голосовые записи этих текстов.

## Доступные команды

- `/start` - Начать взаимодействие с ботом и получить первый текст для записи
- `/mystat` - Просмотр личной статистики записей (общее количество, записи за день, неделю, месяц)
- `/insert` - Загрузка новых предложений из текстового файла (только для администраторов)
- `/download` - Скачать архив всех записанных аудиофайлов с метаданными (только для администраторов)

## Инструкции по установке и запуску

Есть два способа установки и запуска бота:

### Способ 1 - Установка через Makefile (рекомендуется)

Этот способ автоматически настраивает systemd-сервис для автозапуска бота:

1. Настройте бота, отредактировав `config.yaml`:
```yaml
service_name: "voice_bot"  # Имя сервиса для systemd
bot_token: "YOUR_BOT_TOKEN_HERE"  # Ваш токен Telegram бота
authorized_users:  # Список администраторов
  - username1
  - username2
default_language: "ba"  # Язык бота по умолчанию
notifications:
  enabled: true
  interval_hours: 24
```

2. Выполните команды:
```bash
make init    # Первоначальная установка (создает venv, устанавливает зависимости и настраивает systemd)
make start   # Запуск бота как systemd-сервис
```

Дополнительные команды для управления:
```bash
make stop    # Остановка бота
make restart # Перезапуск бота
make logs    # Просмотр логов
```

### Способ 2 - Ручная установка

1. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate
```

2. Установите необходимые зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте бота, отредактировав `config.yaml` как описано выше

4. Запустите бота вручную:
```bash
python main.py
```

При ручном запуске бот будет работать только пока активна сессия терминала. Для постоянной работы рекомендуется использовать Способ 1.

## Требования
- Python 3.7+
- python-telegram-bot
- SQLite3 (включен в Python)
- PyYAML

## Конфигурация

Создайте файл `config.yaml` для настройки:
- Авторизованных пользователей с правами администратора
- Языка по умолчанию для сообщений бота
- Настроек уведомлений

Пример config.yaml:
```yaml
authorized_users:
  - username1
  - username2
default_language: "ba"  # Доступные: "ba", "en", "ru", "mhr"
notifications:
  enabled: true
  interval_hours: 24
```

## Локализация

Бот поддерживает несколько языков:
- Башкирский (ba)
- Русский (ru)
- Марийский (mhr)
- Английский (en)

Сообщения для каждого языка хранятся в YAML-файлах в директории `locales`. Чтобы добавить новый язык:
1. Создайте новый YAML-файл в директории `locales` (например, `de.yaml` для немецкого)
2. Скопируйте структуру из существующего языкового файла
3. Переведите все сообщения на новый язык

## Инструкции по использованию

1. Начните работу с ботом командой `/start`
2. Бот отправит вам текст для записи
3. Запишите и отправьте голосовое сообщение с вашим прочтением текста
4. Бот автоматически отправит вам следующий текст для записи
5. Используйте `/mystat` для отслеживания прогресса записей
6. Администраторы могут использовать `/insert` для добавления новых текстов и `/download` для получения всех записей
