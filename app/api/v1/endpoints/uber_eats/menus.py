"""
Uber Eats Menu Management endpoints
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.menu import (
    Menu,
    MenuCreate,
    MenuItem,
    MenuItemCreate,
    MenuItemUpdate,
    MenuCategory,
    MenuUpload,
    ItemAvailabilityUpdate,
    MenuValidationResult,
    MenuItemStatus,
)
from app.schemas.base import BaseResponse
from app.services.uber_eats import UberEatsMenuService
from app.api.dependencies.auth import get_uber_eats_token

router = APIRouter()


@router.get("/stores/{store_id}/menu", response_model=Menu)
async def get_menu(
    store_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Menu:
    """
    Get the complete menu for a store
    
    Returns the entire menu structure including categories, items, and modifiers
    """
    menu_service = UberEatsMenuService(db, token)
    
    try:
        menu = await menu_service.get_menu(store_id)
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu not found for store {store_id}",
            )
        return menu
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch menu: {str(e)}",
        )


@router.put("/stores/{store_id}/menu", response_model=Menu)
async def upload_menu(
    store_id: str,
    menu_upload: MenuUpload,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Menu:
    """
    Upload/replace entire menu for a store
    
    Replaces the complete menu. Use with caution as this will overwrite existing menu.
    """
    menu_service = UberEatsMenuService(db, token)
    
    try:
        # Validate menu first if requested
        if menu_upload.validate_only:
            validation_result = await menu_service.validate_menu(menu_upload.menu)
            if not validation_result.is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Menu validation failed",
                        "errors": validation_result.errors,
                        "warnings": validation_result.warnings,
                    },
                )
            return {"message": "Menu is valid", "warnings": validation_result.warnings}
        
        # Upload menu
        menu = await menu_service.upload_menu(store_id, menu_upload.menu)
        
        # Sync menu in background
        background_tasks.add_task(menu_service.sync_menu_status, store_id)
        
        return menu
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload menu: {str(e)}",
        )


@router.post("/stores/{store_id}/menu/validate", response_model=MenuValidationResult)
async def validate_menu(
    store_id: str,
    menu: MenuCreate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> MenuValidationResult:
    """
    Validate a menu without uploading
    
    Checks menu structure, required fields, and business rules
    """
    menu_service = UberEatsMenuService(db, token)
    
    try:
        validation_result = await menu_service.validate_menu(menu, store_id)
        return validation_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate menu: {str(e)}",
        )


@router.get("/stores/{store_id}/menu/categories", response_model=List[MenuCategory])
async def get_menu_categories(
    store_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> List[MenuCategory]:
    """
    Get all menu categories for a store
    
    Returns list of categories without items (lighter response)
    """
    menu_service = UberEatsMenuService(db, token)
    
    try:
        categories = await menu_service.get_categories(store_id)
        return categories
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch categories: {str(e)}",
        )


@router.get("/stores/{store_id}/menu/items", response_model=List[MenuItem])
async def get_menu_items(
    store_id: str,
    category_id: Optional[str] = None,
    status: Optional[MenuItemStatus] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> List[MenuItem]:
    """
    Get menu items for a store
    
    Can filter by category, status, or search term
    """
    menu_service = UberEatsMenuService(db, token)
    
    try:
        items = await menu_service.get_items(
            store_id=store_id,
            category_id=category_id,
            status=status,
            search=search,
        )
        return items
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch items: {str(e)}",
        )


@router.get("/stores/{store_id}/menu/items/{item_id}", response_model=MenuItem)
async def get_menu_item(
    store_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> MenuItem:
    """
    Get specific menu item details
    
    Returns complete item information including modifiers
    """
    menu_service = UberEatsMenuService(db, token)
    
    try:
        item = await menu_service.get_item(store_id, item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item {item_id} not found",
            )
        return item
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch item: {str(e)}",
        )


@router.post("/stores/{store_id}/menu/items", response_model=MenuItem)
async def create_menu_item(
    store_id: str,
    item: MenuItemCreate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> MenuItem:
    """
    Create a new menu item
    
    Adds a new item to the specified category
    """
    menu_service = UberEatsMenuService(db, token)
    
    try:
        created_item = await menu_service.create_item(store_id, item)
        return created_item
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create item: {str(e)}",
        )


@router.put("/stores/{store_id}/menu/items/{item_id}", response_model=MenuItem)
async def update_menu_item(
    store_id: str,
    item_id: str,
    item_update: MenuItemUpdate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> MenuItem:
    """
    Update a menu item
    
    Updates item properties like name, price, description, etc.
    """
    menu_service = UberEatsMenuService(db, token)
    
    try:
        updated_item = await menu_service.update_item(store_id, item_id, item_update)
        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item {item_id} not found",
            )
        return updated_item
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update item: {str(e)}",
        )


@router.delete("/stores/{store_id}/menu/items/{item_id}")
async def delete_menu_item(
    store_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> BaseResponse:
    """
    Delete a menu item
    
    Removes item from the menu
    """
    menu_service = UberEatsMenuService(db, token)
    
    try:
        success = await menu_service.delete_item(store_id, item_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item {item_id} not found",
            )
        return BaseResponse(success=True, message="Item deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete item: {str(e)}",
        )


@router.post("/stores/{store_id}/menu/items/availability")
async def update_items_availability(
    store_id: str,
    availability_update: ItemAvailabilityUpdate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> BaseResponse:
    """
    Bulk update item availability
    
    Mark multiple items as available/unavailable or update stock
    """
    menu_service = UberEatsMenuService(db, token)
    
    try:
        success = await menu_service.update_items_availability(
            store_id, 
            availability_update
        )
        
        return BaseResponse(
            success=success,
            message=f"Updated availability for {len(availability_update.item_ids)} items"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update availability: {str(e)}",
        )


@router.post("/stores/{store_id}/menu/sync")
async def sync_menu(
    store_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> BaseResponse:
    """
    Sync menu with Uber Eats
    
    Forces a full menu synchronization
    """
    menu_service = UberEatsMenuService(db, token)
    
    # Add sync task to background
    background_tasks.add_task(menu_service.sync_full_menu, store_id)
    
    return BaseResponse(
        success=True,
        message="Menu sync initiated. This may take a few minutes."
    )