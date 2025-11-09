# jogo.py (trecho relevante)
import pygame
import os
from config import LARGURA, ALTURA, FPS,  IMG_DIR
from assets import load_assets
from ira import BossIra
from classes import Dante
import random

#Configurações da Ira:
BOOS_ATTACK_INTERVAL = 2000     #ms entre os ataques
TRACE_COUNT = 4                 #Quantidade de traços por ataque
TRACE_DURATION = 700            #ms que cada traço fica ativo
FURY_MULT = 1.5                 #multipllicador do modo fúria

pygame.init()
window = pygame.display.set_mode((LARGURA, ALTURA))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Segoe UI Symbol", 40)  # o número ajusta o tamanho do coração
# cor dos corações:
HEART_COLOR = (220, 20, 60)

assets = load_assets()
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()

#player
dante = Dante(groups=[all_sprites], assets=assets)

boss = None

running = True
while running:
    dt = clock.tick(FPS)  # dt em ms

    bg = None
    bg_path = os.path.join(IMG_DIR, 'inferno', 'Cenario_inferno.png')
    try:
        bg = pygame.image.load(bg_path).convert()     # convert() é mais rápido para fundos sem alpha
        # escala a imagem para a resolução do jogo (opcional mas recomendado)
        bg = pygame.transform.scale(bg, (LARGURA, ALTURA))
    except Exception as e:
        print('Erro ao carregar background', bg_path, e)
        bg = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                dante.pular()
            if event.key == pygame.K_z:
                dante.attack(enemies)
                #Identifica se atacou antes do boss:
                if boss is not None:
                    boss.notify_player_attack()
                
    keys = pygame.key.get_pressed()
    left = keys[pygame.K_a] or keys[pygame.K_LEFT]
    right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

    if left and right:
        dante.parar()
    elif left:
        dante.mover_esquerda()
    elif right:
        dante.mover_direita()
    else:
        dante.parar()

    if boss is None and dante.rect.centerx >= LARGURA - 120:
        #teletransporta o player para o começo da segunda janela
        dante.rect.midbottom = (140, ALTURA - 10)
        dante.parar()
        #cria o boss na cena:
        bx = LARGURA // 2 + 100
        by = ALTURA - 10
        boss = BossIra(bx, by, assets=assets)
        enemies.add(boss)
        all_sprites.add(boss)

    all_sprites.update(dt)

    #checa se há colisão entre os traços do boss e o dante
    if boss is not None:
        try:
            boss.update(dt, window_width=LARGURA, ground_y= ALTURA)
        except TypeError:
            boss.update(dt)
    
    if boss is not None:
        now = pygame.time.get_ticks()
        for t in list(boss.traces):
            if dante.rect.colliderect(t['rect']):
                #aplica o dano e expira o traço para não dar mais de um hit
                dante.dano()
                #expira o trace automaticamente:
                t['expire'] = now - 1
    
    #Se o boss morreu, limpa e permite continuar
    if boss is not None and not boss.alive_flag:
        #remove o boss:
        try:
            boss.kill()
        except Exception:
            pass
        boss = None
        enemies.empty()
        
    if bg:
        window.blit(bg, (0,0))
    else:
        window.fill((30,30,30))
    
    if boss is not None:
        boss.draw_traces(window)
    
    all_sprites.draw(window)
    hearts = "♥ " * max(0, dante.lives)
    if hearts:
        heart_surf = font.render(hearts, True, HEART_COLOR)
        window.blit(heart_surf, (10, 10))
    pygame.display.flip()

pygame.quit()
