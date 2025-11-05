import pygame
from config import LARGURA, ALTURA, GRAVIDADE
from assets import DANTE_IMG

class Dante(pygame.sprite.Sprite):
    def __init__(self, groups, assets):
        super().__init__(groups)
        self.frames = assets[DANTE_IMG]

        # --- Índices dos frames ---
        # Na sheet: linha 2 (WALK) tem 8 frames → são frames 10 a 17 (0-based)
        # 5 frames por linha → cada linha = 5 frames
        # DIE (0–4), IDLE (5–9), WALK (10–14), RUN (15–19), ATTACK (20–24)
        self.anim = {
            'idle': [5, 6, 7, 8, 9],
            'walk': [10, 11, 12, 13, 14],
            'run': [15, 16, 17, 18, 19],
            'attack': [20, 21, 22, 23, 24],
        }

        self.state = 'idle'
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_delay = 100  # ms entre frames

        self.image = self.frames[self.anim[self.state][0]]
        self.rect = self.image.get_rect(midbottom=(LARGURA // 2, ALTURA - 10))

        self.speedx = 0
        self.speedy = 0
        self.no_chao = True
        self.facing = 1  # 1 = direita, -1 = esquerda

    def set_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            self.frame_index = 0
            self.frame_timer = 0

    def update(self, dt):
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if not self.no_chao:
            self.speedy += GRAVIDADE

        # Escolhe animação
        if self.speedx != 0:
            anim_key = 'walk'
        else:
            anim_key = 'idle'

        if anim_key != self.state:
            self.set_state(anim_key)

        # Atualiza frame
        self.frame_timer += dt
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.anim[self.state])

        frame_number = self.anim[self.state][self.frame_index]
        self.image = self.frames[frame_number]
        if self.facing == -1:
            self.image = pygame.transform.flip(self.image, True, False)

        # Mantém o personagem no chão
        if self.rect.bottom >= ALTURA - 10:
            self.rect.bottom = ALTURA - 10
            self.speedy = 0
            self.no_chao = True

        if self.rect.top <= 0:
            self.rect.top = 0
            self.speedy = 0

    def pular(self):
        if self.no_chao:
            self.speedy = -15
            self.no_chao = False

    def mover_esquerda(self):
        self.speedx = -8
        self.facing = -1

    def mover_direita(self):
        self.speedx = 8
        self.facing = 1

    def parar(self):
        self.speedx = 0
