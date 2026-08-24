from core.providers.gemini import generate as gemini_generate
from core.providers.groq import generate as groq_generate


def generate(provider: str, api_key: str, model: str, messages: list):
    if provider == "groq":
        return groq_generate(api_key, model, messages)
    elif provider == "gemini":
        return gemini_generate(api_key, model, messages)

    raise ValueError(f"Unsupported provider: {provider}")
