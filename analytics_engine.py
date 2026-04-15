def clean_code(code: str) -> str:
    """
    Cleans LLM-generated code:
    - Removes import statements
    - Removes plotting libraries
    - Removes unsafe keywords
    """

    blocked_keywords = [
        "import",
        "matplotlib",
        "seaborn",
        "plt",
        "__",
        "os.",
        "sys.",
        "subprocess"
    ]

    cleaned_lines = []

    for line in code.split("\n"):
        line_strip = line.strip().lower()

        # Skip unsafe lines
        if any(keyword in line_strip for keyword in blocked_keywords):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def run_code(code: str, df):
    """
    Executes cleaned pandas code safely.
    """

    # 🔧 Step 1: Clean code
    code = clean_code(code)

    # 🔍 Debug (optional)
    # print("CLEANED CODE:\n", code)

    local_vars = {"df": df.copy()}

    try:
        # 🔧 Step 2: Execute code
        exec(code, {}, local_vars)

        # 🔧 Step 3: Ensure result_df exists
        result_df = local_vars.get("result_df", None)

        if result_df is None:
            return df, "⚠️ result_df not created by LLM. Showing original dataset."

        # 🔧 Step 4: Validate type
        import pandas as pd

        if not isinstance(result_df, pd.DataFrame):
            return df, "⚠️ result_df is not a DataFrame."

        # 🔧 Step 5: Clean result_df
        result_df = result_df.drop_duplicates()

        # Limit rows (avoid UI crash)
        if len(result_df) > 1000:
            result_df = result_df.head(1000)

        return result_df, None

    except Exception as e:
        return None, f"❌ Execution error: {str(e)}"
        
