import flet as ft

class Navbar(ft.Container):
    def __init__(self, toggle_menu, title, go_home, toggle_theme, page, theme_colors):
        super().__init__()
        self.page = page
        self.title = title
        self.go_home = go_home
        self.toggle_theme = toggle_theme
        self.theme_colors = theme_colors
        self.content = ft.Row(
            [
                ft.IconButton(
                    icon=ft.icons.MENU,
                    tooltip="Abrir menú",
                    on_click=toggle_menu,
                    icon_color=self.theme_colors["navbar_text"],
                ),
                ft.Container(
                    expand=True,
                    content=ft.Text(self.title, size=24, weight=ft.FontWeight.BOLD, color=self.theme_colors["navbar_text"])
                ),
                ft.IconButton(
                    icon=ft.icons.HOME,
                    tooltip="Ir a Inicio",
                    on_click=self.go_home,
                    icon_color=self.theme_colors["navbar_text"]
                ),
                ft.IconButton(
                    icon=ft.icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.icons.LIGHT_MODE,
                    tooltip="Cambiar tema",
                    on_click=self.toggle_theme,
                    icon_color=self.theme_colors["navbar_text"]
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10,
        )
        self.padding = 15
        self.bgcolor = self.theme_colors["navbar_bg"]
        self.border_radius = 10

    def update_title(self, new_title):
        self.title = new_title
        self.content.controls[1] = ft.Container(
            expand=True,
            content=ft.Text(new_title, size=24, weight=ft.FontWeight.BOLD, color=self.theme_colors["navbar_text"])
        )
        self.page.update()
