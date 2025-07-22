from llm_client import ask_gemini
import textwrap
import re
import logging

logger = logging.getLogger(__name__)

PROMPT = textwrap.dedent("""
You are an AI assistant that recommends appropriate data visualizations.
Based on the user's question, SQL query, and query results, suggest the most suitable type of graph or chart to visualize the data.

Available chart types and their use cases:
- bar: comparing categorical data (e.g., sales by product, revenue by region)
- horizontal_bar: few categories with long names or large value disparities
- line: trends over time (e.g., daily sales, monthly revenue)
- pie: proportions of a whole (e.g., market share, category breakdown)
- scatter: relationship between two continuous variables
- none: no chart needed (single values, text data, or unsuitable for visualization)

Question: {question}
SQL: {sql}
Sample data (first 3 rows): {rows}
Data has {num_rows} rows and {num_cols} columns.

Respond with ONLY the chart type name (bar, line, pie, scatter, or none) and nothing else.
""")


def choose_chart(question: str, sql: str, rows: list) -> str:
    """
    Choose the most appropriate chart type based on question, SQL, and data.
    Returns one of: 'bar', 'horizontal_bar', 'line', 'pie', 'scatter', 'none'
    """
    if not rows or len(rows) == 0:
        return "none"

    num_rows = len(rows)
    num_cols = len(rows[0]) if rows else 0

    logger.debug(f"Choosing chart for {num_rows} rows, {num_cols} columns")

    # Quick heuristic checks first (faster than LLM)
    chart_type = _quick_heuristics(question, sql, rows, num_rows, num_cols)
    if chart_type != "unknown":
        logger.debug(f"Quick heuristic chose: {chart_type}")
        return chart_type

    # Fall back to LLM for complex cases
    try:
        preview = str(rows[:3])
        prompt = PROMPT.format(
            question=question,
            sql=sql,
            rows=preview,
            num_rows=num_rows,
            num_cols=num_cols
        )

        raw_response = ask_gemini(prompt)
        logger.debug(f"LLM raw response: {repr(raw_response)}")

        if not raw_response:
            return "none"

        # Extract chart type from response
        chart_type = _extract_chart_type(raw_response)
        logger.debug(f"Extracted chart type: {chart_type}")

        return chart_type

    except Exception as e:
        logger.error(f"Error in LLM chart selection: {e}")
        return "none"


def _quick_heuristics(question: str, sql: str, rows: list, num_rows: int, num_cols: int) -> str:
    """
    Fast heuristic rules to determine chart type without LLM.
    Returns 'unknown' if heuristics can't decide.
    """
    question_lower = question.lower()
    sql_lower = sql.lower()

    # Single value results - no chart needed
    if num_rows == 1 and num_cols == 1:
        return "none"

    # PRIORITIZE PIE CHARTS FOR DISTRIBUTION QUESTIONS
    # Check for proportion/percentage keywords FIRST
    pie_keywords = ['distribution', 'breakdown', 'share',
                    'proportion', 'percentage', 'split', 'composition', 'allocation']
    if any(keyword in question_lower for keyword in pie_keywords):
        if num_cols == 2:  # We have category + value columns
            # Allow more rows for distribution questions (up to 15 instead of 8)
            if num_rows <= 15:
                return "pie"
            # Even with many rows, still prefer pie for explicit distribution questions
            elif 'distribution' in question_lower or 'breakdown' in question_lower:
                return "pie"

    # Time series detection
    if num_cols == 2:
        first_col = list(rows[0].keys())[0] if isinstance(
            rows[0], dict) else "col1"

        # Check for date/time columns
        if any(keyword in first_col.lower() for keyword in ['date', 'time', 'day', 'month', 'year']):
            return "line"

        # Check for time-related keywords in question
        if any(keyword in question_lower for keyword in ['trend', 'over time', 'daily', 'monthly', 'weekly', 'timeline']):
            return "line"

    # Comparison keywords suggest bar chart
    if any(keyword in question_lower for keyword in ['compare', 'comparison', 'vs', 'versus', 'each', 'by category', 'top', 'highest', 'lowest']):
        if num_cols == 2:  # Category + value
            return "bar"

    # Default for 2 columns with reasonable number of rows
    if num_cols == 2 and 2 <= num_rows <= 20:
        return "bar"

    return "unknown"


def _extract_chart_type(raw_response: str) -> str:
    """
    Extract chart type from LLM response.
    """
    if not raw_response:
        return "none"

    response = raw_response.lower().strip()

    # Valid chart types
    valid_types = ['bar', 'horizontal_bar', 'line', 'pie', 'scatter', 'none']

    # Look for exact matches first
    for chart_type in valid_types:
        if chart_type in response:
            return chart_type

    # If no exact match, try to extract from common patterns
    # Look for "Recommended Visualization: bar" pattern
    match = re.search(r'recommended.*?visualization.*?:?\s*(\w+)', response)
    if match:
        extracted = match.group(1).lower()
        if extracted in valid_types:
            return extracted

    # Look for standalone chart type words
    words = response.split()
    for word in words:
        clean_word = re.sub(r'[^\w]', '', word.lower())
        if clean_word in valid_types:
            return clean_word

    return "none"
