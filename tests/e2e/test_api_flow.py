"""End-to-end tests for API workflows."""
import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_uber_eats_api():
    """Mock Uber Eats API responses."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        yield mock_instance


@pytest.mark.asyncio
async def test_oauth_flow(client, mock_uber_eats_api):
    """Test complete OAuth authentication flow."""
    # Mock token response
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "access_token": "test_access_token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "eats.store eats.order"
    }
    mock_response.raise_for_status.return_value = None
    mock_uber_eats_api.post.return_value = mock_response
    
    # Step 1: Get authorization URL
    auth_response = client.get("/api/v1/oauth/authorize", params={
        "client_id": "test_client",
        "redirect_uri": "https://example.com/callback",
        "scope": "eats.store eats.order",
        "response_type": "code"
    })
    
    assert auth_response.status_code == 307  # Redirect
    assert "uber" in auth_response.headers["location"].lower()
    
    # Step 2: Exchange code for token
    token_response = client.post("/api/v1/oauth/token", json={
        "grant_type": "authorization_code",
        "code": "test_code",
        "client_id": "test_client",
        "client_secret": "test_secret",
        "redirect_uri": "https://example.com/callback"
    })
    
    assert token_response.status_code == 200
    token_data = token_response.json()
    assert token_data["access_token"] == "test_access_token"
    assert token_data["token_type"] == "Bearer"
    
    # Step 3: Use token to access protected endpoint
    with patch('app.api.dependencies.auth.get_uber_eats_token') as mock_auth:
        mock_auth.return_value = "test_access_token"
        
        with patch('app.services.uber_eats.stores.UberEatsStoreService') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.list_stores.return_value = {
                "stores": [],
                "total": 0,
                "page": 1,
                "page_size": 10
            }
            
            stores_response = client.get("/api/v1/stores/")
            assert stores_response.status_code == 200


@pytest.mark.asyncio
async def test_store_management_flow(client, mock_uber_eats_api):
    """Test complete store management workflow."""
    with patch('app.api.dependencies.auth.get_uber_eats_token') as mock_auth:
        mock_auth.return_value = "test_access_token"
        
        with patch('app.services.uber_eats.stores.UberEatsStoreService') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # Step 1: Create store
            new_store_data = {
                "name": "Test Restaurant",
                "address": "123 Test Street",
                "phone_number": "555-1234",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "hours": {
                    "monday": {"open": "09:00", "close": "22:00"}
                }
            }
            
            mock_created_store = {
                "id": "store_123",
                "name": "Test Restaurant",
                "status": "ONLINE",
                **new_store_data
            }
            mock_service_instance.create_store.return_value = mock_created_store
            
            create_response = client.post("/api/v1/stores/", json=new_store_data)
            assert create_response.status_code == 200
            store_data = create_response.json()
            assert store_data["name"] == "Test Restaurant"
            store_id = store_data["id"]
            
            # Step 2: Get store details
            mock_service_instance.get_store.return_value = mock_created_store
            
            get_response = client.get(f"/api/v1/stores/{store_id}")
            assert get_response.status_code == 200
            retrieved_store = get_response.json()
            assert retrieved_store["name"] == "Test Restaurant"
            
            # Step 3: Update store
            update_data = {
                "name": "Updated Restaurant",
                "phone_number": "555-5678"
            }
            
            mock_updated_store = {**mock_created_store, **update_data}
            mock_service_instance.update_store.return_value = mock_updated_store
            
            update_response = client.put(f"/api/v1/stores/{store_id}", json=update_data)
            assert update_response.status_code == 200
            updated_store = update_response.json()
            assert updated_store["name"] == "Updated Restaurant"
            assert updated_store["phone_number"] == "555-5678"
            
            # Step 4: Update store status
            status_update = {
                "status": "OFFLINE",
                "reason": "Temporary closure"
            }
            
            mock_status_updated_store = {**mock_updated_store, "status": "OFFLINE"}
            mock_service_instance.update_store_status.return_value = mock_status_updated_store
            
            status_response = client.post(f"/api/v1/stores/{store_id}/status", json=status_update)
            assert status_response.status_code == 200
            status_updated_store = status_response.json()
            assert status_updated_store["status"] == "OFFLINE"


@pytest.mark.asyncio
async def test_order_processing_flow(client, mock_uber_eats_api):
    """Test complete order processing workflow."""
    with patch('app.api.dependencies.auth.get_uber_eats_token') as mock_auth:
        mock_auth.return_value = "test_access_token"
        
        with patch('app.services.uber_eats.orders.UberEatsOrderService') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # Step 1: List orders
            mock_orders = {
                "orders": [
                    {
                        "id": "order_123",
                        "store_id": "store_123",
                        "status": "PLACED",
                        "total": 25.99,
                        "customer_name": "John Doe",
                        "created_at": datetime.utcnow().isoformat()
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10
            }
            mock_service_instance.list_orders.return_value = mock_orders
            
            list_response = client.get("/api/v1/orders/")
            assert list_response.status_code == 200
            orders_data = list_response.json()
            assert len(orders_data["orders"]) == 1
            order_id = orders_data["orders"][0]["id"]
            
            # Step 2: Get order details
            mock_order_details = {
                "id": "order_123",
                "store_id": "store_123",
                "status": "PLACED",
                "total": 25.99,
                "customer_name": "John Doe",
                "items": [
                    {
                        "id": "item_1",
                        "name": "Pizza Margherita",
                        "quantity": 1,
                        "price": 12.99
                    },
                    {
                        "id": "item_2",
                        "name": "Coca Cola",
                        "quantity": 1,
                        "price": 2.99
                    }
                ],
                "delivery_address": "456 Customer Ave",
                "created_at": datetime.utcnow().isoformat()
            }
            mock_service_instance.get_order.return_value = mock_order_details
            
            get_response = client.get(f"/api/v1/orders/{order_id}")
            assert get_response.status_code == 200
            order_details = get_response.json()
            assert order_details["customer_name"] == "John Doe"
            assert len(order_details["items"]) == 2
            
            # Step 3: Accept order
            accept_data = {
                "estimated_ready_time": 20,
                "notes": "Order accepted"
            }
            
            mock_accepted_order = {**mock_order_details, "status": "ACCEPTED"}
            mock_service_instance.accept_order.return_value = mock_accepted_order
            
            accept_response = client.post(f"/api/v1/orders/{order_id}/accept", json=accept_data)
            assert accept_response.status_code == 200
            accepted_order = accept_response.json()
            assert accepted_order["status"] == "ACCEPTED"
            
            # Step 4: Update order status to ready
            ready_response = client.post(f"/api/v1/orders/{order_id}/ready")
            
            mock_ready_order = {**mock_accepted_order, "status": "READY_FOR_PICKUP"}
            mock_service_instance.update_order_status.return_value = mock_ready_order
            
            assert ready_response.status_code == 200
            ready_order = ready_response.json()
            assert ready_order["status"] == "READY_FOR_PICKUP"


@pytest.mark.asyncio
async def test_menu_management_flow(client, mock_uber_eats_api):
    """Test complete menu management workflow."""
    with patch('app.api.dependencies.auth.get_uber_eats_token') as mock_auth:
        mock_auth.return_value = "test_access_token"
        
        with patch('app.services.uber_eats.menus.UberEatsMenuService') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            store_id = "store_123"
            
            # Step 1: Get current menu
            mock_menu = {
                "id": "menu_123",
                "store_id": store_id,
                "categories": [
                    {
                        "id": "cat_1",
                        "name": "Pizza",
                        "items": [
                            {
                                "id": "item_1",
                                "name": "Margherita",
                                "price": 12.99,
                                "available": True
                            }
                        ]
                    }
                ]
            }
            mock_service_instance.get_menu.return_value = mock_menu
            
            get_response = client.get(f"/api/v1/menus/stores/{store_id}/menu")
            assert get_response.status_code == 200
            menu_data = get_response.json()
            assert len(menu_data["categories"]) == 1
            assert menu_data["categories"][0]["name"] == "Pizza"
            
            # Step 2: Add new menu item
            new_item_data = {
                "name": "Pepperoni Pizza",
                "description": "Classic pepperoni pizza",
                "price": 14.99,
                "category_id": "cat_1",
                "available": True
            }
            
            mock_new_item = {
                "id": "item_2",
                **new_item_data
            }
            mock_service_instance.create_item.return_value = mock_new_item
            
            create_response = client.post(f"/api/v1/menus/stores/{store_id}/menu/items", json=new_item_data)
            assert create_response.status_code == 200
            new_item = create_response.json()
            assert new_item["name"] == "Pepperoni Pizza"
            assert new_item["price"] == 14.99
            
            # Step 3: Update item availability
            item_id = new_item["id"]
            update_data = {
                "available": False,
                "price": 13.99
            }
            
            mock_updated_item = {**mock_new_item, **update_data}
            mock_service_instance.update_item.return_value = mock_updated_item
            
            update_response = client.put(f"/api/v1/menus/stores/{store_id}/menu/items/{item_id}", json=update_data)
            assert update_response.status_code == 200
            updated_item = update_response.json()
            assert updated_item["available"] is False
            assert updated_item["price"] == 13.99
            
            # Step 4: Bulk update availability
            availability_update = {
                "item_ids": ["item_1", "item_2"],
                "available": True
            }
            
            mock_service_instance.update_items_availability.return_value = True
            
            bulk_response = client.post(f"/api/v1/menus/stores/{store_id}/menu/items/availability", json=availability_update)
            assert bulk_response.status_code == 200
            bulk_result = bulk_response.json()
            assert bulk_result["success"] is True


@pytest.mark.asyncio
async def test_webhook_processing_flow(client, mock_uber_eats_api):
    """Test complete webhook processing workflow."""
    with patch('app.services.uber_eats.webhooks.UberEatsWebhookService') as mock_service:
        with patch('app.api.v1.endpoints.uber_eats.webhooks.verify_webhook_signature') as mock_verify:
            mock_verify.return_value = True
            
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.store_webhook_event.return_value = None
            
            # Step 1: Receive order webhook
            order_webhook = {
                "metadata": {
                    "event_type": "order.placed",
                    "event_id": "event_123",
                    "timestamp": datetime.utcnow().isoformat()
                },
                "data": {
                    "order_id": "order_456",
                    "store_id": "store_123",
                    "total": 25.99,
                    "customer_name": "Jane Doe"
                }
            }
            
            webhook_response = client.post(
                "/api/v1/webhooks/",
                json=order_webhook,
                headers={
                    "X-Uber-Signature": "valid_signature",
                    "X-Uber-Timestamp": "1234567890"
                }
            )
            
            assert webhook_response.status_code == 200
            webhook_data = webhook_response.json()
            assert webhook_data["received"] is True
            assert webhook_data["event_id"] == "event_123"
            
            # Step 2: List webhook events
            mock_events = [
                {
                    "id": "event_123",
                    "event_type": "order.placed",
                    "status": "processed",
                    "created_at": datetime.utcnow().isoformat(),
                    "payload": order_webhook
                }
            ]
            mock_service_instance.list_webhook_events.return_value = mock_events
            
            events_response = client.get("/api/v1/webhooks/events")
            assert events_response.status_code == 200
            events_data = events_response.json()
            assert len(events_data) == 1
            assert events_data[0]["event_type"] == "order.placed"
            
            # Step 3: Get specific webhook event
            event_id = events_data[0]["id"]
            mock_service_instance.get_webhook_event.return_value = mock_events[0]
            
            event_response = client.get(f"/api/v1/webhooks/events/{event_id}")
            assert event_response.status_code == 200
            event_data = event_response.json()
            assert event_data["event_type"] == "order.placed"
            assert event_data["status"] == "processed"


@pytest.mark.asyncio
async def test_error_handling_flow(client, mock_uber_eats_api):
    """Test error handling in API flows."""
    with patch('app.api.dependencies.auth.get_uber_eats_token') as mock_auth:
        mock_auth.return_value = "test_access_token"
        
        # Test 404 error
        with patch('app.services.uber_eats.stores.UberEatsStoreService') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.get_store.return_value = None
            
            response = client.get("/api/v1/stores/nonexistent_store")
            assert response.status_code == 404
            assert "not found" in response.json()["detail"]
        
        # Test 500 error
        with patch('app.services.uber_eats.orders.UberEatsOrderService') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.list_orders.side_effect = Exception("Database error")
            
            response = client.get("/api/v1/orders/")
            assert response.status_code == 500
            assert "Failed to fetch orders" in response.json()["detail"]
        
        # Test validation error
        invalid_store_data = {
            "name": "",  # Invalid empty name
            "address": "123 Test St"
        }
        
        with patch('app.services.uber_eats.stores.UberEatsStoreService') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            response = client.post("/api/v1/stores/", json=invalid_store_data)
            assert response.status_code == 422  # Validation error