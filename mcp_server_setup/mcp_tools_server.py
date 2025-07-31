"""Tool wrappers for MCP integration with proper type hints."""
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Union, Tuple, Optional

"""Calculate tools imports"""
# Use relative import to refer to the local calculate.py file
from calculate import (
    convert_units, add, subtract, multiply, divide,
    calculate_years_between, calculate_days_between, calculate_mean,
    calculate_median, calculate_std_dev, calculate_range,
    evaluate_expression, solve_equation, calculate_age,
    count_word_occurrences, estimate_reading_time,
    kg_to_lb, lb_to_kg, miles_to_km, km_to_miles
)

"""Wiki-search tool imports"""
from wiki_search import (
    search_wikipedia, get_wikipedia_content, clean_page_html,
    get_page_sections, get_section_content, get_multiple_sections_content
)

import logging
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import re
import json
from update_user_profile import update_user_profile

# Load environment variables
load_dotenv()

# Setup Gemini 2.0 Flash Lite Model (ensure GOOGLE_API_KEY is in your .env)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    timeout=30.0,
    temperature=0.0,
)

# Set up logging
log_file_path = os.path.join(os.getcwd(), "mcp_debug.log")

logging.basicConfig(
    filename=log_file_path,
    filemode='a',  # append mode
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True 
)

logger = logging.getLogger(__name__)
logger.info("Logging initialized.")
# Create a MCP server instance
mcp = FastMCP(
    name = "MCP-Tool-Server",
    description = "A server for various tools.",
    host = "0.0.0.0",
    port = 8050,
)

# ==============================================================================
#                               Calculate Tools
# ==============================================================================
@mcp.tool()
async def add_tool(numbers: list[float]) -> float:
    """Add a list of numbers together.
    
    Args:
        numbers: List of numbers to add
    
    Returns:
        Sum of all numbers
    """
    return add(numbers)

@mcp.tool()
async def subtract_tool(minuend: float, subtrahend: float) -> float:
    """Subtract one number from another.
    
    Args:
        minuend: Number to subtract from
        subtrahend: Number to subtract
    
    Returns:
        Result of subtraction
    """
    return subtract(minuend, subtrahend)

@mcp.tool()
async def multiply_tool(numbers: list[float]) -> float:
    """Multiply a list of numbers together.
    
    Args:
        numbers: List of numbers to multiply
    
    Returns:
        Product of all numbers
    """
    return multiply(numbers)

@mcp.tool()
async def divide_tool(dividend: float, divisor: float) -> float:
    """Divide one number by another."""
    return divide(dividend, divisor)

# Unit conversion tools
@mcp.tool()
async def convert_units_tool(value: float, from_unit: str, to_unit: str) -> float:
    """Convert between different units of measurement."""
    return convert_units(value, from_unit, to_unit)

@mcp.tool()
async def kg_to_lb_tool(kg: float) -> float:
    """Convert kilograms to pounds."""
    return kg_to_lb(kg)

@mcp.tool()
async def lb_to_kg_tool(lb: float) -> float:
    """Convert pounds to kilograms."""
    return lb_to_kg(lb)

@mcp.tool()
async def miles_to_km_tool(miles: float) -> float:
    """Convert miles to kilometers."""
    return miles_to_km(miles)

@mcp.tool()
async def km_to_miles_tool(km: float) -> float:
    """Convert kilometers to miles."""
    return km_to_miles(km)

# Statistical tools
@mcp.tool()
async def calculate_mean_tool(numbers: List[float]) -> float:
    """Calculate the arithmetic mean of a list of numbers.
    
    Args:
        numbers: List of numbers to calculate mean from
    
    Returns:
        The arithmetic mean
    """
    return calculate_mean(numbers)

@mcp.tool()
async def calculate_median_tool(numbers: List[float]) -> float:
    """Calculate the median of a list of numbers.
    
    Args:
        numbers: List of numbers to calculate median from
    
    Returns:
        The median value
    """
    return calculate_median(numbers)

