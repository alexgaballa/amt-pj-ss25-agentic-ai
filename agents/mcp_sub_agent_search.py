from xmlrpc import client
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from mcp_server_setup.mcp_tool_loader import get_mcp_tools
import asyncio

load_dotenv()

# Create the agent executor with the LLM and tools
tools = asyncio.run(get_mcp_tools([
    "search_wikipedia_tool",
    "get_wikipedia_content_tool",
    "get_page_sections_tool",
    "get_section_content_tool",
    "get_multiple_sections_content_tool"
]))

memory = MemorySaver()
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
 
# Bind the tools to the model
#model_with_tools = model.bind_tools(tools)

# Ensure tools are passed correctly to the agent
agent_executor = create_react_agent(model, tools)

# for step in agent_executor.stream(
#     {"messages": [HumanMessage(content="How many people live in cairo according?")]},
#     stream_mode="values",
# ):
#     step["messages"][-1].pretty_print()

# # Initialize the agent with the tools, making sure to use ReAct (STRUCTURED_CHAT with Gemini works well)
# agent_executor = initialize_agent(
#     tools=tools,
#     llm=llm,
#     agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True,
#     handle_parsing_errors=True,
# )

def run_search_agent(user_query: str, context: dict = {}, verbose: bool = True) -> str:
    """
    Sub-agent responsible for retrieving and returning information via Gemini.
    Uses LangChain agent to search Wikipedia, select relevant pages, and retrieve cleaned content.
    
    Args:
        user_query: The search query from the user
        context: Additional context that might help with the search
        
    Returns:
        A string containing the cleaned content from the selected Wikipedia page
    """    # Prepare prompt for the agent
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
    
    try:
        if verbose:
            # Stream and display the entire conversation
            print("\n=== AGENT CONVERSATION ===")
            final_result = None
            
            for step in agent_executor.stream(
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
            result = agent_executor.invoke({"messages": [HumanMessage(content=prompt_text)]})
            if "messages" in result and result["messages"]:
                return result["messages"][-1].content
            return "No results found."
    except Exception as e:
        return f"Error running search agent: {str(e)}"

if __name__ == "__main__":
    # This will only run when the file is executed directly, not when imported
    result = run_search_agent(
        # user_query="Please provide me with the exact first part of the Economy section on the Berlin wikipedia page. Cite it in your answer.",
        #user_query="the exact first part of the Economy section on the Berlin wikipedia page.",
        user_query="the exact first part of the Economy section on the Berlin wikipedia page!",
        # user_query="Berlin wikipedia page Economy section first part",
        context={"source_preference": "Always use Wikipedia as your primary source"},
        verbose=True  # Set to True to see the entire conversation
    )
    print("\nSearch agent result:")
    print(result)