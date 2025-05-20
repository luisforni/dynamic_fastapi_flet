import flet as ft
from frontend.utils.colors import COLORS

class CreateButton(ft.IconButton):
    def __init__(self, on_click):
        super().__init__(
            icon=ft.icons.ADD,
            tooltip="Agregar",
            on_click=on_click,
            icon_color="green",
        )

def CancelButton(on_click):
    return ft.TextButton(
        "Cancelar", 
        on_click=on_click, 
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=COLORS["cancel"]
        )
    )

def SaveButton(on_click):
    return ft.TextButton(
        "Guardar", 
        on_click=on_click, 
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=COLORS["save"]
        )
    )

def DeleteButton(on_click):
    return ft.TextButton(
        "Eliminar", 
        on_click=on_click, 
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=COLORS["delete"]
        )
    )

