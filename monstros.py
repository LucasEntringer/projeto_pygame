import pygame
pygame.init()



tela = pygame.display.set_mode((800, 600))
ira = pygame.image.load ('assets\imagens\ira.png').convert_alpha()
ira = pygame.transform.scale(ira,(50,50))

#posição inicial

pos_inicial_ira_x = 200
pos_inicial_ira_y = 200

roda = True

while roda == True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False,
            
    tela.fill((0,0,0))
    tela.blit(ira,(pos_inicial_ira_x, pos_inicial_ira_y))

    pygame.display.flip()

pygame.quit()