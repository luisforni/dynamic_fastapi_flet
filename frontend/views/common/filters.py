import flet as ft
import asyncio
from frontend.utils.api import api_client
from frontend.utils.colors import get_theme_colors

class TextFilter(ft.TextField):
    def __init__(self, label, endpoint, update_callback, theme_mode, page):
        super().__init__(
            label=label,
            hint_text="Escriba para filtrar...",
            expand=True,
            border_radius=5,
            border=ft.border.all(1, ft.colors.GREY_400),
            on_change=self.handle_search
        )
        self.endpoint = endpoint
        self.update_callback = update_callback
        self.page = page
        self.theme_mode = theme_mode
        self.theme_colors = get_theme_colors(theme_mode)
        self.apply_theme()

    def apply_theme(self):
        self.theme_colors = get_theme_colors(self.theme_mode)
        self.color = self.theme_colors["table_text"]
        self.border = ft.border.all(1, self.theme_colors["table_border"])
        self.update()
        if self.page:
            self.page.update()

    def update_theme(self, theme_mode):
        self.theme_mode = theme_mode
        self.apply_theme()
        if self.page:
            self.page.update()

    async def handle_search(self, e):
        query = self.value.strip().lower()
        if not query:
            results = await self.search_api(query="", limit=6)
        else:
            results = await self.search_api(query=query, limit=6)
        self.update_callback(results)

    async def search_api(self, query="", limit=6):
        try:
            response = await asyncio.to_thread(
                api_client.get_all, f"api/{self.endpoint}", page=1, page_size=limit, query=query
            )
            return response.get(self.endpoint, [])
        except Exception as e:
            return []


class DropdownFilter(ft.Dropdown):
    def __init__(self, label, options, on_change):
        super().__init__(
            label=label,
            options=[ft.dropdown.Option(text=option, key=option) for option in options],
            on_change=on_change,
            expand=True,
            border_radius=5,
            border=ft.border.all(1, ft.colors.GREY_400),
        )

class DateFilter(ft.DatePicker):
    def __init__(self, label, on_change):
        super().__init__(
            on_change=on_change,
        )
        self.label = label
        self.text_field = ft.TextField(label=label, read_only=True)
    
    def open_picker(self, e):
        self.pick_date()
