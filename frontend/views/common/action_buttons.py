import flet as ft
from frontend.views.common.buttons import CancelButton, SaveButton, DeleteButton

class ActionButtons(ft.Row):
    def __init__(self, on_save, on_cancel, on_delete, current_page, spacing=10):
        super().__init__()

        self.on_save = on_save
        self.on_cancel = on_cancel
        self.on_delete = on_delete
        self.current_page = current_page

        self.controls = [
            DeleteButton(lambda e: self.on_delete(self.current_page)),
            CancelButton(lambda e: self.on_cancel(self.current_page)),
            SaveButton(lambda e: self.on_save(self.current_page)),
        ]

        self.spacing = spacing
