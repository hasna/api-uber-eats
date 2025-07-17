"""
Store-related schemas for Uber Eats API
"""
from datetime import datetime, time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from enum import Enum

from app.schemas.base import TimestampMixin


class StoreStatus(str, Enum):
    """Store status enumeration"""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    PAUSED = "PAUSED"
    INACTIVE = "INACTIVE"


class DayOfWeek(str, Enum):
    """Day of week enumeration"""
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class Address(BaseModel):
    """Address schema"""
    street_address: str = Field(description="Street address")
    city: str = Field(description="City")
    state: str = Field(description="State or province")
    zip_code: str = Field(description="ZIP or postal code")
    country_code: str = Field(description="ISO 3166-1 alpha-2 country code")
    latitude: Optional[float] = Field(default=None, description="Latitude coordinate")
    longitude: Optional[float] = Field(default=None, description="Longitude coordinate")
    
    model_config = ConfigDict(from_attributes=True)


class Contact(BaseModel):
    """Contact information schema"""
    first_name: Optional[str] = Field(default=None, description="First name")
    last_name: Optional[str] = Field(default=None, description="Last name")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: str = Field(description="Phone number")
    
    model_config = ConfigDict(from_attributes=True)


class HoursOfOperation(BaseModel):
    """Hours of operation for a specific day"""
    day_of_week: DayOfWeek = Field(description="Day of the week")
    open_time: time = Field(description="Opening time")
    close_time: time = Field(description="Closing time")
    is_closed: bool = Field(default=False, description="Whether the store is closed this day")
    
    model_config = ConfigDict(from_attributes=True)


class Holiday(BaseModel):
    """Holiday schedule"""
    date: str = Field(description="Holiday date (YYYY-MM-DD)")
    name: str = Field(description="Holiday name")
    is_closed: bool = Field(default=True, description="Whether the store is closed")
    open_time: Optional[time] = Field(default=None, description="Opening time if not closed")
    close_time: Optional[time] = Field(default=None, description="Closing time if not closed")
    
    model_config = ConfigDict(from_attributes=True)


class StoreConfiguration(BaseModel):
    """Store configuration settings"""
    auto_accept_orders: bool = Field(default=False, description="Auto-accept incoming orders")
    prep_time_minutes: int = Field(default=15, description="Default preparation time in minutes")
    max_order_size: Optional[float] = Field(default=None, description="Maximum order size in currency")
    delivery_radius_miles: Optional[float] = Field(default=None, description="Delivery radius in miles")
    supports_delivery: bool = Field(default=True, description="Whether store supports delivery")
    supports_pickup: bool = Field(default=True, description="Whether store supports pickup")
    
    model_config = ConfigDict(from_attributes=True)


class StoreBase(BaseModel):
    """Base store schema"""
    name: str = Field(description="Store name")
    description: Optional[str] = Field(default=None, description="Store description")
    external_store_id: str = Field(description="External store identifier")
    merchant_store_id: Optional[str] = Field(default=None, description="Merchant's internal store ID")
    address: Address = Field(description="Store address")
    contact: Contact = Field(description="Store contact information")
    timezone: str = Field(default="America/New_York", description="Store timezone")
    currency_code: str = Field(default="USD", description="ISO 4217 currency code")
    
    model_config = ConfigDict(from_attributes=True)


class StoreCreate(StoreBase):
    """Schema for creating a store"""
    hours_of_operation: List[HoursOfOperation] = Field(description="Store hours")
    holidays: Optional[List[Holiday]] = Field(default=None, description="Holiday schedule")
    configuration: Optional[StoreConfiguration] = Field(default=None, description="Store configuration")


class StoreUpdate(BaseModel):
    """Schema for updating a store"""
    name: Optional[str] = Field(default=None, description="Store name")
    description: Optional[str] = Field(default=None, description="Store description")
    address: Optional[Address] = Field(default=None, description="Store address")
    contact: Optional[Contact] = Field(default=None, description="Store contact information")
    hours_of_operation: Optional[List[HoursOfOperation]] = Field(default=None, description="Store hours")
    holidays: Optional[List[Holiday]] = Field(default=None, description="Holiday schedule")
    configuration: Optional[StoreConfiguration] = Field(default=None, description="Store configuration")
    
    model_config = ConfigDict(from_attributes=True)


class Store(StoreBase, TimestampMixin):
    """Complete store schema"""
    id: str = Field(description="Store ID")
    uber_store_id: str = Field(description="Uber's internal store ID")
    status: StoreStatus = Field(description="Store status")
    hours_of_operation: List[HoursOfOperation] = Field(description="Store hours")
    holidays: Optional[List[Holiday]] = Field(default=None, description="Holiday schedule")
    configuration: StoreConfiguration = Field(description="Store configuration")
    is_active: bool = Field(default=True, description="Whether store is active")
    
    model_config = ConfigDict(from_attributes=True)


class StoreStatusUpdate(BaseModel):
    """Schema for updating store status"""
    status: StoreStatus = Field(description="New store status")
    reason: Optional[str] = Field(default=None, description="Reason for status change")
    estimated_offline_until: Optional[datetime] = Field(default=None, description="Estimated time until back online")
    
    model_config = ConfigDict(from_attributes=True)


class StorePosData(BaseModel):
    """POS-specific data for a store"""
    pos_store_id: str = Field(description="POS system store ID")
    pos_terminal_id: Optional[str] = Field(default=None, description="POS terminal ID")
    integration_enabled: bool = Field(default=True, description="Whether POS integration is enabled")
    order_injection_enabled: bool = Field(default=True, description="Whether order injection is enabled")
    menu_sync_enabled: bool = Field(default=True, description="Whether menu sync is enabled")
    custom_data: Optional[Dict[str, Any]] = Field(default=None, description="Custom POS data")
    
    model_config = ConfigDict(from_attributes=True)


class StoreList(BaseModel):
    """List of stores response"""
    stores: List[Store] = Field(description="List of stores")
    total: int = Field(description="Total number of stores")
    has_more: bool = Field(description="Whether there are more stores")
    next_cursor: Optional[str] = Field(default=None, description="Cursor for next page")
    
    model_config = ConfigDict(from_attributes=True)