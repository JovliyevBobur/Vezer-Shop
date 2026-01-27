# Vezer Shop Telegram Bot - Main Entry Point
# ===========================================
# Professional e-commerce Telegram bot for selling clothes, electronics, and accessories
# with multi-language support, discount system, and comprehensive admin panel.

import logging
import sys
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)

from config import BOT_TOKEN
from database import init_db

# Import handlers
from handlers import (
    # Start handlers
    start_command, language_callback, main_menu_callback,
    handle_main_menu_buttons, settings_callback,
    # Catalog handlers
    show_catalog, catalog_callback, category_callback,
    category_page_callback, product_callback, add_to_cart_callback,
    product_page_callback,
    # Cart handlers
    show_cart, cart_callback, cart_plus_callback, cart_minus_callback,
    cart_remove_callback, clear_cart_callback, checkout_callback,
    checkout_phone, checkout_address, checkout_cancel,
    PHONE, ADDRESS,
    # Admin handlers
    show_admin_panel, admin_panel_callback, admin_stats_callback,
    admin_categories_callback, admin_delete_category_callback,
    admin_products_callback, admin_delete_product_callback,
    admin_orders_callback, admin_order_detail_callback,
    update_order_status_callback,
    start_add_product, add_product_name_uz, add_product_name_ru,
    add_product_name_en, add_product_desc_uz, add_product_desc_ru,
    add_product_desc_en, add_product_price, add_product_discount,
    add_product_image, add_product_category,
    start_broadcast, send_broadcast,
    start_add_category, add_category_name_uz, add_category_name_ru,
    add_category_name_en, cancel_admin_action,
    ADD_PROD_NAME_UZ, ADD_PROD_NAME_RU, ADD_PROD_NAME_EN,
    ADD_PROD_DESC_UZ, ADD_PROD_DESC_RU, ADD_PROD_DESC_EN,
    ADD_PROD_PRICE, ADD_PROD_DISCOUNT, ADD_PROD_IMAGE, ADD_PROD_CATEGORY,
    BROADCAST_MESSAGE,
    ADD_CAT_NAME_UZ, ADD_CAT_NAME_RU, ADD_CAT_NAME_EN,
    # Registration handlers
    reg_first_name, reg_last_name, reg_age, reg_phone, reg_location, reg_cancel,
    REG_FIRST_NAME, REG_LAST_NAME, REG_AGE, REG_PHONE, REG_LOCATION
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Initialize database after application starts"""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully!")
    logger.info("Vezer Shop Bot is running!")


async def error_handler(update: Update, context) -> None:
    """Handle errors"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ An error occurred. Please try again or use /start to restart."
            )
        except Exception:
            pass


