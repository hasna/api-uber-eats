# Uber Eats API Integration

A comprehensive FastAPI implementation of the Uber Eats Marketplace APIs, providing complete integration with stores, menus, orders, webhooks, delivery, and reporting functionality.

## Features

- **OAuth2 Authentication**: Full implementation of Uber Eats OAuth2 flow
- **Store Management**: Create, update, and manage stores on Uber Eats platform
- **Menu Synchronization**: Complete menu management with items, categories, and modifiers
- **Order Processing**: Real-time order handling with accept/deny/cancel functionality
- **Webhook Integration**: Secure webhook handling for all Uber Eats events
- **Delivery Management**: Track and manage deliveries, including multi-courier support
- **Comprehensive Reporting**: Sales, financial, and performance analytics
- **Rate Limiting**: Built-in rate limiting to comply with API limits
- **Error Handling**: Robust error handling with detailed error responses
- **Logging & Metrics**: Structured logging and Prometheus metrics

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Uber Eats API credentials (Client ID and Client Secret)
- Python 3.11+ (for local development)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd api-uber-eats
```

2. Create a `.env` file:
```env
# Uber Eats API Configuration
UBER_EATS_CLIENT_ID=your_client_id
UBER_EATS_CLIENT_SECRET=your_client_secret
UBER_EATS_WEBHOOK_SECRET=your_webhook_secret
UBER_EATS_SANDBOX_MODE=true

# Database Configuration
POSTGRES_SERVER=postgres
POSTGRES_USER=uber_eats_user
POSTGRES_PASSWORD=uber_eats_pass
POSTGRES_DB=uber_eats_db

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-here

# Environment
ENVIRONMENT=development
DEBUG=true
```

3. Start the services:
```bash
docker-compose up -d
```

4. Access the API documentation:
- API Docs: http://localhost:8065/api/v1/docs
- ReDoc: http://localhost:8065/api/v1/redoc

## API Endpoints

### Authentication

#### OAuth2 Flow
- `GET /api/v1/uber-eats/oauth/authorize` - Initiate OAuth2 authorization
- `POST /api/v1/uber-eats/oauth/token` - Exchange code for access token
- `POST /api/v1/uber-eats/oauth/revoke` - Revoke access token
- `POST /api/v1/uber-eats/oauth/introspect` - Introspect token details

### Store Management

- `GET /api/v1/uber-eats/stores` - List all stores
- `GET /api/v1/uber-eats/stores/{store_id}` - Get store details
- `POST /api/v1/uber-eats/stores` - Create new store
- `PUT /api/v1/uber-eats/stores/{store_id}` - Update store
- `POST /api/v1/uber-eats/stores/{store_id}/status` - Update store status
- `GET /api/v1/uber-eats/stores/{store_id}/pos-data` - Get POS data
- `PUT /api/v1/uber-eats/stores/{store_id}/pos-data` - Update POS data

### Menu Management

- `GET /api/v1/uber-eats/stores/{store_id}/menu` - Get complete menu
- `PUT /api/v1/uber-eats/stores/{store_id}/menu` - Upload/replace menu
- `POST /api/v1/uber-eats/stores/{store_id}/menu/validate` - Validate menu
- `GET /api/v1/uber-eats/stores/{store_id}/menu/items` - List menu items
- `POST /api/v1/uber-eats/stores/{store_id}/menu/items` - Create menu item
- `PUT /api/v1/uber-eats/stores/{store_id}/menu/items/{item_id}` - Update item
- `DELETE /api/v1/uber-eats/stores/{store_id}/menu/items/{item_id}` - Delete item
- `POST /api/v1/uber-eats/stores/{store_id}/menu/items/availability` - Bulk update availability

### Order Management

- `GET /api/v1/uber-eats/orders` - List orders with filters
- `GET /api/v1/uber-eats/orders/{order_id}` - Get order details
- `POST /api/v1/uber-eats/orders/{order_id}/accept` - Accept order
- `POST /api/v1/uber-eats/orders/{order_id}/deny` - Deny order
- `POST /api/v1/uber-eats/orders/{order_id}/cancel` - Cancel order
- `POST /api/v1/uber-eats/orders/{order_id}/status` - Update order status
- `POST /api/v1/uber-eats/orders/{order_id}/ready` - Mark order ready
- `POST /api/v1/uber-eats/orders/{order_id}/resolve-fulfillment-issue` - Handle fulfillment issues

### Webhook Handling

- `POST /api/v1/uber-eats/webhooks` - Main webhook endpoint
- `GET /api/v1/uber-eats/webhooks/events` - List webhook events
- `GET /api/v1/uber-eats/webhooks/events/{event_id}` - Get event details
- `POST /api/v1/uber-eats/webhooks/events/{event_id}/retry` - Retry failed webhook

### Delivery Management

- `POST /api/v1/uber-eats/delivery/quote` - Get delivery quote
- `POST /api/v1/uber-eats/delivery` - Create delivery
- `GET /api/v1/uber-eats/delivery/{delivery_id}` - Get delivery details
- `GET /api/v1/uber-eats/delivery/{delivery_id}/tracking` - Get real-time tracking
- `POST /api/v1/uber-eats/delivery/{delivery_id}/cancel` - Cancel delivery
- `POST /api/v1/uber-eats/delivery/multiple-courier` - Request multiple couriers

### Reports & Analytics

- `POST /api/v1/uber-eats/reports/generate` - Generate report
- `GET /api/v1/uber-eats/reports` - List reports
- `GET /api/v1/uber-eats/reports/{report_id}` - Get report details
- `GET /api/v1/uber-eats/reports/{report_id}/download` - Download report
- `GET /api/v1/uber-eats/reports/sales/summary` - Get sales summary
- `GET /api/v1/uber-eats/reports/items/performance` - Get item performance
- `GET /api/v1/uber-eats/reports/financial/summary` - Get financial summary

## Webhook Events

The API handles the following webhook events:

- **Order Events**:
  - `orders.notification` - New order received
  - `orders.cancel` - Order cancelled
  - `orders.status_update` - Order status changed
  
- **Store Events**:
  - `store.status` - Store status changed
  - `store.provisioned` - Store provisioned
  - `store.deprovisioned` - Store deprovisioned
  
- **Other Events**:
  - `orders.scheduled_notification` - Scheduled order notification
  - `orders.fulfillment_issue` - Fulfillment issue reported
  - `report.success` / `report.failure` - Report generation completed

## Authentication

All API endpoints require authentication using OAuth2 Bearer tokens. Include the access token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

### Obtaining Access Token

1. **Authorization Code Flow** (for user authentication):
   ```bash
   # 1. Redirect user to authorization URL
   GET /api/v1/uber-eats/oauth/authorize?client_id=<client_id>&redirect_uri=<redirect_uri>&scope=eats.store+eats.order
   
   # 2. Exchange authorization code for token
   POST /api/v1/uber-eats/oauth/token
   {
     "grant_type": "authorization_code",
     "code": "<authorization_code>",
     "client_id": "<client_id>",
     "client_secret": "<client_secret>",
     "redirect_uri": "<redirect_uri>"
   }
   ```

2. **Client Credentials Flow** (for server-to-server):
   ```bash
   POST /api/v1/uber-eats/oauth/token
   {
     "grant_type": "client_credentials",
     "client_id": "<client_id>",
     "client_secret": "<client_secret>",
     "scope": "eats.store eats.order eats.report"
   }
   ```

## Rate Limiting

The API implements rate limiting to comply with Uber Eats API limits:
- 60 requests per minute per client
- 3,600 requests per hour per client

Rate limit headers are included in all responses:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1634567890
```

