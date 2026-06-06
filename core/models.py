from core.providers import SUPPORTED_PROVIDERS
import json
from pathlib import Path


MODELS_FILE = Path("data/models.json")

def provider_exists(provider: str) -> bool:
    return provider in SUPPORTED_PROVIDERS


def get_models():
    
    with open(MODELS_FILE) as f:
        return json.load(f)