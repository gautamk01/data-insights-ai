from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from pydantic import BaseModel
from text_to_sql import handle_question
from viz import line_chart
import pandas as pd
from sse_starlette.sse import EventSourceResponse
import asyncio
from choose_visualization import choose_chart
from formatter import format_for_chart
import json
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI(title="E-commerce AI Agent")

# Define the origins your frontend will run on
# For development, this is typically localhost:3000
origins = [
    "http://localhost:3000", "https://data-insights-ai-puce.vercel.app"
]
# Add the CORS middleware to your app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app.mount("/static", StaticFiles(directory="static"), name="static")


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask_endpoint(payload: Question):
    try:
        result = handle_question(payload.question)
        if not result.get("success", True) or not result.get("sql"):
            return {"answer": result.get("answer", "No answer"), "sql": "", "chart": None}

        sql = result["sql"]
        rows = result.get("data", [])
        chart_url = None

        return {"answer": result.get("answer", str(rows)), "sql": sql, "chart": chart_url}
    except Exception as e:
        return {"answer": f"Error: {e}", "sql": "", "chart": None}


@app.post("/ask/viz")
def ask_viz(payload: Question):
    """Enhanced visualization endpoint with better error handling and logging"""
    try:
        logger.info(f"Processing visualization request: {payload.question}")

        # Get SQL result
        result = handle_question(payload.question)
        logger.debug(f"handle_question result: {result}")

        # If rejected or no data, return early
        if not result.get("success") or not result.get("data"):
            logger.warning(
                "No successful data result - skipping visualization")
            return {
                "answer": result.get("answer", "No data available"),
                "sql": result.get("sql", ""),
                "chart_type": "none",
                "chart_data": None,
                "success": False,
                "debug_info": "No data to visualize"
            }

        rows = result["data"]
        logger.info(f"Got {len(rows)} rows of data")
        logger.debug(f"Sample data: {rows[:2] if rows else 'No rows'}")

        # Choose chart type
        chart_type = choose_chart(payload.question, result["sql"], rows)
        logger.info(f"Selected chart type: {chart_type}")

        # Format chart data
        chart_json = None
        if chart_type != "none":
            chart_json = format_for_chart(rows, chart_type)
            logger.info(f"Chart data formatted: {chart_json is not None}")
            if chart_json:
                logger.debug(f"Chart structure: {list(chart_json.keys())}")

        response = {
            "answer": result["answer"],
            "sql": result["sql"],
            "chart_type": chart_type,
            "chart_data": chart_json,
            "success": True,
            "debug_info": {
                "rows_count": len(rows),
                "columns": list(rows[0].keys()) if rows else [],
                "chart_formatted": chart_json is not None
            }
        }

        logger.info(
            f"Returning response with chart_type={chart_type}, has_chart_data={chart_json is not None}")
        return response

    except Exception as e:
        logger.error(f"Error in ask_viz: {str(e)}", exc_info=True)
        return {
            "answer": f"Error processing visualization: {str(e)}",
            "sql": "",
            "chart_type": "error",
            "chart_data": None,
            "success": False,
            "debug_info": f"Exception: {str(e)}"
        }


@app.get("/ask/stream")
async def ask_stream(question: str):
    try:
        result = handle_question(question)

        async def event_generator():
            # Send SQL first
            sql = result.get("sql", "")
            yield {"data": json.dumps({"type": "sql", "text": sql})}
            await asyncio.sleep(0.3)

            # Send answer
            answer = result.get("answer", "No answer available")
            yield {"data": json.dumps({"type": "answer", "text": answer})}

            # If successful query, also send data
            if result.get("success", False) and result.get("data"):
                yield {"data": json.dumps({"type": "data", "text": str(result["data"])})}

            yield {"data": json.dumps({"type": "done"})}

        return EventSourceResponse(event_generator())
    except Exception as e:
        async def error_generator():
            yield {"data": json.dumps({"type": "error", "text": str(e)})}
            yield {"data": json.dumps({"type": "done"})}
        return EventSourceResponse(error_generator())


@app.get("/")
def root():
    return {"status": "ok"}
