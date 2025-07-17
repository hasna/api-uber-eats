"""
Uber Eats Delivery Management endpoints
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.delivery import (
    Delivery,
    CreateDeliveryRequest,
    DeliveryQuote,
    DeliveryTracking,
    DeliveryUpdate,
    DeliveryStatus,
    MultiCourierRequest,
    DeliveryMetrics,
)
from app.schemas.base import BaseResponse
from app.services.uber_eats import UberEatsDeliveryService
from app.api.dependencies.auth import get_uber_eats_token

router = APIRouter()


@router.post("/quote", response_model=DeliveryQuote)
async def get_delivery_quote(
    delivery_request: CreateDeliveryRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> DeliveryQuote:
    """
    Get a delivery quote
    
    Returns estimated price and time for a delivery
    """
    delivery_service = UberEatsDeliveryService(db, token)
    
    try:
        quote = await delivery_service.get_delivery_quote(delivery_request)
        return quote
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get delivery quote: {str(e)}",
        )


@router.post("/", response_model=Delivery)
async def create_delivery(
    delivery_request: CreateDeliveryRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Delivery:
    """
    Create a new delivery
    
    Initiates a delivery request for an order
    """
    delivery_service = UberEatsDeliveryService(db, token)
    
    try:
        delivery = await delivery_service.create_delivery(delivery_request)
        return delivery
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create delivery: {str(e)}",
        )


@router.get("/{delivery_id}", response_model=Delivery)
async def get_delivery(
    delivery_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Delivery:
    """
    Get delivery details
    
    Returns current status and details of a delivery
    """
    delivery_service = UberEatsDeliveryService(db, token)
    
    try:
        delivery = await delivery_service.get_delivery(delivery_id)
        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Delivery {delivery_id} not found",
            )
        return delivery
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch delivery: {str(e)}",
        )


@router.put("/{delivery_id}", response_model=Delivery)
async def update_delivery(
    delivery_id: str,
    delivery_update: DeliveryUpdate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Delivery:
    """
    Update delivery information
    
    Updates delivery status or reports issues
    """
    delivery_service = UberEatsDeliveryService(db, token)
    
    try:
        delivery = await delivery_service.update_delivery(delivery_id, delivery_update)
        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Delivery {delivery_id} not found",
            )
        return delivery
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update delivery: {str(e)}",
        )


@router.post("/{delivery_id}/cancel", response_model=BaseResponse)
async def cancel_delivery(
    delivery_id: str,
    reason: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> BaseResponse:
    """
    Cancel a delivery
    
    Cancels an active delivery (if allowed by current status)
    """
    delivery_service = UberEatsDeliveryService(db, token)
    
    try:
        success = await delivery_service.cancel_delivery(delivery_id, reason)
        
        return BaseResponse(
            success=success,
            message=f"Delivery {delivery_id} cancelled successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel delivery: {str(e)}",
        )


@router.get("/{delivery_id}/tracking", response_model=DeliveryTracking)
async def get_delivery_tracking(
    delivery_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> DeliveryTracking:
    """
    Get real-time delivery tracking
    
    Returns current location and ETA for delivery
    """
    delivery_service = UberEatsDeliveryService(db, token)
    
    try:
        tracking = await delivery_service.get_delivery_tracking(delivery_id)
        if not tracking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tracking not available for delivery {delivery_id}",
            )
        return tracking
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tracking: {str(e)}",
        )


@router.post("/multiple-courier", response_model=Dict[str, Any])
async def request_multiple_couriers(
    request: MultiCourierRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Dict[str, Any]:
    """
    Request multiple couriers for large orders
    
    Dispatches 2-5 couriers for orders that exceed single courier capacity
    Note: Requires special scope approval from Uber
    """
    delivery_service = UberEatsDeliveryService(db, token)
    
    try:
        result = await delivery_service.request_multiple_couriers(request)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to request multiple couriers: {str(e)}",
        )


@router.get("/order/{order_id}/deliveries", response_model=List[Delivery])
async def get_order_deliveries(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> List[Delivery]:
    """
    Get all deliveries for an order
    
    Returns list of deliveries (useful for multi-courier orders)
    """
    delivery_service = UberEatsDeliveryService(db, token)
    
    try:
        deliveries = await delivery_service.get_order_deliveries(order_id)
        return deliveries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch deliveries: {str(e)}",
        )


@router.get("/stores/{store_id}/metrics", response_model=DeliveryMetrics)
async def get_delivery_metrics(
    store_id: str,
    days: int = Query(default=30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> DeliveryMetrics:
    """
    Get delivery performance metrics
    
    Returns metrics like average delivery time, success rate, etc.
    """
    delivery_service = UberEatsDeliveryService(db, token)
    
    try:
        metrics = await delivery_service.get_delivery_metrics(store_id, days)
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch delivery metrics: {str(e)}",
        )


@router.post("/{delivery_id}/proof-of-delivery")
async def upload_proof_of_delivery(
    delivery_id: str,
    signature_image: str,  # Base64 encoded image
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> BaseResponse:
    """
    Upload proof of delivery
    
    Uploads customer signature or photo proof of delivery
    """
    delivery_service = UberEatsDeliveryService(db, token)
    
    try:
        success = await delivery_service.upload_proof_of_delivery(
            delivery_id,
            signature_image
        )
        
        return BaseResponse(
            success=success,
            message="Proof of delivery uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload proof of delivery: {str(e)}",
        )