from typing import Any, Dict, Optional
from app.agents.constants import CONTINUE, LEGACY_CONTINUE


def extract_last_ai_message(messages) -> str:
    """Extract the last meaningful AI message (skip internal severity tags)."""
    for msg in reversed(messages):
        content = msg.content
        if content and not content.startswith("["):
            return content
    return "I'm here to help. Could you tell me what happened?"


def _normalize_next_action(next_action: Optional[str]) -> str:
    """Map internal next_action values to API-facing values."""
    if next_action in (CONTINUE, LEGACY_CONTINUE, None):
        return LEGACY_CONTINUE
    return next_action or LEGACY_CONTINUE


def state_to_chat_response(state: Dict[str, Any], chat_response_cls):
    """Build a ChatResponse from graph state."""
    messages = state.get("messages", [])
    next_action = state.get("next_action")

    return chat_response_cls(
        response=extract_last_ai_message(messages),
        severity_score=state.get("severity_score"),
        doctors_recommended=state.get("doctor_recommendation") or [],
        report_ready=bool(state.get("final_summary")),
        report_download_url=state.get("report_download_url"),
        next_action=_normalize_next_action(next_action),
    )
