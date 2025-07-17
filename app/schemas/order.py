"""
Order-related schemas for Uber Eats API
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

from app.schemas.base import TimestampMixin
from app.schemas.store import Address, Contact


class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DENIED = "DENIED"
    PREPARING = "PREPARING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    DISPATCHED = "DISPATCHED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class OrderType(str, Enum):
    """Order type enumeration"""
    DELIVERY = "DELIVERY"
    PICKUP = "PICKUP"
    DINE_IN = "DINE_IN"


class PaymentMethod(str, Enum):
    """Payment method enumeration"""
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    CASH = "CASH"
    UBER_CASH = "UBER_CASH"
    PAYPAL = "PAYPAL"
    OTHER = "OTHER"


class CancelReason(str, Enum):
    """Order cancellation reason"""
    CUSTOMER_REQUESTED = "CUSTOMER_REQUESTED"
    MERCHANT_REJECTED = "MERCHANT_REJECTED"
    MERCHANT_UNAVAILABLE = "MERCHANT_UNAVAILABLE"
    ITEMS_UNAVAILABLE = "ITEMS_UNAVAILABLE"
    DELIVERY_ISSUE = "DELIVERY_ISSUE"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    FRAUD = "FRAUD"
    OTHER = "OTHER"


class FulfillmentIssueType(str, Enum):
    """Fulfillment issue type"""
    ITEM_UNAVAILABLE = "ITEM_UNAVAILABLE"
    ITEM_SUBSTITUTION = "ITEM_SUBSTITUTION"
    QUANTITY_ADJUSTMENT = "QUANTITY_ADJUSTMENT"
    OTHER = "OTHER"


class Customer(BaseModel):
    """Customer information schema"""
    first_name: str = Field(description="Customer first name")
    last_name: Optional[str] = Field(default=None, description="Customer last name")
    phone: str = Field(description="Customer phone number")
    email: Optional[str] = Field(default=None, description="Customer email")
    
    model_config = ConfigDict(from_attributes=True)


class DeliveryInfo(BaseModel):
    """Delivery information schema"""
    address: Address = Field(description="Delivery address")
    instructions: Optional[str] = Field(default=None, description="Delivery instructions")
    estimated_delivery_time: datetime = Field(description="Estimated delivery time")
    courier_name: Optional[str] = Field(default=None, description="Courier name")
    courier_phone: Optional[str] = Field(default=None, description="Courier phone")
    tracking_url: Optional[str] = Field(default=None, description="Delivery tracking URL")
    
    model_config = ConfigDict(from_attributes=True)


class OrderItemModifier(BaseModel):
    """Order item modifier schema"""
    id: str = Field(description="Modifier ID")
    external_id: str = Field(description="External modifier ID")
    name: str = Field(description="Modifier name")
    quantity: int = Field(description="Modifier quantity")
    price: float = Field(description="Modifier price")
    
    model_config = ConfigDict(from_attributes=True)


class OrderItem(BaseModel):
    """Order item schema"""
    id: str = Field(description="Order item ID")
    external_id: str = Field(description="External item ID")
    name: str = Field(description="Item name")
    quantity: int = Field(description="Item quantity")
    price: float = Field(description="Item unit price")
    total_price: float = Field(description="Total price (quantity * price + modifiers)")
    special_instructions: Optional[str] = Field(default=None, description="Special instructions")
    modifiers: List[OrderItemModifier] = Field(default_factory=list, description="Item modifiers")
    
    model_config = ConfigDict(from_attributes=True)


class OrderTotals(BaseModel):
    """Order totals breakdown"""
    subtotal: float = Field(description="Subtotal before taxes and fees")
    tax: float = Field(description="Tax amount")
    delivery_fee: float = Field(description="Delivery fee")
    service_fee: float = Field(description="Service fee")
    tip: float = Field(description="Tip amount")
    discount: float = Field(default=0, description="Discount amount")
    total: float = Field(description="Total amount")
    currency_code: str = Field(default="USD", description="ISO 4217 currency code")
    
    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    """Base order schema"""
    external_reference_id: str = Field(description="External order reference")
    store_id: str = Field(description="Store ID")
    order_type: OrderType = Field(description="Type of order")
    placed_at: datetime = Field(description="Order placement time")
    
    model_config = ConfigDict(from_attributes=True)


class OrderCreate(OrderBase):
    """Schema for creating an order (webhook payload)"""
    uber_order_id: str = Field(description="Uber's order ID")
    customer: Customer = Field(description="Customer information")
    items: List[OrderItem] = Field(description="Order items")
    totals: OrderTotals = Field(description="Order totals")
    payment_method: PaymentMethod = Field(description="Payment method")
    delivery_info: Optional[DeliveryInfo] = Field(default=None, description="Delivery information")
    estimated_ready_time: datetime = Field(description="Estimated ready time")
    special_instructions: Optional[str] = Field(default=None, description="Special order instructions")


class Order(OrderBase, TimestampMixin):
    """Complete order schema"""
    id: str = Field(description="Order ID")
    uber_order_id: str = Field(description="Uber's order ID")
    status: OrderStatus = Field(description="Order status")
    customer: Customer = Field(description="Customer information")
    items: List[OrderItem] = Field(description="Order items")
    totals: OrderTotals = Field(description="Order totals")
    payment_method: PaymentMethod = Field(description="Payment method")
    delivery_info: Optional[DeliveryInfo] = Field(default=None, description="Delivery information")
    estimated_ready_time: datetime = Field(description="Estimated ready time")
    actual_ready_time: Optional[datetime] = Field(default=None, description="Actual ready time")
    special_instructions: Optional[str] = Field(default=None, description="Special order instructions")
    merchant_notes: Optional[str] = Field(default=None, description="Merchant notes")
    
    model_config = ConfigDict(from_attributes=True)


class OrderAccept(BaseModel):
    """Schema for accepting an order"""
    estimated_ready_time: datetime = Field(description="Estimated ready time")
    external_reference_id: str = Field(description="External order reference")
    confirm_code: Optional[str] = Field(default=None, description="Confirmation code")
    
    model_config = ConfigDict(from_attributes=True)


class OrderDeny(BaseModel):
    """Schema for denying an order"""
    reason: CancelReason = Field(description="Denial reason")
    reason_details: Optional[str] = Field(default=None, description="Additional reason details")
    
    model_config = ConfigDict(from_attributes=True)


class OrderCancel(BaseModel):
    """Schema for cancelling an order"""
    reason: CancelReason = Field(description="Cancellation reason")
    reason_details: Optional[str] = Field(default=None, description="Additional reason details")
    cancelled_by: str = Field(description="Who initiated the cancellation")
    
    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status"""
    status: OrderStatus = Field(description="New order status")
    estimated_ready_time: Optional[datetime] = Field(default=None, description="Updated ready time")
    notes: Optional[str] = Field(default=None, description="Status update notes")
    
    model_config = ConfigDict(from_attributes=True)


