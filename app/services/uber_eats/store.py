"""
Uber Eats Store Management Service
"""
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.services.uber_eats.base import UberEatsBaseService
from app.schemas.store import (
    Store,
    StoreCreate,
    StoreUpdate,
    StoreList,
    StoreStatus,
    StoreStatusUpdate,
    StorePosData,
)
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()


class UberEatsStoreService(UberEatsBaseService):
    """Service for managing Uber Eats stores"""
    
    def __init__(self, db: AsyncSession, access_token: str):
        super().__init__(db, access_token)
    
    async def list_stores(
        self,
        limit: int = 20,
        offset: int = 0,
        status: Optional[StoreStatus] = None,
    ) -> StoreList:
        """
        List all stores associated with the authenticated account
        
        Uber Eats API: GET /v1/eats/stores
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if status:
            params["status"] = status.value
        
        try:
            response_data = await self.get("/v1/eats/stores", params=params)
            
            stores = []
            for store_data in response_data.get("stores", []):
                store = Store(**store_data)
                stores.append(store)
            
            return StoreList(
                stores=stores,
                total=response_data.get("meta", {}).get("total_count", len(stores)),
                limit=limit,
                offset=offset,
            )
            
        except Exception as e:
            logger.error("Failed to list stores", error=str(e))
            raise
    
    async def get_store(self, store_id: str) -> Optional[Store]:
        """
        Get detailed information about a specific store
        
        Uber Eats API: GET /v1/eats/stores/{store_id}
        """
        try:
            response_data = await self.get(f"/v1/eats/stores/{store_id}")
            return Store(**response_data)
            
        except Exception as e:
            logger.error("Failed to get store", store_id=store_id, error=str(e))
            return None
    
    async def create_store(self, store_data: StoreCreate) -> Store:
        """
        Create a new store
        
        Uber Eats API: POST /v1/eats/stores
        """
        try:
            payload = store_data.model_dump(exclude_unset=True)
            response_data = await self.post("/v1/eats/stores", data=payload)
            return Store(**response_data)
            
        except Exception as e:
            logger.error("Failed to create store", error=str(e))
            raise
    
    async def update_store(self, store_id: str, store_update: StoreUpdate) -> Optional[Store]:
        """
        Update store information
        
        Uber Eats API: PUT /v1/eats/stores/{store_id}
        """
        try:
            payload = store_update.model_dump(exclude_unset=True)
            response_data = await self.put(f"/v1/eats/stores/{store_id}", data=payload)
            return Store(**response_data)
            
        except Exception as e:
            logger.error("Failed to update store", store_id=store_id, error=str(e))
            return None
    
    async def update_store_status(
        self, 
        store_id: str, 
        status_update: StoreStatusUpdate
    ) -> Optional[Store]:
        """
        Update store operational status (online/offline/paused)
        
        Uber Eats API: POST /v1/eats/stores/{store_id}/status
        """
        try:
            payload = {
                "status": status_update.status.value,
                "reason": status_update.reason,
                "until": status_update.until.isoformat() if status_update.until else None,
            }
            
            response_data = await self.post(
                f"/v1/eats/stores/{store_id}/status", 
                data=payload
            )
            return Store(**response_data)
            
        except Exception as e:
            logger.error("Failed to update store status", store_id=store_id, error=str(e))
            return None
    
    async def get_store_status(self, store_id: str) -> Dict[str, Any]:
        """
        Get current store operational status
        
        Uber Eats API: GET /v1/eats/stores/{store_id}/status
        """
        try:
            return await self.get(f"/v1/eats/stores/{store_id}/status")
            
        except Exception as e:
            logger.error("Failed to get store status", store_id=store_id, error=str(e))
            raise
    
    async def update_store_hours(
        self, 
        store_id: str, 
        hours: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update store operating hours
        
        Uber Eats API: PUT /v1/eats/stores/{store_id}/hours
        """
        try:
            response_data = await self.put(
                f"/v1/eats/stores/{store_id}/hours", 
                data=hours
            )
            return response_data
            
        except Exception as e:
            logger.error("Failed to update store hours", store_id=store_id, error=str(e))
            raise
    
    async def update_holiday_hours(
        self, 
        store_id: str, 
        holidays: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update holiday hours for a store
        
        Uber Eats API: POST /v1/eats/stores/{store_id}/holiday_hours
        """
        try:
            payload = {"holiday_hours": holidays}
            response_data = await self.post(
                f"/v1/eats/stores/{store_id}/holiday_hours", 
                data=payload
            )
            return response_data
            
        except Exception as e:
            logger.error("Failed to update holiday hours", store_id=store_id, error=str(e))
            raise
    
    async def get_pos_data(self, store_id: str) -> Optional[StorePosData]:
        """
        Get POS-specific data for a store
        
        Custom endpoint for POS integration data
        """
        try:
            response_data = await self.get(f"/v1/eats/stores/{store_id}/pos_data")
            return StorePosData(**response_data)
            
        except Exception as e:
            logger.error("Failed to get POS data", store_id=store_id, error=str(e))
            return None
    
    async def update_pos_data(
        self, 
        store_id: str, 
        pos_data: StorePosData
    ) -> StorePosData:
        """
        Update POS-specific data for a store
        
        Custom endpoint for POS integration data
        """
        try:
            payload = pos_data.model_dump(exclude_unset=True)
            response_data = await self.put(
                f"/v1/eats/stores/{store_id}/pos_data", 
                data=payload
            )
            return StorePosData(**response_data)
            
        except Exception as e:
            logger.error("Failed to update POS data", store_id=store_id, error=str(e))
            raise
    
    async def get_store_metrics(self, store_id: str) -> Dict[str, Any]:
        """
        Get store performance metrics
        
        Uber Eats API: GET /v1/eats/stores/{store_id}/metrics
        """
        try:
            return await self.get(f"/v1/eats/stores/{store_id}/metrics")
            
        except Exception as e:
            logger.error("Failed to get store metrics", store_id=store_id, error=str(e))
            raise
    
    async def pause_store(self, store_id: str, reason: str = "Temporary pause") -> bool:
        """
        Pause store operations (set to offline)
        """
        try:
            status_update = StoreStatusUpdate(
                status=StoreStatus.OFFLINE,
                reason=reason
            )
            result = await self.update_store_status(store_id, status_update)
            return result is not None
            
        except Exception as e:
            logger.error("Failed to pause store", store_id=store_id, error=str(e))
            return False
    
    async def resume_store(self, store_id: str) -> bool:
        """
        Resume store operations (set to online)
        """
        try:
            status_update = StoreStatusUpdate(
                status=StoreStatus.ONLINE,
                reason="Resuming operations"
            )
            result = await self.update_store_status(store_id, status_update)
            return result is not None
            
        except Exception as e:
            logger.error("Failed to resume store", store_id=store_id, error=str(e))
            return False
    
    async def get_store_orders_summary(self, store_id: str) -> Dict[str, Any]:
        """
        Get summary of orders for a store
        
        Uber Eats API: GET /v1/eats/stores/{store_id}/orders/summary
        """
        try:
            return await self.get(f"/v1/eats/stores/{store_id}/orders/summary")
            
        except Exception as e:
            logger.error("Failed to get store orders summary", store_id=store_id, error=str(e))
            raise