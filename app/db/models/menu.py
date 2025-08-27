"""
Menu-related database models
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Table, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.session import Base


# Association table for menu categories and items
menu_category_items = Table(
    'menu_category_items',
    Base.metadata,
    Column('category_id', UUID(as_uuid=True), ForeignKey('menu_categories.id'), primary_key=True),
    Column('item_id', UUID(as_uuid=True), ForeignKey('menu_items.id'), primary_key=True),
    Column('display_order', Integer, default=0),
)

# Association table for items and modifier groups
item_modifier_groups = Table(
    'item_modifier_groups',
    Base.metadata,
    Column('item_id', UUID(as_uuid=True), ForeignKey('menu_items.id'), primary_key=True),
    Column('modifier_group_id', UUID(as_uuid=True), ForeignKey('modifier_groups.id'), primary_key=True),
    Column('is_required', Boolean, default=False),
)


class Menu(Base):
    """Restaurant menu"""
    
    __tablename__ = "menus"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_id = Column(UUID(as_uuid=True), ForeignKey('stores.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    store = relationship("Store", back_populates="menus")
    categories = relationship("MenuCategory", back_populates="menu", cascade="all, delete-orphan")
    items = relationship("MenuItem", back_populates="menu", cascade="all, delete-orphan")


class MenuCategory(Base):
    """Menu category (e.g., Appetizers, Main Courses)"""
    
    __tablename__ = "menu_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_id = Column(UUID(as_uuid=True), ForeignKey('menus.id'), nullable=False)
    external_id = Column(String, index=True)  # Uber Eats category ID
    title = Column(String, nullable=False)
    description = Column(Text)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    menu = relationship("Menu", back_populates="categories")
    items = relationship("MenuItem", secondary=menu_category_items, back_populates="categories")


class MenuItem(Base):
    """Menu item"""
    
    __tablename__ = "menu_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_id = Column(UUID(as_uuid=True), ForeignKey('menus.id'), nullable=False)
    external_id = Column(String, index=True)  # Uber Eats item ID
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String, default="USD")
    image_url = Column(String)
    is_available = Column(Boolean, default=True, nullable=False)
    is_popular = Column(Boolean, default=False)
    
    # Nutritional information
    calories = Column(Integer)
    nutritional_info = Column(JSON)
    dietary_info = Column(JSON)  # vegetarian, vegan, gluten-free, etc.
    
    # Availability
    available_from = Column(DateTime(timezone=True))
    available_until = Column(DateTime(timezone=True))
    max_quantity = Column(Integer)
    
    # Metadata
    preparation_time_minutes = Column(Integer)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    menu = relationship("Menu", back_populates="items")
    categories = relationship("MenuCategory", secondary=menu_category_items, back_populates="items")
    modifier_groups = relationship("ModifierGroup", secondary=item_modifier_groups, back_populates="items")


class ModifierGroup(Base):
    """Modifier group (e.g., Pizza Toppings, Drink Size)"""
    
    __tablename__ = "modifier_groups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, index=True)  # Uber Eats modifier group ID
    title = Column(String, nullable=False)
    description = Column(Text)
    selection_type = Column(String, default="single")  # single, multiple
    min_selections = Column(Integer, default=0)
    max_selections = Column(Integer)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    items = relationship("MenuItem", secondary=item_modifier_groups, back_populates="modifier_groups")
    modifiers = relationship("Modifier", back_populates="modifier_group", cascade="all, delete-orphan")


class Modifier(Base):
    """Individual modifier option"""
    
    __tablename__ = "modifiers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    modifier_group_id = Column(UUID(as_uuid=True), ForeignKey('modifier_groups.id'), nullable=False)
    external_id = Column(String, index=True)  # Uber Eats modifier ID
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), default=0)
    currency = Column(String, default="USD")
    is_available = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    modifier_group = relationship("ModifierGroup", back_populates="modifiers")