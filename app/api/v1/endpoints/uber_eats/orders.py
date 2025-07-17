"""
Uber Eats Order Management endpoints
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.order import (
    Order,
    OrderList,
    OrderAccept,
    OrderDeny,
    OrderCancel,
    OrderStatusUpdate,
    OrderStatus,
    OrderType,
    OrderMetrics,
    FulfillmentIssue,
    ResolveFulfillmentIssue,
)
from app.schemas.base import BaseResponse, PaginationParams
from app.services.uber_eats import UberEatsOrderService
from app.api.dependencies.auth import get_uber_eats_token

router = APIRouter()


@router.get("/", response_model=OrderList)
async def list_orders(
    store_id: Optional[str] = None,
    status: Optional[OrderStatus] = None,
    order_type: Optional[OrderType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> OrderList:
    """
    List orders with filtering options
    
    Returns paginated list of orders based on filters
    """
    order_service = UberEatsOrderService(db, token)
    
    try:
        # Default date range if not specified
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        orders = await order_service.list_orders(
            store_id=store_id,
            status=status,
            order_type=order_type,
            start_date=start_date,
            end_date=end_date,
            limit=pagination.page_size,
            offset=pagination.offset,
        )
        return orders
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch orders: {str(e)}",
        )


@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Order:
    """
    Get detailed order information
    
    Returns complete order details including items, customer info, and delivery details
    """
    order_service = UberEatsOrderService(db, token)
    
    try:
        order = await order_service.get_order(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found",
            )
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch order: {str(e)}",
        )


@router.post("/{order_id}/accept", response_model=Order)
async def accept_order(
    order_id: str,
    accept_data: OrderAccept,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Order:
    """
    Accept an incoming order
    
    Must be called within 11.5 minutes of receiving the order webhook
    """
    order_service = UberEatsOrderService(db, token)
    
    try:
        order = await order_service.accept_order(order_id, accept_data)
        
        # Start order preparation tracking in background
        background_tasks.add_task(
            order_service.track_order_preparation,
            order_id,
            accept_data.estimated_ready_time
        )
        
        return order
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to accept order: {str(e)}",
        )


@router.post("/{order_id}/deny", response_model=BaseResponse)
async def deny_order(
    order_id: str,
    deny_data: OrderDeny,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> BaseResponse:
    """
    Deny/reject an incoming order
    
    Must be called within 11.5 minutes of receiving the order webhook
    """
    order_service = UberEatsOrderService(db, token)
    
    try:
        success = await order_service.deny_order(order_id, deny_data)
        
        return BaseResponse(
            success=success,
            message=f"Order {order_id} denied successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deny order: {str(e)}",
        )


@router.post("/{order_id}/cancel", response_model=BaseResponse)
async def cancel_order(
    order_id: str,
    cancel_data: OrderCancel,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> BaseResponse:
    """
    Cancel an accepted order
    
    Can only cancel orders that haven't been picked up yet
    """
    order_service = UberEatsOrderService(db, token)
    
    try:
        success = await order_service.cancel_order(order_id, cancel_data)
        
        return BaseResponse(
            success=success,
            message=f"Order {order_id} cancelled successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel order: {str(e)}",
        )


@router.post("/{order_id}/status", response_model=Order)
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Order:
    """
    Update order status
    
    Updates order status (e.g., mark as ready for pickup)
    """
    order_service = UberEatsOrderService(db, token)
    
    try:
        order = await order_service.update_order_status(order_id, status_update)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found",
            )
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update order status: {str(e)}",
        )


@router.post("/{order_id}/ready")
async def mark_order_ready(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Order:
    """
    Mark order as ready for pickup
    
    Shorthand for updating status to READY_FOR_PICKUP
    """
    status_update = OrderStatusUpdate(
        status=OrderStatus.READY_FOR_PICKUP,
        notes="Order is ready for pickup"
    )
    
    return await update_order_status(order_id, status_update, db, token)


@router.get("/{order_id}/fulfillment-issues", response_model=List[FulfillmentIssue])
async def get_fulfillment_issues(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> List[FulfillmentIssue]:
    """
    Get fulfillment issues for an order
    
    Returns list of any fulfillment issues (out of stock items, etc.)
    """
    order_service = UberEatsOrderService(db, token)
    
    try:
        issues = await order_service.get_fulfillment_issues(order_id)
        return issues
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fulfillment issues: {str(e)}",
        )


@router.post("/{order_id}/resolve-fulfillment-issue", response_model=BaseResponse)
async def resolve_fulfillment_issue(
    order_id: str,
    resolution: ResolveFulfillmentIssue,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> BaseResponse:
    """
    Resolve a fulfillment issue
    
    Handles item replacements, refunds, or other resolutions
    """
    order_service = UberEatsOrderService(db, token)
    
    try:
        success = await order_service.resolve_fulfillment_issue(order_id, resolution)
        
        return BaseResponse(
            success=success,
            message="Fulfillment issue resolved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve fulfillment issue: {str(e)}",
        )


@router.get("/stores/{store_id}/metrics", response_model=OrderMetrics)
async def get_order_metrics(
    store_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> OrderMetrics:
    """
    Get order metrics for a store
    
    Returns aggregated metrics like acceptance rate, average prep time, etc.
    """
    order_service = UberEatsOrderService(db, token)
    
    try:
        # Default to last 30 days if not specified
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        metrics = await order_service.get_order_metrics(
            store_id=store_id,
            start_date=start_date,
            end_date=end_date,
        )
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch order metrics: {str(e)}",
        )


@router.post("/stores/{store_id}/test-order")
async def create_test_order(
    store_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Dict[str, Any]:
    """
    Create a test order (sandbox only)
    
    Creates a test order for integration testing
    """
    if not settings.UBER_EATS_SANDBOX_MODE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test orders can only be created in sandbox mode",
        )
    
    order_service = UberEatsOrderService(db, token)
    
    try:
        test_order = await order_service.create_test_order(store_id)
        return {
            "message": "Test order created successfully",
            "order": test_order,
            "note": "This order will appear in your webhook endpoint",
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test order: {str(e)}",
        )