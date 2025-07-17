"""
Uber Eats Webhook endpoints
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import hmac
import hashlib
import json
from datetime import datetime

from app.core.config import settings
from app.db.session import get_db
from app.schemas.webhook import (
    WebhookEventType,
    WebhookResponse,
    WebhookEvent,
    OrderNotificationWebhook,
    OrderCancelWebhook,
    OrderStatusUpdateWebhook,
    StoreStatusWebhook,
    StoreProvisionedWebhook,
    FulfillmentIssueWebhook,
    ReportWebhook,
)
from app.services.uber_eats import UberEatsWebhookService

router = APIRouter()


async def verify_webhook_signature(
    request: Request,
    x_uber_signature: Optional[str] = Header(None),
    x_uber_timestamp: Optional[str] = Header(None),
) -> bool:
    """Verify webhook signature from Uber Eats"""
    if not settings.ENABLE_WEBHOOK_VERIFICATION:
        return True
    
    if not x_uber_signature or not x_uber_timestamp:
        return False
    
    # Get raw body
    body = await request.body()
    
    # Create signature
    message = f"{x_uber_timestamp}.{body.decode('utf-8')}"
    expected_signature = hmac.new(
        settings.UBER_EATS_WEBHOOK_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    return hmac.compare_digest(expected_signature, x_uber_signature)


@router.post("/", response_model=WebhookResponse)
async def handle_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    x_uber_signature: Optional[str] = Header(None),
    x_uber_timestamp: Optional[str] = Header(None),
) -> WebhookResponse:
    """
    Main webhook endpoint for Uber Eats events
    
    Handles all incoming webhooks from Uber Eats
    """
    # Verify signature
    if not await verify_webhook_signature(request, x_uber_signature, x_uber_timestamp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )
    
    # Parse request body
    try:
        body = await request.body()
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )
    
    # Extract event type
    event_type = payload.get("metadata", {}).get("event_type")
    if not event_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing event type in webhook",
        )
    
    # Extract event ID
    event_id = payload.get("metadata", {}).get("event_id", "unknown")
    
    # Initialize webhook service
    webhook_service = UberEatsWebhookService(db)
    
    # Store webhook event
    await webhook_service.store_webhook_event(event_id, event_type, payload)
    
    # Process webhook in background
    background_tasks.add_task(
        process_webhook_event,
        event_type,
        payload,
        webhook_service
    )
    
    return WebhookResponse(
        received=True,
        event_id=event_id
    )


async def process_webhook_event(
    event_type: str,
    payload: Dict[str, Any],
    webhook_service: UberEatsWebhookService,
) -> None:
    """Process webhook event based on type"""
    try:
        if event_type == WebhookEventType.ORDER_CREATED:
            await webhook_service.handle_order_notification(payload)
            
        elif event_type == WebhookEventType.ORDER_CANCELLED:
            await webhook_service.handle_order_cancellation(payload)
            
        elif event_type == WebhookEventType.ORDER_STATUS_UPDATED:
            await webhook_service.handle_order_status_update(payload)
            
        elif event_type == WebhookEventType.STORE_STATUS_UPDATED:
            await webhook_service.handle_store_status_update(payload)
            
        elif event_type == WebhookEventType.STORE_PROVISIONED:
            await webhook_service.handle_store_provisioned(payload)
            
        elif event_type == WebhookEventType.FULFILLMENT_ISSUE:
            await webhook_service.handle_fulfillment_issue(payload)
            
        elif event_type == WebhookEventType.REPORT_COMPLETED:
            await webhook_service.handle_report_completion(payload)
            
        else:
            # Log unknown event type
            await webhook_service.handle_unknown_event(event_type, payload)
            
    except Exception as e:
        # Log error
        await webhook_service.log_webhook_error(
            payload.get("metadata", {}).get("event_id"),
            str(e)
        )


@router.get("/events", response_model=List[WebhookEvent])
async def list_webhook_events(
    event_type: Optional[WebhookEventType] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> List[WebhookEvent]:
    """
    List webhook events
    
    Returns historical webhook events for debugging and monitoring
    """
    webhook_service = UberEatsWebhookService(db)
    
    try:
        events = await webhook_service.list_webhook_events(
            event_type=event_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        return events
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch webhook events: {str(e)}",
        )


@router.get("/events/{event_id}", response_model=WebhookEvent)
async def get_webhook_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
) -> WebhookEvent:
    """
    Get specific webhook event
    
    Returns detailed information about a webhook event
    """
    webhook_service = UberEatsWebhookService(db)
    
    try:
        event = await webhook_service.get_webhook_event(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Webhook event {event_id} not found",
            )
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch webhook event: {str(e)}",
        )


@router.post("/events/{event_id}/retry")
async def retry_webhook_event(
    event_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Retry processing a failed webhook event
    
    Reprocesses a webhook event that previously failed
    """
    webhook_service = UberEatsWebhookService(db)
    
    try:
        event = await webhook_service.get_webhook_event(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Webhook event {event_id} not found",
            )
        
        # Add retry to background tasks
        background_tasks.add_task(
            process_webhook_event,
            event.event_type,
            event.payload,
            webhook_service
        )
        
        return {
            "message": "Webhook retry initiated",
            "event_id": event_id,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry webhook: {str(e)}",
        )


@router.post("/test")
async def test_webhook_endpoint(
    webhook_type: WebhookEventType,
    store_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Test webhook endpoint (sandbox only)
    
    Simulates a webhook event for testing
    """
    if not settings.UBER_EATS_SANDBOX_MODE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test webhooks can only be sent in sandbox mode",
        )
    
    webhook_service = UberEatsWebhookService(db)
    
    try:
        # Create test payload based on type
        test_payload = await webhook_service.create_test_webhook_payload(
            webhook_type,
            store_id
        )
        
        # Process the test webhook
        await process_webhook_event(webhook_type, test_payload, webhook_service)
        
        return {
            "message": "Test webhook processed successfully",
            "event_type": webhook_type,
            "payload": test_payload,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process test webhook: {str(e)}",
        )