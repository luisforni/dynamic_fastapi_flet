from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from backend.core.models import MODEL_CONFIGS
from sqlalchemy import MetaData
from backend.core.database import engine
from sqlalchemy import or_, cast, String
from backend.core.models_loader import create_model_class

metadata = MetaData()
metadata.reflect(bind=engine)

def get_all(endpoint: str, db: Session, page: int, page_size: int, query: str = None):
    config = MODEL_CONFIGS.get(endpoint)
    if not config:
        return {"error": "Tabla no encontrada."}

    table_name = config["table_name"]
    columns = [f"{table_name}.{col}" for col in config["data_keys"]]
    join_clause = []  
    foreign_columns = []
    foreign_keys = config.get("foreign_keys", {})
    join_aliases = {}  

    where_conditions = []

    for fk, fk_data in foreign_keys.items():
        fk_table = fk_data["table"]
        fk_display = fk_data["display"]
        fk_column = f"{table_name}.{fk}"

        """print(f"[join_clause]: {join_clause}")
        print(f"[fk_table]: {fk_table}")
        print(f"[fk_display]: {fk_display}")
        print(f"[fk_column]: {fk_column}")"""

        if fk_table in join_aliases:
            alias = join_aliases[fk_table]
        else:
            alias = fk_table  

            for clause in join_clause:
                if f"JOIN {fk_table}" in clause:
                    alias = clause.split(" AS ")[-1].split(" ")[0]  
                    break
            
            if alias == fk_table:
                alias = f"{fk_table}_alias_{len(join_aliases) + 1}"
                join_aliases[fk_table] = alias  

        if not any(f"JOIN {fk_table}" in clause for clause in join_clause):
            join_clause.append(f"LEFT JOIN {fk_table} AS {alias} ON {fk_column} = {alias}.id")

        foreign_columns.append(f"{alias}.{fk_display} AS {fk}_name")

    params = {"limit": page_size, "offset": (page - 1) * page_size}

    if query:
        for col in config["data_keys"]:
            if col != "id":
                field_type = config["inputs"].get(col, {}).get("type", "")
                """print(f"field_type: {field_type}")"""

                if field_type == "text":
                    if col.endswith("_id") and col in foreign_keys:
                        fk_table = foreign_keys[col]["table"]
                        alias = join_aliases[fk_table]
                        where_conditions.append(f"CAST({alias}.{foreign_keys[col]['display']} AS TEXT) ILIKE :query")
                    else:
                        where_conditions.append(f"{table_name}.{col} ILIKE :query")

        if where_conditions:
            where_clause = f"WHERE {' OR '.join(where_conditions)}"
            params["query"] = f"%{query}%"
        else:
            where_clause = ""
    else:
        where_clause = ""

    sql_query = f"""
        SELECT DISTINCT {', '.join(columns + foreign_columns)} 
        FROM {table_name} 
        {' '.join(join_clause)}
        {where_clause}
        LIMIT :limit OFFSET :offset
    """

    try:
        results = db.execute(text(sql_query), params).fetchall()
        all_columns = [col.split(".")[-1] for col in config["data_keys"]]
        all_columns += [f"{fk}_name" for fk in foreign_keys]
        if results and len(results[0]) != len(all_columns):
            raise ValueError(f"Error: La consulta SQL devolvió {len(results[0])} valores, pero se esperaban {len(all_columns)} claves.")

        records = [dict(zip(all_columns, row)) for row in results]

        """for record in records:
            print(record)"""

        return {endpoint: records}

    except Exception as e:
        return {"error": f"Error al obtener datos: {str(e)}"}

def get_one(endpoint: str, record_id: int, db: Session):
    config = MODEL_CONFIGS.get(endpoint)
    if not config:
        return {"error": "Tabla no encontrada."}

    table_name = config["table_name"]
    columns = ", ".join(config["data_keys"])

    query = text(f"SELECT {columns} FROM {table_name} WHERE id = :record_id")
    result = db.execute(query, {"record_id": record_id}).fetchone()

    return dict(result) if result else {"error": "Registro no encontrado."}

def create(endpoint: str, data: dict, db: Session):
    """Crea un nuevo registro."""
    config = MODEL_CONFIGS.get(endpoint)
    if not config:
        return {"error": "Tabla no encontrada."}

    table_name = config["table_name"]
    columns = ", ".join(data.keys())
    values = ", ".join([f":{key}" for key in data.keys()])

    query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({values}) RETURNING *")
    result = db.execute(query, data).fetchone()
    db.commit()

    return dict(result)

def update(endpoint, record_id, updated_data, db):
    try:
        table = metadata.tables.get(endpoint)

        if not table:
            return {"error": f"No se encontró la tabla {endpoint}"}

        if not isinstance(updated_data, dict):
            return {"error": "Datos de actualización inválidos"}

        set_clause = ", ".join([f"{key} = :{key}" for key in updated_data.keys()])

        query = f"UPDATE {endpoint} SET {set_clause} WHERE id = :record_id"

        params = updated_data.copy()
        params["record_id"] = record_id
        db.execute(query, params)
        db.commit()

        return {"success": True, "message": f"Registro {record_id} actualizado correctamente"}

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

def delete(endpoint: str, record_id: int, db: Session):
    config = MODEL_CONFIGS.get(endpoint)
    if not config:
        return {"error": "Tabla no encontrada."}

    table_name = config["table_name"]

    query = text(f"DELETE FROM {table_name} WHERE id = :record_id RETURNING *")
    result = db.execute(query, {"record_id": record_id}).fetchone()
    db.commit()

    return {"message": "Registro eliminado."} if result else {"error": "Registro no encontrado."}
