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

# ---------------- SESSION STATE INIT ----------------
if "query" not in st.session_state:
    st.session_state.query = ""

if "run_analysis" not in st.session_state:
    st.session_state.run_analysis = False

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

    # ---------------- INPUT FIELD ----------------
    def update_query():
        st.session_state.query = st.session_state.input_box

    st.text_input(
        "💬 Ask your question",
        value=st.session_state.query,
        key="input_box",
        on_change=update_query
    )

    # ---------------- ANALYZE BUTTON ----------------
    if st.button("Analyze"):
        st.session_state.run_analysis = True

    # ---------------- RUN ANALYSIS ----------------
    if st.session_state.run_analysis and st.session_state.query:

        st.session_state.run_analysis = False  # reset trigger

        query = st.session_state.query
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

        parsed.setdefault("chart", {"type": "bar", "x": None, "y": None})
        parsed.setdefault("next_questions", [
            "Show summary",
            "Top categories",
            "Trend over time"
        ])

        # ---------------- RUN CODE ----------------
        result_df, error = run_code(parsed["python_code"], df)

        if error:
            st.error(f"⚠️ Code execution error: {error}")
            st.stop()

        # ---------------- OUTPUT ----------------
        st.subheader("🧠 Analysis Steps")
        st.write(parsed["analysis_steps"])

        st.subheader("📊 Result Data")
        st.dataframe(result_df)

        # ---------------- CHART ----------------
        def generate_chart(result_df, chart_info):
            try:
                x = chart_info.get("x")
                y = chart_info.get("y")

                if x not in result_df.columns:
                    x = result_df.columns[0]

                if y not in result_df.columns:
                    y = result_df.columns[1] if len(result_df.columns) > 1 else result_df.columns[0]

                chart_type = chart_info.get("type", "bar")

                if chart_type == "line":
                    return px.line(result_df, x=x, y=y)
                elif chart_type == "scatter":
                    return px.scatter(result_df, x=x, y=y)
                elif chart_type == "pie":
                    return px.pie(result_df, names=x, values=y)
                elif chart_type == "histogram":
                    return px.histogram(result_df, x=x)
                elif chart_type == "box":
                    return px.box(result_df, x=x, y=y)
                elif chart_type == "heatmap":
                    return px.imshow(result_df.corr(numeric_only=True))
                else:
                    return px.bar(result_df, x=x, y=y)

            except Exception as e:
                print("Chart error:", e)
                return None

        fig = generate_chart(result_df, parsed["chart"])

        if fig:
            st.subheader("📊 Visualization")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ Chart generation failed")

        # ---------------- INSIGHTS ----------------
        st.subheader("💡 Insights")
        st.write(parsed["insights"])

        # ---------------- SUGGESTED QUESTIONS ----------------
        st.subheader("🔄 Suggested Next Questions")

        for i, q in enumerate(parsed["next_questions"]):
            if st.button(q, key=f"suggest_{i}"):
                st.session_state.query = q   # ✅ SET QUERY
                st.session_state.input_box = q  # ✅ UPDATE INPUT UI
                st.session_state.run_analysis = True  # ✅ AUTO RUN
                st.rerun()

        # ---------------- MEMORY ----------------
        add_to_memory(query, parsed["insights"])

        # ---------------- DOWNLOAD ----------------
        st.download_button(
            "📥 Download Result",
            result_df.to_csv(index=False),
            "analysis.csv"
        )
