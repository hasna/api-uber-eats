"""
Uber Eats Order Management Service
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.services.uber_eats.base import UberEatsBaseService
from app.schemas.order import (
    Order,
    OrderCreate,
    OrderUpdate,
    OrderStatus,
    OrderList,
    OrderAcceptance,
    OrderCancellation,
    OrderPreparationUpdate,
    OrderReadyForPickup,
    CancelReason,
)
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()


class UberEatsOrderService(UberEatsBaseService):
    """Service for managing Uber Eats orders"""
    
    def __init__(self, db: AsyncSession, access_token: str):
        super().__init__(db, access_token)
    
    async def list_orders(
        self,
        store_id: Optional[str] = None,
        status: Optional[OrderStatus] = None,
        limit: int = 20,
        offset: int = 0,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> OrderList:
        """
        List orders with filtering options
        
        Uber Eats API: GET /v1/eats/orders
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if store_id:
            params["store_id"] = store_id
        if status:
            params["status"] = status.value
        if since:
            params["since"] = since.isoformat()
        if until:
            params["until"] = until.isoformat()
        
        try:
            response_data = await self.get("/v1/eats/orders", params=params)
            
            orders = []
            for order_data in response_data.get("orders", []):
                order = Order(**order_data)
                orders.append(order)
            
            return OrderList(
                orders=orders,
                total=response_data.get("meta", {}).get("total_count", len(orders)),
                limit=limit,
                offset=offset,
            )
            
        except Exception as e:
            logger.error("Failed to list orders", error=str(e))
            raise
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        """
        Get detailed information about a specific order
        
        Uber Eats API: GET /v1/eats/orders/{order_id}
        """
        try:
            response_data = await self.get(f"/v1/eats/orders/{order_id}")
            return Order(**response_data)
            
        except Exception as e:
            logger.error("Failed to get order", order_id=order_id, error=str(e))
            return None
    
    async def accept_order(
        self, 
        order_id: str, 
        acceptance_data: OrderAcceptance
    ) -> Optional[Order]:
        """
        Accept an incoming order
        
        Uber Eats API: POST /v1/eats/orders/{order_id}/accept
        """
        try:
            payload = {
                "reason": acceptance_data.reason,
                "estimated_prep_time_minutes": acceptance_data.estimated_prep_time_minutes,
            }
            
            response_data = await self.post(f"/v1/eats/orders/{order_id}/accept", data=payload)
            return Order(**response_data)
            
        except Exception as e:
            logger.error("Failed to accept order", order_id=order_id, error=str(e))
            return None
    
    async def deny_order(
        self, 
        order_id: str, 
        reason: CancelReason,
        explanation: Optional[str] = None
    ) -> bool:
        """
        Deny/reject an incoming order
        
        Uber Eats API: POST /v1/eats/orders/{order_id}/deny
        """
        try:
            payload = {
                "reason": reason.value,
                "explanation": explanation,
            }
            
            await self.post(f"/v1/eats/orders/{order_id}/deny", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to deny order", order_id=order_id, error=str(e))
            return False
    
    async def cancel_order(
        self, 
        order_id: str, 
        cancellation_data: OrderCancellation
    ) -> bool:
        """
        Cancel an order
        
        Uber Eats API: POST /v1/eats/orders/{order_id}/cancel
        """
        try:
            payload = {
                "reason": cancellation_data.reason.value,
                "explanation": cancellation_data.explanation,
                "details": cancellation_data.details,
            }
            
            await self.post(f"/v1/eats/orders/{order_id}/cancel", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to cancel order", order_id=order_id, error=str(e))
            return False
    
    async def update_preparation_time(
        self, 
        order_id: str, 
        prep_update: OrderPreparationUpdate
    ) -> bool:
        """
        Update order preparation time estimate
        
        Uber Eats API: POST /v1/eats/orders/{order_id}/preparation_time
        """
        try:
            payload = {
                "estimated_prep_time_minutes": prep_update.estimated_prep_time_minutes,
                "reason": prep_update.reason,
            }
            
            await self.post(f"/v1/eats/orders/{order_id}/preparation_time", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to update preparation time", order_id=order_id, error=str(e))
            return False
    
    async def mark_order_ready(
        self, 
        order_id: str, 
        ready_data: OrderReadyForPickup
    ) -> bool:
        """
        Mark order as ready for pickup/delivery
        
        Uber Eats API: POST /v1/eats/orders/{order_id}/ready
        """
        try:
            payload = {
                "ready_for_pickup_at": ready_data.ready_for_pickup_at.isoformat() if ready_data.ready_for_pickup_at else None,
                "special_instructions": ready_data.special_instructions,
            }
            
            await self.post(f"/v1/eats/orders/{order_id}/ready", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to mark order ready", order_id=order_id, error=str(e))
            return False
    
    async def get_order_receipt(self, order_id: str) -> Dict[str, Any]:
        """
        Get order receipt/invoice details
        
        Uber Eats API: GET /v1/eats/orders/{order_id}/receipt
        """
        try:
            return await self.get(f"/v1/eats/orders/{order_id}/receipt")
            
        except Exception as e:
            logger.error("Failed to get order receipt", order_id=order_id, error=str(e))
            raise
    
    async def get_active_orders(self, store_id: Optional[str] = None) -> List[Order]:
        """
        Get all active orders (accepted but not completed)
        
        Returns orders with status: ACCEPTED, IN_PROGRESS, READY_FOR_PICKUP
        """
        try:
            active_statuses = [
                OrderStatus.ACCEPTED,
                OrderStatus.IN_PROGRESS,
                OrderStatus.READY_FOR_PICKUP,
            ]
            
            all_active_orders = []
            for status in active_statuses:
                order_list = await self.list_orders(
                    store_id=store_id,
                    status=status,
                    limit=100,  # Get more orders for active status check
                )
                all_active_orders.extend(order_list.orders)
            
            return all_active_orders
            
        except Exception as e:
            logger.error("Failed to get active orders", store_id=store_id, error=str(e))
            return []
    
    async def get_pending_orders(self, store_id: Optional[str] = None) -> List[Order]:
        """
        Get all pending orders (waiting for acceptance)
        """
        try:
            order_list = await self.list_orders(
                store_id=store_id,
                status=OrderStatus.PENDING,
                limit=100,
            )
            return order_list.orders
            
        except Exception as e:
            logger.error("Failed to get pending orders", store_id=store_id, error=str(e))
            return []
    
    async def get_order_history(
        self,
        store_id: Optional[str] = None,
        days: int = 30,
        limit: int = 50,
    ) -> List[Order]:
        """
        Get order history for the specified number of days
        """
        try:
            since = datetime.utcnow() - timedelta(days=days)
            
            order_list = await self.list_orders(
                store_id=store_id,
                since=since,
                limit=limit,
            )
            return order_list.orders
            
        except Exception as e:
            logger.error("Failed to get order history", store_id=store_id, error=str(e))
            return []
    
    async def bulk_accept_orders(self, order_ids: List[str]) -> Dict[str, bool]:
        """
        Accept multiple orders in bulk
        """
        results = {}
        
        for order_id in order_ids:
            try:
                acceptance = OrderAcceptance(
                    reason="Bulk acceptance",
                    estimated_prep_time_minutes=15,  # Default prep time
                )
                result = await self.accept_order(order_id, acceptance)
                results[order_id] = result is not None
                
            except Exception as e:
                logger.error("Failed to accept order in bulk", order_id=order_id, error=str(e))
                results[order_id] = False
        
        return results
    
    async def get_order_analytics(
        self,
        store_id: Optional[str] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Get order analytics for the specified period
        """
        try:
            since = datetime.utcnow() - timedelta(days=days)
            
            # Get orders for the period
            order_list = await self.list_orders(
                store_id=store_id,
                since=since,
                limit=1000,  # Large limit to get all orders
            )
            
            orders = order_list.orders
            
            # Calculate analytics
            total_orders = len(orders)
            total_revenue = sum(order.subtotal for order in orders if order.subtotal)
            
            status_counts = {}
            for order in orders:
                status = order.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            
            return {
                "period_days": days,
                "total_orders": total_orders,
                "total_revenue": total_revenue,
                "average_order_value": avg_order_value,
                "status_breakdown": status_counts,
                "store_id": store_id,
            }
            
        except Exception as e:
            logger.error("Failed to get order analytics", store_id=store_id, error=str(e))
            return {}
    
    async def update_order_items(
        self, 
        order_id: str, 
        item_updates: List[Dict[str, Any]]
    ) -> bool:
        """
        Update specific items in an order (for modifications)
        
        Uber Eats API: POST /v1/eats/orders/{order_id}/items
        """
        try:
            payload = {"item_updates": item_updates}
            await self.post(f"/v1/eats/orders/{order_id}/items", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to update order items", order_id=order_id, error=str(e))
            return False
    
    # Convenience methods for common order operations
    
    async def quick_accept_order(self, order_id: str, prep_time_minutes: int = 15) -> Optional[Order]:
        """Quick accept order with default values"""
        acceptance = OrderAcceptance(
            reason="Order accepted",
            estimated_prep_time_minutes=prep_time_minutes,
        )
        return await self.accept_order(order_id, acceptance)
    
    async def mark_order_in_progress(self, order_id: str) -> bool:
        """Mark order as in progress (being prepared)"""
        prep_update = OrderPreparationUpdate(
            estimated_prep_time_minutes=10,
            reason="Order is being prepared",
        )
        return await self.update_preparation_time(order_id, prep_update)
    
    async def mark_order_ready_now(self, order_id: str) -> bool:
        """Mark order as ready for pickup immediately"""
        ready_data = OrderReadyForPickup(
            ready_for_pickup_at=datetime.utcnow(),
            special_instructions="Order is ready for pickup",
        )
        return await self.mark_order_ready(order_id, ready_data)