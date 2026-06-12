from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage


def langchain_to_openai(messages: list[BaseMessage]) -> list[dict]:
    """Convert LangChain message history to LiteLLM/OpenAI role format."""
    result = []
    for msg in messages:
        # Skip internal system/debug messages starting with '['
        if msg.content and msg.content.startswith("["):
            continue
            
        if isinstance(msg, SystemMessage):
            result.append({"role": "system", "content": msg.content})
        elif isinstance(msg, HumanMessage):
            result.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            result.append({"role": "assistant", "content": msg.content})
        else:
            result.append({"role": "user", "content": msg.content})
    return result
