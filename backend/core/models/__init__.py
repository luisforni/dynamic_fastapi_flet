import os
import importlib
import pkgutil

MODEL_CONFIGS = {}

models_dir = os.path.dirname(__file__)

# Carga dinámica de configuraciones
for _, module_name, _ in pkgutil.iter_modules([models_dir]):
    if module_name == "__init__":
        continue
    module = importlib.import_module(f"backend.core.models.{module_name}")
    config = getattr(module, "MODEL_CONFIG", None)
    if config:
        MODEL_CONFIGS[config["endpoint"]] = config
