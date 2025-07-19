"""
Uber Eats Authentication Service
"""
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.config import settings
from app.schemas.auth import (
    OAuthTokenResponse,
    TokenInfo,
    GrantType,
    TokenType,
)
from app.db.models.auth import AuthToken

logger = structlog.get_logger()


class UberEatsAuthService:
    """Service for handling Uber Eats OAuth authentication"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_url = settings.UBER_EATS_AUTH_URL
        self.client_id = settings.UBER_EATS_CLIENT_ID
        self.client_secret = settings.UBER_EATS_CLIENT_SECRET
    
    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> OAuthTokenResponse:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": GrantType.AUTHORIZATION_CODE,
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": client_id or self.client_id,
                "client_secret": client_secret or self.client_secret,
            }
            
            response = await client.post(self.auth_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Store token in database
            await self._store_token(token_data)
            
            return OAuthTokenResponse(**token_data)
    
    async def get_client_credentials_token(
        self,
        scope: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> OAuthTokenResponse:
        """Get access token using client credentials flow"""
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": GrantType.CLIENT_CREDENTIALS,
                "client_id": client_id or self.client_id,
                "client_secret": client_secret or self.client_secret,
            }
            
            if scope:
                data["scope"] = scope
            else:
                # Default scopes
                data["scope"] = "eats.store eats.order eats.report"
            
            response = await client.post(self.auth_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Store token in database
            await self._store_token(token_data)
            
            return OAuthTokenResponse(**token_data)
    
    async def refresh_access_token(
        self,
        refresh_token: str,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> OAuthTokenResponse:
        """Refresh access token using refresh token"""
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": GrantType.REFRESH_TOKEN,
                "refresh_token": refresh_token,
                "client_id": client_id or self.client_id,
                "client_secret": client_secret or self.client_secret,
            }
            
            response = await client.post(self.auth_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Store token in database
            await self._store_token(token_data)
            
            return OAuthTokenResponse(**token_data)
    
    async def revoke_token(
        self,
        token: str,
        token_type_hint: Optional[str] = None,
    ) -> bool:
        """Revoke an access or refresh token"""
        async with httpx.AsyncClient() as client:
            data = {
                "token": token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            
            if token_type_hint:
                data["token_type_hint"] = token_type_hint
            
            revoke_url = self.auth_url.replace("/token", "/revoke")
            response = await client.post(revoke_url, data=data)
            
            # Mark token as revoked in database
            if response.status_code == 200:
                await self._revoke_stored_token(token)
            
            return response.status_code == 200
    
    async def introspect_token(self, token: str) -> TokenInfo:
        """Introspect token to get details"""
        async with httpx.AsyncClient() as client:
            data = {
                "token": token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            
            introspect_url = self.auth_url.replace("/token", "/introspect")
            response = await client.post(introspect_url, data=data)
            response.raise_for_status()
            
            return TokenInfo(**response.json())
    
    async def get_stored_token(self) -> Optional[AuthToken]:
        """Get valid stored token from database"""
        stmt = select(AuthToken).where(
            AuthToken.is_active == True,
            AuthToken.expires_at > datetime.utcnow(),
        ).order_by(AuthToken.created_at.desc())
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _store_token(self, token_data: Dict[str, Any]) -> AuthToken:
        """Store token in database"""
        expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
        
        token = AuthToken(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_type=token_data.get("token_type", "Bearer"),
            scope=token_data.get("scope", ""),
            expires_at=expires_at,
            is_active=True,
        )
        
        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)
        
        return token
    
    async def _revoke_stored_token(self, token: str) -> None:
        """Mark token as revoked in database"""
        stmt = select(AuthToken).where(AuthToken.access_token == token)
        result = await self.db.execute(stmt)
        auth_token = result.scalar_one_or_none()
        
        if auth_token:
            auth_token.is_active = False
            await self.db.commit()