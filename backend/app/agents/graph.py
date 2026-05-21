from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import TraumaGraphState
from app.core.config import settings
import os

# Temporary placeholder nodes (we will implement real ones later)
def conversation_node(state: TraumaGraphState):
    print("🤖 Conversation Node called")
    return state

def severity_node(state: TraumaGraphState):
    print("⚠️  Severity Check Node called")
    return state

# Build Graph
def create_trauma_graph():
    workflow = StateGraph(TraumaGraphState)
    
    # Add nodes
    workflow.add_node("conversation", conversation_node)
    workflow.add_node("severity", severity_node)
    
    # Basic flow for now
    workflow.add_edge(START, "conversation")
    workflow.add_edge("conversation", "severity")
    workflow.add_edge("severity", END)
    
    # Add memory (will use Redis later)
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)

# Create global graph instance
trauma_graph = create_trauma_graph()

print("✅ TraumaAI LangGraph Initialized")


