"""
Authentication and OAuth schemas for Uber Eats API
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from enum import Enum


class GrantType(str, Enum):
    """OAuth grant types"""
    CLIENT_CREDENTIALS = "client_credentials"
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"


class TokenType(str, Enum):
    """Token types"""
    BEARER = "Bearer"


class Scope(str, Enum):
    """Uber Eats API scopes"""
    EATS_STORE = "eats.store"
    EATS_STORE_READ = "eats.store:read"
    EATS_STORE_WRITE = "eats.store:write"
    EATS_ORDER = "eats.order"
    EATS_ORDER_READ = "eats.order:read"
    EATS_ORDER_WRITE = "eats.order:write"
    EATS_DELIVERY = "eats.delivery"
    EATS_REPORT = "eats.report"
    EATS_POS_PROVISIONING = "eats.pos_provisioning"


class OAuthTokenRequest(BaseModel):
    """OAuth token request schema"""
    grant_type: GrantType = Field(description="OAuth grant type")
    client_id: str = Field(description="Client ID")
    client_secret: str = Field(description="Client secret")
    code: Optional[str] = Field(default=None, description="Authorization code")
    redirect_uri: Optional[HttpUrl] = Field(default=None, description="Redirect URI")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")
    scope: Optional[str] = Field(default=None, description="Requested scopes")
    
    model_config = ConfigDict(from_attributes=True)


class OAuthTokenResponse(BaseModel):
    """OAuth token response schema"""
    access_token: str = Field(description="Access token")
    token_type: TokenType = Field(description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")
    scope: str = Field(description="Granted scopes")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Token creation time")
    
    model_config = ConfigDict(from_attributes=True)


class AuthorizationRequest(BaseModel):
    """Authorization request schema"""
    response_type: str = Field(default="code", description="Response type")
    client_id: str = Field(description="Client ID")
    redirect_uri: HttpUrl = Field(description="Redirect URI")
    scope: str = Field(description="Requested scopes")
    state: Optional[str] = Field(default=None, description="State parameter")
    
    model_config = ConfigDict(from_attributes=True)


class RevokeTokenRequest(BaseModel):
    """Revoke token request schema"""
    token: str = Field(description="Token to revoke")
    token_type_hint: Optional[str] = Field(default=None, description="Token type hint")
    
    model_config = ConfigDict(from_attributes=True)


class TokenInfo(BaseModel):
    """Token information schema"""
    active: bool = Field(description="Whether token is active")
    scope: Optional[str] = Field(default=None, description="Token scopes")
    client_id: Optional[str] = Field(default=None, description="Client ID")
    username: Optional[str] = Field(default=None, description="Username")
    exp: Optional[int] = Field(default=None, description="Expiration timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class WebhookSignature(BaseModel):
    """Webhook signature verification schema"""
    signature: str = Field(description="Webhook signature header")
    timestamp: str = Field(description="Webhook timestamp header")
    body: str = Field(description="Raw webhook body")
    
    model_config = ConfigDict(from_attributes=True)


class WebhookConfig(BaseModel):
    """Webhook configuration schema"""
    webhook_url: HttpUrl = Field(description="Webhook endpoint URL")
    event_types: List[str] = Field(description="List of event types to subscribe to")
    secret: Optional[str] = Field(default=None, description="Webhook secret for signature verification")
    is_active: bool = Field(default=True, description="Whether webhook is active")
    
    model_config = ConfigDict(from_attributes=True)


class APIKey(BaseModel):
    """API key schema"""
    key: str = Field(description="API key")
    name: str = Field(description="Key name/description")
    scopes: List[Scope] = Field(description="Allowed scopes")
    created_at: datetime = Field(description="Creation timestamp")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration timestamp")
    is_active: bool = Field(default=True, description="Whether key is active")
    
    model_config = ConfigDict(from_attributes=True)


class AuthError(BaseModel):
    """Authentication error schema"""
    error: str = Field(description="Error code")
    error_description: str = Field(description="Error description")
    error_uri: Optional[HttpUrl] = Field(default=None, description="Error documentation URL")
    
    model_config = ConfigDict(from_attributes=True)