"""
Uber Eats Store Management endpoints
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.store import (
    Store,
    StoreCreate,
    StoreUpdate,
    StoreList,
    StoreStatus,
    StoreStatusUpdate,
    StorePosData,
)
from app.schemas.base import PaginationParams, PaginatedResponse
from app.services.uber_eats import UberEatsStoreService
from app.api.dependencies.auth import get_uber_eats_token

router = APIRouter()


@router.get("/", response_model=StoreList)
async def list_stores(
    pagination: PaginationParams = Depends(),
    status: Optional[StoreStatus] = None,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> StoreList:
    """
    List all stores
    
    Returns a paginated list of stores associated with the account
    """
    store_service = UberEatsStoreService(db, token)
    
    try:
        stores = await store_service.list_stores(
            limit=pagination.page_size,
            offset=pagination.offset,
            status=status,
        )
        return stores
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stores: {str(e)}",
        )


@router.get("/{store_id}", response_model=Store)
async def get_store(
    store_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Store:
    """
    Get store details
    
    Returns detailed information about a specific store
    """
    store_service = UberEatsStoreService(db, token)
    
    try:
        store = await store_service.get_store(store_id)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store {store_id} not found",
            )
        return store
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch store: {str(e)}",
        )


@router.post("/", response_model=Store)
async def create_store(
    store_data: StoreCreate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Store:
    """
    Create a new store
    
    Creates a new store on Uber Eats platform
    """
    store_service = UberEatsStoreService(db, token)
    
    try:
        store = await store_service.create_store(store_data)
        return store
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create store: {str(e)}",
        )


@router.put("/{store_id}", response_model=Store)
async def update_store(
    store_id: str,
    store_update: StoreUpdate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Store:
    """
    Update store information
    
    Updates store details like name, address, hours, etc.
    """
    store_service = UberEatsStoreService(db, token)
    
    try:
        store = await store_service.update_store(store_id, store_update)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store {store_id} not found",
            )
        return store
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update store: {str(e)}",
        )


@router.post("/{store_id}/status", response_model=Store)
async def update_store_status(
    store_id: str,
    status_update: StoreStatusUpdate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Store:
    """
    Update store status
    
    Changes store status (online/offline/paused)
    """
    store_service = UberEatsStoreService(db, token)
    
    try:
        store = await store_service.update_store_status(store_id, status_update)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store {store_id} not found",
            )
        return store
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update store status: {str(e)}",
        )


@router.get("/{store_id}/status", response_model=Dict[str, Any])
async def get_store_status(
    store_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Dict[str, Any]:
    """
    Get current store status
    
    Returns the current operational status of the store
    """
    store_service = UberEatsStoreService(db, token)
    
    try:
        status = await store_service.get_store_status(store_id)
        return status
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch store status: {str(e)}",
        )


@router.get("/{store_id}/pos-data", response_model=StorePosData)
async def get_pos_data(
    store_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> StorePosData:
    """
    Get POS-specific data for a store
    
    Returns POS integration data and custom metadata
    """
    store_service = UberEatsStoreService(db, token)
    
    try:
        pos_data = await store_service.get_pos_data(store_id)
        if not pos_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"POS data not found for store {store_id}",
            )
        return pos_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch POS data: {str(e)}",
        )


@router.put("/{store_id}/pos-data", response_model=StorePosData)
async def update_pos_data(
    store_id: str,
    pos_data: StorePosData,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> StorePosData:
    """
    Update POS-specific data for a store
    
    Updates POS integration settings and custom metadata
    """
    store_service = UberEatsStoreService(db, token)
    
    try:
        updated_data = await store_service.update_pos_data(store_id, pos_data)
        return updated_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update POS data: {str(e)}",
        )


@router.post("/{store_id}/holidays")
async def update_holiday_hours(
    store_id: str,
    holidays: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Dict[str, Any]:
    """
    Update holiday hours for a store
    
    Sets special hours or closures for holidays
    """
    store_service = UberEatsStoreService(db, token)
    
    try:
        result = await store_service.update_holiday_hours(store_id, holidays)
        return {"message": "Holiday hours updated successfully", "data": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update holiday hours: {str(e)}",
        )