import pygame
from config import LARGURA, ALTURA, FPS
from assets import load_assets
from classes import Dante


pygame.init()
window = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('Divina Codemédia')
clock = pygame.time.Clock()

# Carregar assets e criar sprites
assets = load_assets()
all_sprites = pygame.sprite.Group()
dante = Dante(all_sprites, assets)

running = True
while running:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_RIGHT:
                dante.mover_direita()
            if event.key == pygame.K_LEFT:
                dante.mover_esquerda()
            if event.key == pygame.K_SPACE:
                dante.pular()

        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                dante.parar()

    all_sprites.update(dt)
    window.fill((25, 25, 35))
    all_sprites.draw(window)
    pygame.display.flip()

pygame.quit()
