"""
Uber Eats Delivery Management Service
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.services.uber_eats.base import UberEatsBaseService
from app.schemas.delivery import (
    Delivery,
    DeliveryCreate,
    DeliveryUpdate,
    DeliveryStatus,
    DeliveryTracking,
    DeliveryEstimate,
    DeliveryPartner,
    DeliveryCancellation,
)

logger = structlog.get_logger()


class UberEatsDeliveryService(UberEatsBaseService):
    """Service for managing Uber Eats deliveries and tracking"""
    
    def __init__(self, db: AsyncSession, access_token: str):
        super().__init__(db, access_token)
    
    async def get_delivery(self, delivery_id: str) -> Optional[Delivery]:
        """
        Get delivery details
        
        Uber Eats API: GET /v1/eats/deliveries/{delivery_id}
        """
        try:
            response_data = await self.get(f"/v1/eats/deliveries/{delivery_id}")
            return Delivery(**response_data)
            
        except Exception as e:
            logger.error("Failed to get delivery", delivery_id=delivery_id, error=str(e))
            return None
    
    async def get_order_delivery(self, order_id: str) -> Optional[Delivery]:
        """
        Get delivery information for an order
        
        Uber Eats API: GET /v1/eats/orders/{order_id}/delivery
        """
        try:
            response_data = await self.get(f"/v1/eats/orders/{order_id}/delivery")
            return Delivery(**response_data)
            
        except Exception as e:
            logger.error("Failed to get order delivery", order_id=order_id, error=str(e))
            return None
    
    async def track_delivery(self, delivery_id: str) -> Optional[DeliveryTracking]:
        """
        Get real-time delivery tracking information
        
        Uber Eats API: GET /v1/eats/deliveries/{delivery_id}/tracking
        """
        try:
            response_data = await self.get(f"/v1/eats/deliveries/{delivery_id}/tracking")
            return DeliveryTracking(**response_data)
            
        except Exception as e:
            logger.error("Failed to track delivery", delivery_id=delivery_id, error=str(e))
            return None
    
    async def get_delivery_estimate(
        self,
        pickup_address: Dict[str, Any],
        dropoff_address: Dict[str, Any],
    ) -> Optional[DeliveryEstimate]:
        """
        Get delivery time and cost estimate
        
        Uber Eats API: POST /v1/eats/deliveries/estimate
        """
        try:
            payload = {
                "pickup": pickup_address,
                "dropoff": dropoff_address,
            }
            
            response_data = await self.post("/v1/eats/deliveries/estimate", data=payload)
            return DeliveryEstimate(**response_data)
            
        except Exception as e:
            logger.error("Failed to get delivery estimate", error=str(e))
            return None
    
    async def create_delivery_request(
        self,
        delivery_data: DeliveryCreate,
    ) -> Optional[Delivery]:
        """
        Create a new delivery request
        
        Uber Eats API: POST /v1/eats/deliveries
        """
        try:
            payload = delivery_data.model_dump(exclude_unset=True)
            response_data = await self.post("/v1/eats/deliveries", data=payload)
            return Delivery(**response_data)
            
        except Exception as e:
            logger.error("Failed to create delivery request", error=str(e))
            return None
    
    async def cancel_delivery(
        self,
        delivery_id: str,
        cancellation_data: DeliveryCancellation,
    ) -> bool:
        """
        Cancel a delivery
        
        Uber Eats API: POST /v1/eats/deliveries/{delivery_id}/cancel
        """
        try:
            payload = {
                "reason": cancellation_data.reason,
                "explanation": cancellation_data.explanation,
            }
            
            await self.post(f"/v1/eats/deliveries/{delivery_id}/cancel", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to cancel delivery", delivery_id=delivery_id, error=str(e))
            return False
    
    async def get_delivery_partner(self, delivery_id: str) -> Optional[DeliveryPartner]:
        """
        Get information about the delivery partner assigned to a delivery
        
        Uber Eats API: GET /v1/eats/deliveries/{delivery_id}/partner
        """
        try:
            response_data = await self.get(f"/v1/eats/deliveries/{delivery_id}/partner")
            return DeliveryPartner(**response_data)
            
        except Exception as e:
            logger.error("Failed to get delivery partner", delivery_id=delivery_id, error=str(e))
            return None
    
    async def update_pickup_instructions(
        self,
        delivery_id: str,
        instructions: str,
    ) -> bool:
        """
        Update pickup instructions for delivery partner
        
        Uber Eats API: POST /v1/eats/deliveries/{delivery_id}/pickup_instructions
        """
        try:
            payload = {"instructions": instructions}
            await self.post(f"/v1/eats/deliveries/{delivery_id}/pickup_instructions", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to update pickup instructions", delivery_id=delivery_id, error=str(e))
            return False
    
    async def report_delivery_issue(
        self,
        delivery_id: str,
        issue_type: str,
        description: str,
    ) -> bool:
        """
        Report an issue with a delivery
        
        Uber Eats API: POST /v1/eats/deliveries/{delivery_id}/issues
        """
        try:
            payload = {
                "issue_type": issue_type,
                "description": description,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            await self.post(f"/v1/eats/deliveries/{delivery_id}/issues", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to report delivery issue", delivery_id=delivery_id, error=str(e))
            return False
    
    async def get_delivery_proof(self, delivery_id: str) -> Dict[str, Any]:
        """
        Get delivery proof (photo, signature, etc.)
        
        Uber Eats API: GET /v1/eats/deliveries/{delivery_id}/proof
        """
        try:
            return await self.get(f"/v1/eats/deliveries/{delivery_id}/proof")
            
        except Exception as e:
            logger.error("Failed to get delivery proof", delivery_id=delivery_id, error=str(e))
            return {}
    
    async def list_active_deliveries(
        self,
        store_id: Optional[str] = None,
    ) -> List[Delivery]:
        """
        List all active deliveries for a store
        
        Uber Eats API: GET /v1/eats/deliveries
        """
        try:
            params = {
                "status": "active",
                "limit": 100,
            }
            
            if store_id:
                params["store_id"] = store_id
            
            response_data = await self.get("/v1/eats/deliveries", params=params)
            
            deliveries = []
            for delivery_data in response_data.get("deliveries", []):
                deliveries.append(Delivery(**delivery_data))
            
            return deliveries
            
        except Exception as e:
            logger.error("Failed to list active deliveries", store_id=store_id, error=str(e))
            return []
    
    async def get_delivery_metrics(
        self,
        store_id: Optional[str] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Get delivery performance metrics
        
        Custom endpoint for delivery analytics
        """
        try:
            params = {
                "days": days,
            }
            
            if store_id:
                params["store_id"] = store_id
            
            response_data = await self.get("/v1/eats/deliveries/metrics", params=params)
            return response_data
            
        except Exception as e:
            logger.error("Failed to get delivery metrics", store_id=store_id, error=str(e))
            return {}
    
    async def update_delivery_eta(
        self,
        delivery_id: str,
        new_eta: datetime,
        reason: str,
    ) -> bool:
        """
        Update estimated delivery time
        
        Uber Eats API: POST /v1/eats/deliveries/{delivery_id}/eta
        """
        try:
            payload = {
                "estimated_arrival_time": new_eta.isoformat(),
                "reason": reason,
            }
            
            await self.post(f"/v1/eats/deliveries/{delivery_id}/eta", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to update delivery ETA", delivery_id=delivery_id, error=str(e))
            return False
    
    async def request_priority_delivery(
        self,
        order_id: str,
        reason: str,
    ) -> bool:
        """
        Request priority/expedited delivery for an order
        
        Uber Eats API: POST /v1/eats/orders/{order_id}/priority_delivery
        """
        try:
            payload = {
                "reason": reason,
                "requested_at": datetime.utcnow().isoformat(),
            }
            
            await self.post(f"/v1/eats/orders/{order_id}/priority_delivery", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to request priority delivery", order_id=order_id, error=str(e))
            return False
    
    # Convenience methods
    
    async def is_delivery_delayed(self, delivery_id: str, threshold_minutes: int = 30) -> bool:
        """Check if a delivery is significantly delayed"""
        try:
            tracking = await self.track_delivery(delivery_id)
            if not tracking or not tracking.estimated_arrival_time:
                return False
            
            now = datetime.utcnow()
            eta = tracking.estimated_arrival_time
            
            # Check if current time is more than threshold past ETA
            if now > eta and (now - eta).total_seconds() > (threshold_minutes * 60):
                return True
            
            return False
            
        except Exception as e:
            logger.error("Failed to check delivery delay", delivery_id=delivery_id, error=str(e))
            return False
    
    async def get_delivery_status_summary(self, store_id: Optional[str] = None) -> Dict[str, int]:
        """Get summary of delivery statuses for a store"""
        try:
            deliveries = await self.list_active_deliveries(store_id)
            
            status_counts = {}
            for delivery in deliveries:
                status = delivery.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return status_counts
            
        except Exception as e:
            logger.error("Failed to get delivery status summary", store_id=store_id, error=str(e))
            return {}
    
    async def notify_delivery_ready(self, order_id: str) -> bool:
        """Notify that order is ready for pickup by delivery partner"""
        try:
            payload = {
                "ready_at": datetime.utcnow().isoformat(),
                "message": "Order is ready for pickup",
            }
            
            await self.post(f"/v1/eats/orders/{order_id}/ready_for_pickup", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to notify delivery ready", order_id=order_id, error=str(e))
            return False