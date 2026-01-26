# Catalog Handler - Product Browsing
# ===================================

from telegram import Update
from telegram.ext import ContextTypes

from database import (
    get_user, get_all_categories, get_category,
    get_products_by_category, get_products_count_by_category,
    get_product, add_to_cart
)
from utils import (
    get_text, format_price, get_categories_keyboard,
    get_products_list_keyboard, get_product_keyboard
)
from config import PRODUCTS_PER_PAGE


async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show product categories"""
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    categories = await get_all_categories()
    
    text = get_text("catalog_title", lang)
    keyboard = get_categories_keyboard(categories, lang)
    
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


async def catalog_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle catalog navigation callback"""
    query = update.callback_query
    await query.answer()
    await show_catalog(update, context)


async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle category selection - show products in category"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    # Extract category ID from callback data
    callback_data = query.data
    category_id = int(callback_data.split("_")[1])
    
    await show_category_products(query, category_id, lang, page=0)


async def category_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle category pagination"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    # Extract category ID and page from callback data (catpage_1_2)
    parts = query.data.split("_")
    category_id = int(parts[1])
    page = int(parts[2])
    
    await show_category_products(query, category_id, lang, page)


async def show_category_products(query, category_id: int, lang: str, page: int = 0) -> None:
    """Show products in a category with pagination"""
    category = await get_category(category_id)
    if not category:
        await query.edit_message_text(get_text("error_occurred", lang))
        return
    
    # Get products with pagination
    offset = page * PRODUCTS_PER_PAGE
    products = await get_products_by_category(category_id, offset, PRODUCTS_PER_PAGE)
    total_count = await get_products_count_by_category(category_id)
    total_pages = (total_count + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE
    
    if not products:
        await query.edit_message_text(
            get_text("category_empty", lang),
            parse_mode="HTML",
            reply_markup=get_products_list_keyboard([], lang, category_id, 0, 0)
        )
        return
    
    category_name = category.get_name(lang)
    text = f"📁 <b>{category_name}</b>\n\n"
    text += f"📦 {get_text('catalog_title', lang).split(':')[0].replace('<b>', '').replace('</b>', '')} ({page + 1}/{total_pages}):\n"
    
    keyboard = get_products_list_keyboard(products, lang, category_id, page, total_pages)
    
    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle product view callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    # Extract product info from callback data (prod_1_2_0 = product_id, category_id, page)
    parts = query.data.split("_")
    product_id = int(parts[1])
    category_id = int(parts[2]) if len(parts) > 2 else None
    page = int(parts[3]) if len(parts) > 3 else 0
    
    await show_product(query, product_id, lang, category_id, page)


async def show_product(query, product_id: int, lang: str, category_id: int = None, page: int = 0) -> None:
    """Show product details"""
    product = await get_product(product_id)
    if not product:
        await query.edit_message_text(get_text("error_occurred", lang))
        return
    
    name = product.get_name(lang)
    description = product.get_description(lang) or "—"
    
    # Format product info
    if product.has_discount:
        text = get_text("product_info_discount", lang,
            name=name,
            description=description,
            old_price=format_price(product.price),
            new_price=format_price(product.discounted_price),
            discount=product.discount_percent
        )
    else:
        text = get_text("product_info", lang,
            name=name,
            description=description,
            price=format_price(product.price)
        )
    
    # Add stock info
    if product.stock > 0:
        text += f"\n📦 Stock: {product.stock}"
    
    # Get total products for pagination
    if category_id:
        total_count = await get_products_count_by_category(category_id)
        total_pages = (total_count + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE
    else:
        total_pages = 1
    
    keyboard = get_product_keyboard(product_id, lang, page, total_pages, category_id or product.category_id)
    
    # Send with image if available
    if product.image_url:
        try:
            await query.message.delete()
            await query.message.reply_photo(
                photo=product.image_url,
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception:
            await query.edit_message_text(
                text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
    else:
        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )


async def add_to_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle add to cart callback"""
    query = update.callback_query
    
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    # Extract product ID from callback data (addcart_1)
    product_id = int(query.data.split("_")[1])
    
    # Add to cart
    cart_item = await add_to_cart(user_id, product_id, 1)
    
    if cart_item:
        await query.answer(get_text("added_to_cart", lang), show_alert=True)
    else:
        await query.answer(get_text("error_occurred", lang), show_alert=True)


async def product_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle product pagination within category"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.language if db_user else "uz"
    
    # Extract category ID and page (prodpage_1_2)
    parts = query.data.split("_")
    category_id = int(parts[1])
    page = int(parts[2])
    
    await show_category_products(query, category_id, lang, page)
