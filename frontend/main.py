import flet as ft
import asyncio
from frontend.views.home.home_view import HomeView

async def main(page: ft.Page):
    page.title = "Aplicación de Gestión"
    theme_mode = page.theme_mode
    page.clean()
    home_view = HomeView(page, theme_mode)
    page.add(home_view)

if __name__ == "__main__":
    asyncio.run(ft.app_async(target=main))
    #asyncio.run(ft.app_async(target=main, view=ft.WEB_BROWSER))
