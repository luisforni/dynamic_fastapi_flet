
# dynamic_fastapi_flet

Aplicación dinámica con generación automática de modelos desde base de datos, backend en **FastAPI** y frontend en **Flet**. Permite crear interfaces CRUD completas a partir de cualquier estructura relacional.

---

## Comandos para ejecutar la aplicación

### 1. Generar modelos desde la base de datos

Este script analiza la estructura de la base de datos y genera modelos dinámicamente en el directorio **backend\core\models**:

```bash
python backend/generate_models.py
```

---

### 2. Levantar el backend con FastAPI

Inicia el servidor backend:

```bash
uvicorn backend.main:app --reload
```

---

### 3. Iniciar el frontend con Flet

Levanta la interfaz gráfica de usuario:

```bash
python -m frontend.main
```

---

## Funcionalidades

- CRUD dinámico desde el frontend
- Generación de modelos automática desde la BBDD
- API REST generada con FastAPI
- Interfaz gráfica multiplataforma con Flet
- Modular y escalable

---

## Configuración del entorno

Antes de ejecutar la aplicación, crea un archivo `.env` en la raíz del proyecto con la configuración de conexión a tu base de datos y la URL base del backend:

```env
DB_ENGINE=postgresql
DB_NAME=db_name
DB_USER=db_user
DB_PASSWORD=db_password
DB_HOST=localhost
DB_PORT=5432

BASE_URL="http://127.0.0.1:8000"
