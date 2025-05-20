from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from backend.core.models import MODEL_CONFIGS

Base = declarative_base()
MODELS = {}

def create_model_class(endpoint: str):
    config = MODEL_CONFIGS.get(endpoint)
    
    if not config:
        raise ValueError(f"No se encontró configuración para '{endpoint}' en MODEL_CONFIGS")

    class_name = config["title"].replace(" ", "")
    table_name = config["table_name"]

    attrs = {
        "__tablename__": table_name,
        "id": Column(Integer, primary_key=True, index=True, autoincrement=True),
    }

    for field in config["data_keys"]:
        if field == "id":
            continue

        field_type = String(255)
        if field.endswith("_id"):
            field_type = Integer
        elif field in ["is_active", "is_superuser", "is_staff"]:
            field_type = Boolean
        elif "date" in field or "time" in field:
            field_type = DateTime

        attrs[field] = Column(field_type, nullable=True)

    for fk, fk_data in config.get("foreign_keys", {}).items():
        if "table" not in fk_data or "name_field" not in fk_data:
            continue

        fk_table = fk_data["table"]
        if fk_table not in MODEL_CONFIGS:
            continue

        attrs[fk] = Column(Integer, ForeignKey(f"{fk_table}.id"), nullable=True)

    model_class = type(class_name, (Base,), attrs)
    MODELS[endpoint] = model_class

    return model_class
