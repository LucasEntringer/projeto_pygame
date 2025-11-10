# ira.py
import pygame
import random

# ====== Configuráveis (edite aqui se quiser ajustar rápido) ======
BOSS_ATTACK_INTERVAL = 2000   # ms entre ataques (padrão)
TRACE_COUNT = 4               # quantos traços por ataque
TRACE_WARNING_DURATION = 500  #Tempo dos traços em alerta
TRACE_ACTIVE_DURATION = 700          # ms que cada traço fica ativo
FURY_MULT = 1.5               # multiplicador quando o boss entra em fúria
TRACE_WIDTH = 80
TRACE_HEIGHT = 18
TRACE_MARGIN_BOTTOM = 10      # distância entre o traço e o "chão" (px)
ATTACK_ANIM_DELAY = 120       # ms entre frames de animação de ataque

class BossIra(pygame.sprite.Sprite):
    def __init__(self, x, y, assets, hp=180, damage=18):

        # animação de morte
        self.die_frames = assets.get('ira_die', [])  # já tem, mas confirma
        self.is_dying = False
        self.die_index = 0
        self.die_timer = 0
        self.die_delay = 120  # ms por frame da animação de morte

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
        # aplica dano em HP
        self.hp -= amount
        # se ainda vivo, só reduz e retorna
        if self.hp > 0:
            return
        # se ja zerou a vida, inicia a animação de morte (em vez de matar de imediato)
        if not self.is_dying:
            self.is_dying = True
            self.die_index = 0
            self.die_timer = 0
            # bloqueia movimentos/traces
            self.traces = []
            # opcional: um som ou efeito aqui


    def spawn_traces(self, window_width, ground_y, count=TRACE_COUNT):
        """Gera traços com fase de warning (pisca) e em seguida fase ativa (causa dano)."""
        self.traces = []
        now = pygame.time.get_ticks()
        for i in range(count):
            w = TRACE_WIDTH
            h = TRACE_HEIGHT
            x = random.randint(100, max(100, window_width - 100 - w))
            y = ground_y - h - TRACE_MARGIN_BOTTOM
            r = pygame.Rect(x, y, w, h)
            warn_until = now + TRACE_WARNING_DURATION
            active_until = warn_until + TRACE_ACTIVE_DURATION
            # store both times and a flag 'active' computed dinamicamente
            self.traces.append({
                'rect': r,
                'warn_until': warn_until,
                'active_until': active_until,
            })

    def update(self, dt, window_width=None, ground_y=None):
        """
        dt: ms
        window_width, ground_y: necessários para spawn_traces (passar LARGURA e ALTURA)
        """
        # Se está na animação de morrer, toca die_frames e finaliza quando acabar
        if getattr(self, 'is_dying', False):
            # anima a morte
            self.die_timer += dt
            if self.die_timer >= self.die_delay:
                self.die_timer -= self.die_delay
                self.die_index += 1
                if self.die_index >= len(self.die_frames):
                    # animação terminou → marcar morto (será removido por jogo)
                    self.is_dying = False
                    self.alive_flag = False
                    # keep last frame visible:
                    if self.die_frames:
                        self.image = self.die_frames[-1]
                    return
            # aplica frame atual da morte
            if self.die_index < len(self.die_frames) and self.die_frames:
                self.image = self.die_frames[self.die_index]
            return

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
        self.traces = [t for t in self.traces if t['active_until'] > now]

    def draw_traces(self, surface):
        """Desenha os traços; piscam enquanto em WARNING e ficam sólidos durante ACTIVE."""
        now = pygame.time.get_ticks()
        for t in self.traces:
            r = t['rect']
            # fase warning
            if now < t['warn_until']:
                # pisca: alterna visível/invisível a cada 120ms
                blink_period = 120
                show = ((now // blink_period) % 2) == 0
                if show:
                    alpha = 140 + int(80 * ((now % blink_period) / blink_period))
                    s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                    s.fill((255, 90, 60, alpha))
                    surface.blit(s, (r.x, r.y))
            # fase ativa
            elif now < t['active_until']:
                s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                s.fill((255, 60, 60, 200))
                surface.blit(s, (r.x, r.y))
            # else: já expirada — será limpa no update()

