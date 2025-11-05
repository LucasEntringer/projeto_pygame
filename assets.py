# assets.py
import os
import re
import pygame
from config import IMG_DIR  # IMG_DIR = "assets/imagens"

DANTE_WALK = 'dante_walk'

def _numeric_sort_key(name):
    # pega último número no filename (Dante_andando.3.png -> 3)
    m = re.search(r'(\d+)(?=\D*$)', name)
    return int(m.group(1)) if m else 0

def load_assets():
    assets = {}
    folder = os.path.join(IMG_DIR, "andando")  # pasta onde você colocou os 8 frames
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Pasta de frames não encontrada: {folder}")

    files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
    files = sorted(files, key=_numeric_sort_key)

    frames = []
    for fn in files:
        path = os.path.join(folder, fn)
        img = pygame.image.load(path).convert_alpha()
        frames.append(img)

    if len(frames) == 0:
        raise RuntimeError("Nenhum frame encontrado em " + folder)

    assets[DANTE_WALK] = frames
    return assets
