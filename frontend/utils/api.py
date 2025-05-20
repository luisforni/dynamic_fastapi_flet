import os
from dotenv import load_dotenv
import requests

class APIClient:
    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

    @staticmethod
    def get_model_titles():
        url = f"{APIClient.BASE_URL}/models/titles/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("titles", [])
        return []

    @staticmethod
    def get_all(endpoint: str, page: int = 1, page_size: int = 10, query: str = None):
        url = f"{APIClient.BASE_URL}/{endpoint}/"
        params = {"page": page, "page_size": page_size}

        if query:
            params["query"] = query  

        response = requests.get(url, params=params)
        return response.json()

    def update(self, endpoint, item_id, data):
        url = f"{self.BASE_URL}/api/{endpoint}/{item_id}/"
        response = requests.put(url, json=data)
        response.raise_for_status()
        return response.json()

    def create(self, endpoint, data):
        url = f"{self.BASE_URL}/api/{endpoint}/"
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint, item_id):
        url = f"{self.BASE_URL}/api/{endpoint}/{item_id}/"
        response = requests.delete(url)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_table_preview(endpoint: str):
        url = f"{APIClient.BASE_URL}/bulk_upload/table_preview/?endpoint={endpoint}"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else {"error": "No se pudo obtener datos."}

    @staticmethod    
    def download_csv(endpoint: str):
        url = f"{APIClient.BASE_URL}/bulk/download/?endpoint={endpoint}"
        response = requests.get(url)
        return response.text if response.status_code == 200 else {"error": "Error en la descarga"}

    @staticmethod
    def upload_file(endpoint: str, file):
        url = f"{APIClient.BASE_URL}/bulk/upload/"

        with open(file.path, "rb") as f:
            files = {"file": (file.name, f, "application/octet-stream")}
            data = {"endpoint": endpoint}
            response = requests.post(url, files=files, data=data)
        
        return response.json() if response.status_code == 200 else {"error": "Error en la carga del archivo"}

    def get_all(self, endpoint, page=1, page_size=10, query=""):
        params = {"page": page, "page_size": page_size}
        if query:
            params["query"] = query
        response = requests.get(f"{self.BASE_URL}/{endpoint}/", params=params)
        return response.json() if response.status_code == 200 else {}

    def get_one(self, endpoint, record_id):
        response = requests.get(f"{self.BASE_URL}/{endpoint}/{record_id}/")
        if response.status_code == 200:
            return response.json()
        return {}.json() if response.status_code == 200 else {}
    
    def get_total_pages(self, endpoint: str, page_size: int = 10, query: str = None):
        url = f"{self.BASE_URL}/{endpoint}/all/"
        params = {"page_size": page_size}
        
        if query:
            params["query"] = query
        
        response = requests.get(url, params=params)
        return response.json()

api_client = APIClient()
