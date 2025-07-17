"""
Base database configuration and imports
"""
# Import all models here for Alembic to detect them
from app.db.session import Base
from app.db.models.user import User
from app.db.models.store import Store
from app.db.models.menu import Menu, MenuItem, MenuCategory, ModifierGroup, Modifier
from app.db.models.order import Order, OrderItem
from app.db.models.webhook import WebhookEvent
from app.db.models.auth import AuthToken

__all__ = [
    "Base",
    "User",
    "Store",
    "Menu",
    "MenuItem",
    "MenuCategory",
    "ModifierGroup",
    "Modifier",
    "Order",
    "OrderItem",
    "WebhookEvent",
    "AuthToken",
]