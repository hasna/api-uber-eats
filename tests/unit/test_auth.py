"""Tests for authentication service."""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
import httpx

from app.services.uber_eats.auth import UberEatsAuthService
from app.schemas.auth import OAuthTokenResponse, GrantType
from app.db.models.auth import AuthToken


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def auth_service(mock_db):
    """Create auth service instance."""
    return UberEatsAuthService(mock_db)


@pytest.mark.asyncio
async def test_exchange_code_for_token(auth_service, mock_db):
    """Test exchanging authorization code for token."""
    # Mock response data
    mock_response_data = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "eats.store eats.order"
    }
    
    # Mock httpx response
    mock_response = AsyncMock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status.return_value = None
    
    # Mock httpx client
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    
    # Mock token storage
    mock_token = AuthToken(
        id=1,
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        token_type="Bearer",
        scope="eats.store eats.order",
        expires_at=datetime.utcnow() + timedelta(seconds=3600),
        is_active=True
    )
    auth_service._store_token = AsyncMock(return_value=mock_token)
    
    with patch('httpx.AsyncClient') as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        result = await auth_service.exchange_code_for_token(
            code="test_code",
            redirect_uri="https://example.com/callback"
        )
        
        assert isinstance(result, OAuthTokenResponse)
        assert result.access_token == "test_access_token"
        assert result.refresh_token == "test_refresh_token"
        assert result.token_type == "Bearer"
        
        # Verify the API call was made correctly
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["grant_type"] == GrantType.AUTHORIZATION_CODE
        assert call_args[1]["data"]["code"] == "test_code"
        assert call_args[1]["data"]["redirect_uri"] == "https://example.com/callback"


@pytest.mark.asyncio
async def test_get_client_credentials_token(auth_service, mock_db):
    """Test getting client credentials token."""
    # Mock response data
    mock_response_data = {
        "access_token": "test_client_token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "eats.store eats.order eats.report"
    }
    
    # Mock httpx response
    mock_response = AsyncMock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status.return_value = None
    
    # Mock httpx client
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    
    # Mock token storage
    mock_token = AuthToken(
        id=1,
        access_token="test_client_token",
        token_type="Bearer",
        scope="eats.store eats.order eats.report",
        expires_at=datetime.utcnow() + timedelta(seconds=3600),
        is_active=True
    )
    auth_service._store_token = AsyncMock(return_value=mock_token)
    
    with patch('httpx.AsyncClient') as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        result = await auth_service.get_client_credentials_token()
        
        assert isinstance(result, OAuthTokenResponse)
        assert result.access_token == "test_client_token"
        assert result.token_type == "Bearer"
        assert result.scope == "eats.store eats.order eats.report"
        
        # Verify the API call was made correctly
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["grant_type"] == GrantType.CLIENT_CREDENTIALS
        assert call_args[1]["data"]["scope"] == "eats.store eats.order eats.report"


@pytest.mark.asyncio
async def test_refresh_access_token(auth_service, mock_db):
    """Test refreshing access token."""
    # Mock response data
    mock_response_data = {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "eats.store eats.order"
    }
    
    # Mock httpx response
    mock_response = AsyncMock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status.return_value = None
    
    # Mock httpx client
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    
    # Mock token storage
    mock_token = AuthToken(
        id=1,
        access_token="new_access_token",
        refresh_token="new_refresh_token",
        token_type="Bearer",
        scope="eats.store eats.order",
        expires_at=datetime.utcnow() + timedelta(seconds=3600),
        is_active=True
    )
    auth_service._store_token = AsyncMock(return_value=mock_token)
    
    with patch('httpx.AsyncClient') as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        result = await auth_service.refresh_access_token(
            refresh_token="old_refresh_token"
        )
        
        assert isinstance(result, OAuthTokenResponse)
        assert result.access_token == "new_access_token"
        assert result.refresh_token == "new_refresh_token"
        
        # Verify the API call was made correctly
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["grant_type"] == GrantType.REFRESH_TOKEN
        assert call_args[1]["data"]["refresh_token"] == "old_refresh_token"


@pytest.mark.asyncio
async def test_revoke_token(auth_service, mock_db):
    """Test revoking a token."""
    # Mock httpx response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    
    # Mock httpx client
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    
    # Mock token revocation
    auth_service._revoke_stored_token = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        result = await auth_service.revoke_token("test_token")
        
        assert result is True
        
        # Verify the API call was made correctly
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["token"] == "test_token"
        
        # Verify token was marked as revoked
        auth_service._revoke_stored_token.assert_called_once_with("test_token")


@pytest.mark.asyncio
async def test_http_error_handling(auth_service, mock_db):
    """Test HTTP error handling."""
    # Mock httpx error
    mock_response = AsyncMock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Unauthorized",
        request=AsyncMock(),
        response=mock_response
    )
    
    # Mock httpx client
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    
    with patch('httpx.AsyncClient') as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(httpx.HTTPStatusError):
            await auth_service.exchange_code_for_token(
                code="invalid_code",
                redirect_uri="https://example.com/callback"
            )


@pytest.mark.asyncio
async def test_get_stored_token(auth_service, mock_db):
    """Test getting stored token from database."""
    # Mock database query result
    mock_token = AuthToken(
        id=1,
        access_token="stored_token",
        token_type="Bearer",
        scope="eats.store",
        expires_at=datetime.utcnow() + timedelta(hours=1),
        is_active=True
    )
    
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = mock_token
    mock_db.execute.return_value = mock_result
    
    result = await auth_service.get_stored_token()
    
    assert result == mock_token
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_store_token(auth_service, mock_db):
    """Test storing token in database."""
    token_data = {
        "access_token": "new_token",
        "refresh_token": "refresh_token",
        "token_type": "Bearer",
        "scope": "eats.store",
        "expires_in": 3600
    }
    
    # Mock database operations
    mock_db.add = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    result = await auth_service._store_token(token_data)
    
    assert isinstance(result, AuthToken)
    assert result.access_token == "new_token"
    assert result.refresh_token == "refresh_token"
    assert result.token_type == "Bearer"
    assert result.scope == "eats.store"
    assert result.is_active is True
    
    # Verify database operations
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()