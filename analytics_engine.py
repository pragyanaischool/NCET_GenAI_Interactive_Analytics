def run_code(code, df):
    # 🔒 Block unsafe code
    blocked = ["import", "matplotlib", "seaborn", "plt", "__"]

    for word in blocked:
        if word in code:
            return None, f"Blocked unsafe code: {word}"

    local_vars = {"df": df}

    try:
        exec(code, {}, local_vars)
        result_df = local_vars.get("result_df", df)
        return result_df, None
    except Exception as e:
        return None, str(e)
        
