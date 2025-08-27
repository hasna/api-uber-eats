"""
Store model for Uber Eats stores
"""
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.session import Base


class StoreStatus(str, enum.Enum):
    """Store status enumeration"""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    PAUSED = "PAUSED"
    INACTIVE = "INACTIVE"


class Store(Base):
    """Store model"""
    
    __tablename__ = "stores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uber_store_id = Column(String, unique=True, nullable=False, index=True)
    external_store_id = Column(String, nullable=False, index=True)
    merchant_store_id = Column(String)
    
    # Basic information
    name = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(StoreStatus), default=StoreStatus.OFFLINE, nullable=False)
    
    # Address
    street_address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Contact
    contact_first_name = Column(String)
    contact_last_name = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String, nullable=False)
    
    # Settings
    timezone = Column(String, default="America/New_York")
    currency_code = Column(String, default="USD")
    auto_accept_orders = Column(Boolean, default=False)
    prep_time_minutes = Column(Integer, default=15)
    max_order_size = Column(Float)
    delivery_radius_miles = Column(Float)
    supports_delivery = Column(Boolean, default=True)
    supports_pickup = Column(Boolean, default=True)
    
    # Hours and holidays stored as JSON
    hours_of_operation = Column(JSON)
    holidays = Column(JSON)
    
    # POS data
    pos_data = Column(JSON)
    
    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    orders = relationship("Order", back_populates="store")
    menus = relationship("Menu", back_populates="store")