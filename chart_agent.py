import json
import pandas as pd

from llm_client import ask_gemini


class ChartAgent:
    def __init__(self):
        self.chart_prompt = """
        You are a data visualization expert. Given query results, determine the best chart type.
        
        Rules:
        - Time series data → Line chart
        - Product comparisons → Bar chart  
        - Parts of whole → Pie chart
        - Relationships → Scatter plot
        
        Return only JSON:
        {
            "chart_type": "line|bar|pie|scatter|table",
            "config": {
                "x_axis": "column_name",
                "y_axis": "column_name",
                "title": "descriptive_title",
                "sort_by": "column_name",
                "limit": 10
            }
        }
        """

    def generate_chart(self, rows, question, sql_query):
        if not rows:
            return None

        df = pd.DataFrame(rows)

        # Analyze data characteristics
        analysis = {
            "question": question,
            "sql_query": sql_query,
            "columns": list(df.columns),
            "data_types": {col: str(df[col].dtype) for col in df.columns},
            "row_count": len(df),
            "has_dates": any('date' in col.lower() for col in df.columns),
            "numeric_cols": list(df.select_dtypes(include=['number']).columns),
            "sample_rows": df.head(2).to_dict('records')
        }

        # Get AI recommendation
        full_prompt = f"{self.chart_prompt}\n\nData Analysis:\n{json.dumps(analysis, indent=2)}"

        response = ask_gemini(full_prompt)
        chart_config = json.loads(response)

        # Execute chart creation
        return self.create_chart_from_config(df, chart_config)

    def create_chart_from_config(self, df, config):
        chart_type = config['chart_type']

        if chart_type == 'line':
            return self.create_line_chart(df, config)
        elif chart_type == 'bar':
            return self.create_bar_chart(df, config)
        elif chart_type == 'pie':
            return self.create_pie_chart(df, config)
        # ... etc
