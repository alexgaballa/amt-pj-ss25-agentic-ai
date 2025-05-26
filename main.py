import os
import sys
from typing import TypedDict, Annotated, List, Optional
import operator
import time # Added import
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent, ToolNode
# from langgraph.checkpoint.memory import MemorySaver # Optional: for persistent memory

# Ensure the project root is in the Python path for imports
# This assumes main.py is in the project root directory.
# If main.py is in a subdirectory, adjust the path accordingly.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import sub-agent runners
# These imports assume 'agents' is a package in the project root.
from agents.sub_agent_search import run_search_agent
from agents.sub_agent_reason import run_reason_agent

# Load environment variables (e.g., GOOGLE_API_KEY)
load_dotenv()

# --- 1. Define State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    # Optional: add other fields if needed for orchestrator logic
    # e.g., original_query: str
    # e.g., collected_results: List[str]

# --- 2. Define Orchestrator Tools (wrapping sub-agents) ---
@tool
def call_search_agent(query: str, context: Optional[dict] = None) -> str:
    """
    Invokes the search agent to find information, search the web or Wikipedia, or look up facts.
    Use this for questions like 'What is the capital of France?', 'Summarize the Wikipedia page for AI', 'What is the current weather in Paris?'.
    Args:
        query: The specific question or search term for the search agent.
        context: Optional additional context for the search agent.
    Returns:
        The result from the search agent.
    """
    if context is None:
        context = {}
    print(f"\\n🤖 Orchestrator: Calling Search Agent with query: '{query}' and context: {context}")
    result = run_search_agent(user_query=query, context=context, verbose=False) # Set verbose to False for sub-agent calls
    print(f"🤖 Orchestrator: Search Agent returned: '{result}'")
    return result

@tool
def call_reason_agent(query: str, context: Optional[dict] = None) -> str:
    """
    Invokes the reason agent for calculations, unit conversions, date manipulations, logical reasoning, or solving math expressions.
    Use this for questions like 'What is 2+2?', 'Convert 100 miles to km', 'How old am I if born on Jan 1, 2000?'.
    Args:
        query: The specific problem or question for the reason agent.
        context: Optional additional context for the reason agent.
    Returns:
        The result from the reason agent.
    """
    if context is None:
        context = {}
    print(f"\\n🤖 Orchestrator: Calling Reason Agent with query: '{query}' and context: {context}")
    result = run_reason_agent(user_query=query, context=context, verbose=False) # Set verbose to False for sub-agent calls
    print(f"🤖 Orchestrator: Reason Agent returned: '{result}'")
    return result

orchestrator_tools = [call_search_agent, call_reason_agent]

# --- 3. Configure Orchestrator LLM and Prompt ---
# Initialize the LLM for the orchestrator
# Make sure GOOGLE_API_KEY is set in your .env file or environment
orchestrator_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

# Define the prompt for the orchestrator agent
orchestrator_system_prompt = """\\
You are a master orchestrator agent. Your primary goal is to understand a user's query and use available specialist agents to construct a comprehensive answer.

You have access to the following tools:
- `call_search_agent`: Use this agent for queries that require finding information, searching the web or Wikipedia, or looking up facts. For example: 'What is the capital of France?', 'Summarize the Wikipedia page for AI', 'What is the current weather in Berlin?'.
- `call_reason_agent`: Use this agent for queries that involve calculations, unit conversions, date manipulations, logical reasoning, or solving mathematical expressions. For example: 'What is 2+2?', 'Convert 100 miles to km', 'How old am I if born on Jan 1, 2000?'.

Your process should be:
1.  **Analyze**: Carefully analyze the user's query provided in the latest human message.
2.  **Decompose (if needed)**: If the query is complex or requires multiple steps (e.g., "Find X and then calculate Y based on X"), break it down into a sequence of smaller, manageable sub-queries.
3.  **Delegate**: For each sub-query, decide which specialist agent (`call_search_agent` or `call_reason_agent`) is the most appropriate. Formulate a precise question for that agent.
4.  **Execute**: Use the chosen tool to call the specialist agent with the formulated sub-query.
5.  **Iterate**: Review the result from the specialist agent. If more information is needed or another step is required (e.g., the first part of a multi-step query is done, now do the second part), go back to step 3. You may need to call multiple agents sequentially, using the output of one as input or context for the next.
6.  **Synthesize**: Once all necessary information has been gathered from the specialist agents and all parts of the user's query have been addressed, combine and synthesize these pieces of information into a single, coherent, and comprehensive final answer to the original user query.
7.  **Respond**: Provide this final synthesized answer directly as your response. Do NOT call any more tools once you are ready to give the final answer. Your last message should be the complete answer.

IMPORTANT:
- When you call a specialist agent, the query you provide to it should be self-contained and clear.
- Pay attention to the conversation history (available in `messages`) to keep track of previous interactions and results from specialist agents. This is crucial for multi-step queries.
- If the user's query is simple and can be handled by a single call to a specialist agent, do so and then present its result (or a slightly rephrased version if needed) as the final answer.
- Your final output to the user must be the answer itself, not a message saying you are about to answer or a call to another tool.
"""

