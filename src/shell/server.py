from typing import Any
import asyncio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import subprocess

server = Server("shell")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="run-shell",
            description="Runs a shell command in a UNIX environment",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute",
                    },
                }
            },
        )
    ]

def run_command(command):
    # Shell=True allows passing the full command as a string
    # capture_output=True captures stdout and stderr (Python 3.7+)
    # text=True returns string instead of bytes (Python 3.7+)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handles tool execution requests.
    """
    if not arguments:
        raise ValueError("Missing arguments")
    
    
  
    if name == "run-shell":
        return [
            types.TextContent(
                type="text",
                text=run_command(dict(arguments)["command"])
            )
        ]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="shell",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

# This is needed if youd like to connect to a custom client
if __name__ == "__main__":
    asyncio.run(main())
