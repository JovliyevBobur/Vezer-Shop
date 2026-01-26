# Admin Handler - Admin Panel Functionality
# =========================================

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from database import (
    get_user, get_all_categories, get_all_products,
    get_all_orders, get_order, update_order_status,
    get_user_count, get_order_count, get_total_revenue,
    create_product, delete_product, get_all_users,
    create_category, delete_category
)
from utils import (
    get_text, format_price, get_admin_keyboard,
    get_admin_categories_keyboard, get_admin_products_keyboard,
    get_admin_orders_keyboard, get_order_status_keyboard,
    get_category_select_keyboard, get_cancel_keyboard,
    get_main_menu_keyboard
)
from config import ADMIN_IDS

# Conversation states for adding product
(ADD_PROD_NAME_UZ, ADD_PROD_NAME_RU, ADD_PROD_NAME_EN,
 ADD_PROD_DESC_UZ, ADD_PROD_DESC_RU, ADD_PROD_DESC_EN,
 ADD_PROD_PRICE, ADD_PROD_DISCOUNT, ADD_PROD_IMAGE, ADD_PROD_CATEGORY) = range(10)

# Conversation states for broadcast
BROADCAST_MESSAGE = 20

# Conversation states for adding category
ADD_CAT_NAME_UZ, ADD_CAT_NAME_RU, ADD_CAT_NAME_EN = range(30, 33)


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS


async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin panel"""
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    if not is_admin(user_id):
        text = get_text("admin_not_authorized", lang)
        if update.callback_query:
            await update.callback_query.answer(text, show_alert=True)
        else:
            await update.message.reply_text(text)
        return
    
    text = get_text("admin_welcome", lang)
    keyboard = get_admin_keyboard(lang)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )


async def admin_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle admin panel callback"""
    query = update.callback_query
    await query.answer()
    await show_admin_panel(update, context)


