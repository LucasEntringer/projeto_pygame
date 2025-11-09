# classes.py (trecho)
import pygame
from config import LARGURA, ALTURA, GRAVIDADE
from assets import DANTE_WALK
import sys

class Dante(pygame.sprite.Sprite):
    def __init__(self, groups=None, assets=None):
        self.lives = 5  # número de vidas iniciais

        if groups is None: groups = []
        super().__init__(groups)

        # frames pré-cortados: list length == 8
        self.walk_frames = assets[DANTE_WALK]

        # frames de morte
        self.die_frames = assets.get('dante_die', [])
        # estado específico para morte: notificação se está tocando
        self.is_dying = False
        self.die_played = False  # marca que a animação de morte já tocou

        # frames de dano
        self.hurt_frames = assets.get('dante_hurt', [])
        self.is_hurt = False
        # tempo específico para hurt 
        self.hurt_delay = 120

        # animação: indices 0..7 da lista walk_frames
        self.anim = {
            'idle': [5],               # frame parado 
            'walk': list(range(len(self.walk_frames))),
        }

        # timing
        self.state = 'idle'
        self.frame_index = 0
        self.frame_timer = 0        # ms
        self.frame_delay = 200       # ms por frame (ajuste para mais/menos fluidez)

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
        # --- animação de dano (prioritária) ---
        if self.is_hurt:
            # avança timer (usando hurt_delay)
            self.frame_timer += dt
            if self.frame_timer >= (getattr(self, 'hurt_delay', self.frame_delay)):
                self.frame_timer -= getattr(self, 'hurt_delay', self.frame_delay)
                self.frame_index += 1
                # se passou do último frame, termina hurt
                if self.frame_index >= len(self.hurt_frames):
                    self.frame_index = len(self.hurt_frames) - 1
                    self.is_hurt = False
                    # se as vidas chegaram a zero, iniciar morte
                    if self.lives <= 0:
                        self.morrer()
            # aplica o frame atual do hurt (espelha se necessário)
            new_image = self.hurt_frames[self.frame_index]
            if self.facing == -1:
                new_image = pygame.transform.flip(new_image, True, False)
            anchor = self.rect.midbottom
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.midbottom = anchor
            return  # para aqui: não processa walk/idle enquanto no hit

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
        if self.is_dying:
            # avança timer
            self.frame_timer += dt
            if self.frame_timer >= self.frame_delay:
                self.frame_timer -= self.frame_delay
                self.frame_index += 1
                # se passou do último frame, finaliza o jogo
                if self.frame_index >= len(self.die_frames):
                    self.frame_index = len(self.die_frames) - 1
                    self.is_dying = False
                    self.die_played = True
                    #coloca o ultimo frame vísivel antes de fechar
                    new_image = self.die_frames[self.frame_index]
                    if self.facing == -1:
                        new_image = pygame.transform.flip(new_image, True, False)
                    anchor = self.rect.midbottom
                    self.image = new_image
                    self.rect = self.image.get_rect()
                    self.rect.midbottom = anchor
                    pygame.quit()
                    sys.exit()
            if self.frame_index < len(self.die_frames):
                new_image = self.die_frames[self.frame_index]
                if self.facing == -1:
                    new_image = pygame.transform.flip(new_image, True, False)
                anchor = self.rect.midbottom
                self.image = new_image
                self.rect = self.image.get_rect()
                self.rect.midbottom = anchor
            return  # pula resto do update
        
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

    def pular(self, power=-20):         #o número altera a altura do pulo
        if self.no_chao:
            self.speedy = power
            self.no_chao = False

    def morrer(self):
        if not self.die_frames:
            return
    # bloqueia o movimento
        self.speedx = 0
        self.speedy = 0
        self.no_chao = True
        # inicia a animação de morrer
        self.is_dying = True
        self.die_played = False
        self.state = 'dead'
        self.frame_index = 0
        self.frame_timer = 0

    def dano(self):
        """Inicia a animação de dano: reduz 1 vida e toca a sequência de hurt_frames."""
        # se já morrendo, ignora
        if getattr(self, 'is_dying', False):
            return
        # se não há frames, apenas reduz vida e checa morte
        if not self.hurt_frames:
            self.lives = max(0, self.lives - 1)
            if self.lives <= 0:
                self.morrer()
            return

        # inicia a animação de dano
        self.is_hurt = True
        self.frame_index = 0
        self.frame_timer = 0
        # travar movimento enquanto recebe dano (opcional)
        self.speedx = 0
        self.speedy = 0
        # decrementa a vida imediatamente (visualiza no HUD)
        self.lives = max(0, self.lives - 1)
        # se zerou vidas, a lógica ao terminar o hurt chamará morrer()
