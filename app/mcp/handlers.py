"""Handler implementations for Uber Eats API MCP tools."""
import os
import httpx
from typing import Dict, Any


class UberEatsAPIClient:
    """Client for interacting with Uber Eats API."""
    
    def __init__(self):
        self.api_key = os.getenv("UBER_EATS_API_KEY", "")
        self.base_url = os.getenv("UBER_EATS_BASE_URL", "https://api.uber.com/eats")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make an HTTP request to Uber Eats API."""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()


async def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    """Handle tool calls and return results."""
    client = UberEatsAPIClient()
    
    try:
        if tool_name == "uber_eats_list_items":
            limit = arguments.get("limit", 50)
            offset = arguments.get("offset", 0)
            result = await client.make_request("GET", f"/items?limit={limit}&offset={offset}")
            return {
                "success": True,
                "items": result.get("items", []),
                "total": result.get("total", 0)
            }
        
        elif tool_name == "uber_eats_get_item":
            item_id = arguments["item_id"]
            result = await client.make_request("GET", f"/items/{item_id}")
            return {
                "success": True,
                "item": result
            }
        
        elif tool_name == "uber_eats_create_item":
            data = {
                "name": arguments["name"],
                **arguments.get("data", {})
            }
            result = await client.make_request("POST", "/items", data)
            return {
                "success": True,
                "item_id": result.get("id"),
                "message": f"Item created successfully"
            }
        
        elif tool_name == "uber_eats_update_item":
            item_id = arguments["item_id"]
            data = arguments["data"]
            result = await client.make_request("PUT", f"/items/{item_id}", data)
            return {
                "success": True,
                "message": f"Item {item_id} updated successfully"
            }
        
        elif tool_name == "uber_eats_delete_item":
            item_id = arguments["item_id"]
            await client.make_request("DELETE", f"/items/{item_id}")
            return {
                "success": True,
                "message": f"Item {item_id} deleted successfully"
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
    
    except httpx.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }
