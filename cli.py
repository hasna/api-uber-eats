#!/usr/bin/env python3
"""CLI for Uber Eats API."""
import typer

app = typer.Typer(help="Uber Eats API CLI")


@app.command()
def mcp():
    """Start the MCP server for Uber Eats API."""
    from app.mcp.server import run
    run()


@app.command()
def health():
    """Check API health status."""
    import requests
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            typer.echo("API is healthy")
        else:
            typer.echo(f"API health check failed: {response.status_code}")
    except Exception as e:
        typer.echo(f"Failed to connect to API: {e}")


if __name__ == "__main__":
    app()
