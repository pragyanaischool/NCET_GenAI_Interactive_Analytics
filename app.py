import streamlit as st
import pandas as pd
import json
import plotly.express as px

from groq_llm import ask_llm
from prompt_templates import build_prompt
from analytics_engine import run_code
from memory import init_memory, add_to_memory, get_history

st.set_page_config(layout="wide")
st.title("🧠 GenAI Interactive Data Analytics")

init_memory()

# ---------------- CSV Upload ----------------
file = st.file_uploader("📂 Upload CSV", type=["csv"])

if file:
    try:
        df = pd.read_csv(file)
    except:
        df = pd.read_csv(file, encoding="latin1")

    df = df.drop_duplicates()

    st.subheader("📊 Dataset Preview")
    st.dataframe(df.head())

    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

    # ---------------- Suggested Query Handling ----------------
    if "auto_query" in st.session_state:
        default_query = st.session_state["auto_query"]
    else:
        default_query = ""

    query = st.text_input("💬 Ask your question", value=default_query)

    if st.button("Analyze") and query:

        history = get_history()

        prompt = build_prompt(query, df.columns.tolist(), history)

        messages = [
            {"role": "system", "content": "You are a professional data analyst."},
            {"role": "user", "content": prompt}
        ]

        response = ask_llm(messages)

        # ---------------- JSON Parse ----------------
        try:
            parsed = json.loads(response)
        except:
            st.error("❌ JSON parsing failed")
            st.write(response)
            st.stop()

        # ---------------- Defaults ----------------
        if "chart" not in parsed:
            parsed["chart"] = {"type": "bar", "x": None, "y": None}

        if "next_questions" not in parsed:
            parsed["next_questions"] = [
                "Show summary",
                "Top categories",
                "Trend over time"
            ]

        # ---------------- Run Code ----------------
        result_df, error = run_code(parsed["python_code"], df)

        if error:
            st.error(f"⚠️ Code execution error: {error}")
            st.stop()

        # ---------------- Output ----------------
        st.subheader("🧠 Analysis Steps")
        st.write(parsed["analysis_steps"])

        st.subheader("📊 Result Data")
        st.dataframe(result_df)

        # ---------------- Chart Engine ----------------
        def generate_chart(result_df, chart_info):
            try:
                chart_type = chart_info.get("type", "auto")
                x = chart_info.get("x")
                y = chart_info.get("y")

                # Fix columns
                if x not in result_df.columns:
                    x = result_df.columns[0]

                if y not in result_df.columns:
                    y = result_df.columns[1] if len(result_df.columns) > 1 else result_df.columns[0]

                if chart_type == "bar":
                    fig = px.bar(result_df, x=x, y=y)
                elif chart_type == "line":
                    fig = px.line(result_df, x=x, y=y)
                elif chart_type == "scatter":
                    fig = px.scatter(result_df, x=x, y=y)
                elif chart_type == "pie":
                    fig = px.pie(result_df, names=x, values=y)
                elif chart_type == "histogram":
                    fig = px.histogram(result_df, x=x)
                elif chart_type == "box":
                    fig = px.box(result_df, x=x, y=y)
                elif chart_type == "heatmap":
                    fig = px.imshow(result_df.corr(numeric_only=True))
                else:
                    fig = px.bar(result_df, x=x, y=y)

                return fig
            except Exception as e:
                print("Chart error:", e)
                return None

        chart_info = parsed["chart"]

        chart_override = st.selectbox(
            "📊 Override Chart Type",
            ["auto","bar","line","scatter","pie","histogram","box","heatmap"]
        )

        if chart_override != "auto":
            chart_info["type"] = chart_override

        fig = generate_chart(result_df, chart_info)

        if fig is not None:
            st.subheader("📊 Visualization")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ Chart generation failed")
            st.write("Chart Info:", chart_info)
            st.write("Columns:", result_df.columns.tolist())

        # ---------------- Insights ----------------
        st.subheader("💡 Insights")
        st.write(parsed["insights"])

        # ---------------- Suggested Questions ----------------
        st.subheader("🔄 Suggested Next Questions")

        for i, q in enumerate(parsed["next_questions"]):
            if st.button(q, key=f"suggest_{i}"):
                st.session_state["auto_query"] = q
                st.rerun()

        # ---------------- Debug ----------------
        with st.expander("🔍 Debug Info"):
            st.write(parsed)
            st.write("Columns:", result_df.columns.tolist())

        # ---------------- Memory ----------------
        add_to_memory(query, parsed["insights"])

        # ---------------- Download ----------------
        csv = result_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Download Result",
            csv,
            "analysis.csv",
            "text/csv"
        )
        
