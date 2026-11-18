from langchain_mistralai import ChatMistralAI
from services.AIAnalysis.utils.config import settings

def get_mistral_llm(temperature: float = 0.3):
    """Initialize and return Mistral LLM instance using open-mistral-7b (high quota, low latency)"""
    return ChatMistralAI(
        model="open-mistral-7b",
        mistral_api_key=settings.MISTRAL_API_KEY,
        temperature=temperature
    )
