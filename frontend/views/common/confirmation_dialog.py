import flet as ft

class ConfirmationDialog(ft.AlertDialog):
    def __init__(self, title, message, on_confirm, on_cancel):
        super().__init__()
        self.title = ft.Text(title, size=20, weight=ft.FontWeight.BOLD)
        self.content = ft.Text(message)
        self.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self.close_dialog(on_cancel)),
            ft.TextButton("Eliminar", on_click=lambda e: self.close_dialog(on_confirm), style=ft.ButtonStyle(color=ft.colors.RED)),
        ]
        self.modal = True

    def close_dialog(self, action):
        self.open = False
        action()
