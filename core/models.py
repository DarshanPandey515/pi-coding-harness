import json
from pathlib import Path

SUPPORTED_PROVIDERS = {
    "gemini": {
        "name": "Google Gemini"
    },
    "groq": {
        "name":"groq"
    }
}


MODELS_FILE = Path("data/models.json")

def provider_exists(provider: str) -> bool:
    return provider in SUPPORTED_PROVIDERS


def get_models():
    
    with open(MODELS_FILE) as f:
        return json.load(f)