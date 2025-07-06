"""
Modular calculation functions for use in a multi-agent system (e.g., Langchain MCP agents)
This toolkit is intended to be used by agents parsing raw text from sources like Wikipedia.
"""
from dateutil import parser as date_parser
from datetime import datetime
from pint import UnitRegistry
import statistics
import sympy as sp
import re
from typing import List, Union, Optional
import sys
import os

# Add parent directory to path to enable relative imports
# This allows importing from siblings of mcp_server_setup directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ureg = UnitRegistry()

# === UNIT CONVERSION ===
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    try:
        quantity = value * ureg(from_unit)
        converted = quantity.to(to_unit)
        return f"{converted.magnitude:.4g} {converted.units}"
    except Exception as e:
        return f"Conversion error: {str(e)}"

# === TIME DELTA CALCULATIONS ===
def calculate_years_between(start_date_str: str, end_date_str: str) -> Union[int, str]:
    try:
        start = date_parser.parse(start_date_str)
        end = date_parser.parse(end_date_str)
        return round((end - start).days / 365.25)
    except Exception as e:
        return f"Date parsing error: {str(e)}"

def calculate_days_between(start_date_str: str, end_date_str: str) -> Union[int, str]:
    try:
        start = date_parser.parse(start_date_str)
        end = date_parser.parse(end_date_str)
        return (end - start).days
    except Exception as e:
        return f"Date parsing error: {str(e)}"

# === STATISTICAL ANALYSIS ===
def calculate_mean(values: List[float]) -> float:
    return statistics.mean(values)

def calculate_median(values: List[float]) -> float:
    return statistics.median(values)

def calculate_std_dev(values: List[float]) -> float:
    return statistics.stdev(values)

def calculate_range(values: List[float]) -> float:
    return max(values) - min(values)

# === BASIC ARITHMETIC EXPRESSION EVALUATOR ===
def evaluate_expression(expr: str) -> Union[float, str]:
    """Evaluate simple math expressions from text like '3 + 4 * (2 - 1)'"""
    try:
        expr_clean = re.sub(r"[^0-9\+\-\*/\(\)\. ]", "", expr)
        result = eval(expr_clean)
        return result
    except Exception as e:
        return f"Evaluation error: {str(e)}"

# === SYMBOLIC SOLVER (e.g., physics equations) ===
def solve_equation(equation_str: str, target_var: str) -> Union[str, float]:
    try:
        lhs, rhs = equation_str.split("=")
        lhs_expr = sp.sympify(lhs)
        rhs_expr = sp.sympify(rhs)
        solution = sp.solve(sp.Eq(lhs_expr, rhs_expr), sp.Symbol(target_var))
        return str(solution[0]) if solution else "No solution found"
    except Exception as e:
        return f"Equation solving error: {str(e)}"

# === HUMAN AGE CALCULATOR ===
def calculate_age(birth_date_str: str) -> Union[int, str]:
    try:
        birth = date_parser.parse(birth_date_str)
        today = datetime.now()
        return round((today - birth).days / 365.25)
    except Exception as e:
        return f"Age calculation error: {str(e)}"

# === WORD FREQUENCY COUNT (basic NLP utility) ===
def count_word_occurrences(text: str, word: str) -> int:
    return text.lower().split().count(word.lower())

# === READING TIME ESTIMATOR ===
def estimate_reading_time(text: str, wpm: int = 220) -> str:
    words = len(text.split())
    minutes = words / wpm
    return f"Estimated reading time: {minutes:.2f} minutes"

# === MASS/WEIGHT CONVERTER (kg <-> lb) ===
def kg_to_lb(kg: float) -> float:
    return kg * 2.20462

def lb_to_kg(lb: float) -> float:
    return lb / 2.20462

# === LENGTH CONVERTER (miles <-> km) ===
def miles_to_km(miles: float) -> float:
    return miles * 1.60934

def km_to_miles(km: float) -> float:
    return km / 1.60934

# === BASIC ARITHMETIC OPERATIONS ===
def add(numbers: List[float]) -> float:
    """Add a list of numbers together."""
    return sum(numbers)

def subtract(minuend: float, subtrahend: float) -> float:
    """Subtract one number from another."""
    return minuend - subtrahend

def multiply(numbers: List[float]) -> float:
    """Multiply a list of numbers together."""
    result = 1
    for number in numbers:
        result *= number
    return result

def divide(dividend: float, divisor: float) -> Union[float, str]:
    """Divide one number by another."""
    try:
        return dividend / divisor
    except ZeroDivisionError:
        return "Division by zero is not allowed."

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
    from agents.mcp_sub_agent_reason import run_reason_agent  # Import here to avoid circular import issues
    print("DEBUG:", run_reason_agent, type(run_reason_agent))
    
    if context is None:
        context = {}
    print(f"\nOrchestrator: Calling Reason Agent with query: '{query}' and context: {context}")
    
    result = await run_reason_agent(user_query=query, context=context, verbose=False)
    print(f"Orchestrator: Reason Agent returned: '{result}'")
    return result