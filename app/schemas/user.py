"""
User-related schemas for Uber Eats API
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum

from app.schemas.base import TimestampMixin, PaginatedResponse


class UserStatus(str, Enum):
    """User status enumeration"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    BANNED = "BANNED"


class UserType(str, Enum):
    """User type enumeration"""
    CUSTOMER = "CUSTOMER"
    DRIVER = "DRIVER"
    RESTAURANT_OWNER = "RESTAURANT_OWNER"
    ADMIN = "ADMIN"


class DietaryRestriction(str, Enum):
    """Dietary restrictions enumeration"""
    VEGETARIAN = "VEGETARIAN"
    VEGAN = "VEGAN"
    GLUTEN_FREE = "GLUTEN_FREE"
    DAIRY_FREE = "DAIRY_FREE"
    NUT_FREE = "NUT_FREE"
    HALAL = "HALAL"
    KOSHER = "KOSHER"
    KETO = "KETO"
    LOW_CARB = "LOW_CARB"


class Address(BaseModel):
    """User address schema"""
    id: Optional[str] = Field(default=None, description="Address ID")
    name: Optional[str] = Field(default=None, description="Address nickname (e.g., 'Home', 'Work')")
    street_address: str = Field(description="Street address")
    city: str = Field(description="City")
    state: str = Field(description="State or province")
    zip_code: str = Field(description="ZIP or postal code")
    country_code: str = Field(description="ISO 3166-1 alpha-2 country code")
    latitude: Optional[float] = Field(default=None, description="Latitude coordinate")
    longitude: Optional[float] = Field(default=None, description="Longitude coordinate")
    instructions: Optional[str] = Field(default=None, description="Delivery instructions")
    is_default: bool = Field(default=False, description="Whether this is the default address")
    
    model_config = ConfigDict(from_attributes=True)


class UserPreferences(BaseModel):
    """User preferences schema"""
    dietary_restrictions: List[DietaryRestriction] = Field(default=[], description="Dietary restrictions")
    favorite_cuisines: List[str] = Field(default=[], description="Favorite cuisine types")
    spice_level: Optional[str] = Field(default=None, description="Preferred spice level")
    price_range: Optional[str] = Field(default=None, description="Preferred price range")
    delivery_time_preference: Optional[str] = Field(default=None, description="Preferred delivery time")
    notifications_enabled: bool = Field(default=True, description="Whether notifications are enabled")
    marketing_emails: bool = Field(default=True, description="Whether marketing emails are allowed")
    push_notifications: bool = Field(default=True, description="Whether push notifications are enabled")
    
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr = Field(description="User email address")
    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
    phone: Optional[str] = Field(default=None, description="Phone number")
    profile_image_url: Optional[str] = Field(default=None, description="Profile image URL")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="User status")
    user_type: UserType = Field(default=UserType.CUSTOMER, description="User type")
    
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(description="User password", min_length=8)
    confirm_password: str = Field(description="Password confirmation")
    address: Optional[Address] = Field(default=None, description="Initial address")
    preferences: Optional[UserPreferences] = Field(default=None, description="User preferences")


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    first_name: Optional[str] = Field(default=None, description="First name")
    last_name: Optional[str] = Field(default=None, description="Last name")
    phone: Optional[str] = Field(default=None, description="Phone number")
    profile_image_url: Optional[str] = Field(default=None, description="Profile image URL")
    status: Optional[UserStatus] = Field(default=None, description="User status")
    preferences: Optional[UserPreferences] = Field(default=None, description="User preferences")
    
    model_config = ConfigDict(from_attributes=True)


class User(UserBase, TimestampMixin):
    """Full user schema"""
    id: str = Field(description="Unique user identifier")
    uber_eats_id: Optional[str] = Field(default=None, description="Uber Eats user ID")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    email_verified: bool = Field(default=False, description="Whether email is verified")
    phone_verified: bool = Field(default=False, description="Whether phone is verified")
    total_orders: int = Field(default=0, description="Total number of orders")
    total_spent: float = Field(default=0.0, description="Total amount spent")
    loyalty_points: int = Field(default=0, description="Loyalty points balance")
    referral_code: Optional[str] = Field(default=None, description="User's referral code")
    referred_by: Optional[str] = Field(default=None, description="Referral code that user signed up with")
    
    model_config = ConfigDict(from_attributes=True)


class UserProfile(User):
    """Extended user profile with additional details"""
    addresses: List[Address] = Field(default=[], description="User addresses")
    preferences: UserPreferences = Field(description="User preferences")
    payment_methods: List[Dict[str, Any]] = Field(default=[], description="Payment methods")
    recent_orders: List[Dict[str, Any]] = Field(default=[], description="Recent orders")
    favorite_restaurants: List[Dict[str, Any]] = Field(default=[], description="Favorite restaurants")
    
    model_config = ConfigDict(from_attributes=True)


class UserList(PaginatedResponse[User]):
    """Paginated list of users"""
    users: List[User] = Field(description="List of users")
    
    # Override the generic items field
    @property
    def items(self) -> List[User]:
        return self.users


class UserAnalytics(BaseModel):
    """User analytics schema"""
    user_id: str = Field(description="User ID")
    period_days: int = Field(description="Analysis period in days")
    total_orders: int = Field(description="Total orders in period")
    total_spent: float = Field(description="Total amount spent in period")
    average_order_value: float = Field(description="Average order value")
    favorite_cuisines: List[Dict[str, Any]] = Field(description="Favorite cuisines with counts")
    ordering_patterns: Dict[str, Any] = Field(description="Ordering patterns analysis")
    
    model_config = ConfigDict(from_attributes=True)


class UserNotification(BaseModel):
    """User notification schema"""
    type: str = Field(description="Notification type")
    title: str = Field(description="Notification title")
    message: str = Field(description="Notification message")
    data: Dict[str, Any] = Field(default={}, description="Additional notification data")
    scheduled_at: Optional[datetime] = Field(default=None, description="Scheduled delivery time")
    
    model_config = ConfigDict(from_attributes=True)


class UserSegment(BaseModel):
    """User segment schema"""
    id: str = Field(description="Segment ID")
    name: str = Field(description="Segment name")
    description: Optional[str] = Field(default=None, description="Segment description")
    criteria: Dict[str, Any] = Field(description="Segmentation criteria")
    user_count: int = Field(default=0, description="Number of users in segment")
    created_at: datetime = Field(description="Creation timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class UserLoyalty(BaseModel):
    """User loyalty information schema"""
    user_id: str = Field(description="User ID")
    tier: str = Field(description="Loyalty tier")
    points_balance: int = Field(description="Current points balance")
    points_earned: int = Field(description="Total points earned")
    points_redeemed: int = Field(description="Total points redeemed")
    tier_progress: Dict[str, Any] = Field(description="Progress to next tier")
    benefits: List[Dict[str, Any]] = Field(description="Available benefits")
    
    model_config = ConfigDict(from_attributes=True)