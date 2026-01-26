# Database Connection and Session Management
# ==========================================

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, List

from config import DATABASE_URL, ADMIN_IDS, DEFAULT_CATEGORIES
from database.models import Base, User, Category, Product, CartItem, Order, OrderItem


# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create async session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Initialize database and create tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Add default categories if none exist
    async with async_session() as session:
        result = await session.execute(select(func.count(Category.id)))
        count = result.scalar()
        
        if count == 0:
            for i, cat_data in enumerate(DEFAULT_CATEGORIES):
                category = Category(
                    name_uz=cat_data["name_uz"],
                    name_ru=cat_data["name_ru"],
                    name_en=cat_data["name_en"],
                    sort_order=i
                )
                session.add(category)
            await session.commit()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ==========================================
# User Operations
# ==========================================

async def get_or_create_user(telegram_id: int, username: str = None, 
                             first_name: str = None, last_name: str = None) -> User:
    """Get existing user or create new one"""
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Update user info
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.is_admin = telegram_id in ADMIN_IDS
        else:
            # Create new user
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_admin=telegram_id in ADMIN_IDS
            )
            session.add(user)
        
        await session.commit()
        return user


async def update_user_language(telegram_id: int, language: str) -> Optional[User]:
    """Update user's preferred language"""
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.language = language
            await session.commit()
        
        return user


async def get_user(telegram_id: int) -> Optional[User]:
    """Get user by telegram ID"""
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def get_user_language(telegram_id: int) -> str:
    """Get user's preferred language"""
    user = await get_user(telegram_id)
    return user.language if user else "uz"


async def get_all_users() -> List[User]:
    """Get all active users"""
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.is_active == True)
        )
        return result.scalars().all()


async def get_user_count() -> int:
    """Get total user count"""
    async with get_session() as session:
        result = await session.execute(select(func.count(User.id)))
        return result.scalar()


# ==========================================
# Category Operations
# ==========================================

async def get_all_categories() -> List[Category]:
    """Get all active categories"""
    async with get_session() as session:
        result = await session.execute(
            select(Category).where(Category.is_active == True).order_by(Category.sort_order)
        )
        return result.scalars().all()


async def get_category(category_id: int) -> Optional[Category]:
    """Get category by ID"""
    async with get_session() as session:
        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()


async def create_category(name_uz: str, name_ru: str, name_en: str) -> Category:
    """Create new category"""
    async with get_session() as session:
        category = Category(name_uz=name_uz, name_ru=name_ru, name_en=name_en)
        session.add(category)
        await session.commit()
        return category


async def delete_category(category_id: int) -> bool:
    """Delete category"""
    async with get_session() as session:
        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        if category:
            await session.delete(category)
            await session.commit()
            return True
        return False


# ==========================================
# Product Operations
# ==========================================

