"""Tests for API endpoints."""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json

from app.main import app
from app.schemas.auth import OAuthTokenResponse
from app.schemas.store import Store, StoreStatus
from app.schemas.order import Order, OrderStatus
from app.schemas.delivery import Delivery, DeliveryStatus


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_auth_token():
    """Mock authentication token."""
    return "test_bearer_token"


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs_url" in data
    assert "health_url" in data


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_oauth_token_endpoint(client):
    """Test OAuth token endpoint."""
    with patch('app.services.uber_eats.auth.UberEatsAuthService') as mock_service:
        # Mock the service
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance
        
        # Mock the token response
        mock_token_response = OAuthTokenResponse(
            access_token="test_token",
            token_type="Bearer",
            expires_in=3600,
            scope="eats.store eats.order"
        )
        mock_service_instance.get_client_credentials_token.return_value = mock_token_response
        
        # Make request
        response = client.post("/api/v1/oauth/token", json={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "test_secret"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test_token"
        assert data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_stores_list_endpoint(client):
    """Test stores list endpoint."""
    with patch('app.services.uber_eats.stores.UberEatsStoreService') as mock_service:
        with patch('app.api.dependencies.auth.get_uber_eats_token') as mock_auth:
            # Mock auth
            mock_auth.return_value = "test_token"
            
            # Mock service
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # Mock store data
            mock_stores = {
                "stores": [
                    {
                        "id": "store1",
                        "name": "Test Store",
                        "status": StoreStatus.ONLINE,
                        "address": "123 Test St",
                        "phone": "555-1234"
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10
            }
            mock_service_instance.list_stores.return_value = mock_stores
            
            # Make request
            response = client.get("/api/v1/stores/")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["stores"]) == 1
            assert data["stores"][0]["id"] == "store1"


@pytest.mark.asyncio
async def test_orders_list_endpoint(client):
    """Test orders list endpoint."""
    with patch('app.services.uber_eats.orders.UberEatsOrderService') as mock_service:
        with patch('app.api.dependencies.auth.get_uber_eats_token') as mock_auth:
            # Mock auth
            mock_auth.return_value = "test_token"
            
            # Mock service
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # Mock order data
            mock_orders = {
                "orders": [
                    {
                        "id": "order1",
                        "store_id": "store1",
                        "status": OrderStatus.PLACED,
                        "total": 25.99,
                        "created_at": datetime.utcnow().isoformat()
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10
            }
            mock_service_instance.list_orders.return_value = mock_orders
            
            # Make request
            response = client.get("/api/v1/orders/")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["orders"]) == 1
            assert data["orders"][0]["id"] == "order1"


@pytest.mark.asyncio
async def test_webhook_endpoint(client):
    """Test webhook endpoint."""
    with patch('app.services.uber_eats.webhooks.UberEatsWebhookService') as mock_service:
        with patch('app.api.v1.endpoints.uber_eats.webhooks.verify_webhook_signature') as mock_verify:
            # Mock signature verification
            mock_verify.return_value = True
            
            # Mock service
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.store_webhook_event.return_value = None
            
            # Mock webhook payload
            webhook_payload = {
                "metadata": {
                    "event_type": "order.placed",
                    "event_id": "test_event_123"
                },
                "data": {
                    "order_id": "order123",
                    "store_id": "store123"
                }
            }
            
            # Make request
            response = client.post(
                "/api/v1/webhooks/",
                json=webhook_payload,
                headers={
                    "X-Uber-Signature": "test_signature",
                    "X-Uber-Timestamp": "1234567890"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["received"] is True
            assert data["event_id"] == "test_event_123"


@pytest.mark.asyncio
async def test_webhook_invalid_signature(client):
    """Test webhook with invalid signature."""
    with patch('app.api.v1.endpoints.uber_eats.webhooks.verify_webhook_signature') as mock_verify:
        # Mock signature verification failure
        mock_verify.return_value = False
        
        webhook_payload = {
            "metadata": {
                "event_type": "order.placed",
                "event_id": "test_event_123"
            }
        }
        
        response = client.post(
            "/api/v1/webhooks/",
            json=webhook_payload,
            headers={
                "X-Uber-Signature": "invalid_signature",
                "X-Uber-Timestamp": "1234567890"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid webhook signature" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delivery_quote_endpoint(client):
    """Test delivery quote endpoint."""
    with patch('app.services.uber_eats.delivery.UberEatsDeliveryService') as mock_service:
        with patch('app.api.dependencies.auth.get_uber_eats_token') as mock_auth:
            # Mock auth
            mock_auth.return_value = "test_token"
            
            # Mock service
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # Mock quote data
            mock_quote = {
                "id": "quote123",
                "estimated_price": 5.99,
                "estimated_time": 30,
                "currency": "USD"
            }
            mock_service_instance.get_delivery_quote.return_value = mock_quote
            
            # Make request
            delivery_request = {
                "pickup_address": "123 Restaurant St",
                "delivery_address": "456 Customer Ave",
                "items": [{"name": "Pizza", "quantity": 1}]
            }
            
            response = client.post("/api/v1/delivery/quote", json=delivery_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["estimated_price"] == 5.99
            assert data["estimated_time"] == 30


@pytest.mark.asyncio
async def test_menu_upload_endpoint(client):
    """Test menu upload endpoint."""
    with patch('app.services.uber_eats.menus.UberEatsMenuService') as mock_service:
        with patch('app.api.dependencies.auth.get_uber_eats_token') as mock_auth:
            # Mock auth
            mock_auth.return_value = "test_token"
            
            # Mock service
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # Mock menu data
            mock_menu = {
                "id": "menu123",
                "store_id": "store123",
                "categories": [
                    {
                        "id": "cat1",
                        "name": "Pizza",
                        "items": [
                            {
                                "id": "item1",
                                "name": "Margherita",
                                "price": 12.99
                            }
                        ]
                    }
                ]
            }
            mock_service_instance.upload_menu.return_value = mock_menu
            
            # Make request
            menu_upload = {
                "menu": mock_menu,
                "validate_only": False
            }
            
            response = client.put("/api/v1/menus/stores/store123/menu", json=menu_upload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "menu123"
            assert len(data["categories"]) == 1


@pytest.mark.asyncio
async def test_error_handling(client):
    """Test error handling in endpoints."""
    with patch('app.services.uber_eats.stores.UberEatsStoreService') as mock_service:
        with patch('app.api.dependencies.auth.get_uber_eats_token') as mock_auth:
            # Mock auth
            mock_auth.return_value = "test_token"
            
            # Mock service to raise exception
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.list_stores.side_effect = Exception("Service error")
            
            # Make request
            response = client.get("/api/v1/stores/")
            
            assert response.status_code == 500
            assert "Failed to fetch stores" in response.json()["detail"]


@pytest.mark.asyncio
async def test_pagination_parameters(client):
    """Test pagination parameters."""
    with patch('app.services.uber_eats.stores.UberEatsStoreService') as mock_service:
        with patch('app.api.dependencies.auth.get_uber_eats_token') as mock_auth:
            # Mock auth
            mock_auth.return_value = "test_token"
            
            # Mock service
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # Mock store data
            mock_stores = {
                "stores": [],
                "total": 0,
                "page": 2,
                "page_size": 5
            }
            mock_service_instance.list_stores.return_value = mock_stores
            
            # Make request with pagination
            response = client.get("/api/v1/stores/?page=2&page_size=5")
            
            assert response.status_code == 200
            data = response.json()
            assert data["page"] == 2
            assert data["page_size"] == 5
            
            # Verify service was called with correct pagination
            mock_service_instance.list_stores.assert_called_once()
            call_args = mock_service_instance.list_stores.call_args
            assert call_args[1]["limit"] == 5
            assert call_args[1]["offset"] == 5  # (page-1) * page_size