# ira.py
import pygame
import random

# ====== Configuráveis (edite aqui se quiser ajustar rápido) ======
BOSS_ATTACK_INTERVAL = 2000   # ms entre ataques (padrão)
TRACE_COUNT = 4               # quantos traços por ataque
TRACE_DURATION = 700          # ms que cada traço fica ativo
FURY_MULT = 1.5               # multiplicador quando o boss entra em fúria
TRACE_WIDTH = 80
TRACE_HEIGHT = 18
TRACE_MARGIN_BOTTOM = 10      # distância entre o traço e o "chão" (px)
ATTACK_ANIM_DELAY = 120       # ms entre frames de animação de ataque

class BossIra(pygame.sprite.Sprite):
    def __init__(self, x, y, assets, hp=180, damage=18):
        super().__init__()
        # assets: dicionário retornado por load_assets()
        self.idle_img = assets.get('ira_idle')            # imagem única (Surface) ou None
        self.attack_frames = assets.get('ira_attack', []) # lista de Surfaces
        self.die_frames = assets.get('ira_die', [])       # lista de Surfaces

        # fallback visual se assets faltarem
        if self.idle_img:
            self.image = self.idle_img.copy()
        elif self.attack_frames:
            self.image = self.attack_frames[0].copy()
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

        # traços no chão: lista de dicts {'rect':Rect, 'expire':timestamp}
        self.traces = []

        # fury mode
        self.fury = False
        self.player_attacked_first = None  # None = undecided
        self.assets = assets

    # ===== comportamentos =====
    def apply_fury(self):
        """Aplica o buff de fúria no boss (aumenta HP, dano, muda visual)."""
        if not self.fury:
            self.fury = True
            # aumenta hp *atual* e dano
            self.hp = int(self.hp * FURY_MULT)
            self.damage = int(self.damage * FURY_MULT)
            # feedback visual simples: tenta colorir a imagem (se for Surface)
            try:
                temp = self.image.copy()
                temp.fill((200, 40, 40), special_flags=pygame.BLEND_RGBA_ADD)
                self.image = temp
            except Exception:
                pass

    def notify_player_attack(self):
        """
        Deve ser chamada assim que o jogador pressionar a tecla de ataque
        enquanto o boss está na cena, para decidir fúria.
        """
        # se o boss ainda não teve tempo de iniciar ataques (attack_timer < 1ms),
        # o jogador atacou primeiro.
        if self.player_attacked_first is None and self.attack_timer < 1:
            self.player_attacked_first = True
            self.apply_fury()

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            self.alive_flag = False

    def spawn_traces(self, window_width, ground_y, count=TRACE_COUNT):
        """Gera traços aleatórios no chão dentro de 100..window_width-100."""
        self.traces = []
        for i in range(count):
            w = TRACE_WIDTH
            h = TRACE_HEIGHT
            x = random.randint(100, max(100, window_width - 100 - w))
            y = ground_y - h - TRACE_MARGIN_BOTTOM
            r = pygame.Rect(x, y, w, h)
            expire = pygame.time.get_ticks() + TRACE_DURATION
            self.traces.append({'rect': r, 'expire': expire})

    def update(self, dt, window_width=None, ground_y=None):
        """
        dt: ms
        window_width, ground_y: necessários para spawn_traces (passar LARGURA e ALTURA)
        """
        if not self.alive_flag:
            return

        # avança timer
        self.attack_timer += dt

        # se atingiu intervalo, faz um ataque: gera traços e reseta
        if self.attack_timer >= self.attack_interval:
            self.attack_timer = 0
            # gera traços; se não recebeu window params, não gera
            if window_width is not None and ground_y is not None:
                self.spawn_traces(window_width, ground_y)
            # reinicia animação
            self.attack_anim_idx = 0
            self.attack_anim_timer = 0

        # animação simples de ataque (se frames presentes)
        if self.attack_frames and len(self.attack_frames) > 0:
            if self.attack_anim_idx < len(self.attack_frames):
                self.attack_anim_timer += dt
                if self.attack_anim_timer >= self.attack_anim_delay:
                    self.attack_anim_timer -= self.attack_anim_delay
                    self.attack_anim_idx += 1
                if self.attack_anim_idx < len(self.attack_frames):
                    self.image = self.attack_frames[self.attack_anim_idx]
                else:
                    # volta ao idle (se disponível)
                    if self.idle_img:
                        self.image = self.idle_img

        # limpa traces expiradas
        now = pygame.time.get_ticks()
        self.traces = [t for t in self.traces if t['expire'] > now]

    def draw_traces(self, surface):
        """Desenha os traços sobre a surface (usar antes de desenhar sprites)."""
        for t in self.traces:
            alpha = 160 + int(80 * (0.5 + 0.5 * ((pygame.time.get_ticks() % 400) / 400)))
            s = pygame.Surface((t['rect'].w, t['rect'].h), pygame.SRCALPHA)
            s.fill((255, 60, 60, alpha))
            surface.blit(s, (t['rect'].x, t['rect'].y))
