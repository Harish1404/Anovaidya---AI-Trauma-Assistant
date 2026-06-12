import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import END

from app.agents.state import TraumaGraphState
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
    route_after_supervisor,
    route_after_geocode,
    route_after_doctor_select,
    route_after_email_parse,
)
from app.agents.nodes.conversation_node import conversation_node
from app.agents.nodes.severity_node import severity_node
from app.agents.nodes.supervisor_node import supervisor_node
from app.agents.nodes.geocode_node import geocode_node
from app.agents.nodes.doctor_finder_node import doctor_finder_node
from app.agents.nodes.doctor_select_node import doctor_select_node
from app.agents.nodes.report_node import report_node
from app.agents.nodes.email_parse_node import email_parse_node
from app.agents.nodes.email_node import email_node


def test_doctor_name_parser_variants():
    """Verify that extract_doctor_name works with different input variants."""
    from app.utils.parsers import extract_doctor_name
    doctors = [
        {"full_name": "Dr. Priya Sharma", "specialization": "Orthopedics"},
        {"full_name": "Dr. Karthik Rajan", "specialization": "Trauma Surgeon"},
    ]

    # Full name match
    assert extract_doctor_name("I want Dr. Priya Sharma", doctors) == "Dr. Priya Sharma"
    # Case insensitive
    assert extract_doctor_name("dr. priya sharma", doctors) == "Dr. Priya Sharma"
    # Last name match
    assert extract_doctor_name("I want Sharma", doctors) == "Dr. Priya Sharma"
    # First name match
    assert extract_doctor_name("Priya please", doctors) == "Dr. Priya Sharma"
    # Index match
    assert extract_doctor_name("I select 1", doctors) == "Dr. Priya Sharma"
    assert extract_doctor_name("choose the second one", doctors) == "Dr. Karthik Rajan"
    # No match
    assert extract_doctor_name("some other person", doctors) is None


@patch("app.agents.nodes.conversation_node.llm_client")
@patch("app.agents.nodes.conversation_node.retriever")
def test_conversation_node(mock_retriever, mock_llm_client):
    """Test conversation node execution and turn count increment."""
    mock_retriever.invoke.return_value = []
    mock_llm_client.call.return_value = "Hello, how can I help?"

    initial_state = {
        "messages": [HumanMessage(content="Hello")],
        "turn_count": 0,
        "should_check_severity": False,
    }

    result = conversation_node(initial_state)

    assert result["turn_count"] == 1
    assert result["should_check_severity"] is False
    assert len(result["messages"]) == 2
    assert result["messages"][-1].content == "Hello, how can I help?"


@patch("app.agents.nodes.severity_node.llm_client")
def test_severity_node(mock_llm_client):
    """Test severity node parsing and fallback safety."""
    mock_llm_client.call.return_value = '```json {"severity_score": 4, "needs_doctor": true, "specialization_needed": "Orthopedics", "reason": "Suspected fracture"} ```'

    initial_state = {
        "messages": [HumanMessage(content="My leg is broken")],
        "severity_score": None,
    }

    result = severity_node(initial_state)

    assert result["severity_score"] == 4
    assert result["needs_doctor"] is True
    assert result["specialization_needed"] == "Orthopedics"
    assert result["severity_reason"] == "Suspected fracture"


@patch("app.agents.nodes.supervisor_node.llm_client")
def test_supervisor_node_escalate(mock_llm_client):
    """Test supervisor node decision and key fallbacks."""
    # LLM returns next_action instead of next
    mock_llm_client.call.return_value = '```json {"next_action": "escalate_to_doctor", "message": "Please share your location."} ```'

    initial_state = {
        "messages": [HumanMessage(content="Bleeding heavily")],
        "severity_score": 4,
        "latitude": None,
        "specialization_needed": "Trauma Surgeon",
    }

    result = supervisor_node(initial_state)

    assert result["next_action"] == "escalate_to_doctor"
    assert result["messages"][-1].content == "Please share your location."


def test_route_after_supervisor_escalate_halts():
    """Verify that route_after_supervisor halts when location is needed (ESCALATE)."""
    # Previously, this incorrectly routed to doctor_finder on the same turn.
    # It must now return END.
    state_escalate = {"next_action": ESCALATE, "latitude": None}
    assert route_after_supervisor(state_escalate) == END

    state_show_docs = {"next_action": SHOW_DOCTORS, "latitude": 13.0827}
    assert route_after_supervisor(state_show_docs) == "doctor_finder"


@patch("app.agents.nodes.geocode_node.geocode_address")
def test_geocode_node_success(mock_geocode):
    """Test geocode node success paths."""
    mock_geocode.return_value = {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "formatted_address": "Royapuram, Chennai, Tamil Nadu",
    }

    initial_state = {
        "messages": [HumanMessage(content="Royapuram Chennai")],
        "latitude": None,
    }

    result = geocode_node(initial_state)

    assert result["latitude"] == 13.0827
    assert result["longitude"] == 80.2707
    assert result["next_action"] == SHOW_DOCTORS
    assert result["user_location_string"] == "Royapuram, Chennai, Tamil Nadu"


@pytest.mark.asyncio
@patch("app.agents.nodes.doctor_finder_node.doctor_repo")
async def test_doctor_finder_node(mock_doctor_repo):
    """Test doctor finder node returns recommendations."""
    mock_doctor_repo.get_nearby_specialized_doctors = AsyncMock(return_value=[
        {
            "full_name": "Dr. Priya Sharma",
            "hospital_name": "Apollo Hospitals",
            "clinic_address": "Greams Road, Chennai",
            "specialization": "Orthopedics",
            "distance_km": 1.2,
            "is_available": True,
        }
    ])

    initial_state = {
        "messages": [],
        "latitude": 13.0827,
        "longitude": 80.2707,
        "specialization_needed": "Orthopedics",
    }

    result = await doctor_finder_node(initial_state)

    assert len(result["doctor_recommendation"]) == 1
    assert result["next_action"] == "select_doctor"
    assert "Dr. Priya Sharma" in result["messages"][-1].content


