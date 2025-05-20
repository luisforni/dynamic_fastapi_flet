import flet as ft

class ConfirmationDialog(ft.AlertDialog):
    def __init__(self, title, message, on_confirm):
        super().__init__()
        self.title = ft.Text(title)
        self.content = ft.Text(message)
        self.actions = [
            ft.ElevatedButton("Cancelar", on_click=self.close_dialog),
            ft.ElevatedButton("Confirmar", on_click=lambda e: self.confirm_action(e, on_confirm), bgcolor=ft.colors.RED),
        ]
        self.modal = True

    def confirm_action(self, e, on_confirm):
        on_confirm(e)
        self.open = False
        self.update()

    def close_dialog(self, e):
        self.open = False
        self.update()


class InputDialog(ft.AlertDialog):
    def __init__(self, title, label, placeholder, on_submit):
        super().__init__()
        self.input_field = ft.TextField(label=label, placeholder=placeholder, expand=True)
        self.title = ft.Text(title)
        self.content = self.input_field
        self.actions = [
            ft.ElevatedButton("Cancelar", on_click=self.close_dialog),
            ft.ElevatedButton("Guardar", on_click=lambda e: self.submit_data(e, on_submit)),
        ]
        self.modal = True

    def submit_data(self, e, on_submit):
        if not self.input_field.value.strip():
            return
        on_submit(self.input_field.value.strip())
        self.open = False
        self.update()

    def close_dialog(self, e):
        self.open = False
        self.update()

