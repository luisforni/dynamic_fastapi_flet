from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, cast, String
from datetime import datetime, date
from backend.core.database import get_db
from backend.core.models import MODEL_CONFIGS
from backend.apps.api.views import get_all, get_one, create, update, delete
from backend.core.models_loader import MODELS
from backend.core.models_loader import create_model_class

router = APIRouter()

@router.get("/{endpoint}/all/")
def get_total_pages(
    endpoint: str,
    db: Session = Depends(get_db),
    page_size: int = 10,
    query: str = Query(None, description="Texto de búsqueda opcional")
):
    model_class = MODELS.get(endpoint) or create_model_class(endpoint)
    if not model_class:
        raise HTTPException(status_code=400, detail=f"Endpoint `{endpoint}` no válido.")
    query_base = db.query(func.count()).select_from(model_class)
    if query:
        search_filters = []
        for column in model_class.__table__.columns:
            if issubclass(column.type.python_type, (str, int, float)):  
                search_filters.append(cast(column, String).ilike(f"%{query}%"))

        if search_filters:
            query_base = query_base.filter(or_(*search_filters))
    total_items = query_base.scalar()
    total_pages = max(1, (total_items // page_size) + (1 if total_items % page_size else 0))
    return {
        "total_items": total_items,
        "total_pages": total_pages
    }

@router.get("/{endpoint}/")
def read_records(endpoint: str, db: Session = Depends(get_db), page: int = 1, page_size: int = 10, query: str = None):
    if endpoint not in MODEL_CONFIGS:
        raise HTTPException(status_code=400, detail="Endpoint no válido")
    return get_all(endpoint, db, page, page_size, query)

@router.get("/{endpoint}/{record_id}")
def read_record(endpoint: str, record_id: int, db: Session = Depends(get_db)):
    if endpoint not in MODEL_CONFIGS:
        raise HTTPException(status_code=400, detail="Endpoint")
    return get_one(endpoint, record_id, db)

@router.post("/{endpoint}/")
def create_record(endpoint: str, data: dict, db: Session = Depends(get_db)):
    model_class = MODELS.get(endpoint) or create_model_class(endpoint)
    if not model_class:
        raise HTTPException(status_code=400, detail="Endpoint")
    model_config = MODEL_CONFIGS.get(endpoint, {})
    column_mapping = model_config.get("column_mapping", {})
    transformed_data = {column_mapping.get(k, k): v for k, v in data.items()}
    try:
        with db.begin():
            db.execute(model_class.__table__.insert().values(**transformed_data))
        db.commit()
        return {"message": "Registro creado exitosamente", "record": transformed_data}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear el registro: {str(e)}")

@router.put("/{endpoint}/{record_id}")
def update_record(endpoint: str, record_id: int, updated_data: dict, db: Session = Depends(get_db)):
    model_class = MODELS.get(endpoint) or create_model_class(endpoint)
    if not model_class:
        raise HTTPException(status_code=400, detail=f"No se encontró el modelo para '{endpoint}'")
    try:
        record = db.query(model_class).filter(model_class.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"Registro con ID {record_id} no encontrado en '{endpoint}'")
        model_fields = {column.name for column in model_class.__table__.columns}
        model_config = MODEL_CONFIGS.get(endpoint, {})
        column_mapping = model_config.get("column_mapping", {})
        transformed_data = {}
        for key, value in updated_data.items():
            mapped_key = column_mapping.get(key, key)
            if mapped_key in model_fields:
                current_value = getattr(record, mapped_key, None)
                if current_value != value:
                    transformed_data[mapped_key] = value
        if not transformed_data:
            raise HTTPException(status_code=400, detail="No se enviaron campos válidos para actualizar")
        update_query = model_class.__table__.update().where(model_class.id == record_id).values(**transformed_data)
        db.execute(update_query)
        db.commit()
        return {"success": True, "record": transformed_data}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

@router.delete("/{endpoint}/{record_id}")
def delete_record(endpoint: str, record_id: int, db: Session = Depends(get_db)):
    if endpoint not in MODEL_CONFIGS:
        raise HTTPException(status_code=400, detail="Endpoint no válido.")
    return delete(endpoint, record_id, db)
