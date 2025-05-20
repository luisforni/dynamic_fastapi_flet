import flet as ft
from frontend.utils.api import APIClient
import re

class GenericBulkDownload(ft.Container):
    def __init__(self, page, endpoint):
        super().__init__()

        self.page = page
        self.endpoint = endpoint

        self.download_button = ft.ElevatedButton("Descargar CSV", on_click=self.download_file, disabled=False)

        self.status_text = ft.Text("", color="green")

        self.content = ft.Column(
            [
                self.download_button,
                self.status_text,
            ]
        )

    def download_file(self, e):
        endpoint = self.endpoint
        if not endpoint:
            return

        file_url = f"{APIClient.BASE_URL}/bulk_download/download?endpoint={endpoint}"

        self.page.launch_url(file_url)

        self.status_text.value = f"✅ Archivo descargado correctamente."
        self.page.update()
