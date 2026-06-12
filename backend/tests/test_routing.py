"""Tests for routing and parsing helpers (no LLM/API required)."""

from langgraph.graph import END

from langchain_core.messages import HumanMessage, AIMessage

from app.agents.constants import (
    ASK_EMAIL,
    ASK_LOCATION,
    COMPLETE,
    CONTINUE,
    ESCALATE,
    SELECT_DOCTOR,
    SHOW_DOCTORS,
)
from app.agents.graph import (
    route_entry,
    route_after_geocode,
    route_after_doctor_select,
    route_after_email_parse,
)
from app.utils.parsers import extract_email, extract_doctor_name, is_email_skip_message
from app.utils.chat_response import state_to_chat_response, extract_last_ai_message


class _FakeChatResponse:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_extract_email():
    assert extract_email("my email is john@gmail.com thanks") == "john@gmail.com"
    assert extract_email("no email here") is None


def test_extract_doctor_name():
    doctors = [{"full_name": "Dr. Priya Sharma"}, {"full_name": "Dr. Rajan Kumar"}]
    assert extract_doctor_name("I want Dr. Priya Sharma", doctors) == "Dr. Priya Sharma"
    assert extract_doctor_name("Sharma please", doctors) == "Dr. Priya Sharma"
    assert extract_doctor_name("unknown", doctors) is None


def test_is_email_skip_message():
    assert is_email_skip_message("no thanks") is True
    assert is_email_skip_message("john@gmail.com") is False


def test_route_entry():
    assert route_entry({"next_action": ASK_LOCATION}) == "geocode"
    assert route_entry({"next_action": ESCALATE}) == "geocode"
    assert route_entry({"next_action": SELECT_DOCTOR}) == "doctor_select"
    assert route_entry({"next_action": ASK_EMAIL}) == "email_parse"
    assert route_entry({"next_action": SHOW_DOCTORS}) == "doctor_finder"
    assert route_entry({"next_action": CONTINUE}) == "conversation"
    assert route_entry({}) == "conversation"
    assert route_entry({"next_action": COMPLETE}) == "conversation"


def test_route_after_geocode():
    assert route_after_geocode({"latitude": 13.0}) == "doctor_finder"
    assert route_after_geocode({}) == END


def test_route_after_doctor_select():
    assert route_after_doctor_select({"selected_doctor_name": "Dr. X"}) == "report"
    assert route_after_doctor_select({}) == END


def test_route_after_email_parse():
    assert route_after_email_parse({"user_email": "a@b.com"}) == "email"
    assert route_after_email_parse({}) == END


def test_extract_last_ai_message():
    msgs = [HumanMessage(content="hi"), AIMessage(content="[Severity Assessment: 3/5]"), AIMessage(content="Hello")]
    assert extract_last_ai_message(msgs) == "Hello"


def test_state_to_chat_response():
    resp = state_to_chat_response(
        {
            "messages": [AIMessage(content="Take care")],
            "severity_score": 3,
            "doctor_recommendation": [{"full_name": "Dr. X"}],
            "final_summary": "report text",
            "next_action": CONTINUE,
        },
        _FakeChatResponse,
    )
    assert resp.response == "Take care"
    assert resp.next_action == "continue"
    assert resp.report_ready is True
