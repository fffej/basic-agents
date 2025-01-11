from typing import Any
import asyncio
import os
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import subprocess

server = Server("shell")
current_working_directory = os.getcwd()  # Store the working directory state

PROMPTS = {
    "define": types.Prompt(
        name="define",
        description="Define a word, term or concept",
        arguments=[
            types.PromptArgument(
                name="term",
                description="The term or concepts to define",
                required=True
            )
        ]
    )
}

@server.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return list(PROMPTS.values())

@server.get_prompt()
async def get_prompt(name: str, arguments: dict[str,str] | None = None
) -> types.GetPromptResult:
    if name not in PROMPTS:
        raise ValueError(f"Prompt not found{name}")
    
    if name == "define":
        term = arguments["term"] # Assume it must exist since required is true
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="assistant",
                    content=types.TextContent(
                        type="text",
                        text=f"Provide a concise definition of {term}, and provide a real world analogy if possible."
                    )
                )
            ]
        )
    
    raise ValueError(f"Unknown prompt: {name}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="web-search",
            description="Searches the internet and retrieves the results in text format",
            inputSchema={
                "type": "object",
                "properties": {
                    "search-expression": {
                        "type": "string",
                        "description": "The text to search for on the internet"
                    }
                }
            }
        ),
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
        ),
        types.Tool(
            name="change_working_directory",
            description="Changes the working directory for subsequent shell commands",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "The directory to change to",
                    },
                }
            },
        )
    ]

def web_search(expr):
    return "done"

def run_command(command):
    """
    Run a shell command in the current working directory
    """
    # Shell=True allows passing the full command as a string
    # capture_output=True captures stdout and stderr (Python 3.7+)
    # text=True returns string instead of bytes (Python 3.7+)
    result = subprocess.run(
        command, 
        shell=True, 
        capture_output=True, 
        text=True,
        cwd=current_working_directory
    )
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
    
    global current_working_directory
    
    if name == "change_working_directory":
        new_dir = dict(arguments)["directory"]
        if not os.path.exists(new_dir):
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: Directory {new_dir} does not exist"
                )
            ]
        current_working_directory = os.path.abspath(new_dir)
        return [
            types.TextContent(
                type="text",
                text=f"Changed working directory to: {current_working_directory}"
            )
        ]
    elif name == "run-shell":
        return [
            types.TextContent(
                type="text",
                text=run_command(dict(arguments)["command"])
            )
        ]
    elif name == "web-search":
        return [
            types.TextContent(
                type="text",
                text=web_search(dict(arguments)["search-expression"])
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
