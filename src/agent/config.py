import os
import streamlit as st
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI

def get_secret(key: str) -> str:
    value = st.secrets.get(key)
    if not value:
        st.error(f"Missing secret: {key}. Add it to .streamlit/secrets.toml")
        st.stop()
    return value

os.environ["TAVILY_API_KEY"] = get_secret("TAVILY_API_KEY")
os.environ["OPENAI_API_KEY"] = get_secret("OPENAI_API_KEY")

os.environ["LANGSMITH_TRACING"] = st.secrets.get("LANGSMITH_TRACING", "true")
os.environ["LANGSMITH_ENDPOINT"] = st.secrets.get("LANGSMITH_ENDPOINT", "https://eu.api.smith.langchain.com")
os.environ["LANGSMITH_PROJECT"] = st.secrets.get("LANGSMITH_PROJECT", "AI_Research_Agent")
os.environ["LANGSMITH_API_KEY"] = get_secret("LANGSMITH_API_KEY")

search_tool = TavilySearch(k=3)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_completion_tokens=250)
