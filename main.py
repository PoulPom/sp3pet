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

def initialize():
    return
def display_photo():
    return
def next_photo():
    return
def fetch_new_photos():
    return

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