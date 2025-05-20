import asyncio
import httpx
import importlib
import os
from frontend.views.tables.table.generic_table import GenericTableView
from frontend.views.tables.table.form_utils import (
    create_text_input,
    create_boolean_switch,
    create_date_input,
    create_filtered_dropdown,
    create_number_input,
    load_model_config
)
from frontend.utils.api import api_client

class TableBuilder:
    def __init__(self, page):
        self.page = page
        self.tables = {}

    async def load_table_configs(self):
        model_data = await self.fetch_model_configs()
        if not model_data:
            self.tables = {}
            return
        tasks = [self.fetch_model_config(model["endpoint"]) for model in model_data]
        results = await asyncio.gather(*tasks)
        self.tables = {
            model_data[i]["endpoint"]: results[i] for i in range(len(model_data)) if results[i]
        }

    async def fetch_model_configs(self):
        url = f"{api_client.BASE_URL}/models/titles/"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json().get("titles", [])
            return []

    async def fetch_model_config(self, endpoint):
        url = f"{api_client.BASE_URL}/models/{endpoint}/config/"
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except:
                pass
        return {}

    def generate_table_ui(self, table_config):
        class TableUI(GenericTableView):
            def __init__(self, page, theme_mode):
                super().__init__(
                    page=page,
                    endpoint=table_config["endpoint"],
                    title=table_config["title"],
                    columns=[col.replace("_id", "_id_name") if "_id" in col else col for col in table_config["columns"]],
                    data_keys=[
                        key.replace("_id", "_id_name") if key.endswith("_id") and key in table_config.get("foreign_keys", {}) else key
                        for key in table_config["data_keys"]
                    ],
                    foreign_keys=table_config.get("foreign_keys", {}),
                    input_config=self.get_input_config(theme_mode)
                )

            def get_input_config(self, theme_mode):
                inputs = {}
                foreign_keys = table_config.get("foreign_keys", {})
                for key, field in table_config["inputs"].items():
                    field_type = field.get("type")
                    if key.endswith("_id") and key not in foreign_keys:
                        field_type = "text"
                    if field_type == "text":
                        inputs[key] = create_text_input(field["label"], key, self, theme_mode)
                    elif field_type == "boolean":
                        inputs[key] = create_boolean_switch(field["label"], key, self)
                    elif field_type == "dropdown":
                        model_config = load_model_config(table_config["endpoint"])
                        if model_config:
                            foreign_keys = model_config.get("foreign_keys", {})
                            foreign_key_column = foreign_keys.get(key, {}).get("display", "")
                            inputs[key] = create_filtered_dropdown(field["label"], key, field["endpoint"], self, foreign_key_column, theme_mode)
                    elif field_type == "number":
                        inputs[key] = create_number_input(field["label"], key, self, theme_mode)
                    elif field_type == "date":
                        inputs[key] = create_date_input(field["label"], key, self)
                return inputs
        return TableUI

    def get_available_tables(self):
        return list(self.tables.keys())

    def get_table_ui(self, endpoint):
        table_config = self.tables.get(endpoint)
        if table_config:
            return self.generate_table_ui(table_config)
        return None
