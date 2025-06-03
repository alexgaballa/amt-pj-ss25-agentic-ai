import os
import sys
from typing import TypedDict, Annotated, List, Optional
import operator
import time # Added import
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode 
from langgraph.checkpoint.memory import MemorySaver # Optional: for persistent memory

import chainlit as cl # Import Chainlit

# Ensure the project root is in the Python path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import sub-agent runners
# These imports assume 'agents' is a package in the project root.
# For this example to run standalone, let's create dummy sub-agents
# Replace these with your actual imports if agents/ directory exists
# from agents.sub_agent_search import run_search_agent
# from agents.sub_agent_reason import run_reason_agent

# --- Dummy Sub-Agent Runners (Replace with your actual imports) ---
def run_search_agent(user_query: str, context: Optional[dict] = None, verbose: bool = False) -> str:
    if verbose:
        print(f"🔎 Mock Search Agent: Query='{user_query}', Context={context}")
    if "capital of Germany" in user_query.lower():
        return "The capital of Germany is Berlin. Its population is approximately 3.7 million."
    if "directed 'inception'" in user_query.lower():
        return "The movie 'Inception' was directed by Christopher Nolan."
    if "wikipedia" in user_query.lower() and "artificial intelligence" in user_query.lower():
        return "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. (Summary of intro)"
    if "weather in london" in user_query.lower():
        return "The current weather in London is partly cloudy, 15°C."
    return f"Search result for '{user_query}'"

def run_reason_agent(user_query: str, context: Optional[dict] = None, verbose: bool = False) -> str:
    if verbose:
        print(f"🧠 Mock Reason Agent: Query='{user_query}', Context={context}")
    if "15%" in user_query and "3.7 million" in user_query: # Simple check for follow-up
        return "15% of 3.7 million is 555,000."
    if user_query == "What is 2+2?":
        return "2+2 equals 4."
    if "10 multiplied by 5" in user_query:
        return "10 multiplied by 5 is 50."
    if "150 pounds to kilograms" in user_query:
        return "150 pounds is approximately 68.04 kilograms."
    if "square root of 144" in user_query and "square root of 169" in user_query:
        # This would ideally be two calls or a more complex reason agent
        return "sqrt(144) is 12, sqrt(169) is 13. Their sum is 25."
    if "2 to the power of 10" in user_query:
        return "2 to the power of 10 is 1024."
    return f"Reasoning result for '{user_query}'"
# --- End Dummy Sub-Agent Runners ---


# Load environment variables (e.g., GOOGLE_API_KEY)
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    print("⚠️ GOOGLE_API_KEY not found in environment variables. Please set it in a .env file.")
    # For Chainlit, you might want to handle this more gracefully or ensure it's set
    # For now, it will likely fail if the LLM tries to initialize without it.

# --- 1. Define State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    # Optional: add other fields if needed for orchestrator logic
    # e.g., original_query: str
    # e.g., collected_results: List[str]

# --- 2. Define Orchestrator Tools (wrapping sub-agents) ---
@tool
async def call_search_agent(query: str, context: Optional[dict] = None) -> str:
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
    
    # Chainlit: Send message about tool usage
    await cl.Message(content=f"📞 Calling Search Agent with query: '{query}'", author="Orchestrator->SearchAgent", parent_id=cl.context.current_step.id).send()

    print(f"\n🤖 Orchestrator: Calling Search Agent with query: '{query}' and context: {context}")
    # In a real scenario, make run_search_agent async or use cl.make_async
    result = await cl.make_async(run_search_agent)(user_query=query, context=context, verbose=False)
    print(f"🤖 Orchestrator: Search Agent returned: '{result}'")
    
    await cl.Message(content=f"🔍 Search Agent Result: '{result}'", author="SearchAgent->Orchestrator", parent_id=cl.context.current_step.id).send()
    return result

@tool
async def call_reason_agent(query: str, context: Optional[dict] = None) -> str:
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

    await cl.Message(content=f"📞 Calling Reason Agent with query: '{query}'", author="Orchestrator->ReasonAgent", parent_id=cl.context.current_step.id).send()

    print(f"\n🤖 Orchestrator: Calling Reason Agent with query: '{query}' and context: {context}")
    # In a real scenario, make run_reason_agent async or use cl.make_async
    result = await cl.make_async(run_reason_agent)(user_query=query, context=context, verbose=False)
    print(f"🤖 Orchestrator: Reason Agent returned: '{result}'")
    
    await cl.Message(content=f"💡 Reason Agent Result: '{result}'", author="ReasonAgent->Orchestrator", parent_id=cl.context.current_step.id).send()
    return result

orchestrator_tools = [call_search_agent, call_reason_agent]

# --- 3. Configure Orchestrator LLM and Prompt ---
orchestrator_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

