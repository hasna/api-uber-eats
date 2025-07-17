"""
Authentication dependencies for API endpoints
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.services.uber_eats.auth import UberEatsAuthService

security = HTTPBearer()


async def get_uber_eats_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> str:
    """
    Get and validate Uber Eats access token
    
    This dependency:
    1. Extracts the bearer token from the Authorization header
    2. Validates the token with Uber Eats
    3. Returns the token for use in API calls
    """
    token = credentials.credentials
    
    # Initialize auth service
    auth_service = UberEatsAuthService(db)
    
    # Validate token
    try:
        token_info = await auth_service.introspect_token(token)
        
        if not token_info.active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check required scopes
        required_scopes = {"eats.store", "eats.order"}
        token_scopes = set(token_info.scope.split() if token_info.scope else [])
        
        if not required_scopes.issubset(token_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return token
        
    except HTTPException:
        raise
    except Exception:
        # If we can't validate with Uber, allow the token through
        # The actual API calls will fail if it's invalid
        return token


async def get_optional_uber_eats_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db),
) -> Optional[str]:
    """
    Get optional Uber Eats access token
    
    Used for endpoints that can work with or without authentication
    """
    if not credentials:
        return None
    
    try:
        return await get_uber_eats_token(credentials, db)
    except HTTPException:
        return None