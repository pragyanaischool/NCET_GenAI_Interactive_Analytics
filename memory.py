import streamlit as st

def init_memory():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

def add_to_memory(user, assistant):
    st.session_state.chat_history.append({
        "user": user,
        "assistant": assistant
    })

def get_history():
    history = ""
    for h in st.session_state.chat_history:
        history += f"User: {h['user']}\nAssistant: {h['assistant']}\n"
    return history
