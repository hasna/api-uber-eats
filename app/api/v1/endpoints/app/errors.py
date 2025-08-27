"""
Error handling endpoints and utilities
"""
from typing import Any, Dict
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings
from app.schemas.base import BaseResponse

logger = structlog.get_logger()

router = APIRouter()


class UberEatsAPIException(Exception):
    """Custom exception for Uber Eats API errors"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Dict[str, Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(UberEatsAPIException):
    """Validation error"""
    
    def __init__(
        self,
        message: str,
        field: str = None,
        details: Dict[str, Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details or {},
        )
        if field:
            self.details["field"] = field


class AuthenticationError(UberEatsAPIException):
    """Authentication error"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Dict[str, Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details or {},
        )


class AuthorizationError(UberEatsAPIException):
    """Authorization error"""
    
    def __init__(
        self,
        message: str = "Insufficient permissions",
        required_scope: str = None,
        details: Dict[str, Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details or {},
        )
        if required_scope:
            self.details["required_scope"] = required_scope


class NotFoundError(UberEatsAPIException):
    """Resource not found error"""
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: str = None,
        resource_id: str = None,
        details: Dict[str, Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
            details=details or {},
        )
        if resource_type:
            self.details["resource_type"] = resource_type
        if resource_id:
            self.details["resource_id"] = resource_id


class RateLimitError(UberEatsAPIException):
    """Rate limit exceeded error"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int = None,
        details: Dict[str, Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details or {},
        )
        if retry_after:
            self.details["retry_after"] = retry_after


class ExternalServiceError(UberEatsAPIException):
    """External service error (e.g., Uber Eats API)"""
    
    def __init__(
        self,
        message: str = "External service error",
        service: str = "uber_eats",
        upstream_status: int = None,
        details: Dict[str, Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details or {},
        )
        self.details["service"] = service
        if upstream_status:
            self.details["upstream_status"] = upstream_status


async def uber_eats_api_exception_handler(
    request: Request, 
    exc: UberEatsAPIException
) -> JSONResponse:
    """Handle custom API exceptions"""
    logger.error(
        "API exception occurred",
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
        path=request.url.path,
        method=request.method,
    )
    
    response = BaseResponse(
        success=False,
        message=exc.message,
        errors=[{
            "code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        }]
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(),
    )


async def http_exception_handler(
    request: Request, 
    exc: HTTPException
) -> JSONResponse:
    """Handle FastAPI HTTP exceptions"""
    logger.error(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
    )
    
    response = BaseResponse(
        success=False,
        message=str(exc.detail),
        errors=[{
            "code": "HTTP_ERROR",
            "message": str(exc.detail),
            "details": {"status_code": exc.status_code},
        }]
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(),
    )


async def validation_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """Handle Pydantic validation exceptions"""
    from pydantic import ValidationError as PydanticValidationError
    
    if isinstance(exc, PydanticValidationError):
        logger.error(
            "Validation exception occurred",
            errors=exc.errors(),
            path=request.url.path,
            method=request.method,
        )
        
        errors = []
        for error in exc.errors():
            field = ".".join(str(x) for x in error["loc"])
            errors.append({
                "code": "VALIDATION_ERROR",
                "message": error["msg"],
                "details": {
                    "field": field,
                    "type": error["type"],
                    "input": error.get("input"),
                }
            })
        
        response = BaseResponse(
            success=False,
            message="Validation error",
            errors=errors,
        )
        
        return JSONResponse(
            status_code=422,
            content=response.model_dump(),
        )
    
    # Fallback for other exceptions
    return await general_exception_handler(request, exc)


async def general_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """Handle all other exceptions"""
    logger.error(
        "Unhandled exception occurred",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )
    
    # Don't expose internal errors in production
    if settings.ENVIRONMENT == "production":
        message = "Internal server error"
        details = {}
    else:
        message = str(exc)
        details = {
            "error_type": type(exc).__name__,
            "traceback": None,  # Could add traceback in development
        }
    
    response = BaseResponse(
        success=False,
        message=message,
        errors=[{
            "code": "INTERNAL_ERROR",
            "message": message,
            "details": details,
        }]
    )
    
    return JSONResponse(
        status_code=500,
        content=response.model_dump(),
    )


# Error endpoint for testing
@router.get("/test-error", include_in_schema=False)
async def test_error():
    """Test error handling (development only)"""
    if settings.ENVIRONMENT == "production":
        raise HTTPException(status_code=404, detail="Not found")
    
    raise UberEatsAPIException(
        message="This is a test error",
        status_code=500,
        error_code="TEST_ERROR",
        details={"test": True}
    )