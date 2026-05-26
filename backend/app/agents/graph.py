from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import TraumaGraphState

from app.agents.nodes.conversation_node import conversation_node
from app.agents.nodes.severity_node import severity_node
from app.agents.nodes.supervisor_node import supervisor_node
from app.agents.nodes.doctor_finder_node import doctor_finder_node
from app.agents.nodes.report_node import report_node
from app.agents.nodes.email_node import email_node


def should_check_severity(state: TraumaGraphState):
    """Decide whether to run severity assessment this turn."""
    return state.get("should_check_severity", False)


def route_after_supervisor(state: TraumaGraphState):
    """Route based on the supervisor's decision."""
    next_action = state.get("next_action", "continue_conversation")
    
    if next_action in ("show_doctors", "escalate_to_doctor"):
        return "doctor_finder"
    
    return END


def create_trauma_graph():
    workflow = StateGraph(TraumaGraphState)
    
    # Register all nodes
    workflow.add_node("conversation", conversation_node)
    workflow.add_node("severity", severity_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("doctor_finder", doctor_finder_node)
    workflow.add_node("report", report_node)
    workflow.add_node("email", email_node)
    
    # Entry point: always start with conversation
    workflow.add_edge(START, "conversation")
    
    # After conversation: conditionally check severity
    workflow.add_conditional_edges(
        "conversation",
        should_check_severity,
        {True: "severity", False: END}
    )
    
    # severity -> supervisor
    workflow.add_edge("severity", "supervisor")
    
    # supervisor -> route based on decision
    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {"doctor_finder": "doctor_finder", END: END}
    )
    
    # doctor_finder -> END (user needs to select a doctor next turn)
    workflow.add_edge("doctor_finder", END)
    
    # report -> END (user will be asked for email next turn)
    workflow.add_edge("report", END)
    
    # email -> END (final step)
    workflow.add_edge("email", END)
    
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


trauma_graph = create_trauma_graph()
print("[GRAPH] TraumaAI graph compiled successfully.")