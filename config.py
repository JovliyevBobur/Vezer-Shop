# Vezer Shop Bot Configuration
# ============================

import os

# Bot Token
BOT_TOKEN = "8097749020:AAEF7lHjKbhinMK0XEo87JeMEBmhnHKTahU"

# Admin Telegram IDs - Only these users can access admin panel
ADMIN_IDS = [8254782802, 7267654564]

# Notification IDs - These users receive order notifications
NOTIFICATION_IDS = [7267654564, 8254782802]

# Payment Provider Token (get from BotFather via /mybots -> Payments)
# For testing, you can use Stripe test mode or other providers
PAYMENT_PROVIDER_TOKEN = ""  # Add your payment provider token here

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

# Sample Products for each category
SAMPLE_PRODUCTS = [
    # Kiyimlar (Clothing) - category_id: 1
    {
        "category_id": 1,
        "name_uz": "Erkaklar futbolkasi",
        "name_ru": "Мужская футболка",
        "name_en": "Men's T-Shirt",
        "description_uz": "Yumshoq paxta, zamonaviy dizayn",
        "description_ru": "Мягкий хлопок, современный дизайн",
        "description_en": "Soft cotton, modern design",
        "price": 89000,
        "discount_percent": 10,
        "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
        "sizes": "S,M,L,XL,XXL",
        "colors": "Qora,Oq,Ko'k,Qizil"
    },
    {
        "category_id": 1,
        "name_uz": "Ayollar ko'ylagi",
        "name_ru": "Женское платье",
        "name_en": "Women's Dress",
        "description_uz": "Elegant yozgi ko'ylak",
        "description_ru": "Элегантное летнее платье",
        "description_en": "Elegant summer dress",
        "price": 159000,
        "discount_percent": 0,
        "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400",
        "sizes": "XS,S,M,L,XL",
        "colors": "Qora,Pushti,Yashil"
    },
    {
        "category_id": 1,
        "name_uz": "Jinsi shim",
        "name_ru": "Джинсы",
        "name_en": "Jeans",
        "description_uz": "Klassik ko'k jinsi shim",
        "description_ru": "Классические синие джинсы",
        "description_en": "Classic blue jeans",
        "price": 199000,
        "discount_percent": 15,
        "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
        "sizes": "28,30,32,34,36",
        "colors": "Ko'k,Qora,Kulrang"
    },
    # Elektronika (Electronics) - category_id: 2
    {
        "category_id": 2,
        "name_uz": "Simsiz quloqchin",
        "name_ru": "Беспроводные наушники",
        "name_en": "Wireless Earbuds",
        "description_uz": "Bluetooth 5.0, 24 soat batareya",
        "description_ru": "Bluetooth 5.0, 24 часа автономной работы",
        "description_en": "Bluetooth 5.0, 24-hour battery",
        "price": 249000,
        "discount_percent": 20,
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400",
        "sizes": "",
        "colors": "Qora,Oq"
    },
    {
        "category_id": 2,
        "name_uz": "Smart soat",
        "name_ru": "Смарт-часы",
        "name_en": "Smart Watch",
        "description_uz": "Yurak urishi, qadamlar, uyqu kuzatuvi",
        "description_ru": "Пульс, шаги, мониторинг сна",
        "description_en": "Heart rate, steps, sleep monitoring",
        "price": 450000,
        "discount_percent": 0,
        "image_url": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=400",
        "sizes": "",
        "colors": "Qora,Kumush,Oltin"
    },
    {
        "category_id": 2,
        "name_uz": "Portativ quvvat banki",
        "name_ru": "Портативный аккумулятор",
        "name_en": "Power Bank",
        "description_uz": "10000mAh, tez quvvatlash",
        "description_ru": "10000mAh, быстрая зарядка",
        "description_en": "10000mAh, fast charging",
        "price": 129000,
        "discount_percent": 5,
        "image_url": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=400",
        "sizes": "",
        "colors": "Qora,Oq,Ko'k"
    },
    # Aksessuarlar (Accessories) - category_id: 3
    {
        "category_id": 3,
        "name_uz": "Charm sumka",
        "name_ru": "Кожаная сумка",
        "name_en": "Leather Bag",
        "description_uz": "Tabiiy charm, klassik dizayn",
        "description_ru": "Натуральная кожа, классический дизайн",
        "description_en": "Genuine leather, classic design",
        "price": 350000,
        "discount_percent": 0,
        "image_url": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400",
        "sizes": "",
        "colors": "Jigarrang,Qora,Sariq"
    },
    {
        "category_id": 3,
        "name_uz": "Quyosh ko'zoynak",
        "name_ru": "Солнцезащитные очки",
        "name_en": "Sunglasses",
        "description_uz": "UV himoya, zamonaviy dizayn",
        "description_ru": "UV защита, современный дизайн",
        "description_en": "UV protection, modern design",
        "price": 89000,
        "discount_percent": 10,
        "image_url": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400",
        "sizes": "",
        "colors": "Qora,Jigarrang,Ko'k"
    },
    {
        "category_id": 3,
        "name_uz": "Kamar",
        "name_ru": "Ремень",
        "name_en": "Belt",
        "description_uz": "Charm kamar, metall tokasi",
        "description_ru": "Кожаный ремень, металлическая пряжка",
        "description_en": "Leather belt, metal buckle",
        "price": 79000,
        "discount_percent": 0,
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400",
        "sizes": "S,M,L,XL",
        "colors": "Qora,Jigarrang"
    },
    # Poyabzallar (Footwear) - category_id: 4
    {
        "category_id": 4,
        "name_uz": "Sport krossovka",
        "name_ru": "Спортивные кроссовки",
        "name_en": "Sports Sneakers",
        "description_uz": "Yengil va qulay, yugurish uchun ideal",
        "description_ru": "Легкие и удобные, идеально для бега",
        "description_en": "Lightweight and comfortable, ideal for running",
        "price": 299000,
        "discount_percent": 15,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
        "sizes": "38,39,40,41,42,43,44",
        "colors": "Qora,Oq,Qizil,Ko'k"
    },
    {
        "category_id": 4,
        "name_uz": "Klassik tufli",
        "name_ru": "Классические туфли",
        "name_en": "Classic Shoes",
        "description_uz": "Rasmiy tadbirlar uchun charm tufli",
        "description_ru": "Кожаные туфли для официальных мероприятий",
        "description_en": "Leather shoes for formal events",
        "price": 399000,
        "discount_percent": 0,
        "image_url": "https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=400",
        "sizes": "39,40,41,42,43,44",
        "colors": "Qora,Jigarrang"
    },
    {
        "category_id": 4,
        "name_uz": "Yozgi shippak",
        "name_ru": "Летние шлёпанцы",
        "name_en": "Summer Sandals",
        "description_uz": "Qulay yozgi poyabzal",
        "description_ru": "Удобная летняя обувь",
        "description_en": "Comfortable summer footwear",
        "price": 69000,
        "discount_percent": 0,
        "image_url": "https://images.unsplash.com/photo-1603487742131-4160ec999306?w=400",
        "sizes": "36,37,38,39,40,41,42,43",
        "colors": "Qora,Oq,Ko'k,Yashil"
    }
]

