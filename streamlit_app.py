import os

import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

from assistant import create_agent

load_dotenv()

st.set_page_config(page_title="Glass Chat")
st.title("Glass Chat")
st.caption("Chat with Groq, with optional DuckDuckGo web search.")

if "search_enabled" not in st.session_state:
    st.session_state.search_enabled = True

search_label = (
    "Turn DuckDuckGo search off"
    if st.session_state.search_enabled
    else "Turn DuckDuckGo search on"
)
if st.button(search_label):
    st.session_state.search_enabled = not st.session_state.search_enabled

api_key = os.getenv("GROQ_API_KEY", "")
if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except (KeyError, StreamlitSecretNotFoundError):
        api_key = ""
if not api_key:
    st.error("GROQ_API_KEY is not configured. Add it to Streamlit secrets or your local .env file.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "agents" not in st.session_state:
    st.session_state.agents = {}

with st.sidebar:
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.agents = {}
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Message Glass Chat")
if prompt:
    search = st.session_state.search_enabled
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if search not in st.session_state.agents:
        st.session_state.agents[search] = create_agent(search, api_key=api_key)
    agent = st.session_state.agents[search]
    with st.chat_message("assistant"):
        try:
            response = st.write_stream(
                str(chunk.content)
                for chunk in agent.run(prompt, stream=True)
                if chunk.content
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )
        except Exception as error:
            st.error(f"Chat request failed: {error}")
