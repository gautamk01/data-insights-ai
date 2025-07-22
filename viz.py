# viz.py
from sqlalchemy import text
from db import SessionLocal
import pandas as pd
import matplotlib.pyplot as plt
import os
import uuid
import matplotlib
import seaborn as sns
matplotlib.use("Agg")  # headless


def line_chart(df, x, y, title):
    plt.figure(figsize=(6, 3))
    plt.plot(df[x], df[y])
    plt.title(title)
    path = f"static/charts/{uuid.uuid4()}.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.savefig(path)
    plt.close()
    return path


STATIC_DIR = "static/charts"
os.makedirs(STATIC_DIR, exist_ok=True)


def plot_daily_revenue():
    with SessionLocal() as s:
        rows = s.execute(text("""
            SELECT date, SUM(ad_sales) AS revenue
            FROM ad_sales
            GROUP BY date
            ORDER BY date
        """)).fetchall()
    df = pd.DataFrame(rows, columns=["date", "revenue"])
    plt.figure(figsize=(6, 3))
    plt.plot(df["date"], df["revenue"])
    plt.title("Daily Revenue")
    plt.xticks(rotation=45)
    path = f"{STATIC_DIR}/{uuid.uuid4()}.png"
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return "/" + path


def auto_chart(rows):
    if not rows:
        return None
    df = pd.DataFrame(rows)
    cols = set(df.columns)

    # ① date + numeric → line
    if "date" in cols:
        y = (cols & {"revenue", "sales", "spend", "clicks"}).pop()
        return line_chart(df, "date", y, f"{y.title()} over time")

    # ② item_id + numeric → bar
    if "item_id" in cols:
        y = (cols & {"cpc", "revenue", "sales"}).pop()
        plt.figure(figsize=(6, 3))
        sns.barplot(data=df.head(10), x="item_id", y=y)
        path = f"{STATIC_DIR}/{uuid.uuid4()}.png"
        plt.savefig(path)
        plt.close()
        return "/" + path

    return None
