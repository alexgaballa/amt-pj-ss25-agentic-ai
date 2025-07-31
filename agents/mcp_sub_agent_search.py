from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
import sys
import asyncio

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp_server_setup.mcp_tool_loader import get_mcp_tools

load_dotenv()

async def run_search_agent(user_query: str, context: dict = {}, verbose: bool = True) -> str:
    """
    Sub-agent responsible for retrieving and returning information via Gemini.
    Uses LangChain agent to search Wikipedia, select relevant pages, and retrieve cleaned content.
    
    Args:
        user_query: The search query from the user
        context: Additional context that might help with the search
        verbose: Whether to show the conversation flow
        
    Returns:
        A string containing the cleaned content from the selected Wikipedia page
    """
    
    # Load tools directly without global state
    tools_to_load = [
        "search_wikipedia_tool",
        "get_wikipedia_content_tool", 
        "get_page_sections_tool",
        "get_section_content_tool",
        "get_multiple_sections_content_tool"
    ]
    
    try:
        # Load MCP tools - this should return tools that work directly with LangGraph
        tools = await get_mcp_tools(tools_to_load)
        
        # Initialize model WITHOUT memory parameter to avoid conflicts
        model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
        
        # Create agent with tools - let LangGraph handle memory internally
        agent_executor = create_react_agent(model, tools)
        
        prompt_text = f"""
        You are a research assistant that can search for information on Wikipedia.
        
        TASK: 
        1. Search Wikipedia for information about: "{user_query}", use keywords.
        2. Review the search results and select the MOST relevant article by its page ID
        3. Use the get_page_sections_tool with the selected page ID to identify relevant sections of the article
        4. Identify the most relevant sections for answering the query (always include section '0' which is the introduction)
        5. Use get_multiple_sections_content_tool to retrieve all relevant sections in a single call by passing the page ID and a list of section indices
        6. Based on the retrieved section contents, formulate a comprehensive answer to the user's query
        
        Use the tools available to you in this sequence. Make your decision about which article and sections 
        to select by evaluating their relevance to the query. Be selective and strategic about which sections you retrieve
        to get the most pertinent information. Using get_multiple_sections_content_tool is more efficient than calling 
        get_section_content_tool multiple times.
        
        Available tools:
        - `search_wikipedia_tool`: Search Wikipedia for articles related to the query
        - `get_wikipedia_content_tool`: Retrieve the full content of a Wikipedia page by its ID
        - `get_page_sections_tool`: Get the sections of a Wikipedia page by its ID
        - `get_section_content_tool`: Get the content of a specific section of a Wikipedia page
        - `get_multiple_sections_content_tool`: Get the content of multiple sections of a Wikipedia page by its ID and section indices

        - Hint:
        -- If a query is about a specific date or event, try to narrow down the topic based on location or time and then go through the content of the most relevant section within that page.
        For example if the query is about a specific event in Berlin, you might want to focus on the 'History' section of the Berlin Wikipedia page. Use this logic for other query topics as well. Take your time to reason.
        -- If the query asks for a section of a Wikipedia page, retrieve the section content directly using the `get_section_content_tool` or `get_multiple_sections_content_tool` with the appropriate section index. Return the text content as it is written on wikipedia.

        Additional context: {context}
        """
        
        if verbose:
            # Stream and display the entire conversation
            print("\n=== AGENT CONVERSATION ===")
            final_result = None
            
            async for step in agent_executor.astream(
                {"messages": [HumanMessage(content=prompt_text)]},
                stream_mode="values",
            ):
                if "messages" in step and step["messages"]:
                    # Print each message in the conversation
                    step["messages"][-1].pretty_print()
                    # Keep track of the final output
                    final_result = step["messages"][-1].content
            
            print("=== END OF CONVERSATION ===\n")
            return final_result if final_result else "No results found."
        else:
            # Just get the final result without showing the conversation
            result = await agent_executor.ainvoke({"messages": [HumanMessage(content=prompt_text)]})
            if "messages" in result and result["messages"]:
                return result["messages"][-1].content
            return "No results found."
            
    except Exception as e:
        return f"Error running search agent: {str(e)}"

# Synchronous wrapper for compatibility with non-async callers
def run_search_agent_sync(user_query: str, context: dict = {}, verbose: bool = True) -> str:
    """Synchronous wrapper for the async search agent."""
    return asyncio.run(run_search_agent(user_query, context, verbose))

if __name__ == "__main__":
    test_queries = [
        "The exact first part of the Economy section on the Berlin wikipedia page!",
        "Berlin wikipedia page Economy section first part", 
        "Please provide me with the exact first part of the Economy section on the Berlin wikipedia page. Cite it in your answer."
    ]

    query = test_queries[0]

    async def run():
        result = await run_search_agent(
            user_query=query,
            context={"source_preference": "Always use Wikipedia as your primary source"},
            verbose=True
        )
        print("\nSearch agent result:")
        print(result)

    asyncio.run(run())