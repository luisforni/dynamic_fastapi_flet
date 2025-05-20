PRIMARY_COLOR = "#b22222"
SECONDARY_COLOR = "#ff6347"
TEXT_COLOR = "#ffffff"
BACKGROUND_COLOR = "#f6f8fa"
BORDER_COLOR = "#d0d7de"

COLORS = {
    "cancel": "#FF4C4C",
    "save": "#28A745",
    "edit": "#007BFF",
    "delete": "#DC3545",
    "primary": "#6C757D",
}

import flet as ft

def get_theme_colors(theme_mode):
    if theme_mode == ft.ThemeMode.DARK:
        return {
            "navbar_bg": "#b22222",  # Rojo
            "navbar_text": "#ffffff",  # Blanco
            "background": "#121212",  # Fondo oscuro estándar
            "table_bg": "#1e1e1e",  # Un poco más claro que el fondo
            "table_border": "#f0f0f0",  # Mismo color que la tabla en modo claro
            "table_text": "#f0f0f0",  # Mismo color que los bordes en modo claro
        }
    elif theme_mode == ft.ThemeMode.LIGHT:
        return {
            "navbar_bg": "#b22222",  # Rojo
            "navbar_text": "#ffffff",  # Blanco
            "background": "#ffffff",  # Fondo claro
            "table_bg": "#f6f6f6",  # Un poco más oscuro que el fondo
            "table_border": "#1e1e1e",  # Mismo color que la tabla en modo oscuro
            "table_text": "#1e1e1e",  # Mismo color que los bordes en modo oscuro
        }
    else:
        return {
            "navbar_bg": "#b22222",  # Rojo
            "navbar_text": "#ffffff",  # Blanco
            "background": "#121212",  # Fondo oscuro estándar
            "table_bg": "#1e1e1e",  # Un poco más claro que el fondo
            "table_border": "#f0f0f0",  # Mismo color que la tabla en modo claro
            "table_text": "#f0f0f0",  # Mismo color que los bordes en modo claro
        }

