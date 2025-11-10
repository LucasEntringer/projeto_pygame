# assets.py
import os
import re
import pygame
from config import IMG_DIR, SND_DIR  # IMG_DIR = "assets/imagens"

DANTE_WALK = 'dante_walk'

def _numeric_sort_key(name):
    # pega último número no filename (Dante_andando.3.png -> 3)
    m = re.search(r'(\d+)(?=\D*$)', name)
    return int(m.group(1)) if m else 0

def load_assets():
    assets = {}
    folder = os.path.join(IMG_DIR, "andando")  # pasta onde você colocou os 8 frames

    files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
    files = sorted(files, key=_numeric_sort_key)

    frames = []
    for fn in files:
        path = os.path.join(folder, fn)
        img = pygame.image.load(path).convert_alpha()
        frames.append(img)
    assets[DANTE_WALK] = frames

    DANTE_DIE = 'dante_die'
    morrendo_folder = os.path.join(IMG_DIR, "morrendo")
    die_frames = []
    if os.path.isdir(morrendo_folder):
        die_files = [f for f in os.listdir(morrendo_folder) if f.lower().endswith(".png")]
        die_files = sorted(die_files, key=_numeric_sort_key)
        for fn in die_files:
            path = os.path.join(morrendo_folder, fn)
            die_frames.append(pygame.image.load(path).convert_alpha())
    assets[DANTE_DIE] = die_frames

    DANTE_HURT = 'dante_hurt'
    hurt_folder = os.path.join(IMG_DIR, "dano")
    hurt_frames = []
    if os.path.isdir(hurt_folder):
        hurt_files = [f for f in os.listdir(hurt_folder) if f.lower().endswith(".png")]
        # ordena por número no nome (Dante_hurt.1.png ...)
        hurt_files = sorted(hurt_files, key=_numeric_sort_key)
        for fn in hurt_files:
            hurt_frames.append(pygame.image.load(os.path.join(hurt_folder, fn)).convert_alpha())
    assets[DANTE_HURT] = hurt_frames

    DANTE_ATTACK = 'dante_attack'
    attack_folder = os.path.join(IMG_DIR, "atacando")
    attack_frames = []
    if os.path.isdir(attack_folder):
        afiles = [f for f in os.listdir(attack_folder) if f.lower().endswith(".png")]
        afiles = sorted(afiles, key=_numeric_sort_key)
        for fn in afiles:
            attack_frames.append(pygame.image.load(os.path.join(attack_folder, fn)).convert_alpha())
    assets[DANTE_ATTACK] = attack_frames

    IRA_IDLE = 'ira_idle'
    ira_idle_path = os.path.join(IMG_DIR, "ira_parado.png")
    ira_idle = None
    if os.path.isfile(ira_idle_path):
        ira_idle = pygame.image.load(ira_idle_path).convert_alpha()
    assets[IRA_IDLE] = ira_idle

    IRA_ATTACK = 'ira_attack'
    ira_attack_folder = os.path.join(IMG_DIR, "ira_ataque")
    ira_attack_frames = []
    if os.path.isdir(ira_attack_folder):
        files = [f for f in os.listdir(ira_attack_folder) if f.lower().endswith(".png")]
        files = sorted(files, key=_numeric_sort_key)
        for fn in files:
            ira_attack_frames.append(pygame.image.load(os.path.join(ira_attack_folder, fn)).convert_alpha())
    assets[IRA_ATTACK] = ira_attack_frames

    IRA_DIE = 'ira_die'
    ira_die_folder = os.path.join(IMG_DIR, "ira_morte")
    ira_die_frames = []
    if os.path.isdir(ira_die_folder):
        files = [f for f in os.listdir(ira_die_folder) if f.lower().endswith(".png")]
        files = sorted(files, key=_numeric_sort_key)
        for fn in files:
            ira_die_frames.append(pygame.image.load(os.path.join(ira_die_folder, fn)).convert_alpha())
    assets[IRA_DIE] = ira_die_frames

    #GULA_IDLE= 'gula_idle'
    #gula_idle_path = os.path.join(IMG_DIR, "")

    #Trilha sonora e sons

    pygame.mixer.music.load(os.path.join(SND_DIR, 'Verdi_s-Requiem_-II.-Dies-Irae-_CUGMZlvrR4c_.ogg'))

    pygame.mixer.music.set_volume(0.5)
    ATK_SOUND='atk_sound'
    assets[ATK_SOUND]=pygame.mixer.Sound(os.path.join(SND_DIR,'sword-slash-and-swing-185432.wav'))


    return assets
