# from db import SessionLocal
# from sqlalchemy import text   # ← add this

# with SessionLocal() as session:
#     result = session.execute(
#         text("SELECT name FROM sqlite_master WHERE type='table';"))
#     print("Tables found:", [row[0] for row in result])

from llm_client import ask_gemini
print(ask_gemini("Reply with 'hello'"))
