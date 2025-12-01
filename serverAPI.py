import fastapi 
import re
from datetime import datetime

app = fastapi.FastAPI()

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