orchestrator_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", orchestrator_system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# --- 4. Create Orchestrator Agent ---\n# memory_for_orchestrator = MemorySaver() # Optional: if you want orchestrator to have memory across invocations
orchestrator_agent_executor = create_react_agent(
    model=orchestrator_llm,
    tools=orchestrator_tools,
    prompt=orchestrator_prompt,
    # checkpointer=memory_for_orchestrator, # Pass memory here if using
    # debug=True # Useful for observing ReAct loop
)

# --- 5. Define Graph ---

# Define delay functions
def delay_node_before_tools(state: AgentState) -> AgentState:
    print("\\n⏳ Delaying 2 seconds before tool execution...\\n")
    time.sleep(2)
    return state

def delay_node_before_orchestrator_reentry(state: AgentState) -> AgentState:
    print("\\n⏳ Delaying 2 seconds before orchestrator re-entry...\\n")
    time.sleep(2)
    return state

workflow = StateGraph(AgentState)

# Add the orchestrator agent node
workflow.add_node("orchestrator", orchestrator_agent_executor)

# Add the tool node for executing sub-agent calls
tool_node = ToolNode(orchestrator_tools)
workflow.add_node("tools", tool_node)

# Add delay nodes
workflow.add_node("delay_before_tools", delay_node_before_tools)
workflow.add_node("delay_before_orchestrator", delay_node_before_orchestrator_reentry)

# Set the entry point
workflow.set_entry_point("orchestrator")

# Define conditional edges
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls and len(last_message.tool_calls) > 0:
        return "delay_before_tools" # Route to delay before tools
    return END

workflow.add_conditional_edges(
    "orchestrator",
    should_continue,
    {
        "delay_before_tools": "delay_before_tools", # Changed from "tools"
        END: END,
    },
)

# Add edges for the new delay flow
workflow.add_edge("delay_before_tools", "tools")
workflow.add_edge("tools", "delay_before_orchestrator")
workflow.add_edge("delay_before_orchestrator", "orchestrator")

# --- 6. Compile and Run ---\n# memory_for_graph = MemorySaver() # Optional: for graph-level checkpointing
app = workflow.compile(
    # checkpointer=memory_for_graph # Pass checkpointer here if using
)

if __name__ == "__main__":
    print("Orchestrator is ready. Testing with sample queries...")

    queries = [
        "What is the capital of Germany and what is its current population according to the latest search results? Then, calculate 15% of that population.",
        "Who directed the movie 'Inception', and what is 10 multiplied by 5?",
        "Convert 150 pounds to kilograms. Then, find a Wikipedia article about 'Artificial Intelligence' and summarize its introduction.",
        "What is the square root of 144 plus the square root of 169?",
        "Find the current weather in London. Separately, what is 2 to the power of 10?"
    ]

    for i, query in enumerate(queries):
        print(f"\\n--- Test Query {i+1} ---")
        print(f"🚀 Invoking orchestrator with query: '{query}'")

        # Prepare the input for the graph
        initial_input = {"messages": [HumanMessage(content=query)]}
        
        # Invoke the graph using stream to observe intermediate steps
        # The final event from the stream will contain the final state
        print("\\n--- Orchestrator Execution Flow ---")
        current_event = None
        for event in app.stream(initial_input, stream_mode="values"):
             last_message = event["messages"][-1]
             print(f"Step: {last_message.type}, Content/ToolCalls: {last_message.content if last_message.content else last_message.tool_calls}")
             print("--------------------")
             current_event = event # Keep track of the latest event

        final_state = current_event # The last event from the stream is the final state

        # The final answer should be in the last AIMessage from the orchestrator
        final_answer = "No answer found or an error occurred."
        if final_state and final_state.get("messages"):
            # Iterate backwards to find the last AI message that is NOT a tool call
            for message in reversed(final_state["messages"]):
                if message.type == "ai" and not (hasattr(message, "tool_calls") and message.tool_calls and len(message.tool_calls) > 0):
                    final_answer = message.content
                    break
        
        print(f"🏁 Orchestrator Final Answer:\\n{final_answer}")
        if i < len(queries) - 1:
            print("\\n=====================================\\n")

    # Example of a simpler query
    # query_simple = "What is 5 plus 5?"
    # print(f"\\n--- Test Query Simple ---")
    # print(f"🚀 Invoking orchestrator with query: '{query_simple}'")
    # initial_input_simple = {"messages": [HumanMessage(content=query_simple)]}
    # final_state_simple = app.invoke(initial_input_simple)
    # final_answer_simple = "No answer found."
    # if final_state_simple and final_state_simple.get("messages"):
    #     for message in reversed(final_state_simple["messages"]):
    #         if message.type == "ai" and not (hasattr(message, "tool_calls") and message.tool_calls):
    #             final_answer_simple = message.content
    #             break
    # print(f"🏁 Orchestrator Final Answer:\\n{final_answer_simple}")