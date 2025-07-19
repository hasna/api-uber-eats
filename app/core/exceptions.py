"""
Custom exceptions for the Uber Eats API integration
"""
from typing import Any, Dict, Optional


class UberEatsAPIException(Exception):
    """Base exception for Uber Eats API errors"""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(UberEatsAPIException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401, error_code="AUTH_ERROR", **kwargs)


class AuthorizationError(UberEatsAPIException):
    """Raised when authorization fails (insufficient permissions)"""
    
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(message, status_code=403, error_code="AUTHZ_ERROR", **kwargs)


class ResourceNotFoundError(UberEatsAPIException):
    """Raised when a requested resource is not found"""
    
    def __init__(self, resource: str, resource_id: str, **kwargs):
        message = f"{resource} with ID {resource_id} not found"
        super().__init__(message, status_code=404, error_code="NOT_FOUND", **kwargs)


class ValidationError(UberEatsAPIException):
    """Raised when validation fails"""
    
    def __init__(self, message: str = "Validation failed", errors: Optional[list] = None, **kwargs):
        details = kwargs.get("details", {})
        if errors:
            details["errors"] = errors
        kwargs["details"] = details
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR", **kwargs)


class RateLimitError(UberEatsAPIException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, retry_after: int, **kwargs):
        message = f"Rate limit exceeded. Retry after {retry_after} seconds"
        details = kwargs.get("details", {})
        details["retry_after"] = retry_after
        kwargs["details"] = details
        super().__init__(message, status_code=429, error_code="RATE_LIMIT", **kwargs)


class WebhookVerificationError(UberEatsAPIException):
    """Raised when webhook signature verification fails"""
    
    def __init__(self, message: str = "Webhook verification failed", **kwargs):
        super().__init__(message, status_code=401, error_code="WEBHOOK_VERIFICATION_FAILED", **kwargs)


class OrderTimeoutError(UberEatsAPIException):
    """Raised when order acceptance/denial times out"""
    
    def __init__(self, order_id: str, **kwargs):
        message = f"Order {order_id} timed out - must accept/deny within 11.5 minutes"
        super().__init__(message, status_code=408, error_code="ORDER_TIMEOUT", **kwargs)


class MenuSyncError(UberEatsAPIException):
    """Raised when menu synchronization fails"""
    
    def __init__(self, message: str = "Menu synchronization failed", **kwargs):
        super().__init__(message, status_code=500, error_code="MENU_SYNC_ERROR", **kwargs)


class DeliveryError(UberEatsAPIException):
    """Raised when delivery operations fail"""
    
    def __init__(self, message: str = "Delivery operation failed", **kwargs):
        super().__init__(message, status_code=500, error_code="DELIVERY_ERROR", **kwargs)


class IntegrationError(UberEatsAPIException):
    """Raised when integration setup or management fails"""
    
    def __init__(self, message: str = "Integration error", **kwargs):
        super().__init__(message, status_code=500, error_code="INTEGRATION_ERROR", **kwargs)