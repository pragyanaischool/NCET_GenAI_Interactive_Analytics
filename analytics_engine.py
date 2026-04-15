def run_code(code, df):
    local_vars = {"df": df}

    try:
        exec(code, {}, local_vars)
        return local_vars.get("result_df", df), None
    except Exception as e:
        return None, str(e)
