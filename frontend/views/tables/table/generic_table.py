import flet as ft
import asyncio
import os
from frontend.utils.api import api_client
from frontend.views.common.pagination import PaginationComponent
from frontend.views.common.filtered_dropdown import FilteredDropdown
from frontend.views.common.buttons import CancelButton, SaveButton, DeleteButton, CreateButton
from frontend.views.common.boolean_switch import BooleanSwitch
from frontend.views.common.date_picker import DatePickerInput
from frontend.views.tables.table.edit_form import EditForm
from frontend.views.tables.table.form_utils import update_text_input
from frontend.views.common.filters import TextFilter
from datetime import datetime
from frontend.views.tables.bulk_download.generic_bulk_download import GenericBulkDownload
from frontend.views.tables.bulk_upload.generic_bulk_upload import GenericBulkUpload

class GenericTableView(ft.Container):
    def __init__(self, page, endpoint, title, columns, data_keys, foreign_keys=None, input_config=None, previous_page=1):
        super().__init__()

        self.page = page
        self.endpoint = endpoint
        self.title = title
        self.columns = columns
        self.data_keys = data_keys
        self.foreign_keys = foreign_keys or {}
        self.input_config = input_config or {}

        self.page_size = 8
        self.current_page = previous_page
        self.data = []
        self.total_items = 0
        self.is_editing = False
        self.current_item = None

        self.page_size = self.calculate_page_size()

        self.filter_field = TextFilter(
            label=f"Filtrar {self.title}",
            endpoint=self.endpoint,
            update_callback=self.apply_filters,
            theme_mode=self.page.theme_mode,
            page=self.page
        )

        self.create_button = CreateButton(on_click=self.create_new_record)

        self.table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(col)) for col in self.columns],
            rows=[],
            expand=True
        )

        self.table_container = ft.Container(
            content=ft.Column([self.table], scroll=ft.ScrollMode.ALWAYS),
            expand=True,
            height=self.page.height * 0.7,
            width=self.page.width,
            padding=ft.padding.only(top=10),
            alignment=ft.alignment.top_left
        )

        self.bulk_upload_modal = ft.AlertDialog(
            content=None, 
            title=ft.Text("Cargar Datos Masivos"),  
            actions=[ft.TextButton("Cerrar", on_click=self.close_bulk_upload_modal)] 
        )

        self.bulk_download_modal = ft.AlertDialog(
            content=None,  
            title=ft.Text("Descargar Datos Masivos"), 
            actions=[ft.TextButton("Cerrar", on_click=self.close_bulk_download_modal)]
        )

        self.pagination = PaginationComponent(
            total_items=self.total_items,
            page_size=self.page_size,
            on_page_change=self.change_page,
            current_page=self.current_page
        )
        
        self.main_container = ft.Container()
        self.build_table_view()
        self.page.run_task(self.get_data)

    async def get_data(self):
        query = self.filter_field.value.strip().lower() if self.filter_field else ""
        endpoint_with_api = f"api/{self.endpoint}"
        total_response = await asyncio.to_thread(api_client.get_all, f"{endpoint_with_api}/all", page_size=self.page_size, query=query)
        self.total_items = total_response.get("total_items", 0)
        self.total_pages = total_response.get("total_pages", 1)
        response = await asyncio.to_thread(api_client.get_all, endpoint_with_api, page=self.current_page, page_size=self.page_size, query=query)
        self.data = response.get(self.endpoint, [])
        self.update_table()
        self.pagination.update_pagination(self.total_items, self.total_pages)
        self.page.update()

    def calculate_page_size(self):
        row_height = 56
        available_height = self.page.height - 250
        return max(5, available_height // row_height)

    def handle_resize(self, e):
        self.page_size = self.calculate_page_size()
        self.page.run_task(self.get_data)

    def build_table_view(self):
        filters_row = ft.Row(
            [
                self.filter_field,
                self.create_button,
                ft.IconButton(ft.icons.UPLOAD, tooltip="Carga Masiva", on_click=lambda e: self.bulk_upload(e, self.endpoint)),
                ft.IconButton(ft.icons.DOWNLOAD, tooltip="Descarga Masiva", on_click=lambda e: self.bulk_download(e, self.endpoint))
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True
        )
        self.table_container = ft.Container(
            content=ft.Row(
                [self.table],
                scroll=ft.ScrollMode.ALWAYS,
            ),
            expand=True,
            height=self.page.height * 0.7,
            width=self.page.width,
            padding=ft.padding.only(top=10),
            alignment=ft.alignment.top_left,
        )
        pagination_container = ft.Container(
            content=self.pagination,
            width=self.page.width,
            height=60,
            alignment=ft.alignment.center,
            padding=ft.padding.only(top=10, bottom=10),
        )
        main_column = ft.Column(
            [
                filters_row,
                self.table_container,
                pagination_container
            ],
            expand=True,
            spacing=10,
            alignment=ft.MainAxisAlignment.START
        )
        self.main_container.content = main_column
        self.content = self.main_container
        self.page.update()

    def create_new_record(self, e=None):
        empty_fields = {key: "" for key in self.input_config}
        self.is_editing = False
        self.build_edit_view(fields_data=empty_fields, is_editing=False)

    def update_table(self):
        self.table.rows.clear()
        for item in self.data:
            row_cells = []
            for key in self.data_keys:
                if key.endswith("_id") and f"{key}_name" in item:
                    key_name = key.replace("_id", "_name")
                else:
                    key_name = key
                value = item.get(key_name, item.get(key, "-----"))
                if isinstance(value, bool):
                    row_cells.append(ft.DataCell(ft.Switch(value=value, disabled=True)))
                    continue
                if isinstance(value, str) and "T" in value and ":" in value:
                    dt_obj = datetime.fromisoformat(value.replace("Z", ""))
                    value = dt_obj.strftime("%d/%m/%Y %H:%M")
                max_length = 30
                display_value = (value[:max_length] + "...") if isinstance(value, str) and len(value) > max_length else value
                text_widget = ft.Text(display_value)
                if isinstance(value, str) and len(value) > max_length:
                    text_widget = ft.Container(content=ft.Text(display_value), tooltip=value)
                column_width = 50 if key == 'id' else 150
                row_cells.append(ft.DataCell(
                    ft.Container(content=text_widget, width=column_width, on_click=lambda e, i=item: self.open_edit_form(i))
                ))
            self.table.rows.append(ft.DataRow(cells=row_cells))
        self.page.update()

    def get_nested_value(self, item, key):
        keys = key.split(".")
        value = item
        for sub_key in keys:
            if isinstance(value, dict):
                value = value.get(sub_key, "-")
            else:
                return "-"
        if value is None:
            return "-"
        if key.endswith("_id"):
            key_name = key.replace("_id", "_id_name")
            return item.get(key_name, item.get(key, "-"))
        return value or "-" 

    def open_edit_form(self, item):
        self.is_editing = True
        self.current_item = item
        self.pagination.current_page = self.current_page 
        self.build_edit_view(is_editing=True)

    def build_edit_view(self, fields_data=None, is_editing=False):
        self.edit_fields = {}
        fields_data = fields_data or self.current_item

        for key, create_input in self.input_config.items():
            value = fields_data.get(key, "")

            if key in self.foreign_keys:
                value = {
                    "id": fields_data.get(f"{key}", None),
                    "name": fields_data.get(f"{key}_name", None)
                }

            self.edit_fields[key] = create_input(
                value,
                lambda e: update_text_input(self.edit_fields, key, e)
            )

            record_id = self.current_item["id"] if is_editing and self.current_item else None

            self.main_container.content = EditForm(
                page=self.page,
                title="Editar registro" if is_editing else "Crear registro",
                fields=self.edit_fields,
                on_save=self.save_edit if is_editing else self.save_create,
                on_cancel=self.go_back_to_table,
                on_delete=self.delete_record if is_editing else None, 
                record_id=record_id,
                current_page=self.current_page,
                endpoint=self.endpoint
            )

        self.page.update()

    def save_edit(self, e=None):
        updated_data = {}

        for key, field in self.edit_fields.items():
            if isinstance(field, FilteredDropdown):
                selected_value = field.get_value()

                if selected_value:
                    mapped_key = f"{key}_id" if not key.endswith("_id") else key  
                    updated_data[mapped_key] = selected_value[field.id_field]  
                else:
                    updated_data[key] = None

            elif isinstance(field, BooleanSwitch):
                updated_data[key] = field.get_value()
            
            elif isinstance(field, DatePickerInput) or "DatePickerInput" in str(type(field)):
                date_value = field.get_value()

                if date_value and isinstance(date_value, str) and date_value.strip():
                    try:
                        formatted_date = self.format_datetime(date_value)
                        updated_data[key] = formatted_date
                    except ValueError:
                        updated_data[key] = ""
                else:
                    updated_data[key] = ""

            else:
                updated_data[key] = field.value

        if hasattr(self, "column_mapping") and isinstance(self.column_mapping, dict):
            mapped_data = {
                self.column_mapping.get(k, k): v for k, v in updated_data.items()
            }
        else:
            mapped_data = {}
            for k, v in updated_data.items():
                if "_id" in k:
                    new_key = k.replace("_id", "_id_name")
                    mapped_data[new_key] = v
                else:
                    mapped_data[k] = v

        response = api_client.update(self.endpoint, self.current_item["id"], mapped_data)
        self.is_editing = False
        self.page.run_task(self.get_data)
        self.go_back_to_table()

    def save_create(self, e=None):
        updated_data = {}

        for key, field in self.edit_fields.items():
            if isinstance(field, FilteredDropdown):
                selected_value = field.get_value()
                if selected_value:
                    mapped_key = f"{key}_id" if not key.endswith("_id") else key
                    updated_data[mapped_key] = selected_value[field.id_field]
                else:
                    updated_data[key] = None

            elif isinstance(field, BooleanSwitch):
                updated_data[key] = field.get_value()
            
            elif isinstance(field, DatePickerInput) or "DatePickerInput" in str(type(field)): 
                date_value = field.get_value()

                if date_value and isinstance(date_value, str) and date_value.strip():  
                    try:
                        formatted_date = self.format_datetime(date_value)  
                        updated_data[key] = formatted_date
                    except ValueError:
                        updated_data[key] = "" 
                else:
                    updated_data[key] = "" 

        if hasattr(self, "column_mapping") and isinstance(self.column_mapping, dict):
            mapped_data = {
                self.column_mapping.get(k, k): v for k, v in updated_data.items()
            }
        else:
            mapped_data = {}
            for k, v in updated_data.items():
                if "_id" in k:
                    new_key = k.replace("_id", "_id_name")
                    mapped_data[new_key] = v
                else:
                    mapped_data[k] = v

        response = api_client.create(self.endpoint, mapped_data)

        if response.get("error"):
            return

        self.page.run_task(self.get_data)
        self.go_back_to_table()

    def go_back_to_table(self, e=None):
        self.is_editing = False
        self.main_container.content = None
        self.build_table_view()

        self.pagination.current_page = self.current_page
        self.pagination.update_pagination(self.total_items, self.total_pages)
        self.page.run_task(self.get_data)

        self.page.update()

    def change_page(self, new_page):
        self.current_page = new_page
        self.page.run_task(self.get_data)

    def apply_filters(self, e=None):
        query = self.filter_field.value.strip().lower()
        self.previous_page = 1
        self.current_page = 1
        self.pagination.current_page = 1
        self.page.run_task(self.get_data)

    def delete_record(self, e=None):
        if not self.current_item or "id" not in self.current_item:
            return
        record_id = self.current_item["id"]
        response = api_client.delete(self.endpoint, record_id)

        self.is_editing = False
        self.page.run_task(self.get_data)
        self.go_back_to_table()

    def is_date(self, value):
        try:
            datetime.fromisoformat(value.replace("Z", ""))
            return True
        except (ValueError, AttributeError):
            return False

    def format_date(self, value):
        try:
            date_obj = datetime.fromisoformat(value.replace("Z", ""))
            return date_obj.strftime("%d/%m/%Y %H:%M")
        except (ValueError, AttributeError):
            return value

    def bulk_upload(self, e, endpoint):
        bulk_upload_view = GenericBulkUpload(self.page, endpoint)
        self.bulk_upload_modal.content = bulk_upload_view.content
        self.page.overlay.append(self.bulk_upload_modal)
        self.bulk_upload_modal.open = True
        self.page.update()

    def bulk_download(self, e, endpoint):
        bulk_download_view = GenericBulkDownload(self.page, endpoint)
        self.bulk_download_modal.content = bulk_download_view.content
        self.page.overlay.append(self.bulk_download_modal)
        self.bulk_download_modal.open = True
        self.page.update()

    def close_bulk_upload_modal(self, e):
        self.bulk_upload_modal.open = False
        self.page.update()

    def close_bulk_download_modal(self, e):
        self.bulk_download_modal.open = False
        self.page.update()