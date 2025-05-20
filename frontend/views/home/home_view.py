import flet as ft
import asyncio
from frontend.utils.colors import get_theme_colors
from frontend.views.common.navbar import Navbar
from frontend.views.tables.builder.builder import TableBuilder
from frontend.utils.api import api_client

class HomeView(ft.Column):
    def __init__(self, page, theme_mode):
        super().__init__()
        self.page = page
        self.theme_mode = theme_mode
        self.theme_colors = get_theme_colors(self.theme_mode)
        self.menu_open = False
        self.navbar = Navbar(self.toggle_menu, "Dynamic CRUD", self.go_home, self.toggle_theme, self.page, self.theme_colors)
        self.builder = TableBuilder(self.page)
        self.menu_items = self.get_dynamic_menu_items()
        self.filtered_menu_items = self.menu_items[:]
        self.search_field = ft.TextField(
            hint_text="Filtrar...",
            on_change=self.filter_menu,
            border_radius=10,
            bgcolor=self.theme_colors["navbar_bg"],
            color=self.theme_colors["navbar_text"]
        )
        self.menu_container = self.build_menu_container()
        self.menu_container.visible = False
        self.content = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        asyncio.create_task(self.load_menu_items())
        self.build_view()
        self.go_home(None)

    async def load_menu_items(self):
        await self.builder.load_table_configs()
        self.menu_items = self.get_dynamic_menu_items()
        self.filtered_menu_items = self.menu_items[:]
        self.update_menu_items()
        self.page.update()

    def get_dynamic_menu_items(self):
        if not self.builder.tables:
            return []
        return [
            {
                "text": table_config["title"],
                "on_click": lambda e, endpoint=endpoint: self.load_view(endpoint),
            }
            for endpoint, table_config in self.builder.tables.items()
        ]

    def update_menu_items(self):
        self.menu_items_column.controls.clear()
        for item in self.filtered_menu_items:
            self.menu_items_column.controls.append(
                ft.TextButton(text=item["text"], on_click=lambda e, action=item["on_click"]: self.handle_menu_click(action))
            )
        self.page.update()

    def build_menu_container(self):
        self.menu_items_column = ft.Column(
            expand=True,
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )    
        self.search_field = ft.TextField(
            hint_text="Filtrar...",
            on_change=self.filter_menu,
            border_radius=10,
            bgcolor=self.theme_colors["navbar_bg"],
            color=self.theme_colors["navbar_text"],
            width=250
        )
        self.update_menu_items()
        return ft.Container(
            content=ft.Column([
                self.search_field,
                self.menu_items_column
            ]),
            width=250,
            height=600,
            bgcolor=self.theme_colors["navbar_bg"],
            padding=15,
            visible=False
        )

    def update_menu_items(self):
        self.menu_items_column.controls.clear()
        for item in self.filtered_menu_items:
            if item.get("type") == "divider":
                self.menu_items_column.controls.append(ft.Divider(thickness=1, color=self.theme_colors["table_text"]))
            else:
                self.menu_items_column.controls.append(
                    ft.TextButton(
                        text=item["text"],
                        on_click=lambda e, action=item["on_click"]: self.handle_menu_click(action),
                        style=ft.ButtonStyle(
                            color=self.theme_colors["navbar_text"],
                            bgcolor=self.theme_colors["navbar_bg"],
                            shape=ft.RoundedRectangleBorder(radius=10),
                        )
                    )
                )
        self.page.update()

    def filter_menu(self, e):
        query = self.search_field.value.lower()
        self.filtered_menu_items = [
            item for item in self.menu_items if item.get("type") == "divider" or query in item["text"].lower()
        ]
        self.update_menu_items()

    def build_view(self):
        self.controls.append(
            ft.Column([
                self.navbar,
                ft.Stack([
                    self.content,
                    self.menu_container
                ])
            ], expand=True, spacing=10)
        )

    def toggle_menu(self, e):
        self.menu_open = not self.menu_open
        self.menu_container.visible = self.menu_open
        self.page.update()

    def handle_menu_click(self, on_click_action):
        self.close_menu()
        if on_click_action:
            on_click_action(None)

    def close_menu(self):
        self.menu_open = False
        self.menu_container.visible = False
        self.page.update()

    def go_home(self, e):
        self.content.controls.clear()
        self.content.controls.append(ft.Text("Dynamic CRUD", size=24, color=self.theme_colors["table_text"]))
        self.page.update()
        self.update_navbar_title("Dynamic CRUD") 

    def load_view(self, endpoint):
        table_ui_class = self.builder.get_table_ui(endpoint)
        if table_ui_class:
            self.content.controls.clear()
            self.content.controls.append(table_ui_class(self.page, self.theme_mode))
            self.page.update()
            self.update_navbar_title(self.builder.tables[endpoint]["title"])

    def update_navbar_title(self, new_title):
        navbar = self.controls[0].controls[0]
        navbar.update_title(new_title)

    def toggle_theme(self, e):
        self.page.theme_mode = (
            ft.ThemeMode.DARK if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        )
        self.theme_mode = self.page.theme_mode
        self.theme_colors = get_theme_colors(self.theme_mode)
        self.menu_container.bgcolor = self.theme_colors["navbar_bg"]
        self.search_field.bgcolor = self.theme_colors["navbar_bg"]
        self.search_field.color = self.theme_colors["navbar_text"]
        self.go_home(None)
        self.page.update()
