from mcp.server.fastmcp import FastMCP
import requests

# Create a MCP server instance
mcp = FastMCP(
    name = "MCP Server",
    host = "0.0.0.0",
    port = 8050,
)

@mcp.tool()
def resolve_did(did: str) -> str:
    """
    Resolves a DID and returns only the public key (Base58).
    """
    url = f"http://localhost:8080/1.0/identifiers/{did}"
    response = requests.get(url)
    data = response.json()

    # Zugriff auf den ersten publicKey in der Liste der verificationMethod
    try:
        return data["didDocument"]["verificationMethod"][0]["publicKeyBase58"]
    except (KeyError, IndexError):
        return "Public key not found"
    
@mcp.tool()
def authenticate_peer(controller: str, token: str) -> str:
    """
    Placeholder peer‐authentication mcp.tool.
    TODO: replace with real ACL/OAuth check returning True/False.
    """
    return "MOCK_AUTHENTICATE_PEER"

@mcp.tool()
def issue_vc(credential_subject: dict, issuer_key: str) -> str:
    """
    Placeholder VC‐issuer mcp.tool.
    TODO: replace with call returning a full VC dict.
    """
    return "MOCK_ISSUE_VC"

@mcp.tool()
def verify_vc(vc: dict) -> str:
    """
    Placeholder VC‐verification mcp.tool.
    TODO: replace with cryptographic proof verification returning True/False.
    """
    return "MOCK_VERIFY_VC"

@mcp.tool()
def store_wallet(vc: dict, wallet_id: str) -> str:
    """
    Placeholder Wallet‐storage mcp.tool.
    TODO: replace with database or wallet‐API integration.
    """
    return "MOCK_STORE_WALLET"

# run the server (do it from client code for prototype, not here)
if __name__ == "__main__":
    transport = "sse"
    # # stdio for basic input/output streams on the same machine
    if transport == "stdio":
     print("Running in stdio mode")
    # mcp.run(transport= "stdio")
    # remote connection across networks
    elif transport == "sse":
        print("Running in sse mode")
        mcp.run(transport= "sse")
    else:
         raise ValueError("Invalid transport mode. Use 'stdio' or 'sse'.")
    
# To run the server:
# uv run server.py or python server.py
# mcp dev server.py
# """