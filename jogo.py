import pygame

pygame.init()

window = pygame.display.set_mode((1000,500))
pygame.display.set_caption('Divina Codemédia')

game = True

while game:
    for event in pygame.event.get():
        #Verifica se apertou o x para sair
        if event.type == pygame.QUIT:
            game = False
        # Verifica se alguma tecla foi clicada
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                #Definindo o esc como opção de finalizar o jogo
                game = False
    window.fill((255,255,255))

    pygame.display.update()

pygame.quit()