# jogo.py (trecho relevante)
import pygame
import os
from config import LARGURA, ALTURA, FPS,  IMG_DIR
from assets import load_assets
from classes import Dante

pygame.init()
window = pygame.display.set_mode((LARGURA, ALTURA))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Segoe UI Symbol", 40)  # o número ajusta o tamanho do coração
# cor dos corações:
HEART_COLOR = (220, 20, 60)

assets = load_assets()
all_sprites = pygame.sprite.Group()
dante = Dante(groups=[all_sprites], assets=assets)

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
                dante.dano()
                
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

    all_sprites.update(dt)
    if bg:
        window.blit(bg, (0,0))
    else:
        window.fill((30,30,30))
    all_sprites.draw(window)
    hearts = "♥ " * max(0, dante.lives)
    if hearts:
        heart_surf = font.render(hearts, True, HEART_COLOR)
        window.blit(heart_surf, (10, 10))
    pygame.display.flip()

pygame.quit()
