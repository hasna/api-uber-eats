"""
Menu-related schemas for Uber Eats API
"""
from datetime import datetime, time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from enum import Enum

from app.schemas.base import TimestampMixin


class MenuItemStatus(str, Enum):
    """Menu item availability status"""
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    HIDDEN = "HIDDEN"


class PriceType(str, Enum):
    """Price type enumeration"""
    BASE_PRICE = "BASE_PRICE"
    MEMBER_PRICE = "MEMBER_PRICE"
    SALE_PRICE = "SALE_PRICE"


class TaxCategory(str, Enum):
    """Tax category enumeration"""
    FOOD = "FOOD"
    BEVERAGE = "BEVERAGE"
    ALCOHOL = "ALCOHOL"
    PREPARED_FOOD = "PREPARED_FOOD"
    NON_TAXABLE = "NON_TAXABLE"


class ModifierSelectionType(str, Enum):
    """Modifier selection type"""
    SINGLE = "SINGLE"
    MULTIPLE = "MULTIPLE"


class NutritionalInfo(BaseModel):
    """Nutritional information schema"""
    calories: Optional[int] = Field(default=None, description="Calories")
    total_fat_g: Optional[float] = Field(default=None, description="Total fat in grams")
    saturated_fat_g: Optional[float] = Field(default=None, description="Saturated fat in grams")
    cholesterol_mg: Optional[float] = Field(default=None, description="Cholesterol in milligrams")
    sodium_mg: Optional[float] = Field(default=None, description="Sodium in milligrams")
    carbohydrates_g: Optional[float] = Field(default=None, description="Carbohydrates in grams")
    fiber_g: Optional[float] = Field(default=None, description="Fiber in grams")
    sugar_g: Optional[float] = Field(default=None, description="Sugar in grams")
    protein_g: Optional[float] = Field(default=None, description="Protein in grams")
    
    model_config = ConfigDict(from_attributes=True)


class DietaryInfo(BaseModel):
    """Dietary information schema"""
    is_vegetarian: bool = Field(default=False, description="Vegetarian")
    is_vegan: bool = Field(default=False, description="Vegan")
    is_gluten_free: bool = Field(default=False, description="Gluten-free")
    is_dairy_free: bool = Field(default=False, description="Dairy-free")
    is_nut_free: bool = Field(default=False, description="Nut-free")
    is_kosher: bool = Field(default=False, description="Kosher")
    is_halal: bool = Field(default=False, description="Halal")
    is_organic: bool = Field(default=False, description="Organic")
    contains_alcohol: bool = Field(default=False, description="Contains alcohol")
    
    model_config = ConfigDict(from_attributes=True)


class Price(BaseModel):
    """Price schema"""
    amount: float = Field(description="Price amount")
    currency_code: str = Field(default="USD", description="ISO 4217 currency code")
    price_type: PriceType = Field(default=PriceType.BASE_PRICE, description="Type of price")
    
    model_config = ConfigDict(from_attributes=True)


class ItemSchedule(BaseModel):
    """Item availability schedule"""
    day_of_week: str = Field(description="Day of week")
    start_time: time = Field(description="Start time")
    end_time: time = Field(description="End time")
    
    model_config = ConfigDict(from_attributes=True)


class ModifierBase(BaseModel):
    """Base modifier schema"""
    name: str = Field(description="Modifier name")
    external_id: str = Field(description="External modifier ID")
    description: Optional[str] = Field(default=None, description="Modifier description")
    price: Price = Field(description="Modifier price")
    is_default: bool = Field(default=False, description="Whether selected by default")
    min_quantity: int = Field(default=0, description="Minimum quantity")
    max_quantity: Optional[int] = Field(default=None, description="Maximum quantity")
    
    model_config = ConfigDict(from_attributes=True)


class Modifier(ModifierBase):
    """Complete modifier schema"""
    id: str = Field(description="Modifier ID")
    nutritional_info: Optional[NutritionalInfo] = Field(default=None, description="Nutritional information")
    dietary_info: Optional[DietaryInfo] = Field(default=None, description="Dietary information")
    
    model_config = ConfigDict(from_attributes=True)


class ModifierGroupBase(BaseModel):
    """Base modifier group schema"""
    name: str = Field(description="Modifier group name")
    external_id: str = Field(description="External modifier group ID")
    description: Optional[str] = Field(default=None, description="Group description")
    selection_type: ModifierSelectionType = Field(description="Selection type")
    is_required: bool = Field(default=False, description="Whether selection is required")
    min_selections: int = Field(default=0, description="Minimum selections required")
    max_selections: Optional[int] = Field(default=None, description="Maximum selections allowed")
    
    model_config = ConfigDict(from_attributes=True)


class ModifierGroup(ModifierGroupBase):
    """Complete modifier group schema"""
    id: str = Field(description="Modifier group ID")
    modifiers: List[Modifier] = Field(description="List of modifiers in group")
    
    model_config = ConfigDict(from_attributes=True)