@mcp.tool()
async def calculate_std_dev_tool(numbers: List[float]) -> float:
    """Calculate the standard deviation of a list of numbers.
    
    Args:
        numbers: List of numbers to calculate standard deviation from
    
    Returns:
        The standard deviation
    """
    return calculate_std_dev(numbers)

@mcp.tool()
async def calculate_range_tool(numbers: List[float]) -> float:
    """Calculate the range (max - min) of a list of numbers.
    
    Args:
        numbers: List of numbers to calculate range from
    
    Returns:
        The range value
    """
    return calculate_range(numbers)

# Date and time tools
@mcp.tool()
async def calculate_years_between_tool(start_date_str: str, end_date_str: str) -> int:
    """Calculate the number of years between two dates."""
    return calculate_years_between(start_date_str, end_date_str)

@mcp.tool()
async def calculate_days_between_tool(start_date_str: str, end_date_str: str) -> int:
    """Calculate the number of days between two dates."""
    return calculate_days_between(start_date_str, end_date_str)

@mcp.tool()
async def calculate_age_tool(birth_date_str: str) -> int:
    """Calculate age based on birth date."""
    return calculate_age(birth_date_str)

# Text analysis tools
@mcp.tool()
async def count_word_occurrences_tool(text: str, word: str) -> int:
    """Count occurrences of a word in text."""
    return count_word_occurrences(text, word)

@mcp.tool()
async def estimate_reading_time_tool(text: str, wpm: int = 200) -> float:
    """Estimate reading time for text in minutes."""
    return estimate_reading_time(text, wpm)

# Math expression tools
@mcp.tool()
async def evaluate_expression_tool(expression: str) -> float:
    """Evaluate a mathematical expression."""
    return evaluate_expression(expression)

@mcp.tool()
async def solve_equation_tool(equation_str: str, target_var: str) -> str:
    """Solve a symbolic equation for a target variable."""
    return solve_equation(equation_str, target_var)

@mcp.tool()
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
    logger.info(f"Orchestrator: Calling Reason Agent with query: '{query}' and context: {context}")
    
    # Import here to avoid circular dependencies
    from agents.mcp_sub_agent_reason import run_reason_agent
    
    result = await run_reason_agent(user_query=query, context=context, verbose=False)
    logger.info(f"Orchestrator: MCP-Reason Agent returned: '{result}'")
    return result

# ==============================================================================
#                               Wiki-Search Tools
# ==============================================================================
@mcp.tool()
async def search_wikipedia_tool(query: str) -> List[Dict[str, Union[str, int]]]:
    """Search Wikipedia for a query and return relevant article titles and snippets.
    
    Args:
        query: Search query string
    
    Returns:
        List of dictionaries with article info (title, pageid, snippet)
    """
    return search_wikipedia(query)

@mcp.tool()
async def get_wikipedia_content_tool(page_id: int) -> str:
    """Retrieve the full content of a Wikipedia article by page ID.
    
    Args:
        page_id: Wikipedia page ID
    
    Returns:
        Article content as cleaned text
    """
    return get_wikipedia_content(page_id)

@mcp.tool()
async def get_page_sections_tool(page_id: int) -> Tuple[List[str], Dict[str, str]]:
    """Get the list of section titles and their indices for a Wikipedia page.
    
    Args:
        page_id: Wikipedia page ID
    
    Returns:
        Tuple of (section titles list, section index dictionary)
    """
    return get_page_sections(page_id)

@mcp.tool()
async def get_section_content_tool(page_id: int, section_index: str) -> str:
    """Get the content of a specific section from a Wikipedia page.
    
    Args:
        page_id: Wikipedia page ID
        section_index: Section index string
    
    Returns:
        Section content as cleaned text
    """
    return get_section_content(page_id, section_index)

@mcp.tool()
async def clean_page_html_tool(html_content: str) -> str:
    """Clean Wikipedia HTML content to extract readable text.
    
    Args:
        html_content: HTML content to clean
    
    Returns:
        Cleaned text content
    """
    return clean_page_html(html_content)

@mcp.tool()
async def get_multiple_sections_content_tool(page_id: int, section_indices: List[str]) -> Dict[str, str]:
    """Get content from multiple sections of a Wikipedia page in a single call.
    
    Args:
        page_id: Wikipedia page ID
        section_indices: List of section indices to retrieve
        
    Returns:
        Dictionary mapping section indices to their content
    """
    return get_multiple_sections_content(page_id, section_indices)

@mcp.tool()
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
    logger.info(f"Orchestrator: Calling Search Agent with query: '{query}' and context: {context}")

    # Import here to avoid circular dependencies
    from agents.mcp_sub_agent_search import run_search_agent

    result = await run_search_agent(user_query=query, context=context, verbose=False)
    logger.info(f"Orchestrator: MCP-Search Agent returned: '{result}'")
    return result
# ==============================================================================
#           User Profile Tool (LLM based extraction of user profile)
# ==============================================================================
@mcp.tool()
def extract_user_profile_info(message: str, user_id: str = "user_001") -> dict:
    """
    Extracts personal user information from a natural language message
    and updates the user's long-term memory profile.
    
    Args:
        message: User input containing personal information
        user_id: Unique user identifier for memory storage
    
    Returns:
        Updated user profile dictionary
    """
    system_prompt = """You are a personal data extractor.  
    Given a user message, extract only the structured personal data in JSON format with the following fields:

    - name: string (capitalize first letter only, e.g., "Alice")  
    - studies: string (capitalize first letter of each word, e.g., "Computer Science")  
    - age: number (e.g., 25)  
    - gender: string ("male", "female", "non-binary")  
    - likes: list of strings  
    Each entry must be:  
    - auto-corrected for spelling errors (e.g., "foottball" → "Football")  
    - capitalized (first letter uppercase, e.g., "football" → "Football")  
    - no empty entries or duplicates

    ### Guidelines:
    - Correct obvious spelling mistakes (e.g., "foottball" → "Football", "tehcnology" → "Technology")  
    - Normalize plural/singular forms (e.g., "movies" → "Movies")  
    - Expand common abbreviations using world knowledge:
    - "CS" → "Computer Science"
    - "AI" → "Artificial Intelligence"
    - "IT" → "Information Technology"  
    - Only extract fields explicitly mentioned in the message  
    - If a field is not mentioned, omit it from the output  
    - Users may provide information incrementally across multiple messages

    ### Example Input:
    "I’m Sarah, 22 years old, studying CS. I like books, foottball, and tech."

    ### Example Output:
    {
    "name": "Sarah",
    "age": 22,
    "studies": "Computer Science",
    "likes": ["Books", "Football", "Tech"]
    }

    Now extract from:
    \"\"\"{user_message}\"\"\"
    """

    prompt = system_prompt.replace("{user_message}", message)
    logger.info(f"Prompting LLM with: {prompt}")
    response = llm.invoke(prompt)
    logger.info(f"Extracted user profile info: {response}")
    
    cleaned = re.sub(r"```(?:json)?\s*([\s\S]+?)\s*```", r"\1", response.content.strip())
    try:
        parsed = json.loads(cleaned)
        logger.info(f"Parsed user profile info: {parsed}")
        # update profile in long-term memory
        updated_profile = update_user_profile(parsed, user_id=user_id)
        return updated_profile
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return {
            "error": f"Failed to parse user profile info: {str(e)}",
            "raw_response": response.content
        }

# to run the server --> mcp dev mcp_tools_server.py (inside of mcp_server_setup folder)
# or python mcp_tools_server.py
# run the server (do it from client code for prototype, not here)
if __name__ == "__main__":
    mcp.run(transport="stdio")