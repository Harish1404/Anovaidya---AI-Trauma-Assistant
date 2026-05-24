from app.agents.state import TraumaGraphState
from app.core.litellm_client import llm_client
from app.utils.prompts import TRAUMA_SYSTEM_PROMPT
from app.rag.vectorstore import retriever
from langchain_core.messages import SystemMessage, AIMessage

def conversation_node(state: TraumaGraphState):
    """Main conversation agent with RAG"""
    
    messages = state["messages"]
    last_user_message = messages[-1].content if messages else ""
    
    # Retrieve relevant medical knowledge
    retrieved_docs = retriever.invoke(last_user_message)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # Build prompt
    system_prompt = f"""{TRAUMA_SYSTEM_PROMPT}

Relevant Medical Knowledge:
{context}

Answer empathetically and helpfully. Ask one follow-up question if needed.
"""
    
    full_messages = [
        SystemMessage(content=system_prompt),
        *messages
    ]
    
    # Call LLM (prefer Groq for speed)
    response = llm_client.call(
        messages=[{"role": "user", "content": msg.content} for msg in full_messages],
        model="fast",
        temperature=0.6
    )
    
    # Return updated state
    return {
        **state,
        "messages": messages + [AIMessage(content=response)]
    }


    