import pygame

pygame.init()

window = pygame.display.set_mode((1000,500))
pygame.display.set_caption('Divina Codemédia')

game = True

while game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game = False
    window.fill((255,255,255))

    pygame.display.update()

pygame.quit()