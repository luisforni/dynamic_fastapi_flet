import flet as ft
import asyncio
from frontend.utils.api import api_client
from frontend.utils.colors import get_theme_colors

class FilteredDropdown(ft.Column):
    def __init__(self, label, on_select, endpoint, id_field="id", name_field="_id_name", selected_value=None, theme_mode=None):
        super().__init__()
        self.label = label
        self.on_select = on_select
        self.endpoint = endpoint
        self.id_field = id_field
        self.name_field = name_field
        self.selected_id = None
        self.selected_name = ""

        self.theme_colors = get_theme_colors(theme_mode)

        self.all_options = []
        self.is_loading_all = False

        if isinstance(selected_value, dict):
            self.selected_id = selected_value.get(self.id_field, None)
            self.selected_name = selected_value.get(self.name_field, "")

        self.search_field = ft.TextField(
            label=label,
            value=self.selected_name,
            on_change=self.handle_search,
            on_focus=self.show_options_on_focus,
            expand=True,
            bgcolor=self.theme_colors["background"],
            color=self.theme_colors["table_text"],
            border_color=self.theme_colors["table_border"] 
        )

        self.list_view = ft.ListView(
            controls=[],
            expand=True,
            visible=False
        )

        self.controls.append(self.search_field)
        self.controls.append(self.list_view)

    async def load_initial_options(self, e):
        if not self.all_options:
            self.all_options = await self.search_api("", limit=6)
            self.update_options(self.all_options)

            if not self.is_loading_all:
                self.is_loading_all = True
                asyncio.create_task(self.load_all_options())

        self.list_view.visible = True
        self.update()

    async def load_all_options(self):
        self.all_options = await self.search_api("", limit=None)

        if self.all_options is None:
            self.all_options = []

    async def handle_search(self, e):
        query = self.search_field.value.strip().lower()

        if not query:
            self.list_view.visible = False
            self.update()
            return

        results = await self.search_api(query, limit=6)
        self.update_options(results)

    async def search_api(self, query="", limit=6):
        try:
            endpoint_with_api = f"api/{self.endpoint}"
            response = await asyncio.to_thread(
                api_client.get_all, endpoint_with_api, page=1, page_size=100
            )
            items = response.get(self.endpoint, [])
            filtered_items = [
                i for i in items if query.lower() in i[self.name_field].lower()
            ] if query else items
            return filtered_items[:limit]

        except Exception as e:
            return []

    def update_options(self, new_options):
        self.list_view.controls.clear()

        limited_options = new_options[:6]

        if limited_options:
            for opt in limited_options:
                btn = ft.TextButton(
                    text=opt[self.name_field],
                    on_click=lambda e, opt=opt: self.select_option(opt[self.id_field], opt[self.name_field]),
                    style=ft.ButtonStyle(alignment=ft.alignment.top_left)
                )
                self.list_view.controls.append(btn)

            self.list_view.visible = True
        else:
            self.list_view.visible = False

        self.update()
    
    def get_value(self):
        return {self.id_field: self.selected_id, self.name_field: self.selected_name} if self.selected_id else None
    
    def select_option(self, id, name):
        self.search_field.value = name
        self.selected_id = id
        self.selected_name = name

        selected_data = {
            self.id_field: id,
            self.name_field: name
        }

        self.on_select(selected_data)

        self.list_view.visible = False
        self.update()

    def show_options_on_focus(self, e):
        if self.all_options:
            self.update_options(self.all_options[:6])
        self.list_view.visible = True
        self.update()

    def get_value(self):
        return {self.id_field: self.selected_id, self.name_field: self.search_field.value} if self.selected_id else None
