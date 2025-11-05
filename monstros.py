import pygame
from config import LARGURA, ALTURA, FPS
pygame.init()

tela = pygame.display.set_mode((LARGURA, ALTURA))
ira = pygame.image.load ('assets\imagens\ira.png').convert()
ira = pygame.transform.scale(ira,(150,150))

#posição inicial

pos_inicial_ira_x = 200
pos_inicial_ira_y = 200

roda = True

while roda == True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            roda = False
            
    tela.fill((0,0,0))
    tela.blit(ira,(pos_inicial_ira_x, pos_inicial_ira_y))

    pygame.display.flip()

pygame.quit()