orchestrator_system_prompt = """\
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

orchestrator_llm_with_tools = orchestrator_llm.bind_tools(orchestrator_tools)

# --- 4. Define Orchestrator Agent Logic (ReAct style) ---
async def orchestrator_agent_node(state: AgentState, config: Optional[dict] = None):
    print(f"\n🧠 Orchestrator Agent Node: Current state messages: {state['messages']}")
    response_message = await orchestrator_llm_with_tools.ainvoke(state["messages"], config)
    print(f"🧠 Orchestrator Agent Node: LLM response: {response_message}")
    return {"messages": [response_message]}


# --- 5. Define Graph ---
async def delay_node_before_tools(state: AgentState) -> AgentState:
    print("\n⏳ Delaying 1 second before tool execution...\n")
    await cl.sleep(1) 
    return state

async def delay_node_before_orchestrator_reentry(state: AgentState) -> AgentState:
    print("\n⏳ Delaying 1 second before orchestrator re-entry...\n")
    await cl.sleep(1)
    return state


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("messages", []) 

    workflow = StateGraph(AgentState)
    workflow.add_node("orchestrator", orchestrator_agent_node)
    
    # ToolNode is now correctly imported
    tool_node_instance = ToolNode(orchestrator_tools) 
    workflow.add_node("tools", tool_node_instance) 

    workflow.add_node("delay_before_tools", delay_node_before_tools)
    workflow.add_node("delay_before_orchestrator", delay_node_before_orchestrator_reentry)

    workflow.set_entry_point("orchestrator")

    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls and len(last_message.tool_calls) > 0:
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

    workflow.add_edge("delay_before_tools", "tools")
    workflow.add_edge("tools", "delay_before_orchestrator") 
    workflow.add_edge("delay_before_orchestrator", "orchestrator")

    app = workflow.compile(
        # checkpointer=MemorySaver() 
    )
    cl.user_session.set("runnable", app)
    await cl.Message(content="Orchestrator is ready. How can I help you?").send()


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")
    # Get the true, complete history from the session
    messages_history_from_session = cl.user_session.get("messages", [])

    # For this specific run, start with the session history and add the new user message
    current_run_input_messages = list(messages_history_from_session)
    current_run_input_messages.append(HumanMessage(content=message.content))

    async with cl.Step(name="Orchestration Process", type="run", show_input=True) as main_step:
        main_step.input = message.content
        config = {"configurable": {"thread_id": cl.context.session.id}}

        await cl.Message(content=f"👤 You: {message.content}", author="User", parent_id=main_step.id).send()
        
        final_answer_content = None
        # This will hold all messages (input + generated) for this particular invocation
        messages_for_this_invocation = [] 

        try:
            async for event in runnable.astream({"messages": current_run_input_messages}, config=config, stream_mode="values"):
                # event is the full AgentState from the graph.
                # event["messages"] is the current list of messages in the graph's state.
                if not event.get("messages"):
                    continue
                
                # Update our record of all messages for this specific invocation
                messages_for_this_invocation = list(event["messages"])
                last_message_in_event = messages_for_this_invocation[-1]

                print(f"📬 Graph Event State: Last message type: {last_message_in_event.type}, "
                      f"Content/ToolCalls: {last_message_in_event.content if last_message_in_event.content else getattr(last_message_in_event, 'tool_calls', 'N/A')}")

                if isinstance(last_message_in_event, AIMessage):
                    if last_message_in_event.tool_calls:
                        tool_call_details = []
                        for tc in last_message_in_event.tool_calls:
                            tool_call_details.append(f"Tool: `{tc['name']}`, Args: `{tc['args']}`")
                        tool_calls_str = "\n".join(tool_call_details)
                        
                        # Display the decision to call a tool.
                        # The tool's own cl.Message calls will show its execution.
                        async with cl.Step(name="Orchestrator Decision: Call Tool(s)", parent_id=main_step.id) as tool_decision_step:
                            tool_decision_step.output = f"🤖 Orchestrator decided to use tool(s):\n{tool_calls_str}"
                        # DO NOT BREAK HERE. Let astream continue.
                        # The ToolNode will run, and a new event with ToolMessage will be yielded by astream.
                    
                    elif last_message_in_event.content: # AIMessage without tool_calls but with content = final answer
                        final_answer_content = last_message_in_event.content
                        print(f"🏁 Orchestrator Final Answer (from AIMessage content): {final_answer_content}")
                        main_step.output = final_answer_content # Update main step output
                        # We have the final answer, so we can break the astream loop.
                        break 
                
                elif isinstance(last_message_in_event, ToolMessage):
                     # The tools themselves send cl.Messages. We can log here if needed.
                     print(f"🛠️ Tool Execution Result processed by graph: {last_message_in_event.name} -> {last_message_in_event.content[:100]}...")
                     # The graph will loop this ToolMessage back to the orchestrator_agent_node.
                     # astream will continue to yield events from that.

        except Exception as e:
            print(f"An error occurred during graph execution: {e}")
            cl.Error(f"An error occurred: {e}").send() # Show error in UI
            main_step.output = f"Error: {e}"
            # Fall through to send a message to the user if no final_answer_content

        # After the astream loop finishes (either by break on final answer or natural end of stream)
        if final_answer_content:
            await cl.Message(content=final_answer_content, author="Orchestrator ✨").send()
            # Update the main user session history with all messages from this successful run
            cl.user_session.set("messages", messages_for_this_invocation)
        else:
            print("⚠️ Orchestrator did not provide a final answer or an error occurred earlier.")
            if not main_step.output: # If no specific error message was set
                 main_step.output = "Sorry, I could not process your request fully."
            await cl.Message(content=main_step.output or "Sorry, I could not process your request fully.", author="Orchestrator ⚠️").send()
            # Decide how to update history on failure. 
            # Storing messages_for_this_invocation allows debugging the partial run.
            cl.user_session.set("messages", messages_for_this_invocation if messages_for_this_invocation else current_run_input_messages)