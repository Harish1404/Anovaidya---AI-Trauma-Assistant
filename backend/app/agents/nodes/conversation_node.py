import logging
from app.agents.state import TraumaGraphState
from app.core.litellm_client import llm_client
from app.utils.prompts import TRAUMA_SYSTEM_PROMPT
from app.utils.llm_messages import langchain_to_openai
from app.rag.vectorstore import retriever
from langchain_core.messages import AIMessage

logger = logging.getLogger("uvicorn")

def conversation_node(state: TraumaGraphState):
    """Interactive triage conversation node with RAG-grounded responses."""
    
    messages = state["messages"]
    last_user_message = messages[-1].content if messages else ""
    turn_count = state.get("turn_count", 0)
    
    # Reformulate query using Advanced RAG strategy to maintain semantic relevance
    search_query = last_user_message
    if turn_count > 0 and len(messages) > 1:
        history_text = "\n".join([f"{m.type}: {m.content}" for m in messages[-6:]])
        reformulate_prompt = [
            {"role": "system", "content": (
                "You are a search query optimizer for a medical first-aid assistant. "
                "Analyze the conversation history and the user's latest message. "
                "Generate a single standalone search query (2-4 words) that describes "
                "the primary injury, trauma, or symptom in English, suitable for looking up "
                "first-aid manuals. "
                "Return ONLY the search query keywords. Do not explain or include extra text."
            )},
            {"role": "user", "content": f"Conversation:\n{history_text}\n\nLatest User Message: {last_user_message}"}
        ]
        try:
            rewritten = llm_client.call(
                messages=reformulate_prompt,
                model="fast",
                temperature=0.1
            )
            rewritten_clean = rewritten.strip().strip('"').strip("'")
            if rewritten_clean:
                search_query = rewritten_clean
                logger.info(f"[RAG] Rewrote query: '{last_user_message}' -> '{search_query}'")
        except Exception as e:
            logger.warning(f"[RAG] Query reformulation failed: {e}")

    # Retrieve relevant first-aid knowledge from vectorstore using optimized search query
    retrieved_docs = retriever.invoke(search_query)
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

    llm_messages = [{"role": "system", "content": system_prompt}]
    llm_messages.extend(langchain_to_openai(messages))

    # Use fast model for conversational turns (cost-efficient)
    response = llm_client.call(
        messages=llm_messages,
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