import flet as ft
from frontend.utils.api import api_client
import requests

class GenericBulkUpload(ft.Container):
    def __init__(self, page, endpoint):
        super().__init__()

        self.page = page
        self.endpoint = endpoint

        self.file_picker = ft.FilePicker(on_result=self.file_selected)
        self.page.overlay.append(self.file_picker)
        self.page.update()

        self.selected_file = None

        self.upload_button = ft.ElevatedButton("Procesar Archivo", on_click=self.upload_file)
        self.file_button = ft.ElevatedButton("Seleccionar Archivo", on_click=lambda _: self.file_picker.pick_files(allow_multiple=False))

        self.status_text = ft.Text("", color="green")

        self.content = ft.Column(
            [self.file_button, self.upload_button, self.status_text]
        )

    def file_selected(self, e):
        if e.files:
            self.selected_file = e.files[0]
            self.status_text.value = f"📁 Archivo seleccionado: {self.selected_file.name}"
        else:
            self.selected_file = None
            self.status_text.value = "⚠️ No se ha seleccionado un archivo."

        self.status_text.update()

    def upload_file(self, e):
        if not self.selected_file:
            self.status_text.value = "⚠️ No se ha seleccionado un archivo."
            self.status_text.update()
            return

        if not self.endpoint:
            self.status_text.value = "⚠️ No se ha seleccionado una tabla (endpoint)."
            self.status_text.update()
            return

        self.status_text.value = "⏳ Subiendo archivo..."
        self.status_text.update()

        with open(self.selected_file.path, "rb") as file_data:
            files = {
                "file": (self.selected_file.name, file_data, "multipart/form-data")
            }
            data = {"table_name": self.endpoint}

            url = f"{api_client.BASE_URL}/bulk_upload/upload/{self.endpoint}"
            response = requests.post(f"{api_client.BASE_URL}/bulk_upload/upload/{self.endpoint}", files=files, data=data)

        if response.status_code == 200:
            self.status_text.value = "✅ Archivo subido exitosamente."
        else:
                self.status_text.value = f"❌ Error: {response.json().get('detail', 'Error desconocido')}"

        self.status_text.update()
