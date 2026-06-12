import logging
from langgraph.graph import StateGraph, START, END
from app.db.mongodb_saver import MongoDBSaver

from app.agents.state import TraumaGraphState
from app.agents.constants import (
    ASK_EMAIL,
    ASK_LOCATION,
    COMPLETE,
    CONTINUE,
    ESCALATE,
    LEGACY_CONTINUE,
    SELECT_DOCTOR,
    SHOW_DOCTORS,
)

from app.agents.nodes.conversation_node import conversation_node
from app.agents.nodes.severity_node import severity_node
from app.agents.nodes.supervisor_node import supervisor_node
from app.agents.nodes.doctor_finder_node import doctor_finder_node
from app.agents.nodes.report_node import report_node
from app.agents.nodes.email_node import email_node
from app.agents.nodes.geocode_node import geocode_node
from app.agents.nodes.doctor_select_node import doctor_select_node
from app.agents.nodes.email_parse_node import email_parse_node

logger = logging.getLogger("uvicorn")


def route_entry(state: TraumaGraphState) -> str:
    """Route each turn to the correct phase based on checkpointed next_action."""
    action = state.get("next_action") or CONTINUE

    if action in (ASK_LOCATION, ESCALATE):
        return "geocode"
    if action == SELECT_DOCTOR:
        return "doctor_select"
    if action == ASK_EMAIL:
        return "email_parse"
    if action == SHOW_DOCTORS:
        return "doctor_finder"
    if action in (CONTINUE, LEGACY_CONTINUE, COMPLETE):
        return "conversation"
    return "conversation"


def should_check_severity(state: TraumaGraphState):
    """Decide whether to run severity assessment this turn."""
    return state.get("should_check_severity", False)


def route_after_supervisor(state: TraumaGraphState):
    """Route based on the supervisor's decision."""
    next_action = state.get("next_action", CONTINUE)

    if next_action == SHOW_DOCTORS:
        return "doctor_finder"

    return END


def route_after_geocode(state: TraumaGraphState):
    """Proceed to doctor search only when geocoding succeeded."""
    if state.get("latitude") is not None:
        return "doctor_finder"
    return END


def route_after_doctor_select(state: TraumaGraphState):
    """Generate report only when a doctor was matched."""
    if state.get("selected_doctor_name"):
        return "report"
    return END


def route_after_email_parse(state: TraumaGraphState):
    """Send email when address parsed; otherwise end (skip or retry)."""
    if state.get("user_email"):
        return "email"
    return END


def create_trauma_graph():
    workflow = StateGraph(TraumaGraphState)

    workflow.add_node("conversation", conversation_node)
    workflow.add_node("severity", severity_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("doctor_finder", doctor_finder_node)
    workflow.add_node("report", report_node)
    workflow.add_node("email", email_node)
    workflow.add_node("geocode", geocode_node)
    workflow.add_node("doctor_select", doctor_select_node)
    workflow.add_node("email_parse", email_parse_node)

    workflow.add_conditional_edges(
        START,
        route_entry,
        {
            "conversation": "conversation",
            "geocode": "geocode",
            "doctor_select": "doctor_select",
            "email_parse": "email_parse",
            "doctor_finder": "doctor_finder",
        },
    )

    workflow.add_conditional_edges(
        "conversation",
        should_check_severity,
        {True: "severity", False: END},
    )

    workflow.add_edge("severity", "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {"doctor_finder": "doctor_finder", END: END},
    )

    workflow.add_conditional_edges(
        "geocode",
        route_after_geocode,
        {"doctor_finder": "doctor_finder", END: END},
    )

    workflow.add_conditional_edges(
        "doctor_select",
        route_after_doctor_select,
        {"report": "report", END: END},
    )

    workflow.add_conditional_edges(
        "email_parse",
        route_after_email_parse,
        {"email": "email", END: END},
    )

    workflow.add_edge("doctor_finder", END)
    workflow.add_edge("report", END)
    workflow.add_edge("email", END)

    memory = MongoDBSaver()
    return workflow.compile(checkpointer=memory)


trauma_graph = create_trauma_graph()
logger.info("[GRAPH] TraumaAI graph compiled successfully.")
