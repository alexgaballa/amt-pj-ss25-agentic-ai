from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
import sys

from langchain.tools import StructuredTool

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp_server_setup.mcp_tool_loader import get_mcp_tools
import asyncio

load_dotenv()

tools = None
agent_executor = None

async def initialize_reason_agent():
    """Initialisiere Tools und Agent nur einmal."""
    global agent_executor
    if agent_executor is None:
        tools_to_load = [
            "add_tool", "subtract_tool", "multiply_tool", "divide_tool",
            "convert_units_tool", "kg_to_lb_tool", "lb_to_kg_tool", "miles_to_km_tool", "km_to_miles_tool",
            "calculate_mean_tool", "calculate_median_tool", "calculate_std_dev_tool", "calculate_range_tool",
            "calculate_years_between_tool", "calculate_days_between_tool", "calculate_age_tool",
            "count_word_occurrences_tool", "estimate_reading_time_tool",
            "evaluate_expression_tool", "solve_equation_tool"
        ]
    
        mcp_tools = await get_mcp_tools(tools_to_load)

        def make_tool_func(tool_coroutine):
            def func(**kwargs):
                print(f"Calling tool with kwargs: {kwargs}")
                return asyncio.run(tool_coroutine(**kwargs))
            return func

        tools = [
            StructuredTool(
                name=t.name,
                description=t.description,
                func=make_tool_func(t.coroutine),
                args_schema=t.args
            )
            for t in mcp_tools
        ]

        memory = MemorySaver()
        model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0, memory=memory)
        agent_executor = create_react_agent(model, tools)

async def run_reason_agent(user_query: str, context: dict = {}, verbose: bool = True) -> str:
    """
    Sub-agent responsible for performing reasoning and calculations.
    Uses LangChain agent to execute mathematical operations, unit conversions,
    and other analytical tasks.
    
    Args:
        user_query: The query from the user requiring reasoning or calculation
        context: Additional context that might help with the reasoning process
        verbose: Whether to print the entire conversation (True) or just return the final result (False)
        
    Returns:
        A string containing the agent's response with reasoning and results
    """
    await initialize_reason_agent()
    prompt_text = f"""
    You are a reasoning assistant capable of performing a wide range of calculations and analytical tasks.
    
    TASK:
    Analyze and solve the following problem: "{user_query}"
    
    Follow these steps:
    1. Understand what the question is asking for
    2. Determine which tools would be most appropriate to solve this problem
    3. Break down complex problems into simpler steps
    4. Use the appropriate calculation tools to solve each step
    5. Provide a clear explanation of your reasoning process
    6. Present the final answer in a concise and understandable format
    
    Available tools include:
    - Mathematical operations (addition, subtraction, multiplication, division)
    - Statistical calculations (mean, median, standard deviation, range)
    - Unit conversions (imperial to metric, currency, etc.)
    - Date calculations (years between dates, age calculation)
    - Text analysis (word count, reading time estimation)
    - Symbolic math operations (expression evaluation, equation solving)
    
    Additional context: {context}
    """
    
    try:
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
        return f"Error running reason agent: {str(e)}"

if __name__ == "__main__":
    test_queries = [
        "Convert 100 miles to kilometers",
        "What is the sum of 145, 232, 378, and 591?",
        "If I'm born on January 15, 1990, how old am I today?",
        "Solve the equation 3x + 7 = 22",
        "Calculate the mean and median of the following values: 5, 8, 12, 14, 15, 22, 35"
    ]

    query = test_queries[1]

    async def run():
        result = await run_reason_agent(
            user_query=query,
            context={"precision": "round to 2 decimal places when appropriate"},
            verbose=True
        )
        print("\nReason agent result:")
        print(result)

    asyncio.run(run())

    