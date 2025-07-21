# main.py
from fastapi.staticfiles import StaticFiles
from viz import plot_daily_revenue
from viz import auto_chart
from fastapi import FastAPI
from pydantic import BaseModel
from text_to_sql import handle_question, execute_sql
from viz import line_chart
import pandas as pd
from sse_starlette.sse import EventSourceResponse
import asyncio
import json


app = FastAPI(title="E-commerce AI Agent")


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
        chart_url = None   # <-- charts off

        return {"answer": result.get("answer", str(rows)), "sql": sql, "chart": chart_url}
    except Exception as e:
        return {"answer": f"Error: {e}", "sql": "", "chart": None}


@app.post("/ask/chart")
def ask_chart(payload: Question):
    try:
        result = handle_question(payload.question)

        # If query was rejected, return error
        if not result.get("success", True) or not result.get("sql"):
            return {
                "answer": result.get("answer", "Cannot generate chart"),
                "chart": None
            }

        sql = result["sql"]
        rows = result.get("data", [])

        if not rows:
            return {"answer": "No data available for chart", "chart": None}

        df = pd.DataFrame(rows)
        if "date" in df.columns and "revenue" in df.columns:
            chart_url = line_chart(df, "date", "revenue", "Revenue trend")
            return {"answer": "Chart generated", "chart": chart_url}
        return {"answer": str(rows), "chart": None}
    except Exception as e:
        return {"answer": f"Error: {e}", "chart": None}


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
