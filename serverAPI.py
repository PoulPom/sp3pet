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
        
        

@app.get("/")
async def read_root():
    return {""}

@app.get("/get-all-data")
async def get_all_data():
    # Placeholder for data retrieval logic
    data = {"data": "This is all the data."}
    return data

@app.get("/get-list")
async def get_info():
    # Placeholder for info retrieval logic
    info = {"info": "This is some information."}
    return info

@app.get("/get-data-by-id/{item_id}")
async def get_data_by_id(item_id: int):
    # Placeholder for data retrieval by ID logic
    data = {"item_id": item_id, "data": f"This is data for item {item_id}."}
    return data

@app.get("/get-status")
async def get_status():
    # Placeholder for status retrieval logic
    status = {"status": "Server is running."}
    return status
