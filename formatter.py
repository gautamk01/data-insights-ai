import pandas as pd
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


def format_for_chart(rows: List[Dict], chart_type: str) -> Optional[Dict[str, Any]]:
    """
    Format data rows for different chart types.

    Args:
        rows: List of dictionaries representing data rows
        chart_type: Type of chart ('bar', 'line', 'pie', 'scatter', 'none')

    Returns:
        Formatted data dictionary or None if formatting fails
    """
    if not rows or chart_type == "none":
        return None

    try:
        df = pd.DataFrame(rows)
        logger.debug(f"Formatting {len(rows)} rows for {chart_type} chart")
        logger.debug(f"Columns: {list(df.columns)}")

        if chart_type == "bar":
            return _format_bar_chart(df)
        elif chart_type == "horizontal_bar":
            return _format_horizontal_bar_chart(df)
        elif chart_type == "line":
            return _format_line_chart(df)
        elif chart_type == "pie":
            return _format_pie_chart(df)
        elif chart_type == "scatter":
            return _format_scatter_chart(df)
        else:
            logger.warning(f"Unknown chart type: {chart_type}")
            return None

    except Exception as e:
        logger.error(f"Error formatting chart data: {e}")
        return None


def _format_bar_chart(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """Format data for bar chart."""
    if len(df.columns) < 2:
        return None

    # Use first column as labels, second as values
    labels_col = df.columns[0]
    values_col = df.columns[1]

    labels = df[labels_col].astype(str).tolist()
    values = pd.to_numeric(df[values_col], errors='coerce').fillna(0).tolist()

    return {
        "type": "bar",
        "labels": labels,
        "datasets": [{
            "label": str(values_col).title(),
            "data": values,
            "backgroundColor": [
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 99, 132, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)',
                'rgba(255, 159, 64, 0.6)'
            ] * (len(values) // 6 + 1),
            "borderColor": [
                'rgba(54, 162, 235, 1)',
                'rgba(255, 99, 132, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ] * (len(values) // 6 + 1),
            "borderWidth": 1
        }]
    }


def _format_horizontal_bar_chart(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """Format data for horizontal bar chart."""
    bar_data = _format_bar_chart(df)
    if bar_data:
        bar_data["type"] = "horizontalBar"
    return bar_data


def _format_line_chart(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """Format data for line chart."""
    if len(df.columns) < 2:
        return None

    x_col = df.columns[0]
    y_col = df.columns[1]

    x_values = df[x_col].tolist()
    y_values = pd.to_numeric(df[y_col], errors='coerce').fillna(0).tolist()

    return {
        "type": "line",
        "labels": [str(x) for x in x_values],
        "datasets": [{
            "label": str(y_col).title(),
            "data": y_values,
            "borderColor": 'rgba(75, 192, 192, 1)',
            "backgroundColor": 'rgba(75, 192, 192, 0.2)',
            "borderWidth": 2,
            "fill": False,
            "tension": 0.1
        }]
    }


def _format_pie_chart(df: pd.DataFrame, top_n: int = 15) -> Optional[Dict[str, Any]]:
    """Format data for pie chart with better error handling."""
    if len(df.columns) < 2:
        return None

    # Handle unnamed columns
    df.columns = [f'col_{i}' if f'sum(' in str(col).lower() and ')' in str(col)
                  else str(col) for i, col in enumerate(df.columns)]

    labels_col = df.columns[0]
    values_col = df.columns[1]

    try:
        # Convert values to numeric first for sorting
        df_clean = df.copy()
        df_clean[values_col] = pd.to_numeric(
            df_clean[values_col], errors='coerce').fillna(0)

        # Remove zero or negative values
        df_clean = df_clean[df_clean[values_col] > 0]

        if len(df_clean) == 0:
            return None

        # Sort by values and take top N
        df_sorted = df_clean.sort_values(values_col, ascending=False)

        if len(df_sorted) > top_n:
            top_items = df_sorted.head(top_n)
            others_sum = df_sorted.tail(
                len(df_sorted) - top_n)[values_col].sum()

            # Add "Others" category
            labels = top_items[labels_col].astype(str).tolist() + ['Others']
            values = top_items[values_col].tolist() + [others_sum]
        else:
            labels = df_sorted[labels_col].astype(str).tolist()
            values = df_sorted[values_col].tolist()

        return {
            "type": "pie",
            "labels": labels,
            "datasets": [{
                "data": values,
                "backgroundColor": [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40', '#C9CBCF', '#4BC0C0',
                    '#FF6384', '#C9CBCF', '#FF6B6B', '#4ECDC4',
                    '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'
                ] * 10,  # Repeat colors if needed
                "borderWidth": 2,
                "borderColor": '#ffffff'
            }]
        }
    except Exception as e:
        logger.error(f"Error in pie chart formatting: {e}")
        return None


def _format_scatter_chart(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """Format data for scatter chart."""
    if len(df.columns) < 2:
        return None

    x_col = df.columns[0]
    y_col = df.columns[1]

    x_values = pd.to_numeric(df[x_col], errors='coerce').fillna(0)
    y_values = pd.to_numeric(df[y_col], errors='coerce').fillna(0)

    scatter_data = [{"x": x, "y": y} for x, y in zip(x_values, y_values)]

    return {
        "type": "scatter",
        "datasets": [{
            "label": f"{x_col} vs {y_col}",
            "data": scatter_data,
            "backgroundColor": 'rgba(255, 99, 132, 0.6)',
            "borderColor": 'rgba(255, 99, 132, 1)',
            "borderWidth": 1
        }],
        "options": {
            "scales": {
                "x": {"title": {"display": True, "text": str(x_col).title()}},
                "y": {"title": {"display": True, "text": str(y_col).title()}}
            }
        }
    }
