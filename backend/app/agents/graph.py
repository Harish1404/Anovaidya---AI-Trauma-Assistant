from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import TraumaGraphState
from app.agents.nodes.conversation_node import conversation_node
from app.agents.nodes.severity_node import severity_node
from app.agents.nodes.supervisor_node import supervisor_node



def route_after_severity(state: TraumaGraphState):
    """Conditional routing"""
    return "supervisor" if state.get("severity_score", 0) >= 4 else "supervisor"
# Build Graph
def create_trauma_graph():
    workflow = StateGraph(TraumaGraphState)
    
    # Add nodes
    workflow.add_node("conversation", conversation_node)
    workflow.add_node("severity", severity_node)
    workflow.add_node("supervisor", supervisor_node)
    
    
    # Define flow
    workflow.add_edge(START, "conversation")
    workflow.add_edge("conversation", "severity")
    workflow.add_edge("severity", "supervisor")

    workflow.add_edge("supervisor", END)

    
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)

trauma_graph = create_trauma_graph()
print("✅ Full TraumaAI LangGraph with Conversation + RAG Initialized")


