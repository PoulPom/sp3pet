import pygame
from PIL import Image, ImageDraw, ImageFont
import schedule
import time
import os
from datetime import datetime
import sys

AUTHOR = "Stacja Odbiorcza SP3PET"


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from klientAPI import (
    create_download_folder,
    check_server_connection,
    get_all_data,
    SERVER_URL,
    DOWNLOAD_FOLDER
)

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()
pygame.display.set_caption("Pętla wyświetlania obrazów z satelity")

photos = []
currr_photo_inx = 0

def get_optimal_font_size(img_width, img_height, text, base_size=50):
    margin = img_width * 0.05  
    max_width = img_width - (2 * margin)
    
    font_size = base_size
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
        return font, font_size
    
    while font_size > 10:
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            break
        
        font_size -= 2
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
            break
    
    return font, font_size

def add_text_to_image(image_path, cach_time, description, author):
    """Dodaje tekst do obrazu i zapisuje z prefiksem 'annotated_'"""
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        img_width, img_height = img.size
        
        try:
            if cach_time and cach_time != "Unknown":
                date_obj = datetime.fromisoformat(cach_time)
                date_text = date_obj.strftime("%Y-%m-%d %H:%M:%S UTC")
            else:
                date_text = "Brak daty"
        except:
            date_text = "Brak daty"
        
        satellite_text = f"Satelita: {description}"
        author_text = f"Autor: {author}"
        
        font_date, size_date = get_optimal_font_size(img_width, img_height, date_text, 40)
        font_sat, size_sat = get_optimal_font_size(img_width, img_height, satellite_text, 40)
        font_author, size_author = get_optimal_font_size(img_width, img_height, author_text, 35)
        
        margin = 20
        
        y_top = margin
        draw.text((margin, y_top), date_text, fill="white", font=font_date, stroke_width=2, stroke_fill="black")
        
        bbox_date = draw.textbbox((margin, y_top), date_text, font=font_date)
        y_satellite = bbox_date[3] + 10
        draw.text((margin, y_satellite), satellite_text, fill="white", font=font_sat, stroke_width=2, stroke_fill="black")
        
        bbox_author = draw.textbbox((0, 0), author_text, font=font_author)
        text_width = bbox_author[2] - bbox_author[0]
        text_height = bbox_author[3] - bbox_author[1]
        x_author = (img_width - text_width) // 2
        y_author = img_height - text_height - margin
        draw.text((x_author, y_author), author_text, fill="white", font=font_author, stroke_width=2, stroke_fill="black")
        
        dir_name = os.path.dirname(image_path)
        base_name = os.path.basename(image_path)
        new_filename = f"annotated_{base_name}"
        new_path = os.path.join(dir_name, new_filename)
        
        img.save(new_path)
        print(f"Zapisano obraz z adnotacjami: {new_path}")
        
        return new_path
        
    except Exception as e:
        print(f"Błąd dodawania tekstu do obrazu {image_path}: {e}")
        return None

def initialize():
    global photos, current_photo_index
    if not os.path.exists(DOWNLOAD_FOLDER):
        create_download_folder()
    if not check_server_connection():
        print("Brak połączenia z serwerem. Kończę działanie.")
        pygame.quit()
        sys.exit(1)
    photos = get_all_data()    
    return
def display_photo():
    global current_photo_index, photos
    
    if not photos:
        # Wyświetl czarny ekran z komunikatem
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 50)
        text = font.render("Brak obrazów do wyświetlenia", True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(text, text_rect)
        pygame.display.flip()
        return
    
    try:
        photo_path = photos[current_photo_index]
        
        # Wczytaj obraz z PIL i konwertuj na Pygame
        pil_image = Image.open(photo_path)
        
        # Skaluj obraz do rozmiaru ekranu zachowując proporcje
        img_width, img_height = pil_image.size
        scale = min(screen_width / img_width, screen_height / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Konwersja do pygame
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        
        pygame_image = pygame.image.fromstring(data, size, mode)
        
        # Wyświetl na środku ekranu
        screen.fill((0, 0, 0))
        x = (screen_width - new_width) // 2
        y = (screen_height - new_height) // 2
        screen.blit(pygame_image, (x, y))
        pygame.display.flip()
        
        print(f"Wyświetlono obraz {current_photo_index + 1}/{len(photos)}: {os.path.basename(photo_path)}")
        
    except Exception as e:
        print(f"Błąd wyświetlania obrazu: {e}")
    return
def next_photo():
    global current_photo_index
    
    if photos:
        current_photo_index = (current_photo_index + 1) % len(photos)
        display_photo()
def prev_photo():
    global current_photo_index
    
    if photos:
        current_photo_index = (current_photo_index - 1) % len(photos)
        display_photo()

def fetch_new_photos():
    global photos, current_photo_index

    if not check_server_connection():
        print("Brak połączenia z serwerem - pominięto pobieranie")
        return
    if os.path.exists(DOWNLOAD_FOLDER):
        for filename in os.listdir(DOWNLOAD_FOLDER):
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
            try:
                os.remove(filepath)
                print(f"Usunięto stary plik: {filename}")
            except Exception as e:
                print(f"Nie można usunąć {filename}: {e}")
    downloaded = get_all_data()
    
    photos = []
    for img in downloaded:
        # Dodaj tekst do każdego obrazu
        annotated_path = add_text_to_image(
            img["path"],
            img.get("cach_time", "Unknown"),
            img.get("description", "Nieznana satelita"),
            AUTHOR
        )
        
        if annotated_path:
            photos.append(annotated_path)
            
            # Usuń oryginalny plik
            try:
                os.remove(img["path"])
                print(f"Usunięto oryginalny plik: {img['path']}")
            except Exception as e:
                print(f"Nie można usunąć pliku {img['path']}: {e}")
    
    current_photo_index = 0
    print(f"Pobrano i przetworzono {len(photos)} obrazów")
    
    if photos:
        display_photo()


schedule.every(90).seconds.do(next_photo)  # 1.5 minuty
schedule.every(4).hours.do(fetch_new_photos)  # 4 godziny

initialize()
display_photo()

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # ESC kończy program
                running = False
            elif event.key == pygame.K_RIGHT:  # Strzałka w prawo - następne zdjęcie
                next_photo()
            elif event.key == pygame.K_LEFT:  # Strzałka w lewo - poprzednie zdjęcie
                if photos:
                    current_photo_index = (current_photo_index - 1) % len(photos)
                    display_photo()
            elif event.key == pygame.K_r:  # R - odśwież teraz
                fetch_new_photos()
    
    schedule.run_pending()

    clock.tick(1)  

print("\nZamykanie programu...")
pygame.quit()
print("Program zakończony.")