from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, Response
import os
from datetime import datetime
from pydantic import BaseModel
import logging
import json

STORAGE_PATH = r"./pendrive/metheor_live/"

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

def fetch_name_and_date(folder_name: str) -> tuple[str, str]:
    try :
        with open(os.path.join(STORAGE_PATH, folder_name, "dataset.json"), "r") as f:
            data = json.load(f)
            name = data.get("name", "Unknown Dataset")
            date = data.get("date", "Unknown Date")
            date = datetime.fromtimestamp(date).isoformat()
            return name, date
    except Exception as e:
        logging.error(f"Nie udało się odczytać danych o zdjęciu {folder_name}: {e}")
        return "Unknown Dataset", "Unknown Date"

def load_images():
    iamges = []
    for folders in os.listdir(STORAGE_PATH):
        for folder in folders:
            folder_path = os.path.join(STORAGE_PATH, folders, folder)
            date, name = fetch_name_and_date(folder)
            for file in os.listdir(folder_path):
                if file.lower().endswith(('_corrected_map.png')):
                    filepath = os.path.join(folder_path,file)
                    with open(filepath, "rb") as f:
                        file_widht, file_height = f.read().size
                    stat = os.stat(filepath)
                    image_info = ImageInfo(
                        image_id = f"{folders}_{folder}_{file}",
                        filename = file,
                        size_bytes = stat.st_size,
                        width = file_widht,
                        height = file_height,
                        format = "PNG",
                        catch_time = date,
                        discription = name,
                        upload_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    )
                    iamges.append(image_info)
    return iamges

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
    def image_generator():
        yield b'{"images": ['
        for idx, image in enumerate(images_store):
            filepath = os.path.join(STORAGE_PATH, image.filename)
            image_data = None
            with open(filepath, "rb") as f:
                image_data = f.read()
            
            import base64
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            
            image_json = {
                "image_id": image.image_id,
                "filename": image.filename,
                "size_bytes": image.size_bytes,
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "upload_time": image.upload_time,
                "cach_time": image.cach_time,
                "description": image.description,
                "image_data": encoded_image
            }
            
            import json
            if idx > 0:
                yield b", "
            yield json.dumps(image_json).encode('utf-8')
        
        yield b']}'
    
    return StreamingResponse(image_generator(), media_type="application/json")

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
async def get_data_by_id(item_id: str): 
    for image in images_store:
        if image.image_id == item_id:
            filepath = os.path.join(IMG_PATH, image.filename)
            with open(filepath, "rb") as f:
                image_data = f.read()
            return Response(content=image_data, media_type=f"image/{image.format.lower()}") 
    raise HTTPException(status_code=404, detail="Obraz nie znaleziony")

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