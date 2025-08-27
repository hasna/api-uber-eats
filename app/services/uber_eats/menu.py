"""
Uber Eats Menu Management Service
"""
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.services.uber_eats.base import UberEatsBaseService
from app.schemas.menu import (
    Menu,
    MenuCreate,
    MenuUpdate,
    MenuItem,
    MenuItemCreate,
    MenuItemUpdate,
    MenuCategory,
    MenuCategoryCreate,
    MenuCategoryUpdate,
    ModifierGroup,
    ModifierGroupCreate,
    ModifierGroupUpdate,
    MenuItemAvailability,
)

logger = structlog.get_logger()


class UberEatsMenuService(UberEatsBaseService):
    """Service for managing Uber Eats menus"""
    
    def __init__(self, db: AsyncSession, access_token: str):
        super().__init__(db, access_token)
    
    async def get_menu(self, store_id: str) -> Optional[Menu]:
        """
        Get the complete menu for a store
        
        Uber Eats API: GET /v1/eats/stores/{store_id}/menus
        """
        try:
            response_data = await self.get(f"/v1/eats/stores/{store_id}/menus")
            return Menu(**response_data)
            
        except Exception as e:
            logger.error("Failed to get menu", store_id=store_id, error=str(e))
            return None
    
    async def create_menu(self, store_id: str, menu_data: MenuCreate) -> Menu:
        """
        Create a new menu for a store
        
        Uber Eats API: POST /v1/eats/stores/{store_id}/menus
        """
        try:
            payload = menu_data.model_dump(exclude_unset=True)
            response_data = await self.post(f"/v1/eats/stores/{store_id}/menus", data=payload)
            return Menu(**response_data)
            
        except Exception as e:
            logger.error("Failed to create menu", store_id=store_id, error=str(e))
            raise
    
    async def update_menu(self, store_id: str, menu_update: MenuUpdate) -> Optional[Menu]:
        """
        Update an existing menu
        
        Uber Eats API: PUT /v1/eats/stores/{store_id}/menus
        """
        try:
            payload = menu_update.model_dump(exclude_unset=True)
            response_data = await self.put(f"/v1/eats/stores/{store_id}/menus", data=payload)
            return Menu(**response_data)
            
        except Exception as e:
            logger.error("Failed to update menu", store_id=store_id, error=str(e))
            return None
    
    async def delete_menu(self, store_id: str) -> bool:
        """
        Delete a menu
        
        Uber Eats API: DELETE /v1/eats/stores/{store_id}/menus
        """
        try:
            return await self.delete(f"/v1/eats/stores/{store_id}/menus")
            
        except Exception as e:
            logger.error("Failed to delete menu", store_id=store_id, error=str(e))
            return False
    
    # Menu Items Management
    
    async def get_menu_items(self, store_id: str) -> List[MenuItem]:
        """
        Get all menu items for a store
        
        Uber Eats API: GET /v1/eats/stores/{store_id}/menus/items
        """
        try:
            response_data = await self.get(f"/v1/eats/stores/{store_id}/menus/items")
            items = []
            for item_data in response_data.get("items", []):
                items.append(MenuItem(**item_data))
            return items
            
        except Exception as e:
            logger.error("Failed to get menu items", store_id=store_id, error=str(e))
            return []
    
    async def get_menu_item(self, store_id: str, item_id: str) -> Optional[MenuItem]:
        """
        Get a specific menu item
        
        Uber Eats API: GET /v1/eats/stores/{store_id}/menus/items/{item_id}
        """
        try:
            response_data = await self.get(f"/v1/eats/stores/{store_id}/menus/items/{item_id}")
            return MenuItem(**response_data)
            
        except Exception as e:
            logger.error("Failed to get menu item", store_id=store_id, item_id=item_id, error=str(e))
            return None
    
    async def create_menu_item(self, store_id: str, item_data: MenuItemCreate) -> MenuItem:
        """
        Create a new menu item
        
        Uber Eats API: POST /v1/eats/stores/{store_id}/menus/items
        """
        try:
            payload = item_data.model_dump(exclude_unset=True)
            response_data = await self.post(f"/v1/eats/stores/{store_id}/menus/items", data=payload)
            return MenuItem(**response_data)
            
        except Exception as e:
            logger.error("Failed to create menu item", store_id=store_id, error=str(e))
            raise
    
    async def update_menu_item(
        self, 
        store_id: str, 
        item_id: str, 
        item_update: MenuItemUpdate
    ) -> Optional[MenuItem]:
        """
        Update a menu item
        
        Uber Eats API: PUT /v1/eats/stores/{store_id}/menus/items/{item_id}
        """
        try:
            payload = item_update.model_dump(exclude_unset=True)
            response_data = await self.put(
                f"/v1/eats/stores/{store_id}/menus/items/{item_id}", 
                data=payload
            )
            return MenuItem(**response_data)
            
        except Exception as e:
            logger.error("Failed to update menu item", store_id=store_id, item_id=item_id, error=str(e))
            return None
    
    async def delete_menu_item(self, store_id: str, item_id: str) -> bool:
        """
        Delete a menu item
        
        Uber Eats API: DELETE /v1/eats/stores/{store_id}/menus/items/{item_id}
        """
        try:
            return await self.delete(f"/v1/eats/stores/{store_id}/menus/items/{item_id}")
            
        except Exception as e:
            logger.error("Failed to delete menu item", store_id=store_id, item_id=item_id, error=str(e))
            return False
    
    # Item Availability Management
    
    async def update_item_availability(
        self, 
        store_id: str, 
        item_id: str, 
        availability: MenuItemAvailability
    ) -> bool:
        """
        Update item availability status (in stock/out of stock)
        
        Uber Eats API: POST /v1/eats/stores/{store_id}/menus/items/{item_id}/availability
        """
        try:
            payload = {
                "available": availability.available,
                "unavailable_until": availability.unavailable_until.isoformat() if availability.unavailable_until else None,
                "reason": availability.reason,
            }
            
            await self.post(
                f"/v1/eats/stores/{store_id}/menus/items/{item_id}/availability", 
                data=payload
            )
            return True
            
        except Exception as e:
            logger.error("Failed to update item availability", store_id=store_id, item_id=item_id, error=str(e))
            return False
    
    async def bulk_update_availability(
        self, 
        store_id: str, 
        updates: List[Dict[str, Any]]
    ) -> bool:
        """
        Bulk update availability for multiple items
        
        Uber Eats API: POST /v1/eats/stores/{store_id}/menus/items/availability
        """
        try:
            payload = {"items": updates}
            await self.post(f"/v1/eats/stores/{store_id}/menus/items/availability", data=payload)
            return True
            
        except Exception as e:
            logger.error("Failed to bulk update availability", store_id=store_id, error=str(e))
            return False
    
    # Menu Categories Management
    
    async def get_menu_categories(self, store_id: str) -> List[MenuCategory]:
        """
        Get all menu categories for a store
        
        Uber Eats API: GET /v1/eats/stores/{store_id}/menus/categories
        """
        try:
            response_data = await self.get(f"/v1/eats/stores/{store_id}/menus/categories")
            categories = []
            for category_data in response_data.get("categories", []):
                categories.append(MenuCategory(**category_data))
            return categories
            
        except Exception as e:
            logger.error("Failed to get menu categories", store_id=store_id, error=str(e))
            return []
    
    async def create_menu_category(
        self, 
        store_id: str, 
        category_data: MenuCategoryCreate
    ) -> MenuCategory:
        """
        Create a new menu category
        
        Uber Eats API: POST /v1/eats/stores/{store_id}/menus/categories
        """
        try:
            payload = category_data.model_dump(exclude_unset=True)
            response_data = await self.post(f"/v1/eats/stores/{store_id}/menus/categories", data=payload)
            return MenuCategory(**response_data)
            
        except Exception as e:
            logger.error("Failed to create menu category", store_id=store_id, error=str(e))
            raise
    
    async def update_menu_category(
        self, 
        store_id: str, 
        category_id: str, 
        category_update: MenuCategoryUpdate
    ) -> Optional[MenuCategory]:
        """
        Update a menu category
        
        Uber Eats API: PUT /v1/eats/stores/{store_id}/menus/categories/{category_id}
        """
        try:
            payload = category_update.model_dump(exclude_unset=True)
            response_data = await self.put(
                f"/v1/eats/stores/{store_id}/menus/categories/{category_id}", 
                data=payload
            )
            return MenuCategory(**response_data)
            
        except Exception as e:
            logger.error("Failed to update menu category", store_id=store_id, category_id=category_id, error=str(e))
            return None
    
    # Modifier Groups Management
    
    async def get_modifier_groups(self, store_id: str) -> List[ModifierGroup]:
        """
        Get all modifier groups for a store
        
        Uber Eats API: GET /v1/eats/stores/{store_id}/menus/modifier_groups
        """
        try:
            response_data = await self.get(f"/v1/eats/stores/{store_id}/menus/modifier_groups")
            groups = []
            for group_data in response_data.get("modifier_groups", []):
                groups.append(ModifierGroup(**group_data))
            return groups
            
        except Exception as e:
            logger.error("Failed to get modifier groups", store_id=store_id, error=str(e))
            return []
    
    async def create_modifier_group(
        self, 
        store_id: str, 
        group_data: ModifierGroupCreate
    ) -> ModifierGroup:
        """
        Create a new modifier group
        
        Uber Eats API: POST /v1/eats/stores/{store_id}/menus/modifier_groups
        """
        try:
            payload = group_data.model_dump(exclude_unset=True)
            response_data = await self.post(f"/v1/eats/stores/{store_id}/menus/modifier_groups", data=payload)
            return ModifierGroup(**response_data)
            
        except Exception as e:
            logger.error("Failed to create modifier group", store_id=store_id, error=str(e))
            raise
    
    # Convenience Methods
    
    async def mark_item_out_of_stock(self, store_id: str, item_id: str, reason: str = "Out of stock") -> bool:
        """Mark an item as out of stock"""
        availability = MenuItemAvailability(available=False, reason=reason)
        return await self.update_item_availability(store_id, item_id, availability)
    
    async def mark_item_in_stock(self, store_id: str, item_id: str) -> bool:
        """Mark an item as back in stock"""
        availability = MenuItemAvailability(available=True, reason="Back in stock")
        return await self.update_item_availability(store_id, item_id, availability)
    
    async def update_item_price(
        self, 
        store_id: str, 
        item_id: str, 
        new_price: int
    ) -> Optional[MenuItem]:
        """Update the price of a menu item"""
        item_update = MenuItemUpdate(price=new_price)
        return await self.update_menu_item(store_id, item_id, item_update)
    
    async def sync_menu_from_pos(self, store_id: str, pos_menu_data: Dict[str, Any]) -> Menu:
        """
        Sync menu from POS system data
        
        This method takes POS system menu data and syncs it with Uber Eats
        """
        try:
            # Transform POS data to Uber Eats menu format
            menu_data = MenuCreate(
                title=pos_menu_data.get("name", "Menu"),
                categories=pos_menu_data.get("categories", []),
                items=pos_menu_data.get("items", []),
            )
            
            # Get existing menu to determine if we should create or update
            existing_menu = await self.get_menu(store_id)
            
            if existing_menu:
                # Update existing menu
                menu_update = MenuUpdate(**menu_data.model_dump())
                return await self.update_menu(store_id, menu_update)
            else:
                # Create new menu
                return await self.create_menu(store_id, menu_data)
                
        except Exception as e:
            logger.error("Failed to sync menu from POS", store_id=store_id, error=str(e))
            raise