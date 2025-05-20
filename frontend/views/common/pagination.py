import flet as ft
import asyncio

class PaginationComponent(ft.Row):
    def __init__(self, total_items, page_size, on_page_change, total_pages=1, current_page=1):
        super().__init__()

        self.total_items = total_items
        self.page_size = page_size
        self.total_pages = total_pages
        self.on_page_change = on_page_change
        self.current_page = current_page

        self.prev_button = ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=self.prev_page, disabled=True)
        self.next_button = ft.IconButton(icon=ft.icons.ARROW_FORWARD, on_click=self.next_page, disabled=True)
        self.page_text = ft.Text(self.get_page_text())

        self.controls = [self.prev_button, self.page_text, self.next_button]

        self.update_buttons()

    def get_page_text(self):
        return f"Página {self.current_page} de {self.total_pages}"

    def update_pagination(self, total_items, total_pages):
        self.total_items = total_items
        self.total_pages = total_pages

        self.page_text.value = self.get_page_text() 

        self.update_buttons()

        if hasattr(self, "page") and self.page:
            self.update()

    def update_buttons(self):
        self.prev_button.disabled = self.current_page <= 1
        self.next_button.disabled = self.current_page >= self.total_pages
        self.page_text.value = self.get_page_text()

    def prev_page(self, e):
        if self.current_page > 1:
            self.current_page -= 1
            self.on_page_change(self.current_page)
            self.update_buttons()

    def next_page(self, e):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.on_page_change(self.current_page)
            self.update_buttons()