def main() -> None:
    """Main function to run the bot"""
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # ==========================================
    # Command Handlers
    # ==========================================
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", show_admin_panel))
    
    # ==========================================
    # Checkout Conversation Handler
    # ==========================================
    checkout_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(checkout_callback, pattern="^checkout$")],
        states={
            PHONE: [MessageHandler(filters.TEXT | filters.CONTACT, checkout_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_address)],
        },
        fallbacks=[
            CommandHandler("cancel", checkout_cancel),
            MessageHandler(filters.Regex("^❌"), checkout_cancel)
        ],
        allow_reentry=True
    )
    application.add_handler(checkout_conv_handler)
    
    # ==========================================
    # Add Product Conversation Handler
    # ==========================================
    add_product_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add_product, pattern="^admin_add_product$")],
        states={
            ADD_PROD_NAME_UZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_name_uz)],
            ADD_PROD_NAME_RU: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_name_ru)],
            ADD_PROD_NAME_EN: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_name_en)],
            ADD_PROD_DESC_UZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_desc_uz)],
            ADD_PROD_DESC_RU: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_desc_ru)],
            ADD_PROD_DESC_EN: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_desc_en)],
            ADD_PROD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_price)],
            ADD_PROD_DISCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_discount)],
            ADD_PROD_IMAGE: [
                MessageHandler(filters.PHOTO, add_product_image),
                MessageHandler(filters.TEXT, add_product_image),
                CommandHandler("skip", add_product_image)
            ],
            ADD_PROD_CATEGORY: [CallbackQueryHandler(add_product_category, pattern="^selcat_|^cancel$")],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_admin_action),
            CallbackQueryHandler(cancel_admin_action, pattern="^cancel$")
        ],
        allow_reentry=True
    )
    application.add_handler(add_product_conv_handler)
    
    # ==========================================
    # Broadcast Conversation Handler
    # ==========================================
    broadcast_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_broadcast, pattern="^admin_broadcast$")],
        states={
            BROADCAST_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_broadcast)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_admin_action),
            CallbackQueryHandler(cancel_admin_action, pattern="^cancel$")
        ],
        allow_reentry=True
    )
    application.add_handler(broadcast_conv_handler)
    
    # ==========================================
    # Add Category Conversation Handler
    # ==========================================
    add_category_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add_category, pattern="^admin_addcat$")],
        states={
            ADD_CAT_NAME_UZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_category_name_uz)],
            ADD_CAT_NAME_RU: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_category_name_ru)],
            ADD_CAT_NAME_EN: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_category_name_en)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_admin_action),
            CallbackQueryHandler(cancel_admin_action, pattern="^cancel$")
        ],
        allow_reentry=True
    )
    application.add_handler(add_category_conv_handler)
    
    # ==========================================
    # Registration Conversation Handler
    # ==========================================
    registration_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(language_callback, pattern="^lang_")],
        states={
            REG_FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_first_name)],
            REG_LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_last_name)],
            REG_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_age)],
            REG_PHONE: [MessageHandler(filters.TEXT | filters.CONTACT, reg_phone)],
            REG_LOCATION: [MessageHandler(filters.LOCATION, reg_location)],
        },
        fallbacks=[
            CommandHandler("start", start_command),
            CommandHandler("cancel", reg_cancel)
        ],
        allow_reentry=True
    )
    application.add_handler(registration_conv_handler)
    
    
    # ==========================================
    # Callback Query Handlers
    # ==========================================
    
    # Main menu
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))
    
    # Settings
    application.add_handler(CallbackQueryHandler(settings_callback, pattern="^change_language$"))
    
    # Catalog navigation
    application.add_handler(CallbackQueryHandler(catalog_callback, pattern="^catalog$"))
    application.add_handler(CallbackQueryHandler(category_callback, pattern="^cat_\\d+$"))
    application.add_handler(CallbackQueryHandler(category_page_callback, pattern="^catpage_"))
    application.add_handler(CallbackQueryHandler(product_callback, pattern="^prod_"))
    application.add_handler(CallbackQueryHandler(product_page_callback, pattern="^prodpage_"))
    application.add_handler(CallbackQueryHandler(add_to_cart_callback, pattern="^addcart_"))
    
    # Cart
    application.add_handler(CallbackQueryHandler(cart_callback, pattern="^cart$"))
    application.add_handler(CallbackQueryHandler(cart_plus_callback, pattern="^cartplus_"))
    application.add_handler(CallbackQueryHandler(cart_minus_callback, pattern="^cartminus_"))
    application.add_handler(CallbackQueryHandler(cart_remove_callback, pattern="^cartremove_"))
    application.add_handler(CallbackQueryHandler(clear_cart_callback, pattern="^clear_cart$"))
    
    # Admin panel
    application.add_handler(CallbackQueryHandler(admin_panel_callback, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(admin_stats_callback, pattern="^admin_stats$"))
    application.add_handler(CallbackQueryHandler(admin_categories_callback, pattern="^admin_categories$"))
    application.add_handler(CallbackQueryHandler(admin_delete_category_callback, pattern="^admin_delcat_"))
    application.add_handler(CallbackQueryHandler(admin_products_callback, pattern="^admin_products$"))
    application.add_handler(CallbackQueryHandler(admin_delete_product_callback, pattern="^admin_delprod_"))
    application.add_handler(CallbackQueryHandler(admin_orders_callback, pattern="^admin_orders$"))
    application.add_handler(CallbackQueryHandler(admin_order_detail_callback, pattern="^admin_order_\\d+$"))
    application.add_handler(CallbackQueryHandler(update_order_status_callback, pattern="^orderstatus_"))
    
    # ==========================================
    # Message Handler for Main Menu Buttons
    # ==========================================
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_main_menu_buttons
    ))
    
    # ==========================================
    # Error Handler
    # ==========================================
    application.add_error_handler(error_handler)
    
    # ==========================================
    # Start the bot
    # ==========================================
    logger.info("Starting Vezer Shop Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
