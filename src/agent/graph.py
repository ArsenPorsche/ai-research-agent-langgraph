from typing import Literal
from langgraph.graph import END, StateGraph
from .nodes import researcher_node, writer_node, critic_node
from .state import AgentState

def should_continue(state: AgentState) -> Literal['researcher', END]:
    if state["critique_notes"] == "OK" or state.get("ln_iterations", 0) >= 3:
        return END
    else:
        return "researcher" 
    
def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("researcher", researcher_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("critic", critic_node)

    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "critic")
    workflow.add_conditional_edges("critic", should_continue)

    return workflow.compile()

agent_app = build_graph()