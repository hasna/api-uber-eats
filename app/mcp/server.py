"""MCP server implementation for Uber Eats API."""
from mcp.server import Server
from mcp.server.stdio import StdioServerTransport
import asyncio
import signal
import sys
from .tools import get_tools
from .handlers import handle_tool_call


def create_mcp_server():
    """Create and configure the MCP server for Uber Eats API."""
    server = Server("uber_eats-api")
    
    @server.list_tools()
    async def list_tools():
        """List all available tools."""
        return get_tools()
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Handle tool execution requests."""
        return await handle_tool_call(name, arguments)
    
    return server


async def main():
    """Main entry point for the MCP server."""
    server = create_mcp_server()
    transport = StdioServerTransport()
    
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        print("\nShutting down MCP server...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the server
    await server.run(transport)


def run():
    """Run the MCP server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
