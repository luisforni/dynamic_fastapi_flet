import flet as ft

class TextInput(ft.TextField):
    def __init__(self, label, value="", on_change=None, theme_colors=None):
        super().__init__(
            label=label,
            value=value,
            on_change=on_change,
            bgcolor=theme_colors["background"],
            color=theme_colors["table_text"],
            border_color=theme_colors["table_border"]
        )
