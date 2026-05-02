import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
import logging
from .config import search_tool, llm
from .state import AgentState

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class CriticVerdict(BaseModel):
    is_approved: bool = Field(description="True if the report contains specific facts about the topic, False otherwise.")
    feedback: str = Field(description="If False, provide a specific search strategy or critique. If True, reply with EXACTLY 'OK'.")

def researcher_node(state: AgentState):
    iterations = state.get("ln_iterations", 0)
    logger.info(f"--- ENTERING RESEARCHER NODE (Iteration: {iterations}) ---")

    topic = state['topic']
    notes = state.get('critique_notes', '')
    

    if notes and notes != "OK":
        query_gen_prompt = f"""You are a search expert. 
        Your previous search for "{topic}" was rejected with this critique: "{notes}".
        Generate a more specific and effective search query to find factual data.
        Return ONLY the text of the new query, no quotes or explanations."""
        
        optimized_query = llm.invoke(query_gen_prompt).content.strip()
        search_query = optimized_query
        logger.info(f"Optimized query: {search_query}")
    else:
        search_query = topic
        logger.info(f"Initial search query: {search_query}")


    try:
        logger.info("Calling search tool...")
        search_result = search_tool.invoke({'query': search_query})
    except Exception as e:
        logger.error(f"Search tool error: {e}")
        st.error(f"Error occurred while searching: {e}")
        return {"sources": [], "critique_notes": "Error occurred while searching. Try again.", "ln_iterations": iterations + 1}

    new_data = []

    results_list = search_result.get("results", []) if isinstance(search_result, dict) else search_result

    if not isinstance(results_list, list):
        results_list = [results_list]

    for res in results_list:
        if isinstance(res, dict):
            content = res.get("content") or res.get("snippet") or str(res)
            url = res.get("url", "No URL")
            new_data.append(f"URL: {url}\nContent: {content}")        
        else:
            new_data.append(str(res))
    
    logger.info(f"Found {len(new_data)} sources.")

    return {
        "sources": new_data, 
        "ln_iterations": iterations + 1
    }


def writer_node(state: AgentState):
    logger.info("--- ENTERING WRITER NODE ---")
    cleaned_sources = [s[:1500] for s in state["sources"]]
    context = "\n\n--- SOURCE ---\n".join(cleaned_sources)

    system_message = f"""Write a purely factual Markdown report on: "{state['topic']}".
        Context data:
        {context}

        Rules:
        1. Extract only verified facts and core concepts. Ignore noise.
        2. Structure dynamically with appropriate Markdown headings (##).
        3. Explicitly state any contradictions.
        """
    
    response = llm.invoke([SystemMessage(content=system_message)])
    
    return {"report": response.content}

def critic_node(state: AgentState):
    logger.info("--- ENTERING CRITIC NODE ---")
    critic_prompt = f"""EXAMINE THIS REPORT:
    
    {state['report']}

    TASK: Does this report contain SPECIFIC facts about "{state['topic']}"?
    Validate the report based on the requirements.
    """
    
    structured_llm = llm.with_structured_output(CriticVerdict)
    response = structured_llm.invoke(critic_prompt)
    
    if response.is_approved:
        logger.info("Critic APPROVED the report.")
        return {"critique_notes": "OK"}
    else:
        logger.info(f"Critic REJECTED the report. Feedback: {response.feedback}")
        return {"critique_notes": response.feedback}
