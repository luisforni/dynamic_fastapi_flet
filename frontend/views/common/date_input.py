import flet as ft

class DateInput(ft.Container):
    def __init__(self, value=None, on_change=None):
        super().__init__()

        self.date_picker = ft.DatePicker(
            on_change=on_change
        )

        self.text_field = ft.TextField(
            value=value,
            read_only=True,
            on_click=self.open_date_picker
        )

        self.content = ft.Column([self.text_field, self.date_picker])

    def open_date_picker(self, e=None):
        self.date_picker.pick_date()
