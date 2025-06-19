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

# Define step-based processing functions
@cl.step(name="🔍 Search Agent", type="tool")
async def search_agent_step(query: str):
    """Execute search agent with COT display"""
    try:
        result = call_search_agent.invoke({"query": query})
        # Ensure we return the actual content, not the tool result object
        if hasattr(result, 'content'):
            return result.content
        elif isinstance(result, str):
            return result
        else:
            return str(result)
    except Exception as e:
        return f"Search failed: {str(e)}"

@cl.step(name="🧮 Reasoning Agent", type="tool")
async def reasoning_agent_step(query: str):
    """Execute reasoning agent with COT display"""
    try:
        result = call_reason_agent.invoke({"query": query})
        # Ensure we return the actual content, not the tool result object
        if hasattr(result, 'content'):
            return result.content
        elif isinstance(result, str):
            return result
        else:
            return str(result)
    except Exception as e:
        return f"Reasoning failed: {str(e)}"

@cl.step(name="🧠 Orchestrator Analysis", type="llm")
async def orchestrator_analysis_step(user_query: str, conversation_context: list):
    """Show orchestrator's planning and analysis process"""
    # Analyze what needs to be done
    needs_search = any(word in user_query.lower() for word in ["what", "who", "where", "find", "search", "wikipedia", "information"])
    needs_reasoning = any(word in user_query.lower() for word in ["calculate", "solve", "math", "convert", "equation", "formula"])
    
    analysis = f"Analyzing query: '{user_query}'"
    
    plan = []
    if needs_search:
        plan.append("🔍 Will use Search Agent for information retrieval")
    if needs_reasoning:
        plan.append("🧮 Will use Reasoning Agent for calculations")
    
    if not plan:
        plan.append("💬 Will provide direct response")
    
    planning_result = f"Analysis complete. Plan:\n" + "\n".join(f"• {p}" for p in plan)
    
    return {
        "needs_search": needs_search,
        "needs_reasoning": needs_reasoning,
        "plan": planning_result
    }

@cl.step(name="🎯 Final Synthesis", type="llm")
async def synthesis_step(user_query: str, search_result: str = None, reasoning_result: str = None):
    """Synthesize final answer from all results"""
    results = []
    if search_result:
        results.append(f"Search findings: {search_result}")
    if reasoning_result:
        results.append(f"Calculation results: {reasoning_result}")
    
    if results:
        synthesis = f"Combining results for '{user_query}':\n" + "\n".join(f"• {r}" for r in results)
    else:
        synthesis = f"Providing direct response to '{user_query}'"
    
    return synthesis

# We'll use a simplified approach with Chainlit Steps instead of the complex workflow
# This provides better COT visualization

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
    """Handle incoming messages with Chain of Thought display"""
    user_query = message.content
    
    # Get conversation memory
    conversation_memory = cl.user_session.get("conversation_memory", [])
    message_count = cl.user_session.get("message_count", 0)
    
    try:
        # Step 1: Orchestrator Analysis (always shown)
        analysis_result = await orchestrator_analysis_step(user_query, conversation_memory)
        
        # Prepare conversation context
        context_messages = []
        for mem in conversation_memory[-5:]:
            if mem["type"] == "human":
                context_messages.append(HumanMessage(content=mem["content"]))
            elif mem["type"] == "ai":
                context_messages.append(AIMessage(content=mem["content"]))
        context_messages.append(HumanMessage(content=user_query))
        
        # Initialize results
        search_result = None
        reasoning_result = None
        
        # Step 2: Execute Search Agent if needed
        if analysis_result["needs_search"]:
            search_result = await search_agent_step(user_query)
        
        # Step 3: Execute Reasoning Agent if needed
        if analysis_result["needs_reasoning"]:
            reasoning_result = await reasoning_agent_step(user_query)
        
        # Step 4: Final Answer Generation
        async with cl.Step(name="🤖 Orchestrator Final Answer", type="llm") as step:
            if search_result or reasoning_result:
                # Prepare comprehensive context with agent results
                synthesis_prompt = f"User Query: {user_query}\n\n"
                
                if search_result:
                    synthesis_prompt += f"Search Agent provided this information:\n{search_result}\n\n"
                if reasoning_result:
                    synthesis_prompt += f"Reasoning Agent calculated:\n{reasoning_result}\n\n"
                
                synthesis_prompt += "Please provide a comprehensive final answer that incorporates the above agent results to fully address the user's query."
                
                step.input = synthesis_prompt
                
                # Create enhanced context for orchestrator
                synthesis_context = context_messages.copy()
                synthesis_context.append(HumanMessage(content=synthesis_prompt))
                
                # Get orchestrator's final synthesis
                orchestrator_input = {"messages": synthesis_context}
                final_response = orchestrator_agent_executor.invoke(orchestrator_input)
                
                # Extract the final answer properly
                if final_response and "messages" in final_response:
                    last_message = final_response["messages"][-1]
                    if hasattr(last_message, 'content') and last_message.content:
                        final_answer = last_message.content
                    else:
                        final_answer = f"Based on the analysis: {synthesis_prompt}"
                else:
                    final_answer = f"I've analyzed your query and used the available agents to provide this response: {user_query}"
                
                step.output = final_answer
            else:
                # Direct response - let orchestrator handle it normally
                step.input = f"Providing direct response to: {user_query}"
                
                # Use orchestrator for direct response with normal context
                orchestrator_input = {"messages": context_messages}
                final_response = orchestrator_agent_executor.invoke(orchestrator_input)
                
                # Extract final answer with better error handling
                if final_response and "messages" in final_response:
                    last_message = final_response["messages"][-1]
                    if hasattr(last_message, 'content') and last_message.content:
                        final_answer = last_message.content
                    else:
                        final_answer = f"I understand you're asking: {user_query}. Let me provide a direct response based on my knowledge."
                else:
                    final_answer = f"I'll help you with: {user_query}"
                
                step.output = final_answer
        
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