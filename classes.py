# classes.py (trecho Dante corrigido)
import pygame
from config import LARGURA, ALTURA, GRAVIDADE
from assets import DANTE_WALK
import sys
import math

class Dante(pygame.sprite.Sprite):
    def __init__(self, groups=None, assets=None):
        # vida visual (corações) fica por compatibilidade, mas usamos HP interno
        # HP interno: 100 (5 corações de 20 HP cada)
        self.max_hp = 100
        self.hp_per_heart = 20
        self.hp = self.max_hp
        self.lives = math.ceil(self.hp / self.hp_per_heart)

        # lidar com groups: mais confiável adicionar manualmente
        if groups is None:
            groups = []
        super().__init__()  # não passar groups direto para evitar incompatibilidade
        for g in groups:
            try:
                g.add(self)
            except Exception:
                pass

        # frames pré-cortados: lista com frames do walk (supõe que assets exista)
        self.walk_frames = assets[DANTE_WALK]

        # frames de ataque do Dante
        self.attack_frames = assets.get('dante_attack', [])
        self.is_attacking = False
        self.attack_frame_index = 0
        self.attack_timer = 0
        self.attack_frame_delay = 30  # ms por frame de ataque
        self.attack_damage = 20        # dano em HP (ajuste)
        # alcance do ataque frontal (px)
        self.attack_range = 120

        # frames de morte
        self.die_frames = assets.get('dante_die', [])
        self.is_dying = False
        self.die_played = False  # marca que a animação de morte já tocou

        # frames de dano (hurt)
        self.hurt_frames = assets.get('dante_hurt', [])
        self.is_hurt = False
        self.hurt_delay = 120

        # animação: índices
        self.anim = {
            'idle': [5],               # frame parado 
            'walk': list(range(len(self.walk_frames))),
        }

        # timing
        self.state = 'idle'
        self.frame_index = 0
        self.frame_timer = 0        # ms
        self.frame_delay = 200      # ms por frame

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
        self.max_jumps = 2   # pulo normal + 1 pulo extra no ar
        self.jumps = self.max_jumps

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
            return  # não processa walk/idle enquanto no hit

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
            #reseta o máximo de pulos quando no chão
            self.jumps = self.max_jumps
        if self.rect.top <= 0:
            self.rect.top = 0
            self.speedy = 0

        # decide estado
        desired = 'walk' if self.speedx != 0 else 'idle'
        self.set_state(desired)

        frames_idx_list = self.anim[self.state]

        # animação de morte (se estiver morrendo)
        if self.is_dying:
            self.frame_timer += dt
            if self.frame_timer >= self.frame_delay:
                self.frame_timer -= self.frame_delay
                self.frame_index += 1
                if self.frame_index >= len(self.die_frames):
                    self.frame_index = len(self.die_frames) - 1
                    self.is_dying = False
                    self.die_played = True
                    # coloca o ultimo frame visível antes de fechar
                    new_image = self.die_frames[self.frame_index]
                    if self.facing == -1:
                        new_image = pygame.transform.flip(new_image, True, False)
                    anchor = self.rect.midbottom
                    self.image = new_image
                    self.rect = self.image.get_rect()
                    self.rect.midbottom = anchor
            # aplica frame atual da morte (se ainda dentro do range)
            if self.frame_index < len(self.die_frames):
                new_image = self.die_frames[self.frame_index]
                if self.facing == -1:
                    new_image = pygame.transform.flip(new_image, True, False)
                anchor = self.rect.midbottom
                self.image = new_image
                self.rect = self.image.get_rect()
                self.rect.midbottom = anchor
            return

        # animação walk/idle normal
        if len(frames_idx_list) > 1:
            self.frame_timer += dt
            if self.frame_timer >= self.frame_delay:
                self.frame_timer -= self.frame_delay
                self.frame_index = (self.frame_index + 1) % len(frames_idx_list)
        else:
            self.frame_index = 0
            self.frame_timer = 0

        # pega frame real (0..n) e aplica flip via cache
        frame_number = frames_idx_list[self.frame_index]
        if self.facing == 1:
            new_image = self.walk_right[frame_number]
        else:
            new_image = self.walk_left[frame_number]

        # --- ataque tem prioridade sobre walk ---
        if getattr(self, 'is_attacking', False) and self.attack_frames:
            self.attack_timer += dt
            if self.attack_timer >= self.attack_frame_delay:
                self.attack_timer -= self.attack_frame_delay
                self.attack_frame_index += 1
                if self.attack_frame_index >= len(self.attack_frames):
                    # fim da animação de ataque
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

        # preserva ponto de ancoragem (evita "saltar" ao trocar frames)
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

    def pular(self, power=-20):         # o número altera a altura do pulo
        # se está morrendo/recebendo dano, ignora pulo (opcional)
        if getattr(self, 'is_dying', False) or getattr(self, 'is_hurt', False):
            return

        # só permite pular se houver 'jumps' disponíveis
        if self.jumps > 0:
            # se estiver no chão, pode pular normalmente
            self.speedy = power
            self.no_chao = False
            self.jumps -= 1

    def morrer(self):
        # se não há frames de morte, só retorna (mas bloqueia movimento)
        if not self.die_frames:
            # bloqueia o movimento e marca is_dying (mesmo sem animação)
            self.speedx = 0
            self.speedy = 0
            self.no_chao = True
            self.is_dying = True
            return
        # bloqueia o movimento e inicia animação de morrer
        self.speedx = 0
        self.speedy = 0
        self.no_chao = True
        self.is_dying = True
        self.die_played = False
        self.frame_index = 0
        self.frame_timer = 0

    def dano(self, amount=20):
        """
        Aplica dano em HP (amount). Atualiza corações visuais.
        Por padrão amount=20 (1 coração).
        """
        # se já morrendo, ignora
        if getattr(self, 'is_dying', False):
            return

        # aplica dano real
        self.hp = max(0, self.hp - amount)
        # recalcula corações
        self.lives = math.ceil(self.hp / self.hp_per_heart) if self.hp > 0 else 0

        # inicia animação de hit se tiver frames
        if self.hurt_frames:
            self.is_hurt = True
            self.frame_index = 0
            self.frame_timer = 0
        # trava movimento enquanto recebe dano
        self.speedx = 0
        self.speedy = 0

        if self.hp <= 0:
            self.morrer()

    def attack(self, enemies_group):
        """
        Inicia um ataque: aplica dano imediato aos inimigos próximos e toca animação.
        enemies_group: pygame.sprite.Group com inimigos.
        """
        # se está morrendo/recebendo dano, ignora
        if getattr(self, 'is_dying', False) or getattr(self, 'is_hurt', False):
            return

        # dispara animação de ataque (se houver frames)
        if self.attack_frames:
            self.is_attacking = True
            self.attack_frame_index = 0
            self.attack_timer = 0

        # aplica dano a inimigos próximos (usa method take_damage se existir)
        for e in enemies_group:
            if abs(e.rect.centerx - self.rect.centerx) <= self.attack_range:
                if hasattr(e, 'take_damage'):
                    e.take_damage(self.attack_damage)
                else:
                    if hasattr(e, 'hp'):
                        e.hp -= self.attack_damage
                        if getattr(e, 'hp', 1) <= 0 and hasattr(e, 'kill'):
                            e.kill()
