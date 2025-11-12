import pygame
from config import LARGURA, ALTURA, GRAVIDADE
from assets import DANTE_WALK
import sys
import math

class Dante(pygame.sprite.Sprite):
    def __init__(self, groups=None, assets=None):
        """
        Inicializa o personagem Dante, definindo atributos de vida, animação e física.

        Parâmetros:
            groups (list): Lista de grupos de sprites aos quais Dante será adicionado.
            assets (dict): Dicionário contendo os sprites e animações carregados.

        Retorna:
            None
        """
        self.max_hp = 100
        self.hp_per_heart = 20
        self.hp = self.max_hp
        self.lives = math.ceil(self.hp / self.hp_per_heart)

        if groups is None:
            groups = []
        super().__init__()
        for g in groups:
            g.add(self)

        self.walk_frames = assets[DANTE_WALK]
        self.attack_frames = assets.get('dante_attack', [])
        self.is_attacking = False
        self.attack_frame_index = 0
        self.attack_timer = 0
        self.attack_frame_delay = 60
        self.attack_damage = 20
        self.attack_range = 120

        self.die_frames = assets.get('dante_die', [])
        self.is_dying = False
        self.die_played = False

        self.hurt_frames = assets.get('dante_hurt', [])
        self.is_hurt = False
        self.hurt_delay = 120

        self.anim = {
            'idle': [5],
            'walk': list(range(len(self.walk_frames))),
        }

        self.state = 'idle'
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_delay = 200

        self.walk_right = self.walk_frames
        self.walk_left = [pygame.transform.flip(f, True, False) for f in self.walk_frames]

        idx = self.anim['idle'][0]
        self.image = self.walk_right[idx]
        self.rect = self.image.get_rect(midbottom=(LARGURA // 2, ALTURA - 10))

        self.speedx = 0
        self.speedy = 0
        self.no_chao = True
        self.facing = 1
        self.max_jumps = 2
        self.jumps = self.max_jumps

    def set_state(self, new_state):
        """
        Altera o estado de animação de Dante (ex.: 'idle', 'walk').

        Parâmetros:
            new_state (str): Novo estado a ser definido.

        Retorna:
            None
        """
        if new_state == self.state:
            return
        self.state = new_state
        self.frame_index = 0
        self.frame_timer = 0

    def update(self, dt):
        """
        Atualiza o estado, a posição e as animações do personagem Dante.

        Parâmetros:
            dt (float): Tempo decorrido desde o último frame (em milissegundos).

        Retorna:
            None
        """
        if self.is_hurt:
            self.frame_timer += dt
            if self.frame_timer >= (getattr(self, 'hurt_delay', self.frame_delay)):
                self.frame_timer -= getattr(self, 'hurt_delay', self.frame_delay)
                self.frame_index += 1
                if self.frame_index >= len(self.hurt_frames):
                    self.frame_index = len(self.hurt_frames) - 1
                    self.is_hurt = False
                    if self.lives <= 0:
                        self.morrer()
            new_image = self.hurt_frames[self.frame_index]
            if self.facing == -1:
                new_image = pygame.transform.flip(new_image, True, False)
            anchor = self.rect.midbottom
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.midbottom = anchor
            return

        self.rect.x += int(self.speedx)
        self.rect.y += int(self.speedy)

        if not self.no_chao:
            self.speedy += GRAVIDADE

        if self.rect.bottom >= ALTURA - 110:
            self.rect.bottom = ALTURA - 110
            self.speedy = 0
            self.no_chao = True
            self.jumps = self.max_jumps
        if self.rect.top <= 0:
            self.rect.top = 0
            self.speedy = 0

        desired = 'walk' if self.speedx != 0 else 'idle'
        self.set_state(desired)

        frames_idx_list = self.anim[self.state]

        if self.is_dying:
            self.frame_timer += dt
            if self.frame_timer >= self.frame_delay:
                self.frame_timer -= self.frame_delay
                self.frame_index += 1
                if self.frame_index >= len(self.die_frames):
                    self.frame_index = len(self.die_frames) - 1
                    self.is_dying = False
                    self.die_played = True
                    new_image = self.die_frames[self.frame_index]
                    if self.facing == -1:
                        new_image = pygame.transform.flip(new_image, True, False)
                    anchor = self.rect.midbottom
                    self.image = new_image
                    self.rect = self.image.get_rect()
                    self.rect.midbottom = anchor
            if self.frame_index < len(self.die_frames):
                new_image = self.die_frames[self.frame_index]
                if self.facing == -1:
                    new_image = pygame.transform.flip(new_image, True, False)
                anchor = self.rect.midbottom
                self.image = new_image
                self.rect = self.image.get_rect()
                self.rect.midbottom = anchor
            return

        if len(frames_idx_list) > 1:
            self.frame_timer += dt
            if self.frame_timer >= self.frame_delay:
                self.frame_timer -= self.frame_delay
                self.frame_index = (self.frame_index + 1) % len(frames_idx_list)
        else:
            self.frame_index = 0
            self.frame_timer = 0

        frame_number = frames_idx_list[self.frame_index]
        if self.facing == 1:
            new_image = self.walk_right[frame_number]
        else:
            new_image = self.walk_left[frame_number]

        if getattr(self, 'is_attacking', False) and self.attack_frames:
            self.attack_timer += dt
            if self.attack_timer >= self.attack_frame_delay:
                self.attack_timer -= self.attack_frame_delay
                self.attack_frame_index += 1
                if self.attack_frame_index >= len(self.attack_frames):
                    self.is_attacking = False
                    self.attack_frame_index = 0
            af = self.attack_frames[min(self.attack_frame_index, len(self.attack_frames)-1)]
            if self.facing == -1:
                af = pygame.transform.flip(af, True, False)
            anchor = self.rect.midbottom
            self.image = af
            self.rect = self.image.get_rect()
            self.rect.midbottom = anchor
            return

        anchor = self.rect.midbottom
        self.image = new_image
        self.rect = self.image.get_rect()
        self.rect.midbottom = anchor

    def mover_direita(self, speed=4):
        """
        Move Dante para a direita.

        Parâmetros:
            speed (int): Velocidade do movimento (padrão = 4).

        Retorna:
            None
        """
        self.speedx = speed
        self.facing = 1

    def mover_esquerda(self, speed=4):
        """
        Move Dante para a esquerda.

        Parâmetros:
            speed (int): Velocidade do movimento (padrão = 4).

        Retorna:
            None
        """
        self.speedx = -speed
        self.facing = -1

    def parar(self):
        """
        Faz Dante parar de se mover.

        Parâmetros:
            None

        Retorna:
            None
        """
        self.speedx = 0

    def pular(self, power=-20):
        """
        Faz Dante pular, aplicando velocidade vertical negativa.

        Parâmetros:
            power (int): Intensidade do pulo (padrão = -20).

        Retorna:
            None
        """
        if getattr(self, 'is_dying', False) or getattr(self, 'is_hurt', False):
            return
        if self.jumps > 0:
            self.speedy = power
            self.no_chao = False
            self.jumps -= 1

    def morrer(self):
        """
        Inicia a animação e o estado de morte de Dante.

        Parâmetros:
            None

        Retorna:
            None
        """
        if not self.die_frames:
            self.speedx = 0
            self.speedy = 0
            self.no_chao = True
            self.is_dying = True
            return
        self.speedx = 0
        self.speedy = 0
        self.no_chao = True
        self.is_dying = True
        self.die_played = False
        self.frame_index = 0
        self.frame_timer = 0

    def dano(self, amount=20):
        """
        Aplica dano a Dante e atualiza o número de vidas.

        Parâmetros:
            amount (int): Quantidade de dano a ser aplicada (padrão = 20).

        Retorna:
            None
        """
        if getattr(self, 'is_dying', False):
            return
        self.hp = max(0, self.hp - amount)
        self.lives = math.ceil(self.hp / self.hp_per_heart) if self.hp > 0 else 0
        if self.hurt_frames:
            self.is_hurt = True
            self.frame_index = 0
            self.frame_timer = 0
        self.speedx = 0
        self.speedy = 0
        if self.hp <= 0:
            self.morrer()

    def attack(self, enemies_group):
        """
        Realiza o ataque de Dante, causando dano aos inimigos próximos.

        Parâmetros:
            enemies_group (pygame.sprite.Group): Grupo de inimigos a serem verificados.

        Retorna:
            None
        """
        if getattr(self, 'is_dying', False) or getattr(self, 'is_hurt', False):
            return
        if self.attack_frames:
            self.is_attacking = True
            self.attack_frame_index = 0
            self.attack_timer = 0

        for e in enemies_group:
            dx = e.rect.centerx - self.rect.centerx
            dy = e.rect.centery - self.rect.centery
            dist = (dx*dx + dy*dy) ** 0.5
            if dist <= self.attack_range:
                if hasattr(e, 'take_damage'):
                    e.take_damage(self.attack_damage)
                elif hasattr(e, 'hp'):
                    e.hp -= self.attack_damage
                    if getattr(e, 'hp', 1) <= 0 and hasattr(e, 'kill'):
                        e.kill()
