import os
import psycopg2
import json
from dotenv import load_dotenv
load_dotenv()

DB_CONFIG = {
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "type":  os.getenv("DB_ENGINE"),
}

MODELS_DIRECTORY = "backend/core/models"

if not os.path.exists(MODELS_DIRECTORY):
    os.makedirs(MODELS_DIRECTORY)

def connect_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
        )
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def get_display_field(cursor, table):
    cursor.execute(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = '{table}' 
        AND data_type IN ('character varying', 'text')
        ORDER BY ordinal_position 
        LIMIT 1;
    """)
    result = cursor.fetchone()
    return result[0] if result else "id"

def save_file(estructura, file_name="estructura_bd.txt"):
    with open(file_name, "w", encoding="utf-8") as f:
        for table, columns in estructura.items():
            f.write(f"Tabla: {table}\n")
            f.write("-" * (7 + len(table)) + "\n")
            for columna in columns:
                linea = (f"Columna: {columna['column']} | Tipo: {columna['type']} | "
                         f"Nullable: {columna['nullable']} | "
                         f"FK: {columna['foreign_table']}({columna['foreign_column']})\n" if columna['foreign_table'] else "\n")
                f.write(linea)
            f.write("\n")

def get_db_structure(cursor):
    cursor.execute("""
        WITH foreign_keys AS (
            SELECT
                kcu.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu 
                ON tc.constraint_name = ccu.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
        )
        SELECT 
            c.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,
            fk.foreign_table,
            fk.foreign_column
        FROM information_schema.columns c
        LEFT JOIN foreign_keys fk
            ON c.table_name = fk.table_name 
            AND c.column_name = fk.column_name
        WHERE c.table_schema = 'public'
        ORDER BY c.table_name, c.ordinal_position;
    """)

    estructura = {}
    for row in cursor.fetchall():
        table, columna, tipo, nullable, foreign_table, foreign_column = row
        if table not in estructura:
            estructura[table] = []
        estructura[table].append({
            "column": columna,
            "type": tipo,
            "nullable": nullable,
            "foreign_table": foreign_table if foreign_table else None,
            "foreign_column": foreign_column if foreign_column else None
        })
    
    return estructura

def formatear_titulo(nombre):
    return " ".join([palabra.capitalize() for palabra in nombre.split("_")])

def determinar_tipo_input(nombre_columna, tipo_dato, foreign_keys):
    text_types = {"character varying", "text", "integer", "bigint", "smallint", "decimal", "numeric", "real", "double precision"}
    number_types = {}
    boolean_types = {"boolean"}
    date_types = {"timestamp without time zone", "timestamp with time zone"}

    es_foreign_key = nombre_columna in foreign_keys

    if es_foreign_key:
        return "dropdown"
    elif tipo_dato in number_types:
        return "text"
    elif tipo_dato in text_types:
        return "text"
    elif tipo_dato in boolean_types:
        return "boolean"
    elif tipo_dato in date_types:
        return "date"
    else:
        return "text"

def generar_modelo(cursor, table, columns):
    foreign_keys = {}
    inputs = {}
    column_mapping = {}

    for col in columns:
        if col["column"].endswith("_id"):
            if col["foreign_table"]:
                display_column = get_display_field(cursor, col["foreign_table"])
                foreign_keys[col["column"]] = {
                    "table": col["foreign_table"],
                    "display": display_column
                }
                inputs[col["column"]] = {
                    "label": formatear_titulo(col["column"]),
                    "type": "dropdown",
                    "endpoint": col["foreign_table"]
                }
            else:
                inputs[col["column"]] = {
                    "label": formatear_titulo(col["column"]),
                    "type": "number"
                }
        elif not col["column"].endswith("id"):
            inputs[col["column"]] = {
                "label": formatear_titulo(col["column"]),
                "type": determinar_tipo_input(col["column"], col["type"], foreign_keys)
            }
        
        column_mapping[formatear_titulo(col["column"])] = col["column"]
    
    formatted_columns = [formatear_titulo(col["column"]) for col in columns]
    data_keys = [col["column"] for col in columns]

    model_config = {
        "title": formatear_titulo(table),
        "table_name": table,
        "endpoint": table,
        "columns": formatted_columns,
        "data_keys": data_keys,
        "foreign_keys": foreign_keys,
        "inputs": inputs,
        "column_mapping": column_mapping,
        "bulk_upload": False,
        "bulk_download": False
    }

    return model_config

def guardar_modelo(table, model_config):
    file_path = os.path.join(MODELS_DIRECTORY, f"{table}.py")
    content = "MODEL_CONFIG = " + json.dumps(model_config, indent=4, ensure_ascii=False)
    content = content.replace("true", "True").replace("false", "False")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def generate_models():
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    estructura_bd = get_db_structure(cursor)

    for table, columns in estructura_bd.items():
        model_config = generar_modelo(cursor, table, columns)
        guardar_modelo(table, model_config)

    cursor.close()
    conn.close()

def main():
    generate_models()

if __name__ == "__main__":
    main()
