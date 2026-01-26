# Cart Handler - Shopping Cart Functionality
# ==========================================

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from database import (
    get_user, get_cart_items, get_cart_total,
    update_cart_quantity, remove_from_cart, clear_cart,
    create_order
)
from utils import get_text, format_price, get_cart_keyboard, get_main_menu_keyboard
from config import ADMIN_IDS

# Conversation states for checkout
PHONE, ADDRESS = range(2)


async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's shopping cart"""
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    cart_items = await get_cart_items(user_id)
    
    if not cart_items:
        text = get_text("cart_empty", lang)
        keyboard = get_cart_keyboard(lang, has_items=False)
    else:
        text = get_text("cart_title", lang) + "\n\n"
        
        total = 0
        for item in cart_items:
            if item.product:
                item_total = item.product.discounted_price * item.quantity
                total += item_total
                text += get_text("cart_item", lang,
                    name=item.product.get_name(lang),
                    quantity=item.quantity,
                    price=format_price(item_total)
                ) + "\n"
        
        text += get_text("cart_total", lang, total=format_price(total))
        keyboard = get_cart_keyboard(lang, has_items=True)
    
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


async def cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle cart view callback"""
    query = update.callback_query
    await query.answer()
    await show_cart(update, context)


async def cart_plus_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Increase cart item quantity"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    product_id = int(query.data.split("_")[1])
    
    # Get current cart items to find quantity
    cart_items = await get_cart_items(user_id)
    for item in cart_items:
        if item.product_id == product_id:
            await update_cart_quantity(user_id, product_id, item.quantity + 1)
            break
    
    await show_cart(update, context)


async def cart_minus_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Decrease cart item quantity"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    product_id = int(query.data.split("_")[1])
    
    # Get current cart items to find quantity
    cart_items = await get_cart_items(user_id)
    for item in cart_items:
        if item.product_id == product_id:
            new_quantity = item.quantity - 1
            if new_quantity <= 0:
                await remove_from_cart(user_id, product_id)
            else:
                await update_cart_quantity(user_id, product_id, new_quantity)
            break
    
    await show_cart(update, context)


async def cart_remove_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove item from cart"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    product_id = int(query.data.split("_")[1])
    
    await remove_from_cart(user_id, product_id)
    await show_cart(update, context)


async def clear_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear entire cart"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    await clear_cart(user_id)
    
    await query.edit_message_text(
        get_text("cart_cleared", lang),
        parse_mode="HTML",
        reply_markup=get_cart_keyboard(lang, has_items=False)
    )


async def checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start checkout process - ask for phone"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    # Check if cart has items
    cart_items = await get_cart_items(user_id)
    if not cart_items:
        await query.edit_message_text(get_text("cart_empty", lang))
        return ConversationHandler.END
    
    context.user_data["checkout_lang"] = lang
    
    await query.edit_message_text(
        get_text("checkout_phone", lang),
        parse_mode="HTML"
    )
    
    return PHONE


async def checkout_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive phone and ask for address"""
    lang = context.user_data.get("checkout_lang", "uz")
    
    # Get phone from message or contact
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text
    
    context.user_data["checkout_phone"] = phone
    
    await update.message.reply_text(
        get_text("checkout_address", lang),
        parse_mode="HTML"
    )
    
    return ADDRESS


async def checkout_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive address and create order"""
    user_id = update.effective_user.id
    lang = context.user_data.get("checkout_lang", "uz")
    phone = context.user_data.get("checkout_phone", "")
    address = update.message.text
    
    # Create order
    order = await create_order(user_id, phone=phone, address=address)
    
    if order:
        is_admin = user_id in ADMIN_IDS
        
        await update.message.reply_text(
            get_text("order_created", lang,
                order_id=order.id,
                phone=phone,
                address=address,
                total=format_price(order.total_amount)
            ),
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(lang, is_admin)
        )
        
        # Notify admins about new order
        from telegram import Bot
        from config import BOT_TOKEN
        
        bot = Bot(token=BOT_TOKEN)
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"🆕 <b>New Order #{order.id}</b>\n\n"
                    f"📱 Phone: {phone}\n"
                    f"📍 Address: {address}\n"
                    f"💰 Total: {format_price(order.total_amount)} so'm",
                    parse_mode="HTML"
                )
            except Exception:
                pass
    else:
        await update.message.reply_text(
            get_text("error_occurred", lang),
            parse_mode="HTML"
        )
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END


async def checkout_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel checkout process"""
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    is_admin = user_id in ADMIN_IDS
    
    context.user_data.clear()
    
    await update.message.reply_text(
        get_text("cancelled", lang),
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(lang, is_admin)
    )
    
    return ConversationHandler.END
