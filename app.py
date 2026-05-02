import streamlit as st
import time

from src.agent.graph import agent_app

st.set_page_config(page_title="AI Research Agent", page_icon="🤖")

st.title("🤖 Autonomous Research Agent")
st.markdown("Enter a topic, and the agent will begin an autonomous investigation involving analysis and cycles.")

topic = st.text_input("Enter research topic:", placeholder="e.g., OpenAI Stargate project details")

if st.button("Start Research"):
    if not topic:
        st.warning("Please enter a topic!")
    else:
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
                        if "search_query" in value:
                             log_container.write(f"Search query: {value['search_query']}")
                        latest_sources = sources

                    if key == "writer":
                        status_container.success("✍️ Writer has drafted a report.")
                        report_container.markdown(value["report"])
                        if latest_sources:
                            st.subheader("Sources")
                            for i, src in enumerate(latest_sources[:3], start=1):
                                st.write(f"{i}. {src[:300]}...")
                    
                    if key == "critic":
                        critique = value.get("critique_notes", "")
                        if critique == "OK":
                            status_container.success("✅ Quality Check Passed!")
                            log_container.write("Critique: OK")
                        else:
                            status_container.error(f"❌ Rejected by Critic. Retrying...")
                            log_container.write(f"Critique: {critique}")
                            time.sleep(1)

        elapsed = time.perf_counter() - start_time
        status_container.success(f"Done in {elapsed:.1f} s")
        st.balloons()