## Error Handling

The API returns structured error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "errors": [
        {
          "field": "price",
          "message": "Price must be greater than 0"
        }
      ]
    }
  }
}
```

Common error codes:
- `AUTH_ERROR` - Authentication failed
- `AUTHZ_ERROR` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `VALIDATION_ERROR` - Request validation failed
- `RATE_LIMIT` - Rate limit exceeded
- `ORDER_TIMEOUT` - Order acceptance timeout

## Development

### Running Tests

```bash
# Run all tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Run specific test file
docker-compose run --rm api pytest tests/test_stores.py

# Run with coverage
docker-compose run --rm api pytest --cov=app --cov-report=html
```

### Database Migrations

```bash
# Create a new migration
docker-compose run --rm api alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose run --rm api alembic upgrade head

# Rollback migration
docker-compose run --rm api alembic downgrade -1
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# Format code
black app tests
isort app tests

# Run linting
flake8 app tests
mypy app
```

## Deployment

### Using Docker

```bash
# Build production image
docker build -t api-uber-eats:latest .

# Run with environment variables
docker run -d \
  --name api-uber-eats \
  -p 8000:8000 \
  --env-file .env \
  api-uber-eats:latest
```

### Environment Variables

Key environment variables for production:

```env
# Required
UBER_EATS_CLIENT_ID=<client_id>
UBER_EATS_CLIENT_SECRET=<client_secret>
UBER_EATS_WEBHOOK_SECRET=<webhook_secret>
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
SECRET_KEY=<secure-random-key>

# Optional
UBER_EATS_SANDBOX_MODE=false
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=3600
SENTRY_DSN=<sentry-dsn>
```

## Monitoring

### Health Checks

- `/health` - Basic health check
- `/api/v1/health/ready` - Readiness check (includes dependencies)
- `/api/v1/health/live` - Liveness check

### Metrics

Prometheus metrics are available at `/metrics`:
- Request counts by endpoint and status
- Request duration histograms
- Active request gauge
- Error counts

### Logging

Structured JSON logs include:
- Request ID for tracing
- User/client identification
- Request/response details
- Error stack traces
- Performance metrics

## Architecture

```
api-uber-eats/
├── app/
│   ├── api/              # API endpoints
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── app/      # Internal endpoints
│   │           └── uber_eats/  # Uber Eats endpoints
│   ├── core/             # Core functionality
│   │   ├── config.py     # Configuration
│   │   └── exceptions.py # Custom exceptions
│   ├── db/               # Database
│   │   ├── models/       # SQLAlchemy models
│   │   └── repositories/ # Data access layer
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   │   └── uber_eats/    # Uber Eats services
│   ├── middleware/       # Custom middleware
│   └── utils/            # Utilities
├── tests/                # Test suite
├── docker-compose.yml    # Docker services
├── Dockerfile           # Container image
└── requirements.txt     # Dependencies
```

## Support

For issues or questions:
1. Check the [API documentation](http://localhost:8065/api/v1/docs)
2. Review [Uber Eats official docs](https://developer.uber.com/docs/eats/introduction)
3. Check the logs: `docker-compose logs -f api`

## License

Copyright © 2025 Hasna. All rights reserved.
## MCP (Model Context Protocol) Integration

The API includes an MCP server that exposes Uber Eats functionality as tools for AI assistants.

Available MCP tools:
- `uber_eats_list_items` - List items
- `uber_eats_get_item` - Get specific item
- `uber_eats_create_item` - Create new item
- `uber_eats_update_item` - Update existing item
- `uber_eats_delete_item` - Delete item

To start the MCP server:
```bash
# Using CLI
python cli.py mcp

# Using Docker
docker-compose up mcp
```

Environment variables:
- `UBER_EATS_API_KEY` - Your Uber Eats API key
- `UBER_EATS_BASE_URL` - API base URL (defaults to https://api.uber.com/eats)
