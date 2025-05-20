import flet as ft
from frontend.views.common.filtered_dropdown import FilteredDropdown
from frontend.views.common.boolean_switch import BooleanSwitch
from frontend.views.common.date_picker import DatePickerInput
from frontend.utils.api import api_client
from datetime import datetime, timezone

class EditForm(ft.Container):
    def __init__(self, page, title, fields, on_save, on_cancel, on_delete, record_id, current_page, endpoint):
        super().__init__(
            padding=20,
            border_radius=10,
            expand=True,
            height=page.height * 0.9,
        )
        self.page = page
        self.title = title
        self.fields = fields
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.on_delete = on_delete
        self.record_id = record_id
        self.current_page = current_page
        self.endpoint = endpoint
        self.build_form()

    def build_form(self):
        header_section = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.on_cancel(self.current_page)),
                    ft.Text(self.title, size=24, weight=ft.FontWeight.BOLD, expand=True),
                    ft.IconButton(ft.icons.SAVE, on_click=self.save_edit if self.record_id else self.save_create),
                    ft.IconButton(ft.icons.DELETE, on_click=self.delete_record if self.record_id else None),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            margin=ft.Margin(left=0, top=0, right=0, bottom=20),
        )
        form_fields = ft.ResponsiveRow(
            [
                ft.Container(
                    content=ft.Column([field], spacing=3),
                    padding=ft.padding.symmetric(horizontal=5),
                    margin=ft.Margin(left=0, top=0, right=0, bottom=5),
                    col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                )
                for key, field in self.fields.items()
            ],
            spacing=10,
        )
        fields_section = ft.Container(
            content=ft.Column(
                controls=[form_fields],
                spacing=10,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
        )
        self.content = ft.Column(
            [
                header_section,
                fields_section,
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    def save_edit(self, e=None):
        updated_data = {}
        for key, field in self.fields.items():
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
            elif isinstance(field, ft.TextField):
                updated_data[key] = field.value
        try:
            current_data = api_client.get_one(self.endpoint, self.record_id)  
        except Exception:
            current_data = {}
        has_changes = any(updated_data.get(k) != current_data.get(k) for k in updated_data)
        if not has_changes:
            self.on_cancel()
            return
        mapped_data = {}
        for k, v in updated_data.items():
            if k.endswith("_id_name"):  
                new_key = k.replace("_id_name", "_id")  
                mapped_data[new_key] = v
            else:
                mapped_data[k] = v  
        try:
            response = api_client.update(self.endpoint, self.record_id, mapped_data)
        except Exception as error:
            self.on_cancel()
            return
        self.on_cancel()

    def save_create(self, e=None):
        updated_data = {}
        for key, field in self.fields.items():
            if isinstance(field, FilteredDropdown):
                selected_value = field.get_value()
                if selected_value:
                    mapped_key = f"{key}_id" if not key.endswith("_id") else key  
                    updated_data[mapped_key] = selected_value[field.id_field]
                else:
                    updated_data[key] = None
            elif isinstance(field, BooleanSwitch):
                updated_data[key] = field.get_value()
            elif isinstance(field, DatePickerInput):  
                date_value = field.get_value()
                if date_value:
                    formatted_date = self.format_datetime(date_value)
                    updated_data[key] = formatted_date
                else:
                    updated_data[key] = ""
            elif isinstance(field, ft.TextField):  
                updated_data[key] = field.value
        response = api_client.create(self.endpoint, updated_data)
        self.on_cancel()

    def format_datetime(self, datetime_value):
        if datetime_value is None:
            return ""
        if isinstance(datetime_value, datetime):
            return datetime_value.astimezone().isoformat(timespec='seconds')
        if isinstance(datetime_value, str):
            datetime_value = datetime_value.strip()
            if not datetime_value: 
                return ""
            try:
                dt_obj = datetime.fromisoformat(datetime_value.replace("Z", ""))
                return dt_obj.astimezone().isoformat(timespec='seconds')
            except ValueError:
                return ""
        return ""

    def update_dropdown_value(self, key, e):
        if key in self.fields and isinstance(self.fields[key], ft.Dropdown):
            new_value = e.control.value
            if key.endswith("_id_name"):
                key_id = key.replace("_id_name", "_id")
                self.fields[key_id].value = new_value
            self.fields[key].value = new_value
            self.update()

    def delete_record(self, e):
        if self.on_delete:
            self.on_delete(self.record_id)
        self.on_cancel()
