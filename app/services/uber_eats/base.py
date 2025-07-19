"""
Base service class for Uber Eats API integration
"""
from typing import Any, Dict, Optional
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class UberEatsBaseService:
    """Base class for all Uber Eats services"""
    
    def __init__(self, db: AsyncSession, access_token: Optional[str] = None):
        self.db = db
        self.access_token = access_token
        self.base_url = settings.UBER_EATS_BASE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(30.0),
            headers=self._get_default_headers(),
        )
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"{settings.PROJECT_NAME}/{settings.VERSION}",
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        return headers
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Make HTTP request to Uber Eats API"""
        try:
            # Merge headers
            request_headers = self._get_default_headers()
            if headers:
                request_headers.update(headers)
            
            # Log request
            logger.info(
                "uber_eats_api_request",
                method=method,
                endpoint=endpoint,
                params=params,
            )
            
            # Make request
            response = await self.client.request(
                method=method,
                url=endpoint,
                json=data,
                params=params,
                headers=request_headers,
            )
            
            # Log response
            logger.info(
                "uber_eats_api_response",
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
            )
            
            # Raise for status
            response.raise_for_status()
            
            return response
            
        except httpx.HTTPStatusError as e:
            logger.error(
                "uber_eats_api_error",
                method=method,
                endpoint=endpoint,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "uber_eats_api_exception",
                method=method,
                endpoint=endpoint,
                error=str(e),
            )
            raise
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make GET request"""
        response = await self._make_request("GET", endpoint, params=params, headers=headers)
        return response.json()
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make POST request"""
        response = await self._make_request("POST", endpoint, data=data, params=params, headers=headers)
        return response.json()
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make PUT request"""
        response = await self._make_request("PUT", endpoint, data=data, params=params, headers=headers)
        return response.json()
    
    async def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make PATCH request"""
        response = await self._make_request("PATCH", endpoint, data=data, params=params, headers=headers)
        return response.json()
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Make DELETE request"""
        response = await self._make_request("DELETE", endpoint, params=params, headers=headers)
        return response.status_code in (200, 204)
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()