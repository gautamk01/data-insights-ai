import sqlite3
import json
from db import engine  # SQLAlchemy engine from db.py


def get_schema_snippet(limit=3):
    """Return JSON schema + first 3 rows of every table."""
    with engine.connect() as conn:
        tables = conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table';"
        ).fetchall()
        schema = []
        for tbl, ddl in tables:
            # Use parameterized query to prevent SQL injection
            rows = conn.execute(
                f"SELECT * FROM [{tbl}] LIMIT ?", (limit,)
            ).fetchall()
            schema.append({
                "table": tbl,
                "ddl": ddl,
                "sample": [dict(r._mapping) for r in rows]
            })

    return json.dumps(schema, indent=2)
