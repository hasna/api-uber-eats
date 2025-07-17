"""
Base schemas for common data structures
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field, ConfigDict


T = TypeVar("T")


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = Field(default=True, description="Indicates if the request was successful")
    message: Optional[str] = Field(default=None, description="Optional message")
    errors: Optional[List[Dict[str, Any]]] = Field(default=None, description="List of errors if any")
    
    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of items per page")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model"""
    items: List[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")
    
    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class UberEatsError(BaseModel):
    """Uber Eats API error response"""
    code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class UberEatsResponse(BaseModel):
    """Standard Uber Eats API response wrapper"""
    status: str = Field(description="Response status")
    data: Optional[Any] = Field(default=None, description="Response data")
    error: Optional[UberEatsError] = Field(default=None, description="Error information if any")
    
    model_config = ConfigDict(from_attributes=True)