# text_to_sql.py
import json
import re
from llm_client import ask_gemini
from db import SessionLocal
from sqlalchemy import text
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load prompts and system prompt
with open("prompts/override.json") as f:
    prompts = json.load(f)
with open("prompts/system_prompt.md") as f:
    SYSTEM = f.read()


def build_prompt(question: str) -> str:
    return f"{SYSTEM}\n\nQ: {question}\nA:"


def text_to_sql(question: str):
    """Convert natural language question to SQL query"""
    try:
        q = question.lower()

        # Handle hardcoded overrides
        if "highest cpc" in q:
            return prompts["highest_cpc"], "Item with highest cost per click"

        # Build and send prompt
        prompt = build_prompt(question)
        logger.debug(f"Sending prompt to Gemini: {prompt[:200]}...")

        raw = ask_gemini(prompt)
        logger.debug(f"Raw Gemini response: {raw}")

        # Check if response is None or empty
        if not raw:
            raise ValueError("Gemini returned empty response")

        # Try to extract JSON with improved regex
        # Look for JSON block that might span multiple lines
        match = re.search(
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw, flags=re.DOTALL)

        if not match:
            logger.error(f"No JSON found in response: {raw}")
            raise ValueError("No valid JSON found in LLM response")

        json_str = match.group()
        logger.debug(f"Extracted JSON: {json_str}")

        # Parse JSON
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}, JSON: {json_str}")
            raise ValueError(f"Invalid JSON in LLM response: {e}")

        # Validate JSON structure
        if not isinstance(data, dict):
            raise ValueError("LLM response is not a JSON object")

        if "sql" not in data or "explanation" not in data:
            raise ValueError(
                "LLM response missing required 'sql' or 'explanation' keys")

        # Handle case where SQL is null (valid rejection)
        sql = data["sql"]
        explanation = data["explanation"]

        if sql is None:
            # This is a valid rejection from the LLM
            return None, explanation

        # Validate SQL is a string
        if not isinstance(sql, str):
            raise ValueError(f"SQL should be string or null, got: {type(sql)}")

        # Clean and return
        cleaned_sql = sql.strip()
        if not cleaned_sql:
            return None, explanation

        return cleaned_sql, explanation

    except Exception as e:
        logger.error(f"Error in text_to_sql: {e}")
        # Re-raise with context
        raise ValueError(f"Failed to convert question to SQL: {str(e)}")


def execute_sql(sql: str):
    """Execute SQL query and return results"""
    if sql is None:
        return []

    try:
        with SessionLocal() as session:
            logger.debug(f"Executing SQL: {sql}")
            rows = session.execute(text(sql)).fetchall()
            result = [dict(r._mapping) for r in rows]
            logger.debug(f"SQL result: {result}")
            return result
    except Exception as e:
        logger.error(f"SQL execution error: {e}")
        raise ValueError(f"Failed to execute SQL: {str(e)}")


def handle_question(question: str):
    """Main handler that processes question and returns structured response"""
    try:
        # Convert to SQL
        sql, explanation = text_to_sql(question)

        # Handle rejected queries (sql is None)
        if sql is None:
            return {
                "answer": explanation,
                "sql": "",
                "chart": None,
                "success": False
            }

        # Execute SQL
        results = execute_sql(sql)

        # Format response
        if not results:
            answer = "No data found for your query."
        elif len(results) == 1 and len(results[0]) == 1:
            # Single value result
            value = list(results[0].values())[0]
            answer = f"Result: {value}"
        else:
            # Multiple results
            answer = f"Found {len(results)} results: {results}"

        return {
            "answer": answer,
            "sql": sql,
            "chart": None,  # You can add chart generation logic here
            "success": True,
            "data": results
        }

    except Exception as e:
        logger.error(f"Error handling question '{question}': {e}")
        return {
            "answer": f"Error: {str(e)}",
            "sql": "",
            "chart": None,
            "success": False
        }


if __name__ == "__main__":
    # Test queries
    test_questions = [
        "What is my total sales?",
        "Which product had the highest CPC?",
        "Generate a complete performance report",  # Should be rejected
        "Show me profit margins"  # Should be rejected
    ]

    for q in test_questions:
        print(f"\nTesting: {q}")
        result = handle_question(q)
        print(f"Result: {result}")