class FulfillmentIssue(BaseModel):
    """Fulfillment issue schema"""
    issue_type: FulfillmentIssueType = Field(description="Type of issue")
    item_id: str = Field(description="Affected item ID")
    description: str = Field(description="Issue description")
    proposed_resolution: Optional[str] = Field(default=None, description="Proposed resolution")
    
    model_config = ConfigDict(from_attributes=True)


class ResolveFulfillmentIssue(BaseModel):
    """Schema for resolving fulfillment issues"""
    issue_id: str = Field(description="Issue ID")
    resolution: str = Field(description="Resolution action")
    replacement_items: Optional[List[OrderItem]] = Field(default=None, description="Replacement items")
    refund_amount: Optional[float] = Field(default=None, description="Refund amount if applicable")
    
    model_config = ConfigDict(from_attributes=True)


class OrderList(BaseModel):
    """List of orders response"""
    orders: List[Order] = Field(description="List of orders")
    total: int = Field(description="Total number of orders")
    has_more: bool = Field(description="Whether there are more orders")
    next_cursor: Optional[str] = Field(default=None, description="Cursor for next page")
    
    model_config = ConfigDict(from_attributes=True)


class OrderMetrics(BaseModel):
    """Order metrics schema"""
    total_orders: int = Field(description="Total number of orders")
    pending_orders: int = Field(description="Number of pending orders")
    active_orders: int = Field(description="Number of active orders")
    completed_orders: int = Field(description="Number of completed orders")
    cancelled_orders: int = Field(description="Number of cancelled orders")
    average_prep_time_minutes: float = Field(description="Average preparation time")
    acceptance_rate: float = Field(description="Order acceptance rate")
    
    model_config = ConfigDict(from_attributes=True)