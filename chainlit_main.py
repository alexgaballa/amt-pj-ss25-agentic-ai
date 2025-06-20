import os
import sys
from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
import operator
import time
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent, ToolNode
import chainlit as cl
from agents.orchestrator_agent import orchestrator_agent_executor
from tools.tool_wrappers import (
    call_search_agent,
    call_reason_agent,
)

# Ensure the project root is in the Python path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables (e.g., GOOGLE_API_KEY)
load_dotenv()
orchestrator_tools = [call_search_agent, call_reason_agent]

# --- Define State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# --- Define Graph ---

# Same workflow as main.py 
def delay_node_before_tools(state: AgentState) -> AgentState:
    return state

def delay_node_before_orchestrator_reentry(state: AgentState) -> AgentState:
    return state

workflow = StateGraph(AgentState)

# Add the orchestrator agent node
workflow.add_node("orchestrator", orchestrator_agent_executor)

# Add the tool node for executing sub-agent calls
tool_node = ToolNode(orchestrator_tools)
workflow.add_node("tools", tool_node)

# Add delay nodes (no actual delay in Chainlit version for better UX)
workflow.add_node("delay_before_tools", delay_node_before_tools)
workflow.add_node("delay_before_orchestrator", delay_node_before_orchestrator_reentry)

# Set the entry point
workflow.set_entry_point("orchestrator")

# Define conditional edges
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls and len(last_message.tool_calls) > 0:
        return "delay_before_tools"
    return END

workflow.add_conditional_edges(
    "orchestrator",
    should_continue,
    {
        "delay_before_tools": "delay_before_tools",
        END: END,
    },
)

# Add edges for the flow
workflow.add_edge("delay_before_tools", "tools")
workflow.add_edge("tools", "delay_before_orchestrator")
workflow.add_edge("delay_before_orchestrator", "orchestrator")

# Compile the workflow
app = workflow.compile()

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    # Initialize session memory
    cl.user_session.set("conversation_memory", [])
    cl.user_session.set("message_count", 0)
    
    await cl.Message(
        content="🤖 **Orchestrator Agent System** is ready!\n\n"
                "I can help you with:\n"
                "- Mathematical calculations and equations\n"
                "- Wikipedia searches and information retrieval\n"
                "- Complex multi-step reasoning tasks\n\n"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    user_query = message.content
    
    # Get conversation memory
    conversation_memory = cl.user_session.get("conversation_memory", [])
    message_count = cl.user_session.get("message_count", 0)
    
    try:
        # Prepare conversation context
        context_messages = []
        for mem in conversation_memory[-5:]:
            if mem["type"] == "human":
                context_messages.append(HumanMessage(content=mem["content"]))
            elif mem["type"] == "ai":
                context_messages.append(AIMessage(content=mem["content"]))
        context_messages.append(HumanMessage(content=user_query))
        
        # Same workflow as main.py 
        async with cl.Step(name="🤖 Orchestrator Workflow", type="llm") as workflow_step:
            workflow_step.input = f"Processing query: {user_query}"
            
            # Prepare the input for the graph (same as main.py)
            initial_input = {"messages": context_messages}
            
            # Track the workflow execution with sub-steps
            final_answer = "No answer found or an error occurred."
            step_count = 0
            
            # Stream through workflow execution
            for event in app.stream(initial_input, stream_mode="values"):
                step_count += 1
                if "messages" in event and event["messages"]:
                    last_message = event["messages"][-1]
                    
                    # Show different types of steps
                    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                        # Tool call step
                        tool_names = [tc['name'] for tc in last_message.tool_calls]
                        async with cl.Step(name=f"🔧 Tool Execution: {', '.join(tool_names)}", type="tool") as tool_step:
                            tool_step.input = f"Executing tools: {tool_names}"
                            tool_step.output = "Tools executed successfully"
                    
                    elif last_message.type == "ai" and last_message.content:
                        # AI reasoning step
                        if not (hasattr(last_message, 'tool_calls') and last_message.tool_calls):
                            final_answer = last_message.content
                            async with cl.Step(name="🧠 Orchestrator Response", type="llm") as ai_step:
                                ai_step.input = "Generating final response"
                                ai_step.output = last_message.content[:200] + ("..." if len(last_message.content) > 200 else "")
                    
                    elif last_message.type == "tool":
                        # Tool result step
                        async with cl.Step(name="📊 Tool Result", type="tool") as result_step:
                            result_step.input = f"Tool: {getattr(last_message, 'name', 'Unknown')}"
                            result_step.output = last_message.content[:200] + ("..." if len(last_message.content) > 200 else "")
            
            workflow_step.output = f"Workflow completed in {step_count} steps"
        
        # Send final answer
        await cl.Message(content=final_answer).send()
        
        # Update conversation memory
        conversation_memory.append({"type": "human", "content": user_query})
        conversation_memory.append({"type": "ai", "content": final_answer})
        
        # Keep only last 20 exchanges (40 messages) to manage memory
        if len(conversation_memory) > 40:
            conversation_memory = conversation_memory[-40:]
        
        cl.user_session.set("conversation_memory", conversation_memory)
        cl.user_session.set("message_count", message_count + 1)
        
    except Exception as e:
        error_message = f"❌ An error occurred while processing your request: {str(e)}"
        await cl.Message(content=error_message).send()

if __name__ == "__main__":
    # This will be handled by chainlit run command
    pass