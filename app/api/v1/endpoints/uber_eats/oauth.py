"""
Uber Eats OAuth2 authentication endpoints
"""
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import secrets
from datetime import datetime, timedelta

from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import (
    OAuthTokenRequest,
    OAuthTokenResponse,
    AuthorizationRequest,
    RevokeTokenRequest,
    TokenInfo,
    AuthError,
    GrantType,
)
from app.services.uber_eats import UberEatsAuthService

router = APIRouter()


@router.get("/authorize")
async def authorize(
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: Optional[str] = None,
    response_type: str = "code",
) -> RedirectResponse:
    """
    Initiate OAuth2 authorization flow
    
    Redirects user to Uber's authorization page
    """
    if response_type != "code":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only authorization code flow is supported",
        )
    
    # Build authorization URL
    auth_params = {
        "response_type": response_type,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
    }
    
    if state:
        auth_params["state"] = state
    
    # Construct authorization URL
    auth_url = f"{settings.UBER_EATS_AUTH_URL.replace('/token', '/authorize')}"
    query_string = "&".join([f"{k}={v}" for k, v in auth_params.items()])
    full_url = f"{auth_url}?{query_string}"
    
    return RedirectResponse(url=full_url)


@router.post("/token", response_model=OAuthTokenResponse)
async def exchange_token(
    request: OAuthTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> OAuthTokenResponse:
    """
    Exchange authorization code for access token
    
    Supports:
    - Authorization code exchange
    - Client credentials
    - Refresh token
    """
    auth_service = UberEatsAuthService(db)
    
    try:
        # Handle different grant types
        if request.grant_type == GrantType.AUTHORIZATION_CODE:
            if not request.code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Authorization code is required",
                )
            
            token_response = await auth_service.exchange_code_for_token(
                code=request.code,
                client_id=request.client_id,
                client_secret=request.client_secret,
                redirect_uri=request.redirect_uri,
            )
            
        elif request.grant_type == GrantType.CLIENT_CREDENTIALS:
            token_response = await auth_service.get_client_credentials_token(
                client_id=request.client_id,
                client_secret=request.client_secret,
                scope=request.scope,
            )
            
        elif request.grant_type == GrantType.REFRESH_TOKEN:
            if not request.refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Refresh token is required",
                )
            
            token_response = await auth_service.refresh_access_token(
                refresh_token=request.refresh_token,
                client_id=request.client_id,
                client_secret=request.client_secret,
            )
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported grant type: {request.grant_type}",
            )
        
        return token_response
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid client credentials",
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to communicate with Uber Eats auth server",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/revoke")
async def revoke_token(
    request: RevokeTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Revoke an access or refresh token"""
    auth_service = UberEatsAuthService(db)
    
    try:
        success = await auth_service.revoke_token(
            token=request.token,
            token_type_hint=request.token_type_hint,
        )
        
        if success:
            return {"message": "Token revoked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to revoke token",
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/introspect", response_model=TokenInfo)
async def introspect_token(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> TokenInfo:
    """
    Introspect a token to get its details
    
    Returns information about the token including:
    - Whether it's active
    - Scopes
    - Expiration time
    """
    auth_service = UberEatsAuthService(db)
    
    try:
        token_info = await auth_service.introspect_token(token)
        return token_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/callback")
async def oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    OAuth callback endpoint
    
    Handles the redirect from Uber's authorization server
    """
    # Check for errors
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authorization failed: {error} - {error_description}",
        )
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided",
        )
    
    # In a real implementation, you would:
    # 1. Verify the state parameter matches what was sent
    # 2. Exchange the code for tokens
    # 3. Store the tokens securely
    # 4. Redirect the user to your application
    
    return {
        "message": "Authorization successful",
        "code": code,
        "state": state,
        "next_step": "Exchange this code for an access token using POST /oauth/token",
    }