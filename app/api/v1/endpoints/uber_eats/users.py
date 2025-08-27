"""
User Management endpoints for Uber Eats API
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.user import (
    User,
    UserCreate,
    UserUpdate,
    UserList,
    UserProfile,
    UserPreferences,
)
from app.schemas.base import PaginationParams
from app.services.uber_eats.user import UberEatsUserService
from app.api.dependencies.auth import get_uber_eats_token

router = APIRouter()


@router.get("/", response_model=UserList)
async def list_users(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> UserList:
    """
    List users (for admin/restaurant management purposes)
    
    Note: This is typically used by restaurant management systems
    to view customer data for order management purposes.
    """
    user_service = UberEatsUserService(db, token)
    
    try:
        users = await user_service.list_users(
            limit=pagination.page_size,
            offset=pagination.offset,
        )
        return users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}",
        )


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> User:
    """
    Get user details
    
    Retrieve basic user information for order management purposes
    """
    user_service = UberEatsUserService(db, token)
    
    try:
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user: {str(e)}",
        )


@router.get("/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> UserProfile:
    """
    Get user profile information
    
    Retrieve detailed user profile for customer service purposes
    """
    user_service = UberEatsUserService(db, token)
    
    try:
        profile = await user_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile for user {user_id} not found",
            )
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user profile: {str(e)}",
        )


@router.get("/{user_id}/preferences", response_model=UserPreferences)
async def get_user_preferences(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> UserPreferences:
    """
    Get user preferences (dietary restrictions, favorites, etc.)
    
    Used for personalizing menu recommendations and order suggestions
    """
    user_service = UberEatsUserService(db, token)
    
    try:
        preferences = await user_service.get_user_preferences(user_id)
        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Preferences for user {user_id} not found",
            )
        return preferences
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user preferences: {str(e)}",
        )


@router.get("/{user_id}/orders", response_model=List[Dict[str, Any]])
async def get_user_orders(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> List[Dict[str, Any]]:
    """
    Get user's order history
    
    Retrieve order history for customer service and analytics
    """
    user_service = UberEatsUserService(db, token)
    
    try:
        orders = await user_service.get_user_orders(
            user_id, 
            limit=limit, 
            offset=offset
        )
        return orders
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user orders: {str(e)}",
        )


@router.get("/{user_id}/addresses", response_model=List[Dict[str, Any]])
async def get_user_addresses(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> List[Dict[str, Any]]:
    """
    Get user's saved addresses
    
    Retrieve saved delivery addresses for order management
    """
    user_service = UberEatsUserService(db, token)
    
    try:
        addresses = await user_service.get_user_addresses(user_id)
        return addresses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user addresses: {str(e)}",
        )


@router.get("/{user_id}/favorites", response_model=List[Dict[str, Any]])
async def get_user_favorites(
    user_id: str,
    store_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> List[Dict[str, Any]]:
    """
    Get user's favorite items and restaurants
    
    Retrieve user favorites for personalized recommendations
    """
    user_service = UberEatsUserService(db, token)
    
    try:
        favorites = await user_service.get_user_favorites(user_id, store_id)
        return favorites
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user favorites: {str(e)}",
        )


@router.get("/{user_id}/analytics", response_model=Dict[str, Any])
async def get_user_analytics(
    user_id: str,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Dict[str, Any]:
    """
    Get user analytics and insights
    
    Retrieve customer behavior analytics for business intelligence
    """
    user_service = UberEatsUserService(db, token)
    
    try:
        analytics = await user_service.get_user_analytics(user_id, days)
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user analytics: {str(e)}",
        )


@router.post("/{user_id}/notifications", response_model=Dict[str, Any])
async def send_user_notification(
    user_id: str,
    notification_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Dict[str, Any]:
    """
    Send notification to user
    
    Send promotional or service notifications to users
    """
    user_service = UberEatsUserService(db, token)
    
    try:
        result = await user_service.send_notification(user_id, notification_data)
        return {"message": "Notification sent successfully", "result": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}",
        )


@router.get("/{user_id}/loyalty", response_model=Dict[str, Any])
async def get_user_loyalty_info(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Dict[str, Any]:
    """
    Get user loyalty program information
    
    Retrieve loyalty points, status, and rewards for the user
    """
    user_service = UberEatsUserService(db, token)
    
    try:
        loyalty_info = await user_service.get_loyalty_info(user_id)
        return loyalty_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch loyalty info: {str(e)}",
        )


@router.get("/{user_id}/recommendations", response_model=List[Dict[str, Any]])
async def get_user_recommendations(
    user_id: str,
    store_id: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> List[Dict[str, Any]]:
    """
    Get personalized recommendations for user
    
    Generate menu item and restaurant recommendations based on user history
    """
    user_service = UberEatsUserService(db, token)
    
    try:
        recommendations = await user_service.get_recommendations(
            user_id, 
            store_id=store_id,
            category=category,
            limit=limit
        )
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}",
        )