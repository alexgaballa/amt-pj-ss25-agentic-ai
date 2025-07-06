import sys
import os
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

# ⬇️ Projektpfad einfügen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp_server_setup.mcp_tool_loader import get_mcp_tools

async def test():
    tools = await get_mcp_tools(["call_search_agent"])
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    agent = create_react_agent(model, tools)

    result = await agent.ainvoke({"messages": "What is otto von guerickes birthday regarding wiikipedia?"})
    print(result)

if __name__ == "__main__":
    asyncio.run(test())
