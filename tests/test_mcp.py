"""Tests for MCP implementation."""
import pytest
from app.mcp.tools import get_tools
from app.mcp.handlers import handle_tool_call


def test_tool_definitions():
    """Test that tools are properly defined."""
    tools = get_tools()
    assert len(tools) > 0
    
    # Check that all tools have required fields
    for tool in tools:
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, 'inputSchema')
        assert tool.inputSchema.type == "object"
        assert hasattr(tool.inputSchema, 'properties')


def test_tool_names():
    """Test that all tool names follow the expected pattern."""
    tools = get_tools()
    tool_names = [tool.name for tool in tools]
    
    expected_prefixes = ["uber_eats_"]
    for name in tool_names:
        assert any(name.startswith(prefix) for prefix in expected_prefixes)


@pytest.mark.asyncio
async def test_unknown_tool_handler():
    """Test handling of unknown tool names."""
    result = await handle_tool_call("unknown_tool", {})
    assert result["success"] is False
    assert "Unknown tool" in result["error"]
