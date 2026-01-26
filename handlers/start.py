# Start Handler - Welcome and Language Selection
# ==============================================

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from database import get_or_create_user, update_user_language, get_user, is_user_registered
from utils import get_text, get_language_keyboard, get_main_menu_keyboard
from config import ADMIN_IDS

# Import registration states for return
from handlers.registration import (
    REG_FIRST_NAME, start_registration
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - welcome user and show language selection"""
    user = update.effective_user
    
    # Get or create user in database
    db_user = await get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Get user's name for personalized greeting
    name = user.first_name or user.username or "Guest"
    lang = db_user.language if db_user else "uz"
    
    # Send welcome message with language selection
    welcome_text = get_text("welcome", lang, name=name)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_language_keyboard()
    )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle language selection callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    callback_data = query.data
    
    # Extract language from callback data (lang_uz, lang_ru, lang_en)
    lang = callback_data.split("_")[1]
    
    # Update user language in database
    await update_user_language(user_id, lang)
    
    # Check if user is registered
    is_registered = await is_user_registered(user_id)
    
    # Send confirmation
    await query.edit_message_text(
        get_text("language_selected", lang),
        parse_mode="HTML"
    )
    
    if not is_registered:
        # Start registration process
        return await start_registration(update, context, lang)
    
    # User is registered, show main menu
    is_admin = user_id in ADMIN_IDS
    
    # Send main menu with reply keyboard
    await query.message.reply_text(
        get_text("main_menu", lang),
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(lang, is_admin)
    )
    
    return ConversationHandler.END



async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu callback - return to main menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    is_admin = user_id in ADMIN_IDS
    
    await query.edit_message_text(
        get_text("main_menu", lang),
        parse_mode="HTML"
    )
    
    await query.message.reply_text(
        "⬇️",
        reply_markup=get_main_menu_keyboard(lang, is_admin)
    )


async def handle_main_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu reply keyboard buttons"""
    from handlers.catalog import show_catalog
    from handlers.cart import show_cart
    from handlers.admin import show_admin_panel
    
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    text = update.message.text
    
    # Check which button was pressed
    if text == get_text("btn_catalog", lang):
        await show_catalog(update, context)
    
    elif text == get_text("btn_cart", lang):
        await show_cart(update, context)
    
    elif text == get_text("btn_orders", lang):
        await show_user_orders(update, context)
    
    elif text == get_text("btn_settings", lang):
        await show_settings(update, context)
    
    elif text == get_text("btn_help", lang):
        await show_help(update, context)
    
    elif text == get_text("btn_admin", lang):
        await show_admin_panel(update, context)


async def show_user_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's order history"""
    from database import get_user_orders
    from config import ORDER_STATUS
    
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    orders = await get_user_orders(user_id)
    
    if not orders:
        await update.message.reply_text(
            get_text("orders_empty", lang),
            parse_mode="HTML"
        )
        return
    
    text = get_text("orders_title", lang) + "\n\n"
    
    for order in orders[:10]:  # Show last 10 orders
        status_text = ORDER_STATUS.get(order.status, {}).get(lang, order.status)
        order_text = get_text("order_item", lang,
            id=order.id,
            date=order.created_at.strftime("%d.%m.%Y"),
            total=f"{order.total_amount:,.0f}".replace(",", " "),
            status=status_text
        )
        text += order_text + "\n\n" + "─" * 20 + "\n\n"
    
    await update.message.reply_text(text, parse_mode="HTML")


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show settings menu"""
    from utils import get_settings_keyboard
    
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    await update.message.reply_text(
        get_text("settings_title", lang),
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(lang)
    )


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle settings callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    if query.data == "change_language":
        await query.edit_message_text(
            get_text("select_language", lang),
            parse_mode="HTML",
            reply_markup=get_language_keyboard()
        )


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help information"""
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    await update.message.reply_text(
        get_text("help_text", lang),
        parse_mode="HTML"
    )
