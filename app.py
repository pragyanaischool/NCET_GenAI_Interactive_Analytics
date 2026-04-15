import streamlit as st
import pandas as pd
import json
import plotly.express as px

from groq_llm import ask_llm
from prompt_templates import build_prompt
from analytics_engine import run_code
from memory import init_memory, add_to_memory, get_history

st.set_page_config(layout="wide")
st.title(" PragyanAI - GenAI Interactive Data Analytics")
st.image("PragyanAI_Transperent.png")
init_memory()
# ------------------ CSV Upload ------------------
file = st.file_uploader(" Upload CSV", type=["csv"])

if file:
    try:
        df = pd.read_csv(file)
    except:
        df = pd.read_csv(file, encoding="latin1")

    df = df.drop_duplicates()

    st.subheader(" Dataset Preview")
    st.dataframe(df.head())

    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

    # ------------------ Query Input ------------------
    query = st.text_input(" Ask your data question")

    # Handle suggested question click
    if "auto_query" in st.session_state:
        query = st.session_state["auto_query"]

    if st.button("Analyze") and query:

        history = get_history()

        prompt = build_prompt(query, df.columns.tolist(), history)

        messages = [
            {"role": "system", "content": "You are a professional data analyst."},
            {"role": "user", "content": prompt}
        ]

        response = ask_llm(messages)

        try:
            parsed = json.loads(response)
        except:
            st.error("❌ LLM JSON parsing failed")
            st.write(response)
            st.stop()

        # ------------------ Run Code ------------------
        result_df, error = run_code(parsed["python_code"], df)

        if error:
            st.error(f"⚠️ Code execution error: {error}")
            st.stop()

        # ------------------ Analysis ------------------
        st.subheader(" Analysis Steps")
        st.write(parsed["analysis_steps"])

        st.subheader(" Result Data")
        st.dataframe(result_df)

        # ------------------ Chart Engine ------------------
        def generate_chart(result_df, chart_info):
            chart_type = chart_info.get("type", "auto")
            x = chart_info.get("x")
            y = chart_info.get("y")
            color = chart_info.get("color", None)

            try:
                if chart_type == "auto":
                    if result_df.shape[1] == 1:
                        fig = px.histogram(result_df, x=result_df.columns[0])
                    elif result_df.shape[1] == 2:
                        c1, c2 = result_df.columns
                        if result_df[c1].dtype == "object":
                            fig = px.bar(result_df, x=c1, y=c2)
                        else:
                            fig = px.line(result_df, x=c1, y=c2)
                    else:
                        fig = px.scatter(result_df, x=result_df.columns[0], y=result_df.columns[1])

                elif chart_type == "bar":
                    fig = px.bar(result_df, x=x, y=y, color=color)

                elif chart_type == "line":
                    fig = px.line(result_df, x=x, y=y, color=color)

                elif chart_type == "scatter":
                    fig = px.scatter(result_df, x=x, y=y, color=color)

                elif chart_type == "area":
                    fig = px.area(result_df, x=x, y=y, color=color)

                elif chart_type == "histogram":
                    fig = px.histogram(result_df, x=x)

                elif chart_type == "box":
                    fig = px.box(result_df, x=x, y=y)

                elif chart_type == "pie":
                    fig = px.pie(result_df, names=x, values=y)

                elif chart_type == "heatmap":
                    fig = px.imshow(result_df.corr(numeric_only=True), text_auto=True)

                else:
                    fig = px.scatter(result_df, x=x, y=y)

                return fig
            except:
                return None

        chart_info = parsed["chart"]

        # Optional override
        chart_override = st.selectbox(
            " Override Chart Type",
            ["auto","bar","line","scatter","area","histogram","box","pie","heatmap"]
        )

        if chart_override != "auto":
            chart_info["type"] = chart_override

        fig = generate_chart(result_df, chart_info)

        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Chart generation failed")

        # ------------------ Insights ------------------
        st.subheader(" Insights")
        st.write(parsed["insights"])

        # ------------------ Next Questions ------------------
        st.subheader(" Suggested Next Questions")

        for q in parsed["next_questions"]:
            if st.button(q):
                st.session_state["auto_query"] = q

        # ------------------ Save Memory ------------------
        add_to_memory(query, parsed["insights"])

        # ------------------ Download ------------------
        csv = result_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            " Download Result",
            csv,
            "analysis.csv",
            "text/csv"
        )
