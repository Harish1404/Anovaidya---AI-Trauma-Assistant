from litellm import completion
from app.core.config import settings

class LiteLLMClient:
    def __init__(self):
        self.groq_model = "groq/llama-3.1-70b-versatile"
        self.gemini_model = "gemini/gemini-1.5-flash"
    
    def call(self, messages, model="groq", temperature=0.7, **kwargs):
        """Unified way to call any LLM"""
        try:
            if model == "groq":
                selected_model = self.groq_model
            elif model == "gemini":
                selected_model = self.gemini_model
            else:
                selected_model = self.groq_model

            response = completion(
                model=selected_model,
                messages=messages,
                temperature=temperature,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error: {e}")
            # Fallback to gemini if groq fails
            if model == "groq":
                return self.call(messages, model="gemini", temperature=temperature, **kwargs)
            raise e

llm_client = LiteLLMClient()


