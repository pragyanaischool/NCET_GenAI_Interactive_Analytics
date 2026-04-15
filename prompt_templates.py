def build_prompt(user_query, df_columns, history):
    return f"""
You are a highly skilled Data Analyst working with a pandas dataframe.

DATASET COLUMNS:
{df_columns}

CONVERSATION HISTORY:
{history}

USER QUESTION:
{user_query}

STRICT RULES:
- Output ONLY valid JSON
- DO NOT use markdown
- DO NOT use 'import'
- DO NOT use matplotlib / seaborn
- DataFrame is already df
- ONLY pandas operations
- MUST create result_df

OUTPUT:

{{
 "analysis_steps": "...",
 "python_code": "...",
 "chart": {{
    "type": "bar/line/scatter/pie/histogram/box/heatmap/auto",
    "x": "column",
    "y": "column"
 }},
 "insights": "...",
 "next_questions": ["Q1","Q2","Q3"]
}}
"""
