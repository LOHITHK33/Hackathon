from langchain_ollama import ChatOllama

from .config import MODEL, OLLAMA_BASE_URL


def get_llm(temperature: float = 0.3, **kwargs) -> ChatOllama:
    return ChatOllama(
        model=MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=temperature,
        **kwargs,
    )