class MenuItemBase(BaseModel):
    """Base menu item schema"""
    name: str = Field(description="Item name")
    external_id: str = Field(description="External item ID")
    description: Optional[str] = Field(default=None, description="Item description")
    price: Price = Field(description="Item price")
    image_url: Optional[HttpUrl] = Field(default=None, description="Item image URL")
    tax_category: TaxCategory = Field(default=TaxCategory.FOOD, description="Tax category")
    barcode: Optional[str] = Field(default=None, description="Item barcode")
    sku: Optional[str] = Field(default=None, description="Stock keeping unit")
    sort_order: int = Field(default=0, description="Display sort order")
    
    model_config = ConfigDict(from_attributes=True)


class MenuItemCreate(MenuItemBase):
    """Schema for creating a menu item"""
    modifier_groups: Optional[List[str]] = Field(default=None, description="List of modifier group IDs")
    nutritional_info: Optional[NutritionalInfo] = Field(default=None, description="Nutritional information")
    dietary_info: Optional[DietaryInfo] = Field(default=None, description="Dietary information")
    schedules: Optional[List[ItemSchedule]] = Field(default=None, description="Availability schedules")


class MenuItemUpdate(BaseModel):
    """Schema for updating a menu item"""
    name: Optional[str] = Field(default=None, description="Item name")
    description: Optional[str] = Field(default=None, description="Item description")
    price: Optional[Price] = Field(default=None, description="Item price")
    status: Optional[MenuItemStatus] = Field(default=None, description="Item status")
    image_url: Optional[HttpUrl] = Field(default=None, description="Item image URL")
    modifier_groups: Optional[List[str]] = Field(default=None, description="List of modifier group IDs")
    nutritional_info: Optional[NutritionalInfo] = Field(default=None, description="Nutritional information")
    dietary_info: Optional[DietaryInfo] = Field(default=None, description="Dietary information")
    
    model_config = ConfigDict(from_attributes=True)


class MenuItem(MenuItemBase, TimestampMixin):
    """Complete menu item schema"""
    id: str = Field(description="Menu item ID")
    status: MenuItemStatus = Field(description="Item availability status")
    category_id: str = Field(description="Category ID")
    modifier_groups: List[ModifierGroup] = Field(default_factory=list, description="Modifier groups")
    nutritional_info: Optional[NutritionalInfo] = Field(default=None, description="Nutritional information")
    dietary_info: Optional[DietaryInfo] = Field(default=None, description="Dietary information")
    schedules: Optional[List[ItemSchedule]] = Field(default=None, description="Availability schedules")
    quantity_available: Optional[int] = Field(default=None, description="Available quantity")
    
    model_config = ConfigDict(from_attributes=True)


class MenuCategoryBase(BaseModel):
    """Base menu category schema"""
    name: str = Field(description="Category name")
    external_id: str = Field(description="External category ID")
    description: Optional[str] = Field(default=None, description="Category description")
    sort_order: int = Field(default=0, description="Display sort order")
    
    model_config = ConfigDict(from_attributes=True)


class MenuCategory(MenuCategoryBase):
    """Complete menu category schema"""
    id: str = Field(description="Category ID")
    items: List[MenuItem] = Field(default_factory=list, description="Items in category")
    
    model_config = ConfigDict(from_attributes=True)


class MenuBase(BaseModel):
    """Base menu schema"""
    name: str = Field(description="Menu name")
    external_id: str = Field(description="External menu ID")
    description: Optional[str] = Field(default=None, description="Menu description")
    
    model_config = ConfigDict(from_attributes=True)


class MenuCreate(MenuBase):
    """Schema for creating a menu"""
    categories: List[MenuCategoryBase] = Field(description="Menu categories")


class Menu(MenuBase, TimestampMixin):
    """Complete menu schema"""
    id: str = Field(description="Menu ID")
    store_id: str = Field(description="Store ID")
    categories: List[MenuCategory] = Field(description="Menu categories")
    is_active: bool = Field(default=True, description="Whether menu is active")
    version: int = Field(default=1, description="Menu version number")
    
    model_config = ConfigDict(from_attributes=True)


class MenuUpload(BaseModel):
    """Schema for bulk menu upload"""
    store_id: str = Field(description="Store ID")
    menu: MenuCreate = Field(description="Menu data")
    validate_only: bool = Field(default=False, description="Only validate without saving")
    
    model_config = ConfigDict(from_attributes=True)


class ItemAvailabilityUpdate(BaseModel):
    """Schema for updating item availability"""
    item_ids: List[str] = Field(description="List of item IDs")
    status: MenuItemStatus = Field(description="New availability status")
    quantity_available: Optional[int] = Field(default=None, description="Available quantity")
    
    model_config = ConfigDict(from_attributes=True)


class MenuValidationResult(BaseModel):
    """Menu validation result"""
    is_valid: bool = Field(description="Whether menu is valid")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Validation errors")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="Validation warnings")
    
    model_config = ConfigDict(from_attributes=True)