import pygame
import os
from config import IMG_DIR

DANTE_IMG = 'dante'

def load_assets():
    assets = {}

    # Caminho da sprite sheet (coloque Dante_1.png em assets/imagens)
    dante_path = os.path.join(IMG_DIR, 'Dante_1.png')
    if not os.path.exists(dante_path):
        raise FileNotFoundError(f"Não achei o arquivo: {dante_path}")

    sheet = pygame.image.load(dante_path).convert_alpha()

    # === Ajuste para a sheet Dante_1 ===
    # São 5 colunas e 5 linhas (5x5)
    COLS = 9
    ROWS = 5
    sheet_w, sheet_h = sheet.get_width(), sheet.get_height()
    FRAME_W = sheet_w // COLS
    FRAME_H = sheet_h // ROWS

    frames = []
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(c * FRAME_W, r * FRAME_H, FRAME_W, FRAME_H)
            frame = sheet.subsurface(rect).copy()
            frame.set_colorkey((0, 0, 0))  # fundo transparente (ajuste se necessário)
            frames.append(frame)

    assets[DANTE_IMG] = frames
    return assets
