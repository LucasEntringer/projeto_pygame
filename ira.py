import pygame
import random

BOSS_ATTACK_INTERVAL = 2000   # ms entre ataques (padrão)
TRACE_COUNT = 7               # quantos traços por ataque
TRACE_WARNING_DURATION = 1500  # ms tempo dos traços em alerta
TRACE_ACTIVE_DURATION = 2000   # ms que cada traço fica ativo
FURY_MULT = 1.5               # multiplicador quando o boss entra em fúria
TRACE_WIDTH = 160
TRACE_HEIGHT = 18
TRACE_MARGIN_BOTTOM = 10      # distância entre o traço e o "chão" (px)
ATTACK_ANIM_DELAY = 120       # ms entre frames de animação de ataque

class BossIra(pygame.sprite.Sprite):
    def __init__(self, x, y, assets, hp=500, damage=18):
        super().__init__()

        # assets: tenta ler de assets dict; use fallback se faltar
        self.idle_img = assets.get('ira_idle') if assets else None
        self.attack_frames = assets.get('ira_attack', []) if assets else []
        self.die_frames = assets.get('ira_die', []) if assets else []

        # caches espelhados (direita / esquerda)
        self.attack_frames_right = list(self.attack_frames)
        self.attack_frames_left = [pygame.transform.flip(f, True, False) for f in self.attack_frames_right]

        self.die_frames_right = list(self.die_frames)
        self.die_frames_left = [pygame.transform.flip(f, True, False) for f in self.die_frames_right]

        self.idle_right = self.idle_img
        self.idle_left = pygame.transform.flip(self.idle_img, True, False) if self.idle_img else None

        # virado para a esquerda por padrão (muda se quiser)
        self.facing = -1

        # fallback visual se assets faltarem
        if self.idle_right:
            self.image = self.idle_right.copy()
        elif self.attack_frames_right:
            self.image = self.attack_frames_right[0].copy()
        else:
            self.image = pygame.Surface((200,200), pygame.SRCALPHA)
            self.image.fill((150,0,0))

        self.rect = self.image.get_rect(midbottom=(x, y))

        # stats
        self.hp = int(hp)
        self.base_hp = int(hp)
        self.base_damage = int(damage)
        self.damage = int(damage)
        self.alive_flag = True

        # timers e animação
        self.attack_timer = 0
        self.attack_interval = BOSS_ATTACK_INTERVAL
        self.attack_anim_idx = 0
        self.attack_anim_timer = 0
        self.attack_anim_delay = ATTACK_ANIM_DELAY

        # animação de morte
        self.is_dying = False
        self.die_index = 0
        self.die_timer = 0
        self.die_delay = 120  # ms por frame da animação de morte

        # traços no chão: lista de dicts {'rect':Rect, 'warn_until':, 'active_until':}
        self.traces = []

        # fury mode
        self.fury = False
        self.player_attacked_first = None  # None = undecided
        self.assets = assets

    # ===== comportamentos =====
    def apply_fury(self):
        if not self.fury:
            self.fury = True
            self.hp = int(self.hp * FURY_MULT)
            self.damage = int(self.damage * FURY_MULT)
            try:
                temp = self.image.copy()
                temp.fill((200, 40, 40), special_flags=pygame.BLEND_RGBA_ADD)
                self.image = temp
            except Exception:
                pass

    def notify_player_attack(self):
        if self.player_attacked_first is None and self.attack_timer < 1:
            self.player_attacked_first = True
            self.apply_fury()

    def take_damage(self, amount):
        """Aplica dano e inicia animação de morte (não mata imediatamente)."""
        if not self.alive_flag:
            return
        self.hp -= amount
        if self.hp > 0:
            return
        if not self.is_dying:
            self.is_dying = True
            self.die_index = 0
            self.die_timer = 0
            self.traces = []  # limpar traços ao iniciar morrer

    def spawn_traces(self, window_width, ground_y, count=TRACE_COUNT):
        """Gera traços com fase de warning (pisca) e em seguida fase ativa (causa dano)."""
        self.traces = []
        now = pygame.time.get_ticks()
        for i in range(count):
            w = TRACE_WIDTH
            h = TRACE_HEIGHT
            x = random.randint(100, max(100, window_width - 100 - w))
            y = ground_y - h - TRACE_MARGIN_BOTTOM
            # hitbox menor que o visual (ajuste pad_x/pad_y conforme preferir)
            pad_x = 10
            pad_y = 4
            hit_rect = pygame.Rect(x + pad_x, y + pad_y, max(4, w - 2*pad_x), max(4, h - 2*pad_y))
            # opcional: manter também rect visual se quiser desenhar diferente do hit_rect
            visual_rect = pygame.Rect(x, y, w, h)
            warn_until = now + TRACE_WARNING_DURATION
            active_until = warn_until + TRACE_ACTIVE_DURATION
            self.traces.append({
                'rect': hit_rect,
                'visual': visual_rect,
                'warn_until': warn_until,
                'active_until': active_until,
            })

    def update(self, dt, window_width=None, ground_y=None):
        """Atualiza timers, animações e gerencia spawn de traços."""
        # --- animação de morte (prioritária) ---
        if getattr(self, 'is_dying', False):
            self.die_timer += dt
            if self.die_timer >= self.die_delay:
                self.die_timer -= self.die_delay
                self.die_index += 1
                if self.die_index >= len(self.die_frames_right):
                    # fim da animação: marca como morto (jogo removerá)
                    self.is_dying = False
                    self.alive_flag = False
                    if self.die_frames_right:
                        last = self.die_frames_right[-1] if self.facing == 1 else self.die_frames_left[-1]
                        anchor = self.rect.midbottom
                        self.image = last
                        self.rect = self.image.get_rect()
                        self.rect.midbottom = anchor
                    return
            # aplica frame atual de morte
            if self.die_index < len(self.die_frames_right):
                frame = self.die_frames_right[self.die_index] if self.facing == 1 else self.die_frames_left[self.die_index]
                anchor = self.rect.midbottom
                self.image = frame
                self.rect = self.image.get_rect()
                self.rect.midbottom = anchor
            return

        if not self.alive_flag:
            return

        # avança timer de ataque
        self.attack_timer += dt

        # se atingiu intervalo, gera traços
        if self.attack_timer >= self.attack_interval:
            self.attack_timer = 0
            if window_width is not None and ground_y is not None:
                self.spawn_traces(window_width, ground_y)
            self.attack_anim_idx = 0
            self.attack_anim_timer = 0

        # animação de ataque (usa caches já flipados)
        frames_right = self.attack_frames_right
        frames_left = self.attack_frames_left
        frames = frames_right if self.facing == 1 else frames_left

        if frames and len(frames) > 0:
            if self.attack_anim_idx < len(frames):
                self.attack_anim_timer += dt
                if self.attack_anim_timer >= self.attack_anim_delay:
                    self.attack_anim_timer -= self.attack_anim_delay
                    self.attack_anim_idx += 1
                if self.attack_anim_idx < len(frames):
                    anchor = self.rect.midbottom
                    self.image = frames[self.attack_anim_idx]
                    self.rect = self.image.get_rect()
                    self.rect.midbottom = anchor
                else:
                    # volta ao idle (se disponível)
                    idle = self.idle_right if self.facing == 1 else self.idle_left
                    if idle:
                        anchor = self.rect.midbottom
                        self.image = idle
                        self.rect = self.image.get_rect()
                        self.rect.midbottom = anchor

        # limpa traces expiradas (após fase ativa)
        now = pygame.time.get_ticks()
        self.traces = [t for t in self.traces if t['active_until'] > now]

    def draw_traces(self, surface):
        """Desenha os traços; piscam enquanto em WARNING e ficam sólidos durante ACTIVE."""
        now = pygame.time.get_ticks()
        for t in self.traces:
            vr = t.get('visual', t['rect'])
            # fase warning (pisca)
            if now < t['warn_until']:
                blink_period = 120
                show = ((now // blink_period) % 2) == 0
                if show:
                    alpha = 140 + int(80 * ((now % blink_period) / blink_period))
                    s = pygame.Surface((vr.w, vr.h), pygame.SRCALPHA)
                    s.fill((255, 90, 60, alpha))
                    surface.blit(s, (vr.x, vr.y))
            # fase ativa (sólida)
            elif now < t['active_until']:
                s = pygame.Surface((vr.w, vr.h), pygame.SRCALPHA)
                s.fill((255, 60, 60, 200))
                surface.blit(s, (vr.x, vr.y))
            # else: expirada (será limpa no update)
