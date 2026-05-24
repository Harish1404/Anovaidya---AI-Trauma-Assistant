from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import TraumaGraphState
from app.agents.nodes.conversation_node import conversation_node
from app.agents.nodes.severity_node import severity_node
from app.agents.nodes.supervisor_node import supervisor_node
from app.agents.nodes.doctor_finder_node import doctor_finder_node
from app.agents.nodes.report_node import report_node


def route_after_supervisor(state: TraumaGraphState):
    """Force escalation for testing"""
    return "doctor_finder" if state.get("severity_score", 0) >= 4 else END
    
# Build Graph
def create_trauma_graph():
    workflow = StateGraph(TraumaGraphState)
    
    # Add nodes
    workflow.add_node("conversation", conversation_node)
    workflow.add_node("severity", severity_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("doctor_finder", doctor_finder_node)
    workflow.add_node("report", report_node)    
    
    # Define flow
    workflow.add_edge(START, "conversation")
    workflow.add_edge("conversation", "severity")
    workflow.add_edge("severity", "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {"doctor_finder": "doctor_finder", END: END}
    )
    
    workflow.add_edge("doctor_finder", "report")
    workflow.add_edge("report", END)

    
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)

trauma_graph = create_trauma_graph()
print("✅ Phase 6 Complete: Escalation Flow with Doctor + Report Added")


