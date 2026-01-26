# Database Models for Vezer Shop
# ==============================

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    """User model - stores Telegram user data and preferences"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language = Column(String(10), default="uz")
    phone = Column(String(20), nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.telegram_id}: {self.first_name}>"


class Category(Base):
    """Category model - product categories"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name_uz = Column(String(255), nullable=False)
    name_ru = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    emoji = Column(String(10), default="📦")
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")
    
    def get_name(self, lang: str = "uz") -> str:
        """Get category name by language"""
        names = {"uz": self.name_uz, "ru": self.name_ru, "en": self.name_en}
        return names.get(lang, self.name_uz)
    
    def __repr__(self):
        return f"<Category {self.id}: {self.name_uz}>"


class Product(Base):
    """Product model - items for sale"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name_uz = Column(String(255), nullable=False)
    name_ru = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    description_uz = Column(Text, nullable=True)
    description_ru = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    discount_percent = Column(Integer, default=0)  # 0-100
    image_url = Column(String(500), nullable=True)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    
    def get_name(self, lang: str = "uz") -> str:
        """Get product name by language"""
        names = {"uz": self.name_uz, "ru": self.name_ru, "en": self.name_en}
        return names.get(lang, self.name_uz)
    
    def get_description(self, lang: str = "uz") -> str:
        """Get product description by language"""
        descriptions = {"uz": self.description_uz, "ru": self.description_ru, "en": self.description_en}
        return descriptions.get(lang, self.description_uz) or ""
    
    @property
    def discounted_price(self) -> float:
        """Calculate discounted price"""
        if self.discount_percent > 0:
            return self.price * (1 - self.discount_percent / 100)
        return self.price
    
    @property
    def has_discount(self) -> bool:
        """Check if product has discount"""
        return self.discount_percent > 0
    
    def __repr__(self):
        return f"<Product {self.id}: {self.name_uz}>"


class CartItem(Base):
    """Shopping cart item"""
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")
    
    @property
    def total_price(self) -> float:
        """Calculate total price for this cart item"""
        return self.product.discounted_price * self.quantity
    
    def __repr__(self):
        return f"<CartItem {self.id}: {self.quantity}x Product {self.product_id}>"


class Order(Base):
    """Order model - completed purchases"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="pending")
    total_amount = Column(Float, nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order {self.id}: {self.status}>"


class OrderItem(Base):
    """Individual items in an order"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(255), nullable=False)  # Store name at time of order
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # Store price at time of order
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    @property
    def total_price(self) -> float:
        """Calculate total price for this order item"""
        return self.price * self.quantity
    
    def __repr__(self):
        return f"<OrderItem {self.id}: {self.quantity}x {self.product_name}>"
