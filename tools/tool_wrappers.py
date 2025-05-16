from langchain_core.tools import tool
from tools.calculate import convert_units, add, subtract, multiply, divide, calculate_years_between, calculate_days_between, calculate_mean, calculate_median, calculate_std_dev, calculate_range, evaluate_expression, solve_equation, calculate_age, count_word_occurrences, estimate_reading_time, kg_to_lb, lb_to_kg, miles_to_km, km_to_miles
from tools.wiki_search import search_wikipedia, get_wikipedia_content, clean_page_html


@tool
def convert_units_tool(value: float, from_unit: str, to_unit: str) -> float:
    """Convert a numerical value between different units."""
    return convert_units(value, from_unit, to_unit)

@tool
def add_tool(numbers: list) -> float:
    """Add a list of numbers together."""
    return add(numbers)

@tool
def subtract_tool(minuend: float, subtrahend: float) -> float:
    """Subtract one number from another."""
    return subtract(minuend, subtrahend)

@tool
def multiply_tool(numbers: list) -> float:
    """Multiply a list of numbers together."""
    return multiply(numbers)

@tool
def divide_tool(dividend: float, divisor: float) -> float:
    """Divide one number by another."""
    return divide(dividend, divisor)

@tool
def search_wikipedia_tool(query: str) -> dict:
    """Search Wikipedia for a query and return relevant article titles and snippets."""
    return search_wikipedia(query)

@tool
def get_wikipedia_content_tool(page_id: int) -> str:
    """Retrieve the full content of a Wikipedia article by page ID."""
    return get_wikipedia_content(page_id)

@tool
def clean_page_html_tool(html_content: str) -> str:
    """Clean Wikipedia HTML content to extract readable text."""
    return clean_page_html(html_content)

# Aggregate all tools
calculation_tools = [
    convert_units_tool,
    add_tool,
    subtract_tool,
    multiply_tool,
    divide_tool
]

wikipedia_tools = [
    search_wikipedia_tool,
    get_wikipedia_content_tool,
    clean_page_html_tool
]

if __name__ == "__main__":
    # Example usage of one of the tools (e.g., add)
    numbers = [1, 2, 3, 4]
    result = add_tool(numbers)
    print(f"Sum of {numbers} is {result}")