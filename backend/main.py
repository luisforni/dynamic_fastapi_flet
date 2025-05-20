from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from sqlalchemy import text
from backend.apps.api.routes import router as api_router
from backend.apps.bulk.bulk_upload.routes import router as bulk_upload_router
from backend.apps.bulk.bulk_download.routes import router as bulk_download_router
import os
import importlib.util

app = FastAPI()

MODELS_DIRECTORY = "backend/core/models"

@app.get("/models/titles/")
def get_model_titles():
    titles = []
    if not os.path.exists(MODELS_DIRECTORY):
        return {"titles": titles}
    for filename in os.listdir(MODELS_DIRECTORY):
        if filename.endswith(".py") and filename != "__init__.py":
            file_path = os.path.join(MODELS_DIRECTORY, filename)
            module_name = filename[:-3]
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "MODEL_CONFIG") and "title" in module.MODEL_CONFIG:
                titles.append({"title": module.MODEL_CONFIG["title"], "endpoint": module.MODEL_CONFIG["endpoint"]})
    return {"titles": titles}

@app.get("/models/{endpoint}/config/")
def get_model_config(endpoint: str):
    file_path = os.path.join(MODELS_DIRECTORY, f"{endpoint}.py")
    if not os.path.exists(file_path):
        return {"error": "Modelo no encontrado"}
    module_name = endpoint
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, "MODEL_CONFIG"):
        return module.MODEL_CONFIG
    return {"error": "MODEL_CONFIG no encontrado"}

@app.get("/healthcheck/")
def healthcheck(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "Conectado a PostgreSQL"}
    except Exception as e:
        return {"status": "Error de conexión", "error": str(e)}

app.include_router(api_router, prefix="/api", tags=["api"])
app.include_router(bulk_upload_router, prefix="/bulk_upload", tags=["bulk_upload"])
app.include_router(bulk_download_router, prefix="/bulk_download", tags=["bulk_download"])
