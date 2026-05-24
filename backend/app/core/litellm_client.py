from litellm import completion
from app.core.config import settings

class LiteLLMClient:
    def __init__(self):
        # Best models for 2026 free tier
        self.fast_model = "groq/llama-3.1-8b-instant"          # Main conversation
        self.strong_model = "groq/llama-3.3-70b-versatile"    # Severity & Reports
        self.fallback_model = "gemini/gemini-3.5-flash"
    
    def call(self, messages, model="fast", temperature=0.7, **kwargs):
        """Smart model routing"""
        try:
            if model == "fast":
                selected_model = self.fast_model
            elif model == "strong":
                selected_model = self.strong_model
            elif model == "gemini":
                selected_model = self.fallback_model
            else:
                selected_model = self.fast_model

            response = completion(
                model=selected_model,
                messages=messages,
                temperature=temperature,
                **kwargs
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ Error with {selected_model}: {e}")
            
            # Intelligent fallback
            if model == "fast":
                print("🔄 Falling back to Gemini...")
                return self.call(messages, model="gemini", temperature=temperature, **kwargs)
            elif model == "gemini":
                print("🔄 Falling back to Strong model...")
                return self.call(messages, model="strong", temperature=temperature, **kwargs)
            
            raise e

llm_client = LiteLLMClient()

