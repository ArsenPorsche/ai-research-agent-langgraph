import os
import streamlit as st
import time
from typing import Annotated, Literal, TypedDict, List
import operator
from langgraph.graph import END, StateGraph
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

class AgentState(TypedDict):
    topic: str
    report: str
    sources: Annotated[List[str], operator.add]
    critique_notes: str
    ln_iterations: int

search_tool = TavilySearchResults(k=3)

def researcher_node(state: AgentState):
    topic = state['topic']
    notes = state.get('critique_notes', '')
    iterations = state.get("ln_iterations", 0)

    if notes and notes != "OK":
        query_gen_prompt = f"""You are a search expert. 
        Your previous search for "{topic}" was rejected with this critique: "{notes}".
        Generate a more specific and effective search query to find factual data.
        Return ONLY the text of the new query, no quotes or explanations."""
        
        optimized_query = llm.invoke(query_gen_prompt).content.strip()
        search_query = optimized_query
    else:
        search_query = topic

    search_result = search_tool.invoke({'query': search_query})

    new_data = [res["content"] for res in search_result]
    
    return {
        "sources": new_data, 
        "ln_iterations": iterations + 1
    }

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_completion_tokens=250)

def writer_node(state: AgentState):
    cleaned_sources = [s[:2000] for s in state["sources"]]
    context = "\n\n--- SOURCE ---\n".join(cleaned_sources)

    system_message = ('''You are a top-tier data analyst. You have been provided with raw search results from the internet.
        IMPORTANT: This data contains a lot of noise (ads, website navigation, footers).”
        Your task: \n
        1. Ignore all noise and irrelevant information.\n
        2. Extract only facts, dates, and specific news items on the topic: {topic}.\n
        3. Compile a structured report.\n
        4. If there are contradictions in the sources, be sure to point them out.''').format(topic = state['topic'])

    human_message = f"Here is the raw data for analysis:\n\n{context}"
    
    response = llm.invoke([SystemMessage(content=system_message), HumanMessage(content=human_message)])
    
    return {"report": response.content}

def critic_node(state: AgentState):
    critic_prompt = f"""EXAMINE THIS REPORT:
    
    {state['report']}

    TASK: Does this report contain SPECIFIC facts about "{state['topic']}"?

    - IF the report is good and has facts: Reply with exactly the word "OK" and nothing else.
    - IF the report is just an apology, empty, or says "I can't find data": Reply with "Data not found. Try a different search strategy."

    YOUR ONE-WORD VERDICT:"""
    
    response = llm.invoke(critic_prompt)
    
    return {"critique_notes": response.content.strip()}

workflow = StateGraph(AgentState)

workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)
workflow.add_node("critic", critic_node)

workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "critic")

def should_continue(state: AgentState) -> Literal['researcher', '__end__']:
    if state["critique_notes"] == "OK" or state.get("ln_iterations", 0) >= 3:
        return "__end__"
    else:
        return "researcher" 
    
workflow.add_conditional_edges("critic", should_continue)

app = workflow.compile()

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

        with st.spinner("Agent is working..."):
            for output in app.stream(inputs):
                for key, value in output.items():
                    log_container.write(f"--- Node: {key} ---")
                    
                    if key == "researcher":
                        status_container.info(f"🔍 Researcher found {len(value.get('sources', []))} sources...")
                    
                    if key == "writer":
                        status_container.success("✍️ Writer has drafted a report.")
                        report_container.markdown(value["report"])
                    
                    if key == "critic":
                        critique = value.get("critique_notes", "")
                        if critique == "OK":
                            status_container.success("✅ Quality Check Passed!")
                            log_container.write("Critique: OK")
                        else:
                            status_container.error(f"❌ Rejected by Critic. Retrying...")
                            log_container.write(f"Critique: {critique}")
                            time.sleep(1)

        st.balloons()