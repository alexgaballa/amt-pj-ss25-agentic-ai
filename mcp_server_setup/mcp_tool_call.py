import json
import asyncio
from langchain_mcp_adapters.client import stdio_client, ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from typing import List, Optional

async def get_mcp_tools_for_agent(server_params, allowed_tool_names=None):
    """
    Connects to the MCP server, loads MCP tools, and returns a filtered list of them
    for use with a React agent.

    Args:
        server_params (dict): Parameters for connecting to the MCP server (e.g., host, port).
        llm: The LLM instance (though not directly used for tool loading, kept for consistency).
        allowed_tool_names (list, optional): A list of tool names (strings) to allow.
                                            If None or empty, all tools will be returned.

    Returns:
        list: A list of MCP tool objects.
    """
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()  # Initialize MCP session

            # Load all MCP tools
            all_tools = await load_mcp_tools(session)

            if allowed_tool_names:
                # Filter the tools based on the allowed_tool_names list
                filtered_tools = [
                    tool for tool in all_tools if tool.name in allowed_tool_names
                ]
                print(f"Loaded {len(filtered_tools)} tools: {[t.name for t in filtered_tools]}")
                return filtered_tools
            else:
                # If no specific names are provided, return all tools
                print(f"Loaded all {len(all_tools)} tools: {[t.name for t in all_tools]}")
                return all_tools