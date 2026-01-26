# Keyboard Utilities for Vezer Shop
# ==================================

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Optional
from utils.translations import get_text


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard"""
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_main_menu_keyboard(lang: str, is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Main menu reply keyboard"""
    keyboard = [
        [KeyboardButton(get_text("btn_catalog", lang)), KeyboardButton(get_text("btn_cart", lang))],
        [KeyboardButton(get_text("btn_orders", lang)), KeyboardButton(get_text("btn_settings", lang))],
        [KeyboardButton(get_text("btn_help", lang))]
    ]
    
    if is_admin:
        keyboard.append([KeyboardButton(get_text("btn_admin", lang))])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_categories_keyboard(categories: list, lang: str) -> InlineKeyboardMarkup:
    """Categories navigation keyboard"""
    keyboard = []
    
    for cat in categories:
        name = cat.get_name(lang)
        keyboard.append([InlineKeyboardButton(name, callback_data=f"cat_{cat.id}")])
    
    keyboard.append([InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def get_product_keyboard(product_id: int, lang: str, 
                         page: int = 0, total_pages: int = 1,
                         category_id: int = None) -> InlineKeyboardMarkup:
    """Product view keyboard with add to cart and pagination"""
    keyboard = []
    
    # Add to cart button
    keyboard.append([
        InlineKeyboardButton(get_text("btn_add_to_cart", lang), callback_data=f"addcart_{product_id}")
    ])
    
    # Pagination
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(get_text("btn_prev", lang), callback_data=f"prodpage_{category_id}_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(get_text("btn_next", lang), callback_data=f"prodpage_{category_id}_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Back to category
    keyboard.append([InlineKeyboardButton(get_text("btn_back", lang), callback_data=f"cat_{category_id}")])
    keyboard.append([InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def get_products_list_keyboard(products: list, lang: str,
                               category_id: int,
                               page: int = 0, total_pages: int = 1) -> InlineKeyboardMarkup:
    """Products list in category with pagination"""
    keyboard = []
    
    for product in products:
        name = product.get_name(lang)
        if product.has_discount:
            name = f"🏷️ {name} (-{product.discount_percent}%)"
        keyboard.append([InlineKeyboardButton(name, callback_data=f"prod_{product.id}_{category_id}_{page}")])
    
    # Pagination
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(get_text("btn_prev", lang), callback_data=f"catpage_{category_id}_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(get_text("btn_next", lang), callback_data=f"catpage_{category_id}_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton(get_text("btn_back", lang), callback_data="catalog")])
    
    return InlineKeyboardMarkup(keyboard)


def get_cart_item_keyboard(product_id: int, quantity: int, lang: str) -> InlineKeyboardMarkup:
    """Cart item quantity control keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("➖", callback_data=f"cartminus_{product_id}"),
            InlineKeyboardButton(f"{quantity}", callback_data="cart_quantity"),
            InlineKeyboardButton("➕", callback_data=f"cartplus_{product_id}")
        ],
        [InlineKeyboardButton(get_text("btn_remove", lang), callback_data=f"cartremove_{product_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cart_keyboard(lang: str, has_items: bool = True) -> InlineKeyboardMarkup:
    """Cart main keyboard"""
    keyboard = []
    
    if has_items:
        keyboard.append([InlineKeyboardButton(get_text("btn_checkout", lang), callback_data="checkout")])
        keyboard.append([InlineKeyboardButton(get_text("btn_clear_cart", lang), callback_data="clear_cart")])
    
    keyboard.append([InlineKeyboardButton(get_text("btn_catalog", lang), callback_data="catalog")])
    keyboard.append([InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def get_settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Settings menu keyboard"""
    keyboard = [
        [InlineKeyboardButton(get_text("btn_change_language", lang), callback_data="change_language")],
        [InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Admin panel keyboard"""
    keyboard = [
        [InlineKeyboardButton(get_text("btn_add_product", lang), callback_data="admin_add_product")],
        [InlineKeyboardButton(get_text("btn_manage_products", lang), callback_data="admin_products")],
        [InlineKeyboardButton(get_text("btn_manage_categories", lang), callback_data="admin_categories")],
        [InlineKeyboardButton(get_text("btn_view_orders", lang), callback_data="admin_orders")],
        [InlineKeyboardButton(get_text("btn_statistics", lang), callback_data="admin_stats")],
        [InlineKeyboardButton(get_text("btn_broadcast", lang), callback_data="admin_broadcast")],
        [InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_categories_keyboard(categories: list, lang: str) -> InlineKeyboardMarkup:
    """Admin categories management keyboard"""
    keyboard = []
    
    for cat in categories:
        name = cat.get_name(lang)
        keyboard.append([
            InlineKeyboardButton(name, callback_data=f"admin_cat_{cat.id}"),
            InlineKeyboardButton("❌", callback_data=f"admin_delcat_{cat.id}")
        ])
    
    keyboard.append([InlineKeyboardButton("➕ Add Category", callback_data="admin_addcat")])
    keyboard.append([InlineKeyboardButton(get_text("btn_back", lang), callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(keyboard)


def get_admin_products_keyboard(products: list, lang: str) -> InlineKeyboardMarkup:
    """Admin products management keyboard"""
    keyboard = []
    
    for product in products:
        name = product.get_name(lang)
        keyboard.append([
            InlineKeyboardButton(name, callback_data=f"admin_prod_{product.id}"),
            InlineKeyboardButton("❌", callback_data=f"admin_delprod_{product.id}")
        ])
    
    keyboard.append([InlineKeyboardButton(get_text("btn_back", lang), callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(keyboard)


def get_admin_orders_keyboard(orders: list, lang: str) -> InlineKeyboardMarkup:
    """Admin orders list keyboard"""
    keyboard = []
    
    for order in orders[:10]:  # Show last 10 orders
        status_emoji = {"pending": "⏳", "confirmed": "✅", "shipped": "🚚", "delivered": "📦", "cancelled": "❌"}
        emoji = status_emoji.get(order.status, "📦")
        keyboard.append([
            InlineKeyboardButton(
                f"{emoji} #{order.id} - {order.total_amount:,.0f} so'm",
                callback_data=f"admin_order_{order.id}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(get_text("btn_back", lang), callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(keyboard)


def get_order_status_keyboard(order_id: int, lang: str) -> InlineKeyboardMarkup:
    """Order status update keyboard for admin"""
    keyboard = [
        [InlineKeyboardButton("⏳ Pending", callback_data=f"orderstatus_{order_id}_pending")],
        [InlineKeyboardButton("✅ Confirmed", callback_data=f"orderstatus_{order_id}_confirmed")],
        [InlineKeyboardButton("🚚 Shipped", callback_data=f"orderstatus_{order_id}_shipped")],
        [InlineKeyboardButton("📦 Delivered", callback_data=f"orderstatus_{order_id}_delivered")],
        [InlineKeyboardButton("❌ Cancelled", callback_data=f"orderstatus_{order_id}_cancelled")],
        [InlineKeyboardButton(get_text("btn_back", lang), callback_data="admin_orders")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_category_select_keyboard(categories: list, lang: str) -> InlineKeyboardMarkup:
    """Category selection for adding product"""
    keyboard = []
    
    for cat in categories:
        name = cat.get_name(lang)
        keyboard.append([InlineKeyboardButton(name, callback_data=f"selcat_{cat.id}")])
    
    keyboard.append([InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(keyboard)


def get_cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Simple cancel keyboard"""
    keyboard = [
        [InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_skip_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Skip keyboard for optional inputs"""
    keyboard = [
        [InlineKeyboardButton("⏭️ Skip", callback_data="skip")],
        [InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirm_keyboard(lang: str, confirm_data: str, cancel_data: str = "cancel") -> InlineKeyboardMarkup:
    """Confirmation keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes", callback_data=confirm_data),
            InlineKeyboardButton("❌ No", callback_data=cancel_data)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_phone_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Phone number request keyboard"""
    keyboard = [
        [KeyboardButton("📱 Send Phone Number", request_contact=True)],
        [KeyboardButton(get_text("btn_cancel", lang))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
