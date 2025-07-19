"""Tool definitions for Uber Eats API MCP server."""
from mcp.types import Tool, ToolSchema


def get_tools() -> list[Tool]:
    """Return all available tools for Uber Eats API."""
    return [
        Tool(
            name="uber_eats_list_items",
            description="List items from Uber Eats",
            inputSchema=ToolSchema(
                type="object",
                properties={
                    "limit": {"type": "integer", "description": "Number of items to return", "default": 50},
                    "offset": {"type": "integer", "description": "Number of items to skip", "default": 0}
                }
            )
        ),
        Tool(
            name="uber_eats_get_item",
            description="Get a specific item from Uber Eats",
            inputSchema=ToolSchema(
                type="object",
                properties={
                    "item_id": {"type": "string", "description": "ID of the item to retrieve"}
                },
                required=["item_id"]
            )
        ),
        Tool(
            name="uber_eats_create_item",
            description="Create a new item in Uber Eats",
            inputSchema=ToolSchema(
                type="object",
                properties={
                    "name": {"type": "string", "description": "Name of the item"},
                    "data": {"type": "object", "description": "Additional data for the item"}
                },
                required=["name"]
            )
        ),
        Tool(
            name="uber_eats_update_item",
            description="Update an existing item in Uber Eats",
            inputSchema=ToolSchema(
                type="object",
                properties={
                    "item_id": {"type": "string", "description": "ID of the item to update"},
                    "data": {"type": "object", "description": "Data to update"}
                },
                required=["item_id", "data"]
            )
        ),
        Tool(
            name="uber_eats_delete_item",
            description="Delete an item from Uber Eats",
            inputSchema=ToolSchema(
                type="object",
                properties={
                    "item_id": {"type": "string", "description": "ID of the item to delete"}
                },
                required=["item_id"]
            )
        )
    ]
