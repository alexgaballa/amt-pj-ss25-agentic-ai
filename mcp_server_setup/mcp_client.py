from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient

mcp_path = Path(__file__).parent / "mcp_tools_server.py"

client = MultiServerMCPClient({
    "MCP-Server-Tools": {
        "command": "python",
        "args": [str(mcp_path)],
        "transport": "stdio",
    }
})
