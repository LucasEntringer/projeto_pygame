# classes.py (trecho)
import pygame
from config import LARGURA, ALTURA, GRAVIDADE
from assets import DANTE_WALK

class Dante(pygame.sprite.Sprite):
    def __init__(self, groups=None, assets=None):
        if groups is None: groups = []
        super().__init__(groups)
        if not assets or DANTE_WALK not in assets:
            raise ValueError("Assets inválidos ou faltando 'dante_walk'")

        # frames pré-cortados: list length == 8
        self.walk_frames = assets[DANTE_WALK]

        # animação: indices 0..7 da lista walk_frames
        self.anim = {
            'idle': [0],               # frame parado 
            'walk': list(range(len(self.walk_frames))),
        }

        # timing
        self.state = 'idle'
        self.frame_index = 0
        self.frame_timer = 0        # ms
        self.frame_delay = 70       # ms por frame (ajuste para mais/menos fluidez)

        # caches flipados (gera uma vez)
        self.walk_right = self.walk_frames
        self.walk_left = [pygame.transform.flip(f, True, False) for f in self.walk_frames]

        # imagem inicial (idle)
        idx = self.anim['idle'][0]
        self.image = self.walk_right[idx]
        self.rect = self.image.get_rect(midbottom=(LARGURA//2, ALTURA - 10))

        # física
        self.speedx = 0
        self.speedy = 0
        self.no_chao = True
        self.facing = 1

    def set_state(self, new_state):
        if new_state == self.state: return
        self.state = new_state
        self.frame_index = 0
        self.frame_timer = 0

    def update(self, dt):
        # dt é em ms (clock.tick)
        # movimento simples
        self.rect.x += int(self.speedx)
        self.rect.y += int(self.speedy)

        if not self.no_chao:
            self.speedy += GRAVIDADE

        # chão/teto
        if self.rect.bottom >= ALTURA - 10:
            self.rect.bottom = ALTURA - 10
            self.speedy = 0
            self.no_chao = True
        if self.rect.top <= 0:
            self.rect.top = 0
            self.speedy = 0

        # decide estado
        desired = 'walk' if self.speedx != 0 else 'idle'
        self.set_state(desired)

        frames_idx_list = self.anim[self.state]
        # animação com dt em ms
        if len(frames_idx_list) > 1:
            self.frame_timer += dt
            if self.frame_timer >= self.frame_delay:
                self.frame_timer -= self.frame_delay
                self.frame_index = (self.frame_index + 1) % len(frames_idx_list)
        else:
            self.frame_index = 0
            self.frame_timer = 0

        # pega frame real (0..7) e aplica flip via cache
        frame_number = frames_idx_list[self.frame_index]  # index dentro walk_frames
        if self.facing == 1:
            new_image = self.walk_right[frame_number]
        else:
            new_image = self.walk_left[frame_number]

        # preserva ponto de ancoragem (evita "sobe" ao andar)
        anchor = self.rect.midbottom
        self.image = new_image
        self.rect = self.image.get_rect()
        self.rect.midbottom = anchor

    # controles simples
    def mover_direita(self, speed=4):
        self.speedx = speed
        self.facing = 1

    def mover_esquerda(self, speed=4):
        self.speedx = -speed
        self.facing = -1

    def parar(self):
        self.speedx = 0

    def pular(self, power=-12):
        if self.no_chao:
            self.speedy = power
            self.no_chao = False
