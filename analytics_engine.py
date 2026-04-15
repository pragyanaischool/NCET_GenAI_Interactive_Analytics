def clean_code(code: str) -> str:
    """
    Clean and sanitize LLM-generated Python code.

    Fixes:
    - Removes unsafe imports
    - Fixes escape characters (\n, \", \')
    - Removes broken line continuation '\'
    - Strips unwanted characters
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

        line = line.strip()

        # 🔒 Skip unsafe lines
        if any(word in line.lower() for word in blocked_keywords):
            continue

        # 🔥 Fix escaped characters
        line = line.replace('\\"', '"')
        line = line.replace("\\'", "'")

        # 🔥 Remove bad line continuation "\"
        if line.endswith("\\"):
            line = line[:-1]

        # 🔥 Remove stray semicolons
        line = line.replace(";", "")

        if line:
            cleaned_lines.append(line)

    cleaned_code = "\n".join(cleaned_lines)

    return cleaned_code


def validate_code(code: str) -> str:
    """
    Additional validation and fixes:
    - Replace escaped newlines
    - Remove double backslashes
    """

    code = code.replace("\\n", "\n")
    code = code.replace("\\\\", "\\")

    return code


def run_code(code: str, df):
    """
    Execute cleaned LLM-generated pandas code safely.
    """

    import pandas as pd

    try:
        # ---------------- CLEAN CODE ----------------
        code = clean_code(code)
        code = validate_code(code)

        # 🔍 Debug (optional)
        # print("FINAL CODE:\n", code)

        # ---------------- EXECUTION ENV ----------------
        local_vars = {"df": df.copy()}

        # ---------------- EXECUTE ----------------
        exec(code, {}, local_vars)

        result_df = local_vars.get("result_df", None)

        # ---------------- VALIDATION ----------------
        if result_df is None:
            return df, "⚠️ result_df not created by LLM. Showing original dataset."

        if not isinstance(result_df, pd.DataFrame):
            return df, "⚠️ result_df is not a valid DataFrame."

        # ---------------- CLEAN RESULT ----------------
        result_df = result_df.drop_duplicates()

        # Limit rows (prevent UI crash)
        if len(result_df) > 1000:
            result_df = result_df.head(1000)

        return result_df, None

    except Exception as e:
        return None, f"❌ Execution error: {str(e)}"