async def admin_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show statistics"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    user_count = await get_user_count()
    order_count = await get_order_count()
    revenue = await get_total_revenue()
    
    text = get_text("statistics", lang,
        users=user_count,
        orders=order_count,
        revenue=format_price(revenue)
    )
    
    keyboard = get_admin_keyboard(lang)
    
    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def admin_categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show categories management"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    categories = await get_all_categories()
    keyboard = get_admin_categories_keyboard(categories, lang)
    
    await query.edit_message_text(
        "📁 <b>Categories Management</b>\n\nSelect a category to edit or delete:",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def admin_delete_category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete category"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    category_id = int(query.data.split("_")[2])
    await delete_category(category_id)
    
    # Refresh categories view
    await admin_categories_callback(update, context)


async def admin_products_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show products management"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    products = await get_all_products()
    keyboard = get_admin_products_keyboard(products, lang)
    
    await query.edit_message_text(
        "📝 <b>Products Management</b>\n\nSelect a product to edit or delete:",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def admin_delete_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete product"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    product_id = int(query.data.split("_")[2])
    await delete_product(product_id)
    
    await query.answer(get_text("product_deleted", lang), show_alert=True)
    
    # Refresh products view
    await admin_products_callback(update, context)


async def admin_orders_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show orders list"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    orders = await get_all_orders()
    keyboard = get_admin_orders_keyboard(orders, lang)
    
    await query.edit_message_text(
        "📦 <b>Orders</b>\n\nSelect an order to manage:",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def admin_order_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show order details"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    order_id = int(query.data.split("_")[2])
    order = await get_order(order_id)
    
    if not order:
        await query.answer("Order not found", show_alert=True)
        return
    
    text = f"📦 <b>Order #{order.id}</b>\n\n"
    text += f"📅 Date: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
    text += f"📱 Phone: {order.phone or 'N/A'}\n"
    text += f"📍 Address: {order.address or 'N/A'}\n"
    text += f"📊 Status: {order.status}\n"
    text += f"💰 Total: {format_price(order.total_amount)} so'm\n\n"
    text += "Update status:"
    
    keyboard = get_order_status_keyboard(order_id, lang)
    
    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def update_order_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Update order status"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    # orderstatus_1_pending
    parts = query.data.split("_")
    order_id = int(parts[1])
    new_status = parts[2]
    
    await update_order_status(order_id, new_status)
    
    await query.answer(f"Status updated to {new_status}", show_alert=True)
    
    # Refresh order view
    await admin_orders_callback(update, context)


# ==========================================
# Add Product Conversation
# ==========================================

async def start_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start adding product - ask for Uzbek name"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return ConversationHandler.END
    
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    context.user_data["admin_lang"] = lang
    context.user_data["new_product"] = {}
    
    await query.edit_message_text(
        get_text("enter_product_name_uz", lang),
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(lang)
    )
    
    return ADD_PROD_NAME_UZ


async def add_product_name_uz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive Uzbek name, ask for Russian name"""
    lang = context.user_data.get("admin_lang", "uz")
    context.user_data["new_product"]["name_uz"] = update.message.text
    
    await update.message.reply_text(
        get_text("enter_product_name_ru", lang),
        parse_mode="HTML"
    )
    
    return ADD_PROD_NAME_RU


async def add_product_name_ru(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive Russian name, ask for English name"""
    lang = context.user_data.get("admin_lang", "uz")
    context.user_data["new_product"]["name_ru"] = update.message.text
    
    await update.message.reply_text(
        get_text("enter_product_name_en", lang),
        parse_mode="HTML"
    )
    
    return ADD_PROD_NAME_EN


async def add_product_name_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive English name, ask for Uzbek description"""
    lang = context.user_data.get("admin_lang", "uz")
    context.user_data["new_product"]["name_en"] = update.message.text
    
    await update.message.reply_text(
        get_text("enter_product_desc_uz", lang),
        parse_mode="HTML"
    )
    
    return ADD_PROD_DESC_UZ


async def add_product_desc_uz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive Uzbek description, ask for Russian description"""
    lang = context.user_data.get("admin_lang", "uz")
    context.user_data["new_product"]["description_uz"] = update.message.text
    
    await update.message.reply_text(
        get_text("enter_product_desc_ru", lang),
        parse_mode="HTML"
    )
    
    return ADD_PROD_DESC_RU


async def add_product_desc_ru(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive Russian description, ask for English description"""
    lang = context.user_data.get("admin_lang", "uz")
    context.user_data["new_product"]["description_ru"] = update.message.text
    
    await update.message.reply_text(
        get_text("enter_product_desc_en", lang),
        parse_mode="HTML"
    )
    
    return ADD_PROD_DESC_EN


async def add_product_desc_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive English description, ask for price"""
    lang = context.user_data.get("admin_lang", "uz")
    context.user_data["new_product"]["description_en"] = update.message.text
    
    await update.message.reply_text(
        get_text("enter_product_price", lang),
        parse_mode="HTML"
    )
    
    return ADD_PROD_PRICE


async def add_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive price, ask for discount"""
    lang = context.user_data.get("admin_lang", "uz")
    
    try:
        price = float(update.message.text.replace(" ", "").replace(",", ""))
        context.user_data["new_product"]["price"] = price
    except ValueError:
        await update.message.reply_text(get_text("invalid_input", lang))
        return ADD_PROD_PRICE
    
    await update.message.reply_text(
        get_text("enter_product_discount", lang),
        parse_mode="HTML"
    )
    
    return ADD_PROD_DISCOUNT


async def add_product_discount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive discount, ask for image"""
    lang = context.user_data.get("admin_lang", "uz")
    
    try:
        discount = int(update.message.text)
        if discount < 0 or discount > 100:
            raise ValueError
        context.user_data["new_product"]["discount_percent"] = discount
    except ValueError:
        context.user_data["new_product"]["discount_percent"] = 0
    
    await update.message.reply_text(
        get_text("enter_product_image", lang),
        parse_mode="HTML"
    )
    
    return ADD_PROD_IMAGE


async def add_product_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive image, ask for category"""
    lang = context.user_data.get("admin_lang", "uz")
    
    # Handle image
    if update.message.photo:
        # Get file ID of largest photo
        photo = update.message.photo[-1]
        context.user_data["new_product"]["image_url"] = photo.file_id
    elif update.message.text and update.message.text != "/skip":
        context.user_data["new_product"]["image_url"] = update.message.text
    else:
        context.user_data["new_product"]["image_url"] = None
    
    # Show category selection
    categories = await get_all_categories()
    keyboard = get_category_select_keyboard(categories, lang)
    
    await update.message.reply_text(
        get_text("select_category", lang),
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    return ADD_PROD_CATEGORY


async def add_product_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive category and create product"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = context.user_data.get("admin_lang", "uz")
    
    if query.data == "cancel":
        await query.edit_message_text(get_text("cancelled", lang))
        context.user_data.clear()
        return ConversationHandler.END
    
    # selcat_1
    category_id = int(query.data.split("_")[1])
    product_data = context.user_data.get("new_product", {})
    
    # Create product
    await create_product(
        category_id=category_id,
        name_uz=product_data.get("name_uz", ""),
        name_ru=product_data.get("name_ru", ""),
        name_en=product_data.get("name_en", ""),
        description_uz=product_data.get("description_uz", ""),
        description_ru=product_data.get("description_ru", ""),
        description_en=product_data.get("description_en", ""),
        price=product_data.get("price", 0),
        discount_percent=product_data.get("discount_percent", 0),
        image_url=product_data.get("image_url"),
        stock=100
    )
    
    await query.edit_message_text(
        get_text("product_added", lang),
        parse_mode="HTML"
    )
    
    context.user_data.clear()
    
    # Show admin panel again
    await query.message.reply_text(
        get_text("admin_welcome", lang),
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(lang)
    )
    
    return ConversationHandler.END


# ==========================================
# Broadcast Conversation
# ==========================================

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start broadcast - ask for message"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return ConversationHandler.END
    
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    context.user_data["admin_lang"] = lang
    
    await query.edit_message_text(
        get_text("broadcast_enter_message", lang),
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(lang)
    )
    
    return BROADCAST_MESSAGE


async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send broadcast message to all users"""
    lang = context.user_data.get("admin_lang", "uz")
    message_text = update.message.text
    
    users = await get_all_users()
    sent_count = 0
    
    for user in users:
        try:
            await update.message.bot.send_message(
                user.telegram_id,
                f"📢 <b>Vezer Shop</b>\n\n{message_text}",
                parse_mode="HTML"
            )
            sent_count += 1
        except Exception:
            pass
    
    await update.message.reply_text(
        get_text("broadcast_sent", lang, count=sent_count),
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(lang)
    )
    
    context.user_data.clear()
    return ConversationHandler.END


# ==========================================
# Add Category Conversation
# ==========================================

async def start_add_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start adding category"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return ConversationHandler.END
    
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    context.user_data["admin_lang"] = lang
    context.user_data["new_category"] = {}
    
    await query.edit_message_text(
        "📁 Enter category name (Uzbek):",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(lang)
    )
    
    return ADD_CAT_NAME_UZ


async def add_category_name_uz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive Uzbek name"""
    context.user_data["new_category"]["name_uz"] = update.message.text
    
    await update.message.reply_text(
        "📁 Enter category name (Russian):",
        parse_mode="HTML"
    )
    
    return ADD_CAT_NAME_RU


async def add_category_name_ru(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive Russian name"""
    context.user_data["new_category"]["name_ru"] = update.message.text
    
    await update.message.reply_text(
        "📁 Enter category name (English):",
        parse_mode="HTML"
    )
    
    return ADD_CAT_NAME_EN


async def add_category_name_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive English name and create category"""
    lang = context.user_data.get("admin_lang", "uz")
    context.user_data["new_category"]["name_en"] = update.message.text
    
    cat_data = context.user_data.get("new_category", {})
    
    await create_category(
        name_uz=cat_data.get("name_uz", ""),
        name_ru=cat_data.get("name_ru", ""),
        name_en=cat_data.get("name_en", "")
    )
    
    await update.message.reply_text(
        "✅ Category added successfully!",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(lang)
    )
    
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel any admin conversation"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        db_user = await get_user(user_id)
        lang = db_user.language if db_user else "uz"
        
        await query.edit_message_text(
            get_text("cancelled", lang),
            parse_mode="HTML"
        )
        
        await query.message.reply_text(
            get_text("admin_welcome", lang),
            parse_mode="HTML",
            reply_markup=get_admin_keyboard(lang)
        )
    else:
        user_id = update.effective_user.id
        db_user = await get_user(user_id)
        lang = db_user.language if db_user else "uz"
        
        await update.message.reply_text(
            get_text("cancelled", lang),
            parse_mode="HTML",
            reply_markup=get_admin_keyboard(lang)
        )
    
    context.user_data.clear()
    return ConversationHandler.END
