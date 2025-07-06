# from mcp_server_setup.mcp_client import client
from mcp_server_setup.mcp_client import client

# asynchroneous function to get (subset of )MCP tools
async def get_mcp_tools(allowed_tool_names: list[str]):
    """
    Get a subset of MCP tools from the MCP server based on allowed tool names.

    Args:
        allowed_tool_names: List of tool names (str) to include.

    Returns:
        List of MCP tools matching the given names.
    """
    all_tools = await client.get_tools()

    filtered_tools = [tool for tool in all_tools if tool.name in allowed_tool_names]
    
    # print(f"MCP Tools loaded. Returning {len(filtered_tools)} of {len(all_tools)} tools.")
    return filtered_tools