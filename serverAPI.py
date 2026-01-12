import json
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, Response
import re
import os
from datetime import datetime
from pydantic import BaseModel

IMG_PATH = r"/mnt/pendrive/satdump_live"
#IMG_PATH = r"C:\Users\1\Documents\sutdia\SP3PET\Modernizacja"
app = FastAPI(title="Serwer Obrazów - API")


class ImageInfo(BaseModel):
    image_id: str
    filename: str  # msu_mr_rgb_MSA_corrected_map.png
    size_bytes: int
    width: int
    height: int
    format: str
    upload_time: str
    cach_time: str  # z jsona
    description: str  # nazwa satelity z jsona


class DataStatus(BaseModel):
    total_images: int
    total_size_mb: float
    last_update: str
    is_connected: bool
    available_space_mb: float
    free_space_mb: float


# do wyjebania
def load_images():
    if not os.path.exists(IMG_PATH):
        os.makedirs(IMG_PATH)
    images = []
    for filename in os.listdir(IMG_PATH):
        #print(IMG_PATH, " ", filename)
        #print(os.path.join(IMG_PATH, filename))	
        filepath = os.path.join(IMG_PATH, filename)
        if os.path.isdir(filepath):
            try:
                #print(filepath, " ")
                with open(os.path.join(filepath, "dataset.json")) as json_file:
                    json_data = json.load(json_file)
                description = json_data["satellite"]
                cache_date = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(json_data["timestamp"]))
                #print(description)
                #print(cache_date)
                #filepath = os.path.join()
                from PIL import Image
                size_bytes = os.path.getsize(filepath)
                upload_time = datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                width, height = 0, 0
                image_path=os.path.join(filepath, "MSU-MR", "msu_mr_rgb_MSA_corrected_map.png")
                if os.path.exists(image_path):
                    with Image.open(image_path) as img:
                        width, height = img.size
                        #print(width,"x", height)
                        image_format = img.format or "Unknown"
                cach_time =  cache_date 
                image_info = ImageInfo(
                    image_id=filename,
                    filename=image_path, #redundant, ja bym da?a image_path or smthn
                    size_bytes=size_bytes,
                    width=width,
                    height=height,
                    format=image_format,
                    upload_time=upload_time,
                    cach_time=cach_time,
                    description=description
                ) #czy nie b?dzie nam potrzebne filepath do ka?dego zdj?cia?
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
    def image_generator():
        yield b'{"images": ['
        for idx, image in enumerate(images_store):
            filepath = image.filename
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
    """Prze?aduj obrazy z folderu."""
    load_images()
    return {"message": "Obrazy zosta?y prze?adowane."}


