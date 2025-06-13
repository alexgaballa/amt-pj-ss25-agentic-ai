import os
import sys
from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
import operator
import time # Added import
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent, ToolNode
from agents.orchestrator_agent import orchestrator_agent_executor
from tools.tool_wrappers import (
    call_search_agent,
    call_reason_agent,
)

# Ensure the project root is in the Python path for imports
# This assumes main.py is in the project root directory.
# If main.py is in a subdirectory, adjust the path accordingly.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# Load environment variables (e.g., GOOGLE_API_KEY)
load_dotenv()
orchestrator_tools = [call_search_agent, call_reason_agent]

# --- Define State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    # Optional: add other fields if needed for orchestrator logic
    # e.g., original_query: str
    # e.g., collected_results: List[str]

# --- Define Graph ---

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
        # "What is the current population of the capital of Germany? And, assuming the average weight of 70 kg calculate the total weight of that population.",
        # "Convert 150 pounds to kilograms. Then, find a Wikipedia article about 'Artificial Intelligence' and summarize its introduction.",
        # "What is the square root of 144 plus the square root of 169?",
        # "Find the current weather in London. Separately, what is 2 to the power of 10?"
    ]

    test_queries = [
        #"Convert 25 parsecs to gallons. Then, find a Wikipedia article about 'Quantum Computing' and summarize its introduction.",
        # "How old was Marie Curie when she received her second Nobel Prize?",
        "Solve the equation F = m * a for m when F = 98 and a = 9.8"
    ]

    for i, query in enumerate(test_queries):
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