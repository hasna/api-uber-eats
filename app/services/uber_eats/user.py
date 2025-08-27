"""
Uber Eats User Management Service
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.services.uber_eats.base import UberEatsBaseService
from app.schemas.user import (
    User,
    UserCreate,
    UserUpdate,
    UserList,
    UserProfile,
    UserPreferences,
)

logger = structlog.get_logger()


class UberEatsUserService(UberEatsBaseService):
    """Service for managing Uber Eats users and customer data"""
    
    def __init__(self, db: AsyncSession, access_token: str):
        super().__init__(db, access_token)
    
    async def list_users(
        self,
        limit: int = 20,
        offset: int = 0,
        store_id: Optional[str] = None,
    ) -> UserList:
        """
        List users who have ordered from stores
        
        Note: This is typically used for customer management by restaurants
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if store_id:
            params["store_id"] = store_id
        
        try:
            response_data = await self.get("/v1/eats/users", params=params)
            
            users = []
            for user_data in response_data.get("users", []):
                user = User(**user_data)
                users.append(user)
            
            return UserList(
                users=users,
                total=response_data.get("meta", {}).get("total_count", len(users)),
                limit=limit,
                offset=offset,
            )
            
        except Exception as e:
            logger.error("Failed to list users", error=str(e))
            raise
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """
        Get basic user information
        
        Uber Eats API: GET /v1/eats/users/{user_id}
        """
        try:
            response_data = await self.get(f"/v1/eats/users/{user_id}")
            return User(**response_data)
            
        except Exception as e:
            logger.error("Failed to get user", user_id=user_id, error=str(e))
            return None
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get detailed user profile information
        
        Uber Eats API: GET /v1/eats/users/{user_id}/profile
        """
        try:
            response_data = await self.get(f"/v1/eats/users/{user_id}/profile")
            return UserProfile(**response_data)
            
        except Exception as e:
            logger.error("Failed to get user profile", user_id=user_id, error=str(e))
            return None
    
    async def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """
        Get user preferences including dietary restrictions and favorites
        
        Uber Eats API: GET /v1/eats/users/{user_id}/preferences
        """
        try:
            response_data = await self.get(f"/v1/eats/users/{user_id}/preferences")
            return UserPreferences(**response_data)
            
        except Exception as e:
            logger.error("Failed to get user preferences", user_id=user_id, error=str(e))
            return None
    
    async def get_user_orders(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        since: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get user's order history
        
        Uber Eats API: GET /v1/eats/users/{user_id}/orders
        """
        try:
            params = {
                "limit": limit,
                "offset": offset,
            }
            
            if since:
                params["since"] = since.isoformat()
            
            response_data = await self.get(f"/v1/eats/users/{user_id}/orders", params=params)
            return response_data.get("orders", [])
            
        except Exception as e:
            logger.error("Failed to get user orders", user_id=user_id, error=str(e))
            return []
    
    async def get_user_addresses(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's saved delivery addresses
        
        Uber Eats API: GET /v1/eats/users/{user_id}/addresses
        """
        try:
            response_data = await self.get(f"/v1/eats/users/{user_id}/addresses")
            return response_data.get("addresses", [])
            
        except Exception as e:
            logger.error("Failed to get user addresses", user_id=user_id, error=str(e))
            return []
    
    async def get_user_favorites(
        self,
        user_id: str,
        store_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get user's favorite items and restaurants
        
        Uber Eats API: GET /v1/eats/users/{user_id}/favorites
        """
        try:
            params = {}
            if store_id:
                params["store_id"] = store_id
            
            response_data = await self.get(f"/v1/eats/users/{user_id}/favorites", params=params)
            return response_data.get("favorites", [])
            
        except Exception as e:
            logger.error("Failed to get user favorites", user_id=user_id, error=str(e))
            return []
    
    async def get_user_analytics(
        self,
        user_id: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Get user analytics and ordering patterns
        
        Custom analytics endpoint
        """
        try:
            # Get user orders for analysis period
            since = datetime.utcnow() - timedelta(days=days)
            orders = await self.get_user_orders(user_id, limit=1000, since=since)
            
            if not orders:
                return {
                    "user_id": user_id,
                    "period_days": days,
                    "total_orders": 0,
                    "total_spent": 0,
                    "average_order_value": 0,
                    "favorite_cuisines": [],
                    "ordering_patterns": {},
                }
            
            # Calculate analytics
            total_orders = len(orders)
            total_spent = sum(order.get("total", 0) for order in orders)
            avg_order_value = total_spent / total_orders if total_orders > 0 else 0
            
            # Analyze cuisine preferences
            cuisine_counts = {}
            for order in orders:
                cuisine = order.get("store", {}).get("cuisine", "Unknown")
                cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
            
            favorite_cuisines = sorted(
                cuisine_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            # Analyze ordering patterns (by hour, day of week)
            ordering_patterns = self._analyze_ordering_patterns(orders)
            
            return {
                "user_id": user_id,
                "period_days": days,
                "total_orders": total_orders,
                "total_spent": total_spent,
                "average_order_value": avg_order_value,
                "favorite_cuisines": [{"cuisine": cuisine, "count": count} for cuisine, count in favorite_cuisines],
                "ordering_patterns": ordering_patterns,
            }
            
        except Exception as e:
            logger.error("Failed to get user analytics", user_id=user_id, error=str(e))
            return {}
    
    async def send_notification(
        self,
        user_id: str,
        notification_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Send notification to user
        
        Uber Eats API: POST /v1/eats/users/{user_id}/notifications
        """
        try:
            payload = {
                "type": notification_data.get("type", "promotional"),
                "title": notification_data.get("title", ""),
                "message": notification_data.get("message", ""),
                "data": notification_data.get("data", {}),
            }
            
            response_data = await self.post(f"/v1/eats/users/{user_id}/notifications", data=payload)
            return response_data
            
        except Exception as e:
            logger.error("Failed to send notification", user_id=user_id, error=str(e))
            raise
    
    async def get_loyalty_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get user loyalty program information
        
        Uber Eats API: GET /v1/eats/users/{user_id}/loyalty
        """
        try:
            response_data = await self.get(f"/v1/eats/users/{user_id}/loyalty")
            return response_data
            
        except Exception as e:
            logger.error("Failed to get loyalty info", user_id=user_id, error=str(e))
            return {}
    
    async def get_recommendations(
        self,
        user_id: str,
        store_id: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations for user
        
        Uber Eats API: GET /v1/eats/users/{user_id}/recommendations
        """
        try:
            params = {
                "limit": limit,
            }
            
            if store_id:
                params["store_id"] = store_id
            if category:
                params["category"] = category
            
            response_data = await self.get(f"/v1/eats/users/{user_id}/recommendations", params=params)
            return response_data.get("recommendations", [])
            
        except Exception as e:
            logger.error("Failed to get recommendations", user_id=user_id, error=str(e))
            return []
    
    async def create_user_segment(
        self,
        segment_name: str,
        criteria: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create user segment for targeted marketing
        
        Custom endpoint for customer segmentation
        """
        try:
            payload = {
                "name": segment_name,
                "criteria": criteria,
            }
            
            response_data = await self.post("/v1/eats/users/segments", data=payload)
            return response_data
            
        except Exception as e:
            logger.error("Failed to create user segment", segment_name=segment_name, error=str(e))
            raise
    
    async def get_user_segments(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get segments that a user belongs to
        
        Custom endpoint for user segmentation
        """
        try:
            response_data = await self.get(f"/v1/eats/users/{user_id}/segments")
            return response_data.get("segments", [])
            
        except Exception as e:
            logger.error("Failed to get user segments", user_id=user_id, error=str(e))
            return []
    
    def _analyze_ordering_patterns(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze ordering patterns from order history"""
        try:
            hour_counts = {}
            day_counts = {}
            
            for order in orders:
                order_time_str = order.get("placed_at")
                if not order_time_str:
                    continue
                
                try:
                    order_time = datetime.fromisoformat(order_time_str.replace('Z', '+00:00'))
                    
                    # Count by hour
                    hour = order_time.hour
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
                    
                    # Count by day of week (0 = Monday, 6 = Sunday)
                    day = order_time.weekday()
                    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    day_name = day_names[day]
                    day_counts[day_name] = day_counts.get(day_name, 0) + 1
                    
                except (ValueError, AttributeError):
                    continue
            
            # Find peak hours and days
            peak_hour = max(hour_counts.items(), key=lambda x: x[1]) if hour_counts else (None, 0)
            peak_day = max(day_counts.items(), key=lambda x: x[1]) if day_counts else (None, 0)
            
            return {
                "hourly_distribution": hour_counts,
                "daily_distribution": day_counts,
                "peak_hour": {"hour": peak_hour[0], "count": peak_hour[1]} if peak_hour[0] is not None else None,
                "peak_day": {"day": peak_day[0], "count": peak_day[1]} if peak_day[0] is not None else None,
            }
            
        except Exception as e:
            logger.error("Failed to analyze ordering patterns", error=str(e))
            return {}
    
    # Convenience methods for common user management tasks
    
    async def get_high_value_customers(
        self,
        store_id: Optional[str] = None,
        min_order_value: float = 100.0,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get high-value customers for targeted promotions"""
        try:
            params = {
                "min_total_spent": min_order_value,
                "days": days,
            }
            
            if store_id:
                params["store_id"] = store_id
            
            response_data = await self.get("/v1/eats/users/high_value", params=params)
            return response_data.get("users", [])
            
        except Exception as e:
            logger.error("Failed to get high value customers", error=str(e))
            return []
    
    async def get_inactive_users(
        self,
        store_id: Optional[str] = None,
        days_inactive: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get users who haven't ordered recently for re-engagement campaigns"""
        try:
            params = {
                "days_inactive": days_inactive,
            }
            
            if store_id:
                params["store_id"] = store_id
            
            response_data = await self.get("/v1/eats/users/inactive", params=params)
            return response_data.get("users", [])
            
        except Exception as e:
            logger.error("Failed to get inactive users", error=str(e))
            return []