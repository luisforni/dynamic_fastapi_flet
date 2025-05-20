from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from backend.core.models import MODEL_CONFIGS

Base = declarative_base()
MODELS = {}


def create_model_class(endpoint: str):
    config = MODEL_CONFIGS.get(endpoint)
    if not config:
        return None

    class_attrs = {
        "__tablename__": config["table_name"],
        "id": Column(Integer, primary_key=True, index=True, autoincrement=True),
    }

    for field in config["data_keys"]:
        field_type = String(255)
        if field.endswith("_id"):
            field_type = Integer
        elif field in ["is_active", "is_superuser", "is_staff"]:
            field_type = Boolean
        elif "date" in field or "time" in field:
            field_type = DateTime

        class_attrs[field] = Column(field_type, nullable=True)

    for fk, fk_data in config.get("foreign_keys", {}).items():
        fk_column_name = f"{fk}_id"
        class_attrs[fk_column_name] = Column(Integer, ForeignKey(f"{fk_data['table']}.id"), nullable=True)
        class_attrs[fk_data["display"]] = relationship(fk_data["table"].capitalize())

    model_class = type(config["table_name"].capitalize(), (Base,), class_attrs)

    MODELS[endpoint] = model_class
    return model_class

for endpoint in MODEL_CONFIGS.keys():
    create_model_class(endpoint)

