"""
Orchestrator agent that coordinates between search and reasoning agents.
"""
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from tools.tool_wrappers import call_search_agent, call_reason_agent

# Load environment variables
load_dotenv()

# Define the list of tools that the orchestrator can use
orchestrator_tools = [call_search_agent, call_reason_agent]

# Initialize the LLM for the orchestrator
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

# Create Orchestrator Agent
orchestrator_agent_executor = create_react_agent(
    model=orchestrator_llm,
    tools=orchestrator_tools,
    prompt=orchestrator_prompt,
)