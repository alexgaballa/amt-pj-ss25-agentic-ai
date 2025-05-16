from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from tools.tool_wrappers import search_wikipedia_tool, get_wikipedia_content_tool, clean_page_html_tool
# from langchain.agents import initialize_agent
# from utils.mcp_protocol import format_mcp_protocol

load_dotenv()

# Create the agent executor with the LLM and tools
tools = [search_wikipedia_tool, get_wikipedia_content_tool, clean_page_html_tool]
memory = MemorySaver()
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7, memory=memory)
 
# Bind the tools to the model
#model_with_tools = model.bind_tools(tools)

# Ensure tools are passed correctly to the agent
agent_executor = create_react_agent(model, tools)

for step in agent_executor.stream(
    {"messages": [HumanMessage(content="whats the population of cairo according to wikipedia?")]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()

"""# Initialize the agent with the tools, making sure to use ReAct (STRUCTURED_CHAT with Gemini works well)
agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
)"""

def run_search_agent(user_query: str, context: dict = {}) -> str:
    """
    Sub-agent responsible for retrieving and returning information via Gemini.
    Uses LangChain agent to search Wikipedia, select relevant pages, and retrieve cleaned content.
    
    Args:
        user_query: The search query from the user
        context: Additional context that might help with the search
        
    Returns:
        A string containing the cleaned content from the selected Wikipedia page
    """
    # Prepare prompt for the agent
    prompt = f"""
    You are a research assistant that can search for information on Wikipedia.
    
    TASK: 
    1. Search Wikipedia for information about: "{user_query}"
    2. Review the search results and select the MOST relevant article by its page ID
    3. Get the full content of that Wikipedia page
    4. Return the cleaned content to me
    
    Use the tools available to you in this sequence. Make your decision about which article to select
    by evaluating the relevance of each search result's title and snippet to the query.
    
    Additional context: {context}
    """
    
    try:
        # Execute the agent with the prompt
        result = agent_executor.invoke({"input": prompt})
        return result.get("output", "No results found.")
    except Exception as e:
        return f"Error running search agent: {str(e)}"
