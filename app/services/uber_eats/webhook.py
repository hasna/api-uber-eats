"""
Uber Eats Webhook Management Service
"""
from typing import Any, Dict, List, Optional
import hmac
import hashlib
import json
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.services.uber_eats.base import UberEatsBaseService
from app.schemas.webhook import (
    WebhookEvent,
    WebhookEventType,
    OrderWebhook,
    StoreWebhook,
    FulfillmentIssueWebhook,
)
from app.core.config import settings

logger = structlog.get_logger()


class UberEatsWebhookService(UberEatsBaseService):
    """Service for handling Uber Eats webhooks"""
    
    def __init__(self, db: AsyncSession, access_token: Optional[str] = None):
        super().__init__(db, access_token)
        self.webhook_secret = settings.UBER_EATS_WEBHOOK_SECRET
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: str,
    ) -> bool:
        """
        Verify webhook signature to ensure authenticity
        
        Uber Eats webhooks include a signature header for verification
        """
        if not self.webhook_secret or not settings.ENABLE_WEBHOOK_VERIFICATION:
            return True  # Skip verification if not configured
        
        try:
            # Create expected signature
            message = f"{timestamp}.{payload.decode('utf-8')}"
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(f"sha256={expected_signature}", signature)
            
        except Exception as e:
            logger.error("Failed to verify webhook signature", error=str(e))
            return False
    
    async def process_webhook_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
    ) -> bool:
        """
        Process incoming webhook event based on type
        """
        try:
            # Verify signature if enabled
            if settings.ENABLE_WEBHOOK_VERIFICATION:
                signature = headers.get("X-Uber-Signature")
                timestamp = headers.get("X-Uber-Timestamp")
                payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
                
                if not self.verify_webhook_signature(payload_bytes, signature, timestamp):
                    logger.warning("Invalid webhook signature")
                    return False
            
            # Route to appropriate handler based on event type
            if event_type == WebhookEventType.ORDER_CREATED.value:
                return await self._handle_order_created(payload)
            elif event_type == WebhookEventType.ORDER_CANCELLED.value:
                return await self._handle_order_cancelled(payload)
            elif event_type == WebhookEventType.ORDER_STATUS_UPDATED.value:
                return await self._handle_order_status_updated(payload)
            elif event_type == WebhookEventType.STORE_STATUS_UPDATED.value:
                return await self._handle_store_status_updated(payload)
            elif event_type == WebhookEventType.STORE_PROVISIONED.value:
                return await self._handle_store_provisioned(payload)
            elif event_type == WebhookEventType.STORE_DEPROVISIONED.value:
                return await self._handle_store_deprovisioned(payload)
            elif event_type == WebhookEventType.SCHEDULED_ORDER_CREATED.value:
                return await self._handle_scheduled_order_created(payload)
            elif event_type == WebhookEventType.FULFILLMENT_ISSUE.value:
                return await self._handle_fulfillment_issue(payload)
            else:
                logger.warning("Unknown webhook event type", event_type=event_type)
                return False
                
        except Exception as e:
            logger.error("Failed to process webhook event", event_type=event_type, error=str(e))
            return False
    
    async def _handle_order_created(self, payload: Dict[str, Any]) -> bool:
        """Handle new order webhook"""
        try:
            order_webhook = OrderWebhook(**payload)
            
            logger.info(
                "New order received",
                order_id=order_webhook.order_id,
                store_id=order_webhook.store_id,
                total=order_webhook.total,
            )
            
            # TODO: Add business logic for new order processing
            # - Store order in database
            # - Send notification to restaurant
            # - Update inventory if needed
            # - Trigger POS integration
            
            return True
            
        except Exception as e:
            logger.error("Failed to handle order created webhook", error=str(e))
            return False
    
    async def _handle_order_cancelled(self, payload: Dict[str, Any]) -> bool:
        """Handle order cancellation webhook"""
        try:
            order_webhook = OrderWebhook(**payload)
            
            logger.info(
                "Order cancelled",
                order_id=order_webhook.order_id,
                store_id=order_webhook.store_id,
                reason=payload.get("cancellation_reason"),
            )
            
            # TODO: Add business logic for order cancellation
            # - Update order status in database
            # - Refund inventory
            # - Notify restaurant
            # - Update POS system
            
            return True
            
        except Exception as e:
            logger.error("Failed to handle order cancelled webhook", error=str(e))
            return False
    
    async def _handle_order_status_updated(self, payload: Dict[str, Any]) -> bool:
        """Handle order status update webhook"""
        try:
            order_webhook = OrderWebhook(**payload)
            
            logger.info(
                "Order status updated",
                order_id=order_webhook.order_id,
                store_id=order_webhook.store_id,
                new_status=payload.get("status"),
            )
            
            # TODO: Add business logic for status updates
            # - Update order status in database
            # - Send notifications based on status
            # - Update delivery tracking
            # - Sync with POS system
            
            return True
            
        except Exception as e:
            logger.error("Failed to handle order status updated webhook", error=str(e))
            return False
    
    async def _handle_store_status_updated(self, payload: Dict[str, Any]) -> bool:
        """Handle store status change webhook"""
        try:
            store_webhook = StoreWebhook(**payload)
            
            logger.info(
                "Store status updated",
                store_id=store_webhook.store_id,
                new_status=payload.get("status"),
            )
            
            # TODO: Add business logic for store status changes
            # - Update store status in database
            # - Notify staff of status changes
            # - Update external systems
            
            return True
            
        except Exception as e:
            logger.error("Failed to handle store status updated webhook", error=str(e))
            return False
    
    async def _handle_store_provisioned(self, payload: Dict[str, Any]) -> bool:
        """Handle store provisioning webhook"""
        try:
            store_webhook = StoreWebhook(**payload)
            
            logger.info(
                "Store provisioned",
                store_id=store_webhook.store_id,
            )
            
            # TODO: Add business logic for store provisioning
            # - Initialize store data
            # - Set up initial configuration
            # - Send welcome notification
            
            return True
            
        except Exception as e:
            logger.error("Failed to handle store provisioned webhook", error=str(e))
            return False
    
    async def _handle_store_deprovisioned(self, payload: Dict[str, Any]) -> bool:
        """Handle store deprovisioning webhook"""
        try:
            store_webhook = StoreWebhook(**payload)
            
            logger.info(
                "Store deprovisioned",
                store_id=store_webhook.store_id,
            )
            
            # TODO: Add business logic for store deprovisioning
            # - Archive store data
            # - Disable integrations
            # - Send notification
            
            return True
            
        except Exception as e:
            logger.error("Failed to handle store deprovisioned webhook", error=str(e))
            return False
    
    async def _handle_scheduled_order_created(self, payload: Dict[str, Any]) -> bool:
        """Handle scheduled order webhook"""
        try:
            order_webhook = OrderWebhook(**payload)
            
            logger.info(
                "Scheduled order created",
                order_id=order_webhook.order_id,
                store_id=order_webhook.store_id,
                scheduled_time=payload.get("scheduled_for"),
            )
            
            # TODO: Add business logic for scheduled orders
            # - Store scheduled order
            # - Set up preparation reminders
            # - Plan inventory allocation
            
            return True
            
        except Exception as e:
            logger.error("Failed to handle scheduled order created webhook", error=str(e))
            return False
    
    async def _handle_fulfillment_issue(self, payload: Dict[str, Any]) -> bool:
        """Handle fulfillment issue webhook"""
        try:
            issue_webhook = FulfillmentIssueWebhook(**payload)
            
            logger.warning(
                "Fulfillment issue reported",
                order_id=issue_webhook.order_id,
                store_id=issue_webhook.store_id,
                issue_type=issue_webhook.issue_type,
                description=issue_webhook.description,
            )
            
            # TODO: Add business logic for fulfillment issues
            # - Log issue in database
            # - Send alert to management
            # - Initiate resolution process
            # - Update customer if needed
            
            return True
            
        except Exception as e:
            logger.error("Failed to handle fulfillment issue webhook", error=str(e))
            return False
    
    async def configure_webhook_endpoints(
        self,
        webhook_url: str,
        events: List[WebhookEventType],
    ) -> bool:
        """
        Configure webhook endpoints with Uber Eats
        
        Uber Eats API: POST /v1/eats/webhooks
        """
        try:
            payload = {
                "url": webhook_url,
                "events": [event.value for event in events],
                "active": True,
            }
            
            await self.post("/v1/eats/webhooks", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to configure webhook endpoints", error=str(e))
            return False
    
    async def list_webhook_configurations(self) -> List[Dict[str, Any]]:
        """
        List configured webhook endpoints
        
        Uber Eats API: GET /v1/eats/webhooks
        """
        try:
            response_data = await self.get("/v1/eats/webhooks")
            return response_data.get("webhooks", [])
            
        except Exception as e:
            logger.error("Failed to list webhook configurations", error=str(e))
            return []
    
    async def update_webhook_configuration(
        self,
        webhook_id: str,
        webhook_url: Optional[str] = None,
        events: Optional[List[WebhookEventType]] = None,
        active: Optional[bool] = None,
    ) -> bool:
        """
        Update webhook configuration
        
        Uber Eats API: PUT /v1/eats/webhooks/{webhook_id}
        """
        try:
            payload = {}
            
            if webhook_url:
                payload["url"] = webhook_url
            if events:
                payload["events"] = [event.value for event in events]
            if active is not None:
                payload["active"] = active
            
            await self.put(f"/v1/eats/webhooks/{webhook_id}", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to update webhook configuration", webhook_id=webhook_id, error=str(e))
            return False
    
    async def delete_webhook_configuration(self, webhook_id: str) -> bool:
        """
        Delete webhook configuration
        
        Uber Eats API: DELETE /v1/eats/webhooks/{webhook_id}
        """
        try:
            return await self.delete(f"/v1/eats/webhooks/{webhook_id}")
            
        except Exception as e:
            logger.error("Failed to delete webhook configuration", webhook_id=webhook_id, error=str(e))
            return False
    
    async def test_webhook_endpoint(self, webhook_url: str) -> bool:
        """
        Test webhook endpoint connectivity
        
        Uber Eats API: POST /v1/eats/webhooks/test
        """
        try:
            payload = {
                "url": webhook_url,
                "event_type": WebhookEventType.ORDER_CREATED.value,
            }
            
            await self.post("/v1/eats/webhooks/test", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to test webhook endpoint", webhook_url=webhook_url, error=str(e))
            return False
    
    # Utility methods
    
    def create_webhook_response(self, success: bool = True, message: str = "OK") -> Dict[str, Any]:
        """Create standard webhook response"""
        return {
            "success": success,
            "message": message,
            "timestamp": logger.info,
        }
    
    async def log_webhook_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        processed: bool,
        error: Optional[str] = None,
    ) -> None:
        """Log webhook event for audit purposes"""
        try:
            # TODO: Store webhook events in database for audit trail
            logger.info(
                "Webhook event logged",
                event_type=event_type,
                processed=processed,
                error=error,
                payload_size=len(str(payload)),
            )
            
        except Exception as e:
            logger.error("Failed to log webhook event", error=str(e))