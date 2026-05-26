from app.agents.state import TraumaGraphState
from app.core.litellm_client import llm_client
from app.utils.prompts import TRAUMA_SYSTEM_PROMPT
from app.rag.vectorstore import retriever
from langchain_core.messages import SystemMessage, AIMessage

def conversation_node(state: TraumaGraphState):
    """Interactive triage conversation node with RAG-grounded responses."""
    
    messages = state["messages"]
    last_user_message = messages[-1].content if messages else ""
    turn_count = state.get("turn_count", 0)
    
    # Retrieve relevant first-aid knowledge from vectorstore
    retrieved_docs = retriever.invoke(last_user_message)
    context = "\n\n".join([doc.page_content[:600] for doc in retrieved_docs])

    # Build turn-aware system prompt
    turn_guidance = ""
    if turn_count == 0:
        turn_guidance = "This is the user's FIRST message. Acknowledge warmly. Ask what happened and where they are hurt."
    elif turn_count == 1:
        turn_guidance = "This is turn 2. Ask about the severity of pain, visible symptoms like bleeding, swelling, or mobility issues."
    elif turn_count == 2:
        turn_guidance = "This is turn 3. Ask if the injury just happened or if symptoms are worsening. Check for any additional context."
    elif turn_count >= 3:
        turn_guidance = "You now have enough context. Summarize what you understand about the injury and provide immediate first-aid tips. Be specific and actionable."

    system_prompt = f"""{TRAUMA_SYSTEM_PROMPT}

{turn_guidance}

Relevant First-Aid Knowledge (use this to ground your response):
{context}
"""

    full_messages = [SystemMessage(content=system_prompt), *messages]
    
    # Use fast model for conversational turns (cost-efficient)
    response = llm_client.call(
        messages=[{"role": "user", "content": msg.content} for msg in full_messages],
        model="fast",
        temperature=0.7
    )
    
    new_turn_count = turn_count + 1
    
    # Trigger severity check at turn 4 and every 3 turns after
    should_check = new_turn_count >= 4 and (new_turn_count == 4 or (new_turn_count - 4) % 3 == 0)
    
    return {
        **state,
        "messages": messages + [AIMessage(content=response)],
        "turn_count": new_turn_count,
        "should_check_severity": should_check
    }