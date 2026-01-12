import requests
import os
from datetime import datetime
from pathlib import Path
import json
import base64

# ===== ZMIENNE GLOBALNE =====
SERVER_URL = "http://192.168.87.28:8000"
DOWNLOAD_FOLDER = r".\downloaded_images"

def create_download_folder():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
        print(f"Utworzono folder: {DOWNLOAD_FOLDER}")

def check_server_connection():
    try:
        response = requests.get(f"{SERVER_URL}/", timeout=5)
        if response.status_code == 200:
            print(f"Połączono z serwerem: {SERVER_URL}")
            return True
        else:
            print(f"Błąd połączenia: status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Nie można połączyć z serwerem: {e}")
        return False
    
def get_server_status():
    try:
        response = requests.get(f"{SERVER_URL}/get-status")
        if response.status_code == 200:
            status = response.json()
            print("\nSTATUS SERWERA:")
            print("=" * 60)
            for key, value in status.items():
                print(f"   {key}: {value}")
            print("=" * 60)
            return status
        else:
            print(f"Błąd pobierania statusu: {response.status_code}")
            return None
    except Exception as e:
        print(f"Błąd: {e}")
        return None
    
def get_images_list():
    try:
        response = requests.get(f"{SERVER_URL}/get-list")
        if response.status_code == 200:
            data = response.json()
            images = data.get("images", [])
            print(f"Pobrano listę {len(images)} obrazów z serwera.")
            return images
        else:
            print(f"Błąd pobierania listy obrazów: {response.status_code}")
            return []
    except Exception as e:
        print(f"Błąd: {e}")
        return []
    
def download_image(image_id, filename):
    try:
        response = requests.get(f"{SERVER_URL}/get-data-by-id/{image_id}")
        if response.status_code == 200:
            image_data = response.content
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            with open(file_path, "wb") as f:
                f.write(image_data)
            print(f"Pobrano obraz przez sieć: {file_path}")
            return file_path
        else:
            print(f"Błąd pobierania obrazu {image_id}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Błąd: {e}")
        return None
    
def get_all_data():
    try:
        response = requests.get(f"{SERVER_URL}/get-all-data", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"Pobrano wszystkie dane z serwera przez sieć.")
            return data
        else:
            print(f"Błąd pobierania danych: {response.status_code}")
            return None
    except Exception as e:
        print(f"Błąd: {e}")
        return None

def download_all_images():
    create_download_folder()
    
    images_list = get_images_list()
    
    if not images_list:
        print("Brak obrazów do pobrania")
        return []
    
    downloaded = []
    for img_info in images_list:
        image_id = img_info.get("image_id")
        filename = img_info.get("filename")
        
        file_path = download_image(image_id, filename)
        
        if file_path:
            downloaded.append({
                "filename": filename,
                "path": file_path,
                "cach_time": img_info.get("cach_time"),
                "description": img_info.get("description"),
                "width": img_info.get("width"),
                "height": img_info.get("height")
            })
    
    return downloaded

def download_all_images_base64():
    """Alternatywna metoda - pobiera obrazy jako base64 PRZEZ SIEĆ"""
    create_download_folder()
    
    data = get_all_data()
    
    if not data or "images" not in data:
        print("Brak danych do pobrania")
        return []
    
    downloaded = []
    for img in data["images"]:
        try:
            image_data = base64.b64decode(img["image_data"])
            
            filename = img["filename"]
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            with open(file_path, "wb") as f:
                f.write(image_data)
            
            print(f"Pobrano i zapisano: {file_path}")
            
            downloaded.append({
                "filename": filename,
                "path": file_path,
                "cach_time": img.get("cach_time"),
                "description": img.get("description"),
                "width": img.get("width"),
                "height": img.get("height")
            })
            
        except Exception as e:
            print(f"Błąd przetwarzania obrazu {img.get('filename')}: {e}")
            continue
    
    return downloaded
