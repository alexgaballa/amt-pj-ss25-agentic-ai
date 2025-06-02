from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

# Create a MCP server instance
mcp = FastMCP(
    name = "Calculator",
    host = "0.0.0.0",
    port = 8050,
)

# add a simple calculator function
@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Add two numbers together.
    """
    return a + b

# to run the server --> mcp dev server.py
if __name__ == "__main__":
    transport = "stdio"
    # stdio for basic input/output streams on the same machine
    if transport == "stdio":
        print("Running in stdio mode")
        mcp.run(transport= "stdio")
    # remote connection across networks
    elif transport == "sse":
        print("Running in sse mode")
        mcp.run(transport= "sse")
    else:
        raise ValueError("Invalid transport mode. Use 'stdio' or 'sse'.")