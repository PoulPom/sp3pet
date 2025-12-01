import pygame
from PIL import Image, ImageDraw, ImageFont
import schedule
import time
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from klientAPI import (
    create_download_folder,
    check_server_connection,
    SERVER_URL,
    DOWNLOAD_FOLDER
)

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()
pygame.display.set_caption("Pętla wyświetlania obrazów z satelity")



