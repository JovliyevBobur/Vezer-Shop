# Vezer Shop Bot Configuration
# ============================

import os

# Bot Token
BOT_TOKEN = "8097749020:AAEF7lHjKbhinMK0XEo87JeMEBmhnHKTahU"

# Admin Telegram IDs - Only these users can access admin panel
ADMIN_IDS = [8254782802, 7267654564]

# Database Configuration
DATABASE_URL = "sqlite+aiosqlite:///./vezer_shop.db"

# Default Language
DEFAULT_LANGUAGE = "uz"

# Supported Languages
LANGUAGES = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский", 
    "en": "🇬🇧 English"
}

# Shop Settings
SHOP_NAME = "Vezer Shop"
CURRENCY = "so'm"
CURRENCY_SYMBOL = "💰"

# Pagination
PRODUCTS_PER_PAGE = 5
ORDERS_PER_PAGE = 10

# Order Statuses
ORDER_STATUS = {
    "pending": {"uz": "⏳ Kutilmoqda", "ru": "⏳ Ожидает", "en": "⏳ Pending"},
    "confirmed": {"uz": "✅ Tasdiqlandi", "ru": "✅ Подтверждён", "en": "✅ Confirmed"},
    "shipped": {"uz": "🚚 Yetkazilmoqda", "ru": "🚚 Отправлен", "en": "🚚 Shipped"},
    "delivered": {"uz": "📦 Yetkazildi", "ru": "📦 Доставлен", "en": "📦 Delivered"},
    "cancelled": {"uz": "❌ Bekor qilindi", "ru": "❌ Отменён", "en": "❌ Cancelled"}
}

# Default Categories with Emojis
DEFAULT_CATEGORIES = [
    {"name_uz": "👕 Kiyimlar", "name_ru": "👕 Одежда", "name_en": "👕 Clothes"},
    {"name_uz": "📱 Elektronika", "name_ru": "📱 Электроника", "name_en": "📱 Electronics"},
    {"name_uz": "👜 Aksessuarlar", "name_ru": "👜 Аксессуары", "name_en": "👜 Accessories"},
    {"name_uz": "👟 Poyabzallar", "name_ru": "👟 Обувь", "name_en": "👟 Footwear"},
]
