from typing import Annotated, TypedDict, List
import operator

class AgentState(TypedDict):
    topic: str
    report: str
    sources: Annotated[List[str], operator.add]
    critique_notes: str
    ln_iterations: int