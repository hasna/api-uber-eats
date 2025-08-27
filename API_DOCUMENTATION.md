# Uber Eats API Documentation

## Overview

This comprehensive API provides full integration with Uber Eats for restaurant partners, including:

- **Store Management** - Complete store configuration and status management
- **Menu Management** - Full CRUD operations for menus, categories, items, and modifiers  
- **Order Management** - Real-time order processing and lifecycle management
- **Delivery Tracking** - Real-time delivery status and partner coordination
- **User Management** - Customer data management and analytics
- **Webhook Handling** - Real-time event processing and notifications
- **Reporting & Analytics** - Comprehensive business intelligence and insights

## Architecture

The API is built using:
- **FastAPI** - High-performance Python web framework
- **PostgreSQL** - Primary database for persistent data
- **Redis** - Caching and rate limiting
- **Docker** - Containerized deployment
- **Prometheus** - Metrics and monitoring
- **Structured Logging** - Request tracing and debugging

## Base URL

```
Production: https://api.uber-eats-integration.com
Development: http://localhost:8000
```

## Authentication

All API endpoints require OAuth 2.0 authentication using the Uber Eats client credentials flow.

### Getting an Access Token

```bash
POST /api/v1/oauth/token
Content-Type: application/json

{
    "grant_type": "client_credentials",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "scope": "eats.store eats.order eats.report"
}
```

### Using the Access Token

Include the access token in the Authorization header for all API requests:

```bash
Authorization: Bearer your_access_token
```

## Rate Limiting

- **Standard endpoints**: 1000 requests per hour
- **Webhook endpoints**: 10,000 requests per hour
- **Menu upload**: 100 requests per hour

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Maximum requests per hour
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Error Handling

The API uses standard HTTP status codes and returns errors in the following format:

