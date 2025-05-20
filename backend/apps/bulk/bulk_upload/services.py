import importlib
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from backend.core.database import get_db
from io import BytesIO
import os

router = APIRouter()

dir_path = os.path.dirname(__file__)
models_path = os.path.join(dir_path, "../models")

def get_model_config_by_endpoint(endpoint: str):
    try:
        model_module = importlib.import_module(f"backend.models.{endpoint}")
        return getattr(model_module, "MODEL_CONFIG", None)
    except ModuleNotFoundError:
        return None

def transform_foreign_keys(model_config, columns):
    foreign_keys = model_config.get("foreign_keys", {})
    return [f"{col}_id" if col in foreign_keys else col for col in columns]

def process_file(file: UploadFile, expected_columns):
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(file.file.read()), engine='openpyxl')
        else:
            return None, "Formato de archivo no válido"

  
        missing_columns = [col for col in expected_columns if col not in df.columns]
        extra_columns = [col for col in df.columns if col not in expected_columns]

        if missing_columns or extra_columns:
            error_message = "⚠️ Columnas incorrectas. "
            if missing_columns:
                error_message += f"Faltan: {', '.join(missing_columns)}. "
            if extra_columns:
                error_message += f"Columnas extra: {', '.join(extra_columns)}."
            return None, error_message

        return df, None 

    except Exception as e:
        return None, f"❌ Error procesando archivo: {e}"

@router.post("/upload/")
def upload_file(
    file: UploadFile = File(...),
    endpoint: str = Form(...),
    db: Session = Depends(get_db),
):
    model_config = get_model_config_by_endpoint(endpoint)
    if not model_config:
        raise HTTPException(status_code=400, detail="Endpoint no válido para carga de datos.")

    table_name_real = model_config["table_name"]
    columns = transform_foreign_keys(model_config, model_config["data_keys"])

    df, error = process_file(file, columns)
    if error:
        raise HTTPException(status_code=400, detail=error)

    try:
        existing_records = db.execute(text(f"SELECT {columns[0]} FROM {table_name_real}")).fetchall()
        existing_records = {row[0] for row in existing_records}

        new_records = [
            {col: row[col] for col in columns} 
            for _, row in df.iterrows() if row[columns[0]] not in existing_records
        ]

        if not new_records:
            raise HTTPException(status_code=400, detail="No hay nuevos registros para insertar.")

        query_insert = text(
            f"INSERT INTO {table_name_real} ({', '.join(columns)}) VALUES ({', '.join([f':{col}' for col in columns])})"
        )

        db.execute(query_insert, new_records)
        db.commit()

        return {"message": "Datos cargados exitosamente", "rows_inserted": len(new_records)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
