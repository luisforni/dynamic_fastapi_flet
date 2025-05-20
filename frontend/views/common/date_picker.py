import flet as ft
from datetime import datetime
from frontend.utils.colors import get_theme_colors

class DatePickerInput(ft.Row):
    def __init__(self, label, value=None, theme_mode=None):
        super().__init__(expand=True)
        self.label = label
        self.value = value
        self.theme_colors = get_theme_colors(theme_mode)
        initial_value = self.format_display_datetime(value) if value else ""
        self.date_picker = ft.DatePicker(on_change=self.update_value)
        self.text_field = ft.TextField(
            label=label,
            value=initial_value, 
            read_only=True,
            on_click=self.open_picker,
            expand=True,
            bgcolor=self.theme_colors["background"],
            color=self.theme_colors["table_text"],
            border_color=self.theme_colors["table_border"],
        )
        self.controls = [self.text_field, self.date_picker]  

    def open_picker(self, e):
        self.date_picker.open = True
        self.update()

    def update_value(self, e):
        date_value = self.date_picker.value
        if date_value:
            formatted_display_date = self.format_display_datetime(date_value)
            formatted_iso_date = self.format_datetime(date_value)
            self.text_field.value = formatted_display_date
            self.value = formatted_iso_date
        self.update()

    def format_display_datetime(self, datetime_value):
        if datetime_value is None:
            
            return ""
        if isinstance(datetime_value, datetime):
            return datetime_value.strftime("%d/%m/%Y %H:%M")
        if isinstance(datetime_value, str):
            try:
                dt_obj = datetime.fromisoformat(datetime_value.replace("Z", ""))
                return dt_obj.strftime("%d/%m/%Y %H:%M")
            except ValueError:
                return ""
        return ""

    def format_datetime(self, datetime_value):
        if datetime_value is None:
            return ""
        if isinstance(datetime_value, datetime):
            return datetime_value.astimezone().isoformat(timespec='seconds')
        if isinstance(datetime_value, str):
            try:
                dt_obj = datetime.fromisoformat(datetime_value.replace("Z", ""))
                return dt_obj.astimezone().isoformat(timespec='seconds')
            except ValueError:
                return ""
        return ""

    def get_value(self):
        if self.date_picker.value:
            return self.format_datetime(self.date_picker.value)
        if self.text_field.value and self.text_field.value.strip():
            return self.value
        return ""
    
    def update_theme(self, theme_mode):
        self.theme_colors = get_theme_colors(theme_mode)
        self.text_field.bgcolor = self.theme_colors["background"]
        self.text_field.color = self.theme_colors["table_text"]
        self.text_field.border_color = self.theme_colors["table_border"]
        self.update()
