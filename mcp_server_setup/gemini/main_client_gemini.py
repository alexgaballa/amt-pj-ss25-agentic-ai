import asyncio
from dotenv import load_dotenv
from mcp_server_setup.gemini.langchain_mcp_client import MCPGoogleGenAIClient


async def main():
    """Main entry point for the client."""
    client = MCPGoogleGenAIClient()
    await client.connect_to_server("server.py")

    # Example query
    query = "Was ist die Summe aus 150 und 37?"
    print(f"\nQuery: {query}")

    response = await client.process_query(query)
    print(f"\nResponse: {response}")

if __name__ == "__main__":
    asyncio.run(main())