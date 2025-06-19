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
    kg_to_lb, lb_to_kg, miles_to_km, km_to_miles, run_reason_agent
)

"""Wiki-search tool imports"""
from wiki_search import (
    search_wikipedia, get_wikipedia_content, clean_page_html,
    get_page_sections, get_section_content, get_multiple_sections_content, call_search_agent
)

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
def add_tool(numbers: list[float]) -> float:
    """Add a list of numbers together.
    
    Args:
        numbers: List of numbers to add
    
    Returns:
        Sum of all numbers
    """
    return add(numbers)

@mcp.tool()
def subtract_tool(minuend: float, subtrahend: float) -> float:
    """Subtract one number from another.
    
    Args:
        minuend: Number to subtract from
        subtrahend: Number to subtract
    
    Returns:
        Result of subtraction
    """
    return subtract(minuend, subtrahend)

@mcp.tool()
def multiply_tool(numbers: list[float]) -> float:
    """Multiply a list of numbers together.
    
    Args:
        numbers: List of numbers to multiply
    
    Returns:
        Product of all numbers
    """
    return multiply(numbers)

@mcp.tool()
def divide_tool(dividend: float, divisor: float) -> float:
    """Divide one number by another."""
    return divide(dividend, divisor)

# Unit conversion tools
@mcp.tool()
def convert_units_tool(value: float, from_unit: str, to_unit: str) -> float:
    """Convert between different units of measurement."""
    return convert_units(value, from_unit, to_unit)

@mcp.tool()
def kg_to_lb_tool(kg: float) -> float:
    """Convert kilograms to pounds."""
    return kg_to_lb(kg)

@mcp.tool()
def lb_to_kg_tool(lb: float) -> float:
    """Convert pounds to kilograms."""
    return lb_to_kg(lb)

@mcp.tool()
def miles_to_km_tool(miles: float) -> float:
    """Convert miles to kilometers."""
    return miles_to_km(miles)

@mcp.tool()
def km_to_miles_tool(km: float) -> float:
    """Convert kilometers to miles."""
    return km_to_miles(km)

# Statistical tools
@mcp.tool()
def calculate_mean_tool(numbers: List[float]) -> float:
    """Calculate the arithmetic mean of a list of numbers.
    
    Args:
        numbers: List of numbers to calculate mean from
    
    Returns:
        The arithmetic mean
    """
    return calculate_mean(numbers)

@mcp.tool()
def calculate_median_tool(numbers: List[float]) -> float:
    """Calculate the median of a list of numbers.
    
    Args:
        numbers: List of numbers to calculate median from
    
    Returns:
        The median value
    """
    return calculate_median(numbers)

@mcp.tool()
def calculate_std_dev_tool(numbers: List[float]) -> float:
    """Calculate the standard deviation of a list of numbers.
    
    Args:
        numbers: List of numbers to calculate standard deviation from
    
    Returns:
        The standard deviation
    """
    return calculate_std_dev(numbers)

@mcp.tool()
def calculate_range_tool(numbers: List[float]) -> float:
    """Calculate the range (max - min) of a list of numbers.
    
    Args:
        numbers: List of numbers to calculate range from
    
    Returns:
        The range value
    """
    return calculate_range(numbers)

# Date and time tools
@mcp.tool()
def calculate_years_between_tool(start_date_str: str, end_date_str: str) -> int:
    """Calculate the number of years between two dates."""
    return calculate_years_between(start_date_str, end_date_str)

@mcp.tool()
def calculate_days_between_tool(start_date_str: str, end_date_str: str) -> int:
    """Calculate the number of days between two dates."""
    return calculate_days_between(start_date_str, end_date_str)

@mcp.tool()
def calculate_age_tool(birth_date_str: str) -> int:
    """Calculate age based on birth date."""
    return calculate_age(birth_date_str)

# Text analysis tools
@mcp.tool()
def count_word_occurrences_tool(text: str, word: str) -> int:
    """Count occurrences of a word in text."""
    return count_word_occurrences(text, word)

@mcp.tool()
def estimate_reading_time_tool(text: str, wpm: int = 200) -> float:
    """Estimate reading time for text in minutes."""
    return estimate_reading_time(text, wpm)

# Math expression tools
@mcp.tool()
def evaluate_expression_tool(expression: str) -> float:
    """Evaluate a mathematical expression."""
    return evaluate_expression(expression)

@mcp.tool()
def solve_equation_tool(equation_str: str, target_var: str) -> str:
    """Solve a symbolic equation for a target variable."""
    return solve_equation(equation_str, target_var)

@mcp.tool()
def call_reason_agent_tool(query: str, context: Optional[dict] = None) -> str:
    """Call the reasoning agent to perform calculations or analysis.
    
    Args:
        query: The specific question or calculation request
        context: Optional additional context for the agent"""
    return run_reason_agent(query, context)



# ==============================================================================
#                               Wiki-Search Tools
# ==============================================================================
@mcp.tool()
def search_wikipedia_tool(query: str) -> List[Dict[str, Union[str, int]]]:
    """Search Wikipedia for a query and return relevant article titles and snippets.
    
    Args:
        query: Search query string
    
    Returns:
        List of dictionaries with article info (title, pageid, snippet)
    """
    return search_wikipedia(query)

@mcp.tool()
def get_wikipedia_content_tool(page_id: int) -> str:
    """Retrieve the full content of a Wikipedia article by page ID.
    
    Args:
        page_id: Wikipedia page ID
    
    Returns:
        Article content as cleaned text
    """
    return get_wikipedia_content(page_id)

@mcp.tool()
def get_page_sections_tool(page_id: int) -> Tuple[List[str], Dict[str, str]]:
    """Get the list of section titles and their indices for a Wikipedia page.
    
    Args:
        page_id: Wikipedia page ID
    
    Returns:
        Tuple of (section titles list, section index dictionary)
    """
    return get_page_sections(page_id)

@mcp.tool()
def get_section_content_tool(page_id: int, section_index: str) -> str:
    """Get the content of a specific section from a Wikipedia page.
    
    Args:
        page_id: Wikipedia page ID
        section_index: Section index string
    
    Returns:
        Section content as cleaned text
    """
    return get_section_content(page_id, section_index)

@mcp.tool()
def clean_page_html_tool(html_content: str) -> str:
    """Clean Wikipedia HTML content to extract readable text.
    
    Args:
        html_content: HTML content to clean
    
    Returns:
        Cleaned text content
    """
    return clean_page_html(html_content)

@mcp.tool()
def get_multiple_sections_content_tool(page_id: int, section_indices: List[str]) -> Dict[str, str]:
    """Get content from multiple sections of a Wikipedia page in a single call.
    
    Args:
        page_id: Wikipedia page ID
        section_indices: List of section indices to retrieve
        
    Returns:
        Dictionary mapping section indices to their content
    """
    return get_multiple_sections_content(page_id, section_indices)

@mcp.tool()
def call_search_agent_tool(query, context) -> str:
    """
    Invokes the search agent to find information, search the web or Wikipedia, or look up facts.
    Use this for questions like 'What is the capital of France?', 'Summarize the Wikipedia page for AI', 'What is the current weather in Paris?'.
    Args:
        query: The specific question or search term for the search agent.
        context: Optional additional context for the search agent.
    Returns:
        The result from the search agent.
    """
    return call_search_agent(query, context)

# to run the server --> mcp dev mcp_tools_server.py (inside of mcp_server_setup folder)
# or python mcp_tools_server.py
# run the server (do it from client code for prototype, not here)
if __name__ == "__main__":
    mcp.run(transport="stdio")