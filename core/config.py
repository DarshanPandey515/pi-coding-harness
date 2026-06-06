from pathlib import Path
import json

CONFIG_DIR = Path.home() / ".opencode"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config():
    if not CONFIG_FILE.exists():
        return {}

    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data):
    CONFIG_DIR.mkdir(exist_ok=True, parents=True)

    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)
        
        
        
def get_provider_api_key(provider):
    
    config = load_config()
    
    providers = config.get(
        "providers",
        {}
    )
    
    provider_data = providers.get(
        provider,
        {}
    )
    
    return provider_data.get(
        "api_key"
    )
    
    
    
def get_default_model():
    
    config = load_config()
    
    return config.get(
        "default_model"
    )
    
    