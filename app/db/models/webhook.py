"""
Webhook event logging model
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.session import Base


class WebhookEvent(Base):
    """Webhook event log for audit and debugging"""
    
    __tablename__ = "webhook_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event identification
    event_id = Column(String, index=True)  # Uber Eats event ID if provided
    event_type = Column(String, nullable=False, index=True)
    source = Column(String, default="uber_eats", nullable=False)
    
    # Payload data
    payload = Column(JSON, nullable=False)
    headers = Column(JSON)
    
    # Processing information
    processed = Column(Boolean, default=False, nullable=False)
    processing_attempts = Column(Integer, default=0)
    processing_error = Column(Text)
    processed_at = Column(DateTime(timezone=True))
    
    # Verification
    signature_verified = Column(Boolean, default=False)
    
    # Related entities
    store_id = Column(String, index=True)
    order_id = Column(String, index=True)
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)