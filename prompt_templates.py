def build_prompt(user_query, df_columns, history):
    return f"""
You are an expert Data Analyst.

Dataset columns: {df_columns}

Conversation history:
{history}

User question:
{user_query}

Return STRICT JSON:

{{
 "analysis_steps": "...",
 "python_code": "... (must create result_df)",
 "chart": {{
    "type": "bar/line/scatter/pie/histogram/box/heatmap/auto",
    "x": "column",
    "y": "column"
 }},
 "insights": "...",
 "next_questions": ["Q1", "Q2", "Q3"]
}}

Rules:
- Use pandas only
- DO NOT import anything
- DO NOT use matplotlib or seaborn
- result_df must be created
"""
