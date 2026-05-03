import streamlit as st
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
import logging
from typing import Literal, Dict, Any 
from .config import search_tool, llm
from .state import AgentState
from .prompts import RESEARCHER_PROMPT, WRITER_PROMPT, CRITIC_PROMPT

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class CriticVerdict(BaseModel):
    is_approved: bool = Field(description="True if the report is perfect and ready.")
    feedback: str = Field(description="If not approved, explain what needs to be fixed.")
    next_action: Literal["writer", "researcher", "end"] = Field(
        description="If approved, 'end'. If missing info from internet, 'researcher'. If poor synthesis or formatting, 'writer'."
    )

def researcher_node(state: AgentState) -> Dict[str, Any]:
    iterations = state.get("ln_iterations", 0)
    topic = state['topic']
    notes = state.get('critique_notes', '')
    
    logger.info(f"--- ENTERING RESEARCHER NODE (Iteration: {iterations}) ---")

    if notes and notes != "OK":
        optimized_query = llm.invoke(RESEARCHER_PROMPT.format(topic=topic, notes=notes)).content.strip()
        search_query = optimized_query
        logger.info(f"Optimized query: {search_query}")
    else:
        search_query = topic
        logger.info(f"Initial search query: {search_query}")

    try:
        search_result = search_tool.invoke({'query': search_query})
    except Exception as e:
        logger.error(f"Search tool error: {e}")
        st.error(f"Error occurred while searching: {e}")
        return {"sources": [], "critique_notes": "Error occurred while searching. Try again."}

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
    return { "sources": new_data }


def writer_node(state: AgentState) -> Dict[str, Any]:
    logger.info("--- ENTERING WRITER NODE ---")
    
    cleaned_sources = [s[:1500] for s in state["sources"]]
    context = "\n\n--- SOURCE ---\n".join(cleaned_sources)

    notes = state.get('critique_notes', '')
    critique_context = f"\n--- CRITIC'S FEEDBACK ---\n{notes}\nIMPERATIVE: Fix ONLY the specific errors mentioned." if notes and notes.startswith("WRITER:") else ""
    
    formatted_prompt = WRITER_PROMPT.format(
        topic=state['topic'], 
        context=context, 
        critique_context=critique_context
    )
    
    response = llm.invoke([SystemMessage(content=formatted_prompt)])
    return {"report": response.content}

def critic_node(state: AgentState) -> Dict[str, Any]:
    logger.info("--- ENTERING CRITIC NODE ---")
    
    formatted_prompt = CRITIC_PROMPT.format(report=state['report'], topic=state['topic'])
    structured_llm = llm.with_structured_output(CriticVerdict)
    response = structured_llm.invoke(formatted_prompt)
    
    iterations = state.get("ln_iterations", 0)

    if response.is_approved or response.next_action == "end":
        logger.info("Critic APPROVED the report.")
        return {"critique_notes": "END: OK", "ln_iterations": iterations + 1}
    else:
        logger.warning(f"Critic REJECTED. Next action: {response.next_action}")
        return {
            "critique_notes": f"{response.next_action.upper()}: {response.feedback}", 
            "ln_iterations": iterations + 1
        }