```json
{
    "detail": "Error message",
    "error_code": "UBER_EATS_ERROR_CODE",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid or missing authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Endpoints

### Authentication

#### POST /api/v1/oauth/token
Exchange credentials for access token

**Request Body:**
```json
{
    "grant_type": "client_credentials",
    "client_id": "string",
    "client_secret": "string",
    "scope": "string"
}
```

**Response:**
```json
{
    "access_token": "string",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "string"
}
```

#### POST /api/v1/oauth/revoke
Revoke an access token

**Request Body:**
```json
{
    "token": "string",
    "token_type_hint": "access_token"
}
```

### Store Management

#### GET /api/v1/stores/
List all stores

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)
- `status`: Filter by store status (ONLINE, OFFLINE, PAUSED)

**Response:**
```json
{
    "stores": [
        {
            "id": "string",
            "name": "string",
            "address": "string",
            "phone_number": "string",
            "status": "ONLINE",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "hours": {
                "monday": {"open": "09:00", "close": "22:00"}
            }
        }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
}
```

#### GET /api/v1/stores/{store_id}
Get store details

**Response:**
```json
{
    "id": "string",
    "name": "string",
    "address": "string",
    "phone_number": "string",
    "status": "ONLINE",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "hours": {
        "monday": {"open": "09:00", "close": "22:00"}
    }
}
```

#### POST /api/v1/stores/
Create a new store

**Request Body:**
```json
{
    "name": "string",
    "address": "string",
    "phone_number": "string",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "hours": {
        "monday": {"open": "09:00", "close": "22:00"}
    }
}
```

#### PUT /api/v1/stores/{store_id}
Update store information

**Request Body:**
```json
{
    "name": "string",
    "address": "string",
    "phone_number": "string",
    "hours": {
        "monday": {"open": "09:00", "close": "22:00"}
    }
}
```

#### POST /api/v1/stores/{store_id}/status
Update store status

**Request Body:**
```json
{
    "status": "OFFLINE",
    "reason": "string"
}
```

### Menu Management

#### GET /api/v1/menus/stores/{store_id}/menu
Get complete menu for a store

**Response:**
```json
{
    "id": "string",
    "store_id": "string",
    "categories": [
        {
            "id": "string",
            "name": "string",
            "display_order": 1,
            "items": [
                {
                    "id": "string",
                    "name": "string",
                    "description": "string",
                    "price": 12.99,
                    "available": true,
                    "modifiers": []
                }
            ]
        }
    ]
}
```

#### PUT /api/v1/menus/stores/{store_id}/menu
Upload/replace complete menu

**Request Body:**
```json
{
    "menu": {
        "categories": [
            {
                "name": "string",
                "items": [
                    {
                        "name": "string",
                        "description": "string",
                        "price": 12.99,
                        "available": true
                    }
                ]
            }
        ]
    },
    "validate_only": false
}
```

#### POST /api/v1/menus/stores/{store_id}/menu/items
Create a new menu item

**Request Body:**
```json
{
    "name": "string",
    "description": "string",
    "price": 12.99,
    "category_id": "string",
    "available": true,
    "modifiers": []
}
```

#### PUT /api/v1/menus/stores/{store_id}/menu/items/{item_id}
Update menu item

**Request Body:**
```json
{
    "name": "string",
    "description": "string",
    "price": 12.99,
    "available": true
}
```

#### DELETE /api/v1/menus/stores/{store_id}/menu/items/{item_id}
Delete menu item

### Order Management

#### GET /api/v1/orders/
List orders with filtering

**Query Parameters:**
- `store_id`: Filter by store ID
- `status`: Filter by order status
- `start_date`: Start date filter (ISO format)
- `end_date`: End date filter (ISO format)
- `page`: Page number
- `page_size`: Items per page

**Response:**
```json
{
    "orders": [
        {
            "id": "string",
            "store_id": "string",
            "status": "PLACED",
            "total": 25.99,
            "customer_name": "string",
            "items": [
                {
                    "id": "string",
                    "name": "string",
                    "quantity": 1,
                    "price": 12.99
                }
            ],
            "created_at": "2024-01-01T12:00:00Z"
        }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
}
```

#### GET /api/v1/orders/{order_id}
Get order details

**Response:**
```json
{
    "id": "string",
    "store_id": "string",
    "status": "PLACED",
    "total": 25.99,
    "customer_name": "string",
    "customer_phone": "string",
    "delivery_address": "string",
    "items": [
        {
            "id": "string",
            "name": "string",
            "quantity": 1,
            "price": 12.99,
            "modifiers": []
        }
    ],
    "created_at": "2024-01-01T12:00:00Z",
    "estimated_ready_time": "2024-01-01T12:30:00Z"
}
```

#### POST /api/v1/orders/{order_id}/accept
Accept an order

**Request Body:**
```json
{
    "estimated_ready_time": 20,
    "notes": "string"
}
```

#### POST /api/v1/orders/{order_id}/deny
Deny an order

**Request Body:**
```json
{
    "reason": "ITEM_UNAVAILABLE",
    "notes": "string"
}
```

#### POST /api/v1/orders/{order_id}/cancel
Cancel an order

**Request Body:**
```json
{
    "reason": "STORE_CLOSED",
    "notes": "string"
}
```

#### POST /api/v1/orders/{order_id}/ready
Mark order as ready for pickup

### Delivery Management

#### POST /api/v1/delivery/quote
Get delivery quote

**Request Body:**
```json
{
    "pickup_address": "string",
    "delivery_address": "string",
    "items": [
        {
            "name": "string",
            "quantity": 1,
            "weight": 0.5
        }
    ]
}
```

**Response:**
```json
{
    "id": "string",
    "estimated_price": 5.99,
    "estimated_time": 30,
    "currency": "USD"
}
```

#### POST /api/v1/delivery/
Create delivery

**Request Body:**
```json
{
    "order_id": "string",
    "pickup_address": "string",
    "delivery_address": "string",
    "customer_name": "string",
    "customer_phone": "string",
    "items": []
}
```

#### GET /api/v1/delivery/{delivery_id}
Get delivery details

**Response:**
```json
{
    "id": "string",
    "order_id": "string",
    "status": "DISPATCHED",
    "courier": {
        "name": "string",
        "phone": "string",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060
        }
    },
    "estimated_arrival": "2024-01-01T13:00:00Z"
}
```

#### GET /api/v1/delivery/{delivery_id}/tracking
Get real-time tracking

**Response:**
```json
{
    "delivery_id": "string",
    "status": "EN_ROUTE",
    "courier_location": {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "last_updated": "2024-01-01T12:45:00Z"
    },
    "estimated_arrival": "2024-01-01T13:00:00Z"
}
```

### Webhook Management

#### POST /api/v1/webhooks/
Main webhook endpoint for receiving events

**Headers:**
- `X-Uber-Signature`: Webhook signature for verification
- `X-Uber-Timestamp`: Timestamp of webhook

**Request Body:**
```json
{
    "metadata": {
        "event_type": "order.placed",
        "event_id": "string",
        "timestamp": "2024-01-01T12:00:00Z"
    },
    "data": {
        "order_id": "string",
        "store_id": "string"
    }
}
```

**Response:**
```json
{
    "received": true,
    "event_id": "string"
}
```

#### GET /api/v1/webhooks/events
List webhook events

**Query Parameters:**
- `event_type`: Filter by event type
- `status`: Filter by processing status
- `start_date`: Start date filter
- `end_date`: End date filter
- `limit`: Number of events to return
- `offset`: Offset for pagination

**Response:**
```json
[
    {
        "id": "string",
        "event_type": "order.placed",
        "status": "processed",
        "created_at": "2024-01-01T12:00:00Z",
        "processed_at": "2024-01-01T12:00:01Z",
        "payload": {}
    }
]
```

#### GET /api/v1/webhooks/events/{event_id}
Get specific webhook event

#### POST /api/v1/webhooks/events/{event_id}/retry
Retry processing a failed webhook event

## Webhook Events

### Event Types

- `order.placed`: New order received
- `order.cancelled`: Order cancelled by customer
- `order.status_updated`: Order status changed
- `store.status_updated`: Store status changed
- `store.provisioned`: Store setup completed
- `fulfillment.issue`: Issue with order fulfillment
- `report.completed`: Report generation completed

### Webhook Signatures

All webhooks are signed using HMAC-SHA256. Verify the signature using:

```python
import hmac
import hashlib

def verify_signature(payload, signature, secret, timestamp):
    message = f"{timestamp}.{payload}"
    expected_signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)
```

## Data Models

### Store
```json
{
    "id": "string",
    "name": "string",
    "address": "string",
    "phone_number": "string",
    "status": "ONLINE|OFFLINE|PAUSED",
    "latitude": "number",
    "longitude": "number",
    "hours": {
        "monday": {"open": "09:00", "close": "22:00", "closed": false}
    }
}
```

### Order
```json
{
    "id": "string",
    "store_id": "string",
    "status": "PLACED|ACCEPTED|PREPARING|READY|PICKED_UP|DELIVERED|CANCELLED",
    "total": "number",
    "customer_name": "string",
    "customer_phone": "string",
    "delivery_address": "string",
    "items": [
        {
            "id": "string",
            "name": "string",
            "quantity": "number",
            "price": "number",
            "modifiers": []
        }
    ],
    "created_at": "string",
    "estimated_ready_time": "string"
}
```

### Menu Item
```json
{
    "id": "string",
    "name": "string",
    "description": "string",
    "price": "number",
    "available": "boolean",
    "category_id": "string",
    "modifiers": [
        {
            "id": "string",
            "name": "string",
            "options": [
                {
                    "id": "string",
                    "name": "string",
                    "price": "number"
                }
            ]
        }
    ]
}
```

## SDK Examples

### Python

```python
import requests

class UberEatsAPI:
    def __init__(self, client_id, client_secret, base_url="https://api.uber-eats-integration.com"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.token = None
    
    def authenticate(self):
        response = requests.post(f"{self.base_url}/api/v1/oauth/token", json={
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "eats.store eats.order"
        })
        self.token = response.json()["access_token"]
    
    def get_stores(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/api/v1/stores/", headers=headers)
        return response.json()
    
    def accept_order(self, order_id, estimated_ready_time):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"estimated_ready_time": estimated_ready_time}
        response = requests.post(
            f"{self.base_url}/api/v1/orders/{order_id}/accept",
            headers=headers,
            json=data
        )
        return response.json()

# Usage
api = UberEatsAPI("your_client_id", "your_client_secret")
api.authenticate()
stores = api.get_stores()
```

### Node.js

```javascript
const axios = require('axios');

class UberEatsAPI {
    constructor(clientId, clientSecret, baseUrl = 'https://api.uber-eats-integration.com') {
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.baseUrl = baseUrl;
        this.token = null;
    }
    
    async authenticate() {
        const response = await axios.post(`${this.baseUrl}/api/v1/oauth/token`, {
            grant_type: 'client_credentials',
            client_id: this.clientId,
            client_secret: this.clientSecret,
            scope: 'eats.store eats.order'
        });
        this.token = response.data.access_token;
    }
    
    async getStores() {
        const headers = { Authorization: `Bearer ${this.token}` };
        const response = await axios.get(`${this.baseUrl}/api/v1/stores/`, { headers });
        return response.data;
    }
    
    async acceptOrder(orderId, estimatedReadyTime) {
        const headers = { Authorization: `Bearer ${this.token}` };
        const data = { estimated_ready_time: estimatedReadyTime };
        const response = await axios.post(
            `${this.baseUrl}/api/v1/orders/${orderId}/accept`,
            data,
            { headers }
        );
        return response.data;
    }
}

// Usage
const api = new UberEatsAPI('your_client_id', 'your_client_secret');
await api.authenticate();
const stores = await api.getStores();
```

## Testing

### Sandbox Environment

The API provides a sandbox environment for testing:

- **Base URL**: `https://sandbox-api.uber-eats-integration.com`
- **Test credentials**: Contact support for test credentials
- **Mock data**: Sandbox returns realistic test data
- **Webhook testing**: Use `/api/v1/webhooks/test` to generate test events

### Test Endpoints

#### POST /api/v1/orders/stores/{store_id}/test-order
Create a test order (sandbox only)

#### POST /api/v1/webhooks/test
Send test webhook (sandbox only)

**Request Body:**
```json
{
    "webhook_type": "order.placed",
    "store_id": "string"
}
```

## Support

- **Documentation**: [https://docs.uber-eats-integration.com](https://docs.uber-eats-integration.com)
- **Support Email**: support@uber-eats-integration.com
- **Developer Portal**: [https://developer.uber-eats-integration.com](https://developer.uber-eats-integration.com)
- **Status Page**: [https://status.uber-eats-integration.com](https://status.uber-eats-integration.com)

## Changelog

### Version 1.0.0 (2024-01-01)
- Initial release
- OAuth 2.0 authentication
- Store management endpoints
- Menu management endpoints
- Order processing endpoints
- Delivery tracking endpoints
- Webhook support
- Comprehensive test coverage