"""
Delivery-related schemas for Uber Eats API
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from enum import Enum

from app.schemas.store import Address, Contact


class DeliveryStatus(str, Enum):
    """Delivery status enumeration"""
    PENDING = "PENDING"
    COURIER_ASSIGNED = "COURIER_ASSIGNED"
    COURIER_EN_ROUTE_TO_PICKUP = "COURIER_EN_ROUTE_TO_PICKUP"
    COURIER_ARRIVED_AT_PICKUP = "COURIER_ARRIVED_AT_PICKUP"
    ORDER_PICKED_UP = "ORDER_PICKED_UP"
    COURIER_EN_ROUTE_TO_DROPOFF = "COURIER_EN_ROUTE_TO_DROPOFF"
    COURIER_ARRIVED_AT_DROPOFF = "COURIER_ARRIVED_AT_DROPOFF"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"


class CourierVehicleType(str, Enum):
    """Courier vehicle type"""
    BICYCLE = "BICYCLE"
    SCOOTER = "SCOOTER"
    MOTORCYCLE = "MOTORCYCLE"
    CAR = "CAR"
    WALKER = "WALKER"


class DeliveryPriority(str, Enum):
    """Delivery priority level"""
    STANDARD = "STANDARD"
    PRIORITY = "PRIORITY"
    EXPRESS = "EXPRESS"


class PackageSize(str, Enum):
    """Package size category"""
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
    EXTRA_LARGE = "EXTRA_LARGE"


class Courier(BaseModel):
    """Courier information schema"""
    id: str = Field(description="Courier ID")
    name: str = Field(description="Courier name")
    phone: str = Field(description="Courier phone number")
    vehicle_type: CourierVehicleType = Field(description="Vehicle type")
    vehicle_make: Optional[str] = Field(default=None, description="Vehicle make")
    vehicle_model: Optional[str] = Field(default=None, description="Vehicle model")
    vehicle_license_plate: Optional[str] = Field(default=None, description="License plate")
    photo_url: Optional[HttpUrl] = Field(default=None, description="Courier photo URL")
    rating: Optional[float] = Field(default=None, ge=0, le=5, description="Courier rating")
    
    model_config = ConfigDict(from_attributes=True)


class DeliveryLocation(BaseModel):
    """Delivery location with GPS coordinates"""
    address: Address = Field(description="Address details")
    latitude: float = Field(description="Latitude coordinate")
    longitude: float = Field(description="Longitude coordinate")
    notes: Optional[str] = Field(default=None, description="Location notes")
    
    model_config = ConfigDict(from_attributes=True)


class DeliveryWindow(BaseModel):
    """Delivery time window"""
    start_time: datetime = Field(description="Window start time")
    end_time: datetime = Field(description="Window end time")
    
    model_config = ConfigDict(from_attributes=True)


class DeliveryTracking(BaseModel):
    """Real-time delivery tracking information"""
    courier_location: Optional[DeliveryLocation] = Field(default=None, description="Current courier location")
    estimated_arrival_time: datetime = Field(description="Estimated arrival time")
    distance_remaining_meters: Optional[int] = Field(default=None, description="Distance remaining in meters")
    time_remaining_seconds: Optional[int] = Field(default=None, description="Time remaining in seconds")
    tracking_url: HttpUrl = Field(description="Public tracking URL")
    last_updated: datetime = Field(description="Last tracking update timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class DeliveryQuote(BaseModel):
    """Delivery quote/estimate"""
    quote_id: str = Field(description="Quote ID")
    delivery_fee: float = Field(description="Delivery fee amount")
    estimated_pickup_time: datetime = Field(description="Estimated pickup time")
    estimated_delivery_time: datetime = Field(description="Estimated delivery time")
    distance_miles: float = Field(description="Delivery distance in miles")
    currency_code: str = Field(default="USD", description="ISO 4217 currency code")
    expires_at: datetime = Field(description="Quote expiration time")
    
    model_config = ConfigDict(from_attributes=True)


class CreateDeliveryRequest(BaseModel):
    """Request to create a new delivery"""
    order_id: str = Field(description="Associated order ID")
    pickup_location: DeliveryLocation = Field(description="Pickup location")
    dropoff_location: DeliveryLocation = Field(description="Dropoff location")
    pickup_contact: Contact = Field(description="Pickup contact")
    dropoff_contact: Contact = Field(description="Dropoff contact")
    package_description: str = Field(description="Package description")
    package_size: PackageSize = Field(description="Package size")
    priority: DeliveryPriority = Field(default=DeliveryPriority.STANDARD, description="Delivery priority")
    delivery_window: Optional[DeliveryWindow] = Field(default=None, description="Preferred delivery window")
    requires_signature: bool = Field(default=False, description="Signature required on delivery")
    tip_amount: Optional[float] = Field(default=None, description="Tip amount")
    
    model_config = ConfigDict(from_attributes=True)


class Delivery(BaseModel):
    """Complete delivery schema"""
    id: str = Field(description="Delivery ID")
    order_id: str = Field(description="Associated order ID")
    status: DeliveryStatus = Field(description="Current delivery status")
    courier: Optional[Courier] = Field(default=None, description="Assigned courier")
    pickup_location: DeliveryLocation = Field(description="Pickup location")
    dropoff_location: DeliveryLocation = Field(description="Dropoff location")
    pickup_contact: Contact = Field(description="Pickup contact")
    dropoff_contact: Contact = Field(description="Dropoff contact")
    package_description: str = Field(description="Package description")
    package_size: PackageSize = Field(description="Package size")
    priority: DeliveryPriority = Field(description="Delivery priority")
    tracking: Optional[DeliveryTracking] = Field(default=None, description="Tracking information")
    created_at: datetime = Field(description="Creation timestamp")
    picked_up_at: Optional[datetime] = Field(default=None, description="Pickup timestamp")
    delivered_at: Optional[datetime] = Field(default=None, description="Delivery timestamp")
    signature_image_url: Optional[HttpUrl] = Field(default=None, description="Signature image URL")
    proof_of_delivery_url: Optional[HttpUrl] = Field(default=None, description="Proof of delivery URL")
    
    model_config = ConfigDict(from_attributes=True)


class MultiCourierRequest(BaseModel):
    """Request for multiple couriers (large orders)"""
    order_id: str = Field(description="Order ID")
    num_couriers: int = Field(ge=2, le=5, description="Number of couriers needed")
    reason: str = Field(description="Reason for multiple couriers")
    package_details: List[Dict[str, Any]] = Field(description="Details of packages for each courier")
    
    model_config = ConfigDict(from_attributes=True)


class DeliveryUpdate(BaseModel):
    """Delivery update schema"""
    status: Optional[DeliveryStatus] = Field(default=None, description="New status")
    notes: Optional[str] = Field(default=None, description="Update notes")
    issue_type: Optional[str] = Field(default=None, description="Issue type if any")
    issue_description: Optional[str] = Field(default=None, description="Issue description")
    
    model_config = ConfigDict(from_attributes=True)


class DeliveryMetrics(BaseModel):
    """Delivery performance metrics"""
    average_delivery_time_minutes: float = Field(description="Average delivery time")
    on_time_delivery_rate: float = Field(description="On-time delivery rate")
    delivery_success_rate: float = Field(description="Successful delivery rate")
    average_courier_rating: float = Field(description="Average courier rating")
    total_deliveries: int = Field(description="Total number of deliveries")
    
    model_config = ConfigDict(from_attributes=True)