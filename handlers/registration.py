# Registration Handler - Mandatory User Registration Flow
# =======================================================

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from database import get_user, update_user_registration
from utils import get_text, get_main_menu_keyboard
from config import ADMIN_IDS, NOTIFICATION_IDS

# Registration conversation states
REG_FIRST_NAME, REG_LAST_NAME, REG_AGE, REG_PHONE, REG_LOCATION = range(5)


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str) -> int:
    """Start the registration process after language selection"""
    context.user_data["registration_lang"] = lang
    
    await update.callback_query.message.reply_text(
        get_text("reg_welcome", lang),
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    
    await update.callback_query.message.reply_text(
        get_text("reg_first_name", lang),
        parse_mode="HTML"
    )
    
    return REG_FIRST_NAME


async def reg_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive first name and ask for last name"""
    lang = context.user_data.get("registration_lang", "uz")
    first_name = update.message.text.strip()
    
    if len(first_name) < 2:
        await update.message.reply_text(
            get_text("reg_invalid_name", lang),
            parse_mode="HTML"
        )
        return REG_FIRST_NAME
    
    context.user_data["reg_first_name"] = first_name
    
    await update.message.reply_text(
        get_text("reg_last_name", lang),
        parse_mode="HTML"
    )
    
    return REG_LAST_NAME


async def reg_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive last name and ask for age"""
    lang = context.user_data.get("registration_lang", "uz")
    last_name = update.message.text.strip()
    
    if len(last_name) < 2:
        await update.message.reply_text(
            get_text("reg_invalid_name", lang),
            parse_mode="HTML"
        )
        return REG_LAST_NAME
    
    context.user_data["reg_last_name"] = last_name
    
    await update.message.reply_text(
        get_text("reg_age", lang),
        parse_mode="HTML"
    )
    
    return REG_AGE


async def reg_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive age and ask for phone"""
    lang = context.user_data.get("registration_lang", "uz")
    
    try:
        age = int(update.message.text.strip())
        if age < 10 or age > 100:
            raise ValueError()
    except ValueError:
        await update.message.reply_text(
            get_text("reg_invalid_age", lang),
            parse_mode="HTML"
        )
        return REG_AGE
    
    context.user_data["reg_age"] = age
    
    # Create phone request keyboard
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(get_text("btn_send_phone", lang), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await update.message.reply_text(
        get_text("reg_phone", lang),
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    return REG_PHONE


async def reg_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive phone and ask for location"""
    lang = context.user_data.get("registration_lang", "uz")
    
    # Get phone from contact or text
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()
        # Basic phone validation
        phone_digits = ''.join(filter(str.isdigit, phone))
        if len(phone_digits) < 9:
            await update.message.reply_text(
                get_text("reg_invalid_phone", lang),
                parse_mode="HTML"
            )
            return REG_PHONE
    
    context.user_data["reg_phone"] = phone
    
    # Create location request keyboard
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(get_text("btn_send_location", lang), request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await update.message.reply_text(
        get_text("reg_location", lang),
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    return REG_LOCATION


async def reg_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive location and complete registration"""
    lang = context.user_data.get("registration_lang", "uz")
    user_id = update.effective_user.id
    
    # Get location
    if update.message.location:
        lat = update.message.location.latitude
        lon = update.message.location.longitude
    else:
        await update.message.reply_text(
            get_text("reg_invalid_location", lang),
            parse_mode="HTML"
        )
        return REG_LOCATION
    
    # Get registration data
    first_name = context.user_data.get("reg_first_name", "")
    last_name = context.user_data.get("reg_last_name", "")
    age = context.user_data.get("reg_age", 0)
    phone = context.user_data.get("reg_phone", "")
    
    # Save to database
    await update_user_registration(
        telegram_id=user_id,
        first_name=first_name,
        last_name=last_name,
        age=age,
        phone=phone,
        location_lat=lat,
        location_lon=lon
    )
    
    is_admin = user_id in ADMIN_IDS
    
    # Send notification to admins about new registration
    username = update.effective_user.username or "N/A"
    notification_text = (
        f"🆕 <b>Yangi foydalanuvchi ro'yxatdan o'tdi!</b>\n\n"
        f"👤 <b>ID:</b> <code>{user_id}</code>\n"
        f"📛 <b>Username:</b> @{username}\n"
        f"📝 <b>Ism:</b> {first_name}\n"
        f"📝 <b>Familiya:</b> {last_name}\n"
        f"🎂 <b>Yosh:</b> {age}\n"
        f"📞 <b>Telefon:</b> {phone}\n"
        f"📍 <b>Lokatsiya:</b> <a href='https://www.google.com/maps?q={lat},{lon}'>Xaritada ko'rish</a>"
    )
    
    for admin_id in NOTIFICATION_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=notification_text,
                parse_mode="HTML"
            )
        except Exception as e:
            pass  # Ignore if admin is not available
    
    # Clear user data
    context.user_data.clear()
    
    # Send success message and main menu
    await update.message.reply_text(
        get_text("reg_success", lang, name=first_name),
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(lang, is_admin)
    )
    
    return ConversationHandler.END


async def reg_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel registration - but still require it"""
    lang = context.user_data.get("registration_lang", "uz")
    
    await update.message.reply_text(
        get_text("reg_required", lang),
        parse_mode="HTML"
    )
    
    # Restart registration
    await update.message.reply_text(
        get_text("reg_first_name", lang),
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    
    return REG_FIRST_NAME
