from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from backend.core.database import get_db
import pandas as pd
from io import BytesIO
from sqlalchemy import inspect
import importlib

router = APIRouter()

def get_model_config_by_endpoint(endpoint: str):
    try:
        endpoint = endpoint.lower().strip("/")  
        model_module = importlib.import_module(f"backend.core.models.{endpoint}")
        model_config = getattr(model_module, "MODEL_CONFIG", None)

        if model_config:
            return model_config
        else:
            return None

    except:
        return None

def get_table_structure(endpoint: str, db: Session):
    try:
        model_config = get_model_config_by_endpoint(endpoint)
        if not model_config:
            return None

        table_name = model_config["table_name"]
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()

        if table_name not in tables:
            return None

        columns_info = inspector.get_columns(table_name)
        primary_keys = [col["name"] for col in columns_info if col.get("primary_key")]
        foreign_keys = {col["name"]: col["foreign_keys"] for col in columns_info if col.get("foreign_keys")}

        return {
            "table_name": table_name,
            "data_keys": [col["name"] for col in columns_info],
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys
        }

    except:
        return None

def process_file(file: UploadFile, expected_columns):
    try:
        file.file.seek(0)
        content = file.file.read()
        file.file.seek(0)

        if file.filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(content))
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(content), engine='openpyxl')
        else:
            return None

        expected_columns = [col for col in expected_columns if col != "id"]
        missing_columns = [col for col in expected_columns if col not in df.columns]

        if missing_columns:
            error_message = f"Columnas incorrectas. Faltan: {', '.join(missing_columns)}."
            return None, error_message

        return df, None  

    except Exception as e:
        return None, f"Error procesando archivo: {e}"

@router.post("/upload/{endpoint}")
async def upload_file(
    endpoint: str, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    table_config = get_table_structure(endpoint, db)
    if not table_config:
        raise HTTPException(status_code=400, detail="Tabla no encontrada en la base de datos.")

    table_name = table_config["table_name"]
    columns = table_config["data_keys"]

    columns_to_insert = [col for col in columns if col != "id"]

    df, error = process_file(file, columns_to_insert)
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    try:
        new_records = [
            {col: row[col] for col in columns_to_insert}  # Asegurar que incluya `cliente_id`
            for _, row in df.iterrows()
        ]

        if not new_records:
            raise HTTPException(status_code=400, detail="No hay nuevos registros para insertar.")

        query_insert = text(
            f"INSERT INTO {table_name} ({', '.join(columns_to_insert)}) VALUES ({', '.join([f':{col}' for col in columns_to_insert])})"
        )

        db.execute(query_insert, new_records)
        db.commit()

        return {"message": "Datos cargados exitosamente", "rows_inserted": len(new_records)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