def test_doctor_select_node_success():
    """Test selecting a doctor successfully."""
    initial_state = {
        "messages": [HumanMessage(content="1")],
        "doctor_recommendation": [{"full_name": "Dr. Priya Sharma"}],
        "selected_doctor_name": None,
    }

    result = doctor_select_node(initial_state)

    assert result["selected_doctor_name"] == "Dr. Priya Sharma"


@patch("app.agents.nodes.report_node.llm_client")
def test_report_node(mock_llm_client):
    """Test report generation node."""
    mock_llm_client.call.return_value = "Detailed medical summary."

    initial_state = {
        "messages": [HumanMessage(content="Hello")],
        "selected_doctor_name": "Dr. Priya Sharma",
        "final_summary": None,
    }

    result = report_node(initial_state)

    assert result["final_summary"] == "Detailed medical summary."
    assert result["next_action"] == "ask_email"


@pytest.mark.asyncio
@patch("app.agents.nodes.email_node.send_report_via_brevo")
@patch("app.agents.nodes.email_node.doctor_repo")
async def test_email_node_success(mock_doctor_repo, mock_send_email):
    """Test email sending node."""
    mock_doctor_repo.get_doctor_by_name = AsyncMock(return_value={
        "full_name": "Dr. Priya Sharma",
        "email": "priya@apollo.com",
        "hospital_name": "Apollo Hospitals",
    })
    mock_send_email.return_value = True

    initial_state = {
        "messages": [],
        "user_email": "patient@example.com",
        "selected_doctor_name": "Dr. Priya Sharma",
        "final_summary": "Summary text",
        "severity_score": 3,
    }

    result = await email_node(initial_state)

    assert result["email_sent_success"] is True
    assert result["report_sent"] is True
    assert result["next_action"] == COMPLETE


from datetime import datetime
from app.db.mongodb_saver import MongoDBSaver
from app.routes.history_router import get_user_sessions, get_session_history, delete_session

@pytest.mark.asyncio
async def test_mongodb_saver_put_and_get():
    """Verify that MongoDBSaver checkpointer puts and gets checkpoints using mock collection operations."""
    mock_db = MagicMock()
    mock_checkpoints = MagicMock()
    mock_checkpoints.update_one = AsyncMock()
    mock_writes = MagicMock()
    mock_writes.insert_many = AsyncMock()
    
    mock_db.__getitem__.side_effect = lambda key: mock_checkpoints if key == "checkpoints" else mock_writes
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    saver = MongoDBSaver(client=mock_client, db_name="test_db")
    
    config = {"configurable": {"thread_id": "test-thread", "checkpoint_ns": "", "checkpoint_id": "1ef82a"}}
    checkpoint = {"id": "1ef82a", "v": 1, "channel_values": {}}
    metadata = {"source": "input"}
    new_versions = {}
    
    # 1. Test aput
    await saver.aput(config, checkpoint, metadata, new_versions)
    assert mock_checkpoints.update_one.call_count == 1
    
    # 2. Test aget_tuple
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    fmt_cp, data_cp = saver.serde.dumps_typed(checkpoint)
    fmt_meta, data_meta = saver.serde.dumps_typed(metadata)
    
    mock_cursor.to_list = AsyncMock(return_value=[{
        "thread_id": "test-thread",
        "checkpoint_ns": "",
        "checkpoint_id": "1ef82a",
        "checkpoint_type": fmt_cp,
        "checkpoint": data_cp,
        "metadata_type": fmt_meta,
        "metadata": data_meta,
        "parent_checkpoint_id": None
    }])
    mock_checkpoints.find.return_value = mock_cursor
    
    # Mock writes cursor
    mock_writes_cursor = MagicMock()
    mock_writes_cursor.to_list = AsyncMock(return_value=[])
    mock_writes_cursor.sort.return_value = mock_writes_cursor
    mock_writes.find.return_value = mock_writes_cursor
    
    res = await saver.aget_tuple(config)
    assert res is not None
    assert res.checkpoint["id"] == "1ef82a"
    assert res.metadata["source"] == "input"

    # 3. Test aput_writes
    writes = [("channel1", "val1")]
    await saver.aput_writes(config, writes, "task1")
    assert mock_writes.insert_many.call_count == 1


@pytest.mark.asyncio
@patch("app.routes.history_router.get_database_client")
async def test_get_user_sessions(mock_get_client):
    """Test get_user_sessions endpoint returns summary lists."""
    mock_db = MagicMock()
    mock_collection = MagicMock()
    
    # db[settings.DB_NAME] returns mock_collection
    mock_db.__getitem__.return_value = mock_collection
    # mock_collection["chat_history"] returns mock_collection
    mock_collection.__getitem__.return_value = mock_collection
    mock_get_client.return_value = mock_db
    
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=[
        {
            "session_id": "session-123",
            "user_id": "user-456",
            "messages": [{"role": "user", "content": "My arm hurts"}],
            "severity_score": 3,
            "updated_at": datetime.utcnow()
        }
    ])
    mock_cursor.sort.return_value = mock_cursor
    mock_collection.find.return_value = mock_cursor
    
    sessions = await get_user_sessions("user-456")
    assert len(sessions) == 1
    assert sessions[0].session_id == "session-123"
    assert sessions[0].chief_complaint == "My arm hurts"

