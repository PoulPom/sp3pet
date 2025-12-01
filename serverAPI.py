from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse 
import re
import os
from datetime import datetime
from pydantic import BaseModel

IMG_PATH = r".\images"

app = FastAPI(title="Serwer Obrazów - API")

class ImageInfo(BaseModel):
    image_id: str
    filename: str
    size_bytes: int
    width: int
    height: int
    format: str
    upload_time: str
    cach_time: str
    description: str

class DataStatus(BaseModel):
    total_images: int
    total_size_mb: float
    last_update: str
    is_connected: bool
    available_space_mb: float
    free_space_mb: float

def extract_satellite_name(filename):
    patterns = [
        r'Meteor M2 3',
        r'Meteor M2 4',
        r'Meteor-M2-3',
        r'Meteor-M2-4',
        r'Meteor\s*M\s*\d+',
        r'Meteor\s*M2\s*3',
        r'Meteor\s*M2\s*4'
    ]

    filename_upper = filename.upper()
    for pattern in patterns:
        match = re.search(pattern, filename_upper, re.IGNORECASE)
        if match:
            return match.group(0).replace(" ", "").replace("-", "")
    return "Inna satelita"

def extract_date_from_filename(filename):
    date_pattern = r'(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})' # Tutaj trzeba poprawić patern daty i godziny bo nie pamiętam jaki był :/
    match = re.search(date_pattern, filename)
    if match:
        year, month, day, hour, minute, second = match.groups()
        return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    return None

def load_images():
    if not os.path.exists(IMG_PATH):
        os.makedirs(IMG_PATH)
    images = []
    for filename in os.listdir(IMG_PATH):
        filepath = os.path.join(IMG_PATH, filename)
        if os.path.isfile(filepath):
            try:
                from PIL import Image
                size_bytes = os.path.getsize(filepath)
                upload_time = datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                width, height = 0, 0
                with Image.open(filepath) as img:
                    width, height = img.size
                    image_format = img.format or "Unknown"
                description = extract_satellite_name(filename)
                cache_date = extract_date_from_filename(filename)
                cach_time = cache_date.isoformat() if cache_date else "Unknown"
                image_info = ImageInfo(
                    image_id=filename,
                    filename=filename,
                    size_bytes=size_bytes,
                    width=width,
                    height=height,
                    format=image_format,
                    upload_time=upload_time,
                    cach_time=cach_time,
                    description=description
                )
                images.append(image_info)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue
    return images

images_store = []

@app.on_event("startup")
async def startup_event():
    global images_store
    images_store = load_images()

@app.get("/")
async def read_root():
    return {""}

@app.get("/get-all-data")
async def get_all_data():
    
    data = {"data": "This is all the data."}
    return data

@app.get("/get-list")
async def get_info():
    image_lsit = []
    for image in images_store:
        image_lsit.append({
            "image_id": image.image_id,
            "filename": image.filename,
            "size_bytes": image.size_bytes,
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "upload_time": image.upload_time,
            "cach_time": image.cach_time,
            "description": image.description
        })
    return {
        "total": len(image_lsit),
        "images": image_lsit
        }


@app.get("/get-data-by-id/{item_id}")
async def get_data_by_id(item_id: int):
    # Placeholder for data retrieval by ID logic
    data = {"item_id": item_id, "data": f"This is data for item {item_id}."}
    return data

@app.get("/get-status")
async def get_status():
    length = len(images_store)
    if length > 0:
        last_update = images_store[-1].upload_time
    status = {"status": "Server is running.",
              "total_images": length,
              "last_update": last_update if length > 0 else "N/A"
             }
    
    return status

@app.post("/reload")
async def reload_images():
    """Przeładuj obrazy z folderu."""
    load_images()
    return {"message": "Obrazy zostały przeładowane."}