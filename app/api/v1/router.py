"""
Main API router for v1 endpoints
"""
from fastapi import APIRouter

from app.api.v1.endpoints.app import auth, health
from app.api.v1.endpoints.uber_eats import (
    stores,
    menus,
    orders,
    webhooks,
    oauth,
    reports,
    delivery,
    users,
)

api_router = APIRouter()

# Include app endpoints
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include Uber Eats endpoints
api_router.include_router(oauth.router, prefix="/uber-eats/oauth", tags=["Uber Eats OAuth"])
api_router.include_router(stores.router, prefix="/uber-eats/stores", tags=["Uber Eats Stores"])
api_router.include_router(menus.router, prefix="/uber-eats/menus", tags=["Uber Eats Menus"])
api_router.include_router(orders.router, prefix="/uber-eats/orders", tags=["Uber Eats Orders"])
api_router.include_router(webhooks.router, prefix="/uber-eats/webhooks", tags=["Uber Eats Webhooks"])
api_router.include_router(reports.router, prefix="/uber-eats/reports", tags=["Uber Eats Reports"])
api_router.include_router(delivery.router, prefix="/uber-eats/delivery", tags=["Uber Eats Delivery"])
api_router.include_router(users.router, prefix="/uber-eats/users", tags=["Uber Eats Users"])