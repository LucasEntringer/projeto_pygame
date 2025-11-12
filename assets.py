# assets.py
import os
import re
import pygame
from config import IMG_DIR, SND_DIR, LARGURA, ALTURA  # IMG_DIR = "assets/imagens"

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

        # GULA
    GULA_IDLE = 'gula_idle'
    gula_idle_folder = os.path.join(IMG_DIR, "gula_parado")
    gula_idle_frames = []
    if os.path.isdir(gula_idle_folder):
        files = [f for f in os.listdir(gula_idle_folder) if f.lower().endswith(".png")]
        files = sorted(files, key=_numeric_sort_key)
        for fn in files:
            gula_idle_frames.append(pygame.image.load(os.path.join(gula_idle_folder, fn)).convert_alpha())
    assets[GULA_IDLE] = gula_idle_frames

    GULA_WALK = 'gula_walk'
    gula_walk_folder = os.path.join(IMG_DIR, "gula_andando")
    gula_walk_frames = []
    if os.path.isdir(gula_walk_folder):
        files = [f for f in os.listdir(gula_walk_folder) if f.lower().endswith(".png")]
        files = sorted(files, key=_numeric_sort_key)
        for fn in files:
            gula_walk_frames.append(pygame.image.load(os.path.join(gula_walk_folder, fn)).convert_alpha())
    assets[GULA_WALK] = gula_walk_frames

    GULA_ATTACK = 'gula_attack'
    gula_attack_folder = os.path.join(IMG_DIR, "gula_ataque")
    gula_attack_frames = []
    if os.path.isdir(gula_attack_folder):
        files = [f for f in os.listdir(gula_attack_folder) if f.lower().endswith(".png")]
        files = sorted(files, key=_numeric_sort_key)
        for fn in files:
            gula_attack_frames.append(pygame.image.load(os.path.join(gula_attack_folder, fn)).convert_alpha())
    assets[GULA_ATTACK] = gula_attack_frames

    GULA_DIE = 'gula_die'
    gula_die_folder = os.path.join(IMG_DIR, "gula_morrendo")
    gula_die_frames = []
    if os.path.isdir(gula_die_folder):
        files = [f for f in os.listdir(gula_die_folder) if f.lower().endswith(".png")]
        files = sorted(files, key=_numeric_sort_key)
        for fn in files:
            gula_die_frames.append(pygame.image.load(os.path.join(gula_die_folder, fn)).convert_alpha())
    assets[GULA_DIE] = gula_die_frames

     # GULA COXA DE FRANGO
    GULA_COXA = 'gula_coxa'
    coxa_folder = os.path.join(IMG_DIR, "coxa_de_frango")
    coxa_img = None
    if os.path.isdir(coxa_folder):
        
        for f in os.listdir(coxa_folder):
            if f.lower().endswith(".png"):
                coxa_img = pygame.image.load(os.path.join(coxa_folder, f)).convert_alpha()
                break
    assets[GULA_COXA] = coxa_img

        # ===== GANÂNCIA =====
    GANANCIA_IDLE = 'ganancia_idle'
    ganancia_idle_folder = os.path.join(IMG_DIR, "ganancia_parado")
    ganancia_idle_frames = []
    if os.path.isdir(ganancia_idle_folder):
        files = [f for f in os.listdir(ganancia_idle_folder) if f.lower().endswith(".png")]
        files = sorted(files, key=_numeric_sort_key)
        for fn in files:
            ganancia_idle_frames.append(pygame.image.load(os.path.join(ganancia_idle_folder, fn)).convert_alpha())
    assets[GANANCIA_IDLE] = ganancia_idle_frames

    GANANCIA_WALK = 'ganancia_walk'
    ganancia_walk_folder = os.path.join(IMG_DIR, "ganancia_andando")
    ganancia_walk_frames = []
    if os.path.isdir(ganancia_walk_folder):
        files = [f for f in os.listdir(ganancia_walk_folder) if f.lower().endswith(".png")]
        files = sorted(files, key=_numeric_sort_key)
        for fn in files:
            ganancia_walk_frames.append(pygame.image.load(os.path.join(ganancia_walk_folder, fn)).convert_alpha())
    assets[GANANCIA_WALK] = ganancia_walk_frames

    GANANCIA_ATTACK = 'ganancia_attack'
    ganancia_attack_folder = os.path.join(IMG_DIR, "ganancia_ataque")
    ganancia_attack_frames = []
    if os.path.isdir(ganancia_attack_folder):
        files = [f for f in os.listdir(ganancia_attack_folder) if f.lower().endswith(".png")]
        files = sorted(files, key=_numeric_sort_key)
        for fn in files:
            ganancia_attack_frames.append(pygame.image.load(os.path.join(ganancia_attack_folder, fn)).convert_alpha())
    assets[GANANCIA_ATTACK] = ganancia_attack_frames

    GANANCIA_DIE = 'ganancia_die'
    ganancia_die_folder = os.path.join(IMG_DIR, "ganancia_morrendo")
    ganancia_die_frames = []
    if os.path.isdir(ganancia_die_folder):
        files = [f for f in os.listdir(ganancia_die_folder) if f.lower().endswith(".png")]
        files = sorted(files, key=_numeric_sort_key)
        for fn in files:
            ganancia_die_frames.append(pygame.image.load(os.path.join(ganancia_die_folder, fn)).convert_alpha())
    assets[GANANCIA_DIE] = ganancia_die_frames


    #Background menu
    MENU_BACK = 'menu_back'
    assets[MENU_BACK] = pygame.image.load(os.path.join(IMG_DIR, "menu_hell.jpg")).convert()
    assets[MENU_BACK] = pygame.transform.scale(assets[MENU_BACK],(LARGURA,ALTURA))

    #imagem dos comandos
    COMMAND_SCR = 'command_scr'

    assets[COMMAND_SCR] = pygame.image.load(os.path.join(IMG_DIR, "Gemini_Generated_Image_4trti34trti34trt.png")).convert()
    assets[COMMAND_SCR] = pygame.transform.scale(assets[COMMAND_SCR],(LARGURA,ALTURA))


    #Sons

    ATK_SOUND='atk_sound'
    assets[ATK_SOUND]=pygame.mixer.Sound(os.path.join(SND_DIR,'sword-slash-and-swing-185432.wav'))
    HURT_SOUND = 'hurt_sound'
    assets[HURT_SOUND] = pygame.mixer.Sound(os.path.join(SND_DIR,'male_hurt7-48124.wav'))


    return assets
