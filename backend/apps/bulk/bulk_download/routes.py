from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from backend.core.database import get_db
import pandas as pd
from io import StringIO
import importlib
from backend.core.models_loader import MODEL_CONFIGS

router = APIRouter()

def get_model_config_by_endpoint(endpoint: str):
    if endpoint in MODEL_CONFIGS:
        return MODEL_CONFIGS[endpoint]

    model_module = importlib.import_module(f"backend.models.{endpoint}")
    model_config = getattr(model_module, "MODEL_CONFIG", None)

    if model_config is None:
        return None

    return model_config

def transform_foreign_keys(model_config, columns):
    foreign_keys = model_config.get("foreign_keys", {})
    return [f"{col}_id" if col in foreign_keys else col for col in columns]

@router.get("/download/")
def download_csv(
    endpoint: str = Query(..., description="Nombre del endpoint"),
    db: Session = Depends(get_db)
):
    model_config = get_model_config_by_endpoint(endpoint)
    if not model_config:
        raise HTTPException(status_code=400, detail="Endpoint no válido para descarga.")

    if not model_config.get("bulk_download", False):
        raise HTTPException(status_code=400, detail="Este endpoint no permite descarga masiva.")

    table_real_name = model_config["table_name"]
    columns = model_config["data_keys"]

    query = text(f"SELECT {', '.join(columns)} FROM {table_real_name}")
    results = db.execute(query).fetchall()
    if not results:
        raise HTTPException(status_code=404, detail="No hay datos disponibles en la tabla.")
    
    df = pd.DataFrame(results, columns=columns)

    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{table_real_name}.csv"'
        }
    )

