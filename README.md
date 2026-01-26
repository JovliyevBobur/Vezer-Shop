# Vezer Shop Telegram Bot
# ========================

Professional e-commerce Telegram bot for selling clothes, electronics, and accessories.

## Features

- 🌐 Multi-language support (Uzbek, Russian, English)
- 🛒 Product catalog with categories
- 💰 Discount system
- 🛍️ Shopping cart
- 📦 Order management
- 🔐 Admin panel

## Installation

```bash
pip install python-telegram-bot sqlalchemy aiosqlite
```

## Running the Bot

```bash
python main.py
```

## Project Structure

```
vezer shop/
├── main.py              # Main entry point
├── config.py            # Bot configuration
├── database/
│   ├── __init__.py
│   ├── db.py           # Database operations
│   └── models.py       # SQLAlchemy models
├── handlers/
│   ├── __init__.py
│   ├── start.py        # Start and menu handlers
│   ├── catalog.py      # Product browsing
│   ├── cart.py         # Shopping cart
│   └── admin.py        # Admin panel
└── utils/
    ├── __init__.py
    ├── keyboards.py    # Keyboard utilities
    └── translations.py # Multi-language translations
```

## Admin Commands

- `/admin` - Open admin panel
- Add/edit/delete products
- Manage categories
- View orders and update status
- Broadcast messages to users
- View statistics

## Bot Commands

- `/start` - Start the bot and select language
