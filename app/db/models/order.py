"""
Order-related database models
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.session import Base


class Order(Base):
    """Customer order"""
    
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, unique=True, nullable=False, index=True)  # Uber Eats order ID
    store_id = Column(UUID(as_uuid=True), ForeignKey('stores.id'), nullable=False)
    
    # Order details
    display_id = Column(String)  # User-friendly order ID
    status = Column(String, nullable=False, index=True)
    type = Column(String)  # delivery, pickup
    
    # Customer information
    customer_name = Column(String)
    customer_phone = Column(String)
    customer_email = Column(String)
    
    # Delivery information
    delivery_address = Column(JSON)
    delivery_instructions = Column(Text)
    estimated_delivery_time = Column(DateTime(timezone=True))
    
    # Pricing
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    tax_amount = Column(DECIMAL(10, 2), default=0)
    tip_amount = Column(DECIMAL(10, 2), default=0)
    delivery_fee = Column(DECIMAL(10, 2), default=0)
    service_fee = Column(DECIMAL(10, 2), default=0)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String, default="USD")
    
    # Payment
    payment_method = Column(String)
    payment_status = Column(String)
    
    # Timing
    placed_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True))
    ready_at = Column(DateTime(timezone=True))
    picked_up_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    
    # Preparation
    estimated_prep_time_minutes = Column(Integer)
    actual_prep_time_minutes = Column(Integer)
    
    # Special instructions
    special_instructions = Column(Text)
    
    # Metadata
    is_scheduled = Column(Boolean, default=False)
    scheduled_for = Column(DateTime(timezone=True))
    cancellation_reason = Column(String)
    pos_synced = Column(Boolean, default=False)
    pos_order_id = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    store = relationship("Store", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Individual item in an order"""
    
    __tablename__ = "order_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey('menu_items.id'), nullable=True)
    
    # Item details (stored for historical purposes)
    external_id = Column(String)  # Uber Eats item ID
    title = Column(String, nullable=False)
    description = Column(Text)
    quantity = Column(Integer, nullable=False, default=1)
    
    # Pricing
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String, default="USD")
    
    # Modifiers and customizations
    modifiers = Column(JSON)  # List of selected modifiers
    special_instructions = Column(Text)
    
    # Fulfillment
    is_ready = Column(Boolean, default=False)
    is_unavailable = Column(Boolean, default=False)
    unavailable_reason = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")