import time
import streamlit as st
from typing import List, Dict, Any
from src.agent.graph import agent_app

def configure_page() -> None:
    st.set_page_config(page_title="AI Research Agent", page_icon="🤖")
    st.title("🤖 Autonomous Research Agent")
    st.markdown("Enter a topic, and the agent will begin an autonomous investigation involving analysis and cycles.")

def display_sources(latest_sources: List[str], final_text: str) -> str:
    """Formats and deduplicates sources for display."""
    if not latest_sources:
        return final_text
    
    unique_sources = list(dict.fromkeys(latest_sources))
    for i, src in enumerate(unique_sources, start=1):
        first_line = src.split('\n')[0]
        if first_line.startswith("URL: "):
            content_preview = src.replace(first_line, '').strip()[:150]
            final_text += f"{i}. **{first_line}**\n   _{content_preview}..._\n\n"
        else:
            final_text += f"{i}. {src[:200]}...\n\n"
    return final_text

def run_agent(topic: str) -> None:
    status_container = st.empty()
    report_container = st.empty()
    log_container = st.expander("View Agent Logs", expanded=True)

    inputs = {"topic": topic, "ln_iterations": 0}
    latest_sources = []
    start_time = time.perf_counter()

    with st.spinner("Agent is working..."):
        for output in agent_app.stream(inputs):
            for key, value in output.items():
                log_container.write(f"--- Node: {key} ---")
                    
                if key == "researcher":
                    sources = value.get('sources', [])
                    status_container.info(f"🔍 Researcher found {len(sources)} sources...")
                    latest_sources = sources

                elif key == "writer":
                    status_container.success("✍️ Writer has drafted a report.")
                    final_text = value["report"] + "\n\n### Sources\n"
                    final_text = display_sources(latest_sources, final_text)
                    report_container.markdown(final_text)
                    
                elif key == "critic":
                    critique = value.get("critique_notes", "")
                    if critique.startswith("END:"):
                        status_container.success("✅ Quality Check Passed!")
                        log_container.write("Critique: OK")
                    else:
                        status_container.error(f"❌ Rejected by Critic. Retrying...")
                        log_container.write(f"Critique: {critique}")
                        time.sleep(1)

    elapsed = time.perf_counter() - start_time
    status_container.success(f"Done in {elapsed:.1f} s")
    st.balloons()

if __name__ == "__main__":
    configure_page()
    user_topic = st.text_input("Enter research topic:", placeholder="e.g., OpenAI Stargate project details")

    if st.button("Start Research"):
        if not user_topic:
            st.warning("Please enter a topic!")
        else:
            run_agent(user_topic)