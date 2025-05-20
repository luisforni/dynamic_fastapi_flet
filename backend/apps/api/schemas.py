from pydantic import BaseModel
from typing import Dict, Any
from backend.core.models import MODEL_CONFIGS

def create_schema(endpoint: str) -> Any:
    config = MODEL_CONFIGS.get(endpoint)
    if not config:
        return None
    fields = {key: (str, ...) for key in config["data_keys"]}
    return type(f"{endpoint.capitalize()}Schema", (BaseModel,), fields)

SCHEMAS: Dict[str, Any] = {endpoint: create_schema(endpoint) for endpoint in MODEL_CONFIGS}