async def get_products_by_category(category_id: int, offset: int = 0, limit: int = 5) -> List[Product]:
    """Get products by category with pagination"""
    async with get_session() as session:
        result = await session.execute(
            select(Product)
            .where(Product.category_id == category_id, Product.is_active == True)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()


async def get_product(product_id: int) -> Optional[Product]:
    """Get product by ID"""
    async with get_session() as session:
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()


async def get_products_count_by_category(category_id: int) -> int:
    """Get total products count in category"""
    async with get_session() as session:
        result = await session.execute(
            select(func.count(Product.id))
            .where(Product.category_id == category_id, Product.is_active == True)
        )
        return result.scalar()


async def create_product(category_id: int, name_uz: str, name_ru: str, name_en: str,
                        description_uz: str, description_ru: str, description_en: str,
                        price: float, discount_percent: int = 0, 
                        image_url: str = None, stock: int = 0) -> Product:
    """Create new product"""
    async with get_session() as session:
        product = Product(
            category_id=category_id,
            name_uz=name_uz, name_ru=name_ru, name_en=name_en,
            description_uz=description_uz, description_ru=description_ru, description_en=description_en,
            price=price, discount_percent=discount_percent,
            image_url=image_url, stock=stock
        )
        session.add(product)
        await session.commit()
        return product


async def update_product(product_id: int, **kwargs) -> Optional[Product]:
    """Update product"""
    async with get_session() as session:
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if product:
            for key, value in kwargs.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            await session.commit()
        
        return product


async def delete_product(product_id: int) -> bool:
    """Delete product"""
    async with get_session() as session:
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        if product:
            await session.delete(product)
            await session.commit()
            return True
        return False


async def get_all_products() -> List[Product]:
    """Get all active products"""
    async with get_session() as session:
        result = await session.execute(
            select(Product).where(Product.is_active == True)
        )
        return result.scalars().all()


# ==========================================
# Cart Operations
# ==========================================

async def add_to_cart(telegram_id: int, product_id: int, quantity: int = 1) -> Optional[CartItem]:
    """Add item to cart or update quantity if exists"""
    async with get_session() as session:
        # Get user
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return None
        
        # Check if item already in cart
        cart_result = await session.execute(
            select(CartItem).where(
                CartItem.user_id == user.id,
                CartItem.product_id == product_id
            )
        )
        cart_item = cart_result.scalar_one_or_none()
        
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(
                user_id=user.id,
                product_id=product_id,
                quantity=quantity
            )
            session.add(cart_item)
        
        await session.commit()
        return cart_item


async def get_cart_items(telegram_id: int) -> List[CartItem]:
    """Get all cart items for user"""
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return []
        
        result = await session.execute(
            select(CartItem)
            .where(CartItem.user_id == user.id)
            .options()
        )
        cart_items = result.scalars().all()
        
        # Load products for each cart item
        for item in cart_items:
            product_result = await session.execute(
                select(Product).where(Product.id == item.product_id)
            )
            item.product = product_result.scalar_one_or_none()
        
        return cart_items


async def update_cart_quantity(telegram_id: int, product_id: int, quantity: int) -> Optional[CartItem]:
    """Update cart item quantity"""
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return None
        
        result = await session.execute(
            select(CartItem).where(
                CartItem.user_id == user.id,
                CartItem.product_id == product_id
            )
        )
        cart_item = result.scalar_one_or_none()
        
        if cart_item:
            if quantity <= 0:
                await session.delete(cart_item)
            else:
                cart_item.quantity = quantity
            await session.commit()
        
        return cart_item


async def remove_from_cart(telegram_id: int, product_id: int) -> bool:
    """Remove item from cart"""
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return False
        
        result = await session.execute(
            select(CartItem).where(
                CartItem.user_id == user.id,
                CartItem.product_id == product_id
            )
        )
        cart_item = result.scalar_one_or_none()
        
        if cart_item:
            await session.delete(cart_item)
            await session.commit()
            return True
        return False


async def clear_cart(telegram_id: int) -> bool:
    """Clear all items from cart"""
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return False
        
        result = await session.execute(
            select(CartItem).where(CartItem.user_id == user.id)
        )
        cart_items = result.scalars().all()
        
        for item in cart_items:
            await session.delete(item)
        
        await session.commit()
        return True


async def get_cart_total(telegram_id: int) -> float:
    """Calculate cart total"""
    cart_items = await get_cart_items(telegram_id)
    total = 0.0
    for item in cart_items:
        if item.product:
            total += item.product.discounted_price * item.quantity
    return total


# ==========================================
# Order Operations
# ==========================================

async def create_order(telegram_id: int, phone: str = None, 
                       address: str = None, notes: str = None) -> Optional[Order]:
    """Create order from cart items"""
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return None
        
        # Get cart items
        cart_result = await session.execute(
            select(CartItem).where(CartItem.user_id == user.id)
        )
        cart_items = cart_result.scalars().all()
        
        if not cart_items:
            return None
        
        # Calculate total and create order
        total = 0.0
        order = Order(
            user_id=user.id,
            phone=phone or user.phone,
            address=address,
            notes=notes,
            total_amount=0
        )
        session.add(order)
        await session.flush()
        
        # Create order items
        for cart_item in cart_items:
            product_result = await session.execute(
                select(Product).where(Product.id == cart_item.product_id)
            )
            product = product_result.scalar_one_or_none()
            if product:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name_uz,
                    quantity=cart_item.quantity,
                    price=product.discounted_price
                )
                session.add(order_item)
                total += product.discounted_price * cart_item.quantity
        
        order.total_amount = total
        
        # Clear cart
        for cart_item in cart_items:
            await session.delete(cart_item)
        
        await session.commit()
        return order


async def get_user_orders(telegram_id: int) -> List[Order]:
    """Get all orders for user"""
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return []
        
        result = await session.execute(
            select(Order)
            .where(Order.user_id == user.id)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()


async def get_order(order_id: int) -> Optional[Order]:
    """Get order by ID"""
    async with get_session() as session:
        result = await session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()


async def update_order_status(order_id: int, status: str) -> Optional[Order]:
    """Update order status"""
    async with get_session() as session:
        result = await session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if order:
            order.status = status
            await session.commit()
        
        return order


async def get_all_orders(status: str = None) -> List[Order]:
    """Get all orders, optionally filtered by status"""
    async with get_session() as session:
        query = select(Order).order_by(Order.created_at.desc())
        if status:
            query = query.where(Order.status == status)
        
        result = await session.execute(query)
        return result.scalars().all()


async def get_order_count() -> int:
    """Get total order count"""
    async with get_session() as session:
        result = await session.execute(select(func.count(Order.id)))
        return result.scalar()


async def get_total_revenue() -> float:
    """Get total revenue from delivered orders"""
    async with get_session() as session:
        result = await session.execute(
            select(func.sum(Order.total_amount))
            .where(Order.status == "delivered")
        )
        return result.scalar() or 0.0
