"""
Webhook-related schemas for Uber Eats API
"""
from datetime import datetime
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

from app.schemas.order import OrderCreate, OrderStatus, CancelReason
from app.schemas.store import StoreStatus


class WebhookEventType(str, Enum):
    """Webhook event types"""
    # Order events
    ORDER_CREATED = "orders.notification"
    ORDER_CANCELLED = "orders.cancel"
    ORDER_STATUS_UPDATED = "orders.status_update"
    
    # Store events
    STORE_STATUS_UPDATED = "store.status"
    STORE_PROVISIONED = "store.provisioned"
    STORE_DEPROVISIONED = "store.deprovisioned"
    
    # Schedule order events
    SCHEDULED_ORDER_CREATED = "orders.scheduled_notification"
    
    # Fulfillment events
    FULFILLMENT_ISSUE = "orders.fulfillment_issue"
    
    # Report events
    REPORT_COMPLETED = "report.success"
    REPORT_FAILED = "report.failure"


class WebhookStatus(str, Enum):
    """Webhook processing status"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class WebhookMetadata(BaseModel):
    """Webhook metadata"""
    event_id: str = Field(description="Unique event ID")
    event_type: WebhookEventType = Field(description="Event type")
    event_time: datetime = Field(description="Event timestamp")
    resource_id: str = Field(description="ID of the resource that triggered the event")
    webhook_version: str = Field(default="1.0", description="Webhook version")
    
    model_config = ConfigDict(from_attributes=True)


class WebhookBase(BaseModel):
    """Base webhook schema"""
    metadata: WebhookMetadata = Field(description="Event metadata")
    
    model_config = ConfigDict(from_attributes=True)


class OrderNotificationWebhook(WebhookBase):
    """Order notification webhook"""
    order: OrderCreate = Field(description="New order data")
    store_id: str = Field(description="Store ID")
    
    model_config = ConfigDict(from_attributes=True)


class OrderCancelWebhook(WebhookBase):
    """Order cancellation webhook"""
    order_id: str = Field(description="Order ID")
    uber_order_id: str = Field(description="Uber order ID")
    store_id: str = Field(description="Store ID")
    cancel_reason: CancelReason = Field(description="Cancellation reason")
    cancel_details: Optional[str] = Field(default=None, description="Additional cancellation details")
    cancelled_by: str = Field(description="Who cancelled the order")
    cancelled_at: datetime = Field(description="Cancellation timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdateWebhook(WebhookBase):
    """Order status update webhook"""
    order_id: str = Field(description="Order ID")
    uber_order_id: str = Field(description="Uber order ID")
    store_id: str = Field(description="Store ID")
    old_status: OrderStatus = Field(description="Previous order status")
    new_status: OrderStatus = Field(description="New order status")
    updated_at: datetime = Field(description="Update timestamp")
    notes: Optional[str] = Field(default=None, description="Status update notes")
    
    model_config = ConfigDict(from_attributes=True)


class StoreStatusWebhook(WebhookBase):
    """Store status update webhook"""
    store_id: str = Field(description="Store ID")
    uber_store_id: str = Field(description="Uber store ID")
    old_status: StoreStatus = Field(description="Previous store status")
    new_status: StoreStatus = Field(description="New store status")
    reason: Optional[str] = Field(default=None, description="Status change reason")
    updated_at: datetime = Field(description="Update timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class StoreProvisionedWebhook(WebhookBase):
    """Store provisioned webhook"""
    store_id: str = Field(description="Store ID")
    uber_store_id: str = Field(description="Uber store ID")
    external_store_id: str = Field(description="External store ID")
    provisioned_at: datetime = Field(description="Provisioning timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class FulfillmentIssueWebhook(WebhookBase):
    """Fulfillment issue webhook"""
    order_id: str = Field(description="Order ID")
    uber_order_id: str = Field(description="Uber order ID")
    store_id: str = Field(description="Store ID")
    issue_type: str = Field(description="Type of fulfillment issue")
    issue_description: str = Field(description="Issue description")
    affected_items: List[Dict[str, Any]] = Field(description="Affected order items")
    customer_preference: Optional[Dict[str, Any]] = Field(default=None, description="Customer replacement preference")
    
    model_config = ConfigDict(from_attributes=True)


class ReportWebhook(WebhookBase):
    """Report completion webhook"""
    report_id: str = Field(description="Report ID")
    report_type: str = Field(description="Type of report")
    status: str = Field(description="Report status")
    download_url: Optional[str] = Field(default=None, description="Report download URL")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    completed_at: datetime = Field(description="Completion timestamp")
    
    model_config = ConfigDict(from_attributes=True)


# Union type for all webhook payloads
WebhookPayload = Union[
    OrderNotificationWebhook,
    OrderCancelWebhook,
    OrderStatusUpdateWebhook,
    StoreStatusWebhook,
    StoreProvisionedWebhook,
    FulfillmentIssueWebhook,
    ReportWebhook,
]


class WebhookEvent(BaseModel):
    """Webhook event record schema"""
    id: str = Field(description="Event record ID")
    event_id: str = Field(description="Uber event ID")
    event_type: WebhookEventType = Field(description="Event type")
    payload: Dict[str, Any] = Field(description="Raw webhook payload")
    status: WebhookStatus = Field(description="Processing status")
    attempts: int = Field(default=0, description="Number of processing attempts")
    error_message: Optional[str] = Field(default=None, description="Error message if processing failed")
    processed_at: Optional[datetime] = Field(default=None, description="Processing timestamp")
    created_at: datetime = Field(description="Event received timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class WebhookResponse(BaseModel):
    """Standard webhook response"""
    received: bool = Field(default=True, description="Indicates webhook was received")
    event_id: str = Field(description="Event ID for tracking")
    
    model_config = ConfigDict(from_attributes=True)


class WebhookRetry(BaseModel):
    """Webhook retry configuration"""
    max_attempts: int = Field(default=3, description="Maximum retry attempts")
    backoff_seconds: int = Field(default=60, description="Initial backoff in seconds")
    max_backoff_seconds: int = Field(default=3600, description="Maximum backoff in seconds")
    
    model_config = ConfigDict(from_attributes=True)