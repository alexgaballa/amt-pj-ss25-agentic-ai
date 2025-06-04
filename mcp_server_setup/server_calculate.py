"""Calculate tool wrappers for MCP integration with proper type hints."""
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import List
from calculate import (
    convert_units, add, subtract, multiply, divide,
    calculate_years_between, calculate_days_between, calculate_mean,
    calculate_median, calculate_std_dev, calculate_range,
    evaluate_expression, solve_equation, calculate_age,
    count_word_occurrences, estimate_reading_time,
    kg_to_lb, lb_to_kg, miles_to_km, km_to_miles
)


load_dotenv()

# Create a MCP server instance
mcp = FastMCP(
    name = "Calculate-Server",
    description = "A server for performing various calculations and unit conversions.",
    host = "0.0.0.0",
    port = 8050,
)

# Math operation tools
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

# to run the server --> mcp dev server_calculate.py 
if __name__ == "__main__":
    transport = "stdio"
    # stdio for basic input/output streams on the same machine
    if transport == "stdio":
        print("Running in stdio mode")
        mcp.run(transport= "stdio")
    # remote connection across networks
    elif transport == "sse":
        print("Running in sse mode")
        mcp.run(transport= "sse")
    else:
        raise ValueError("Invalid transport mode. Use 'stdio' or 'sse'.")