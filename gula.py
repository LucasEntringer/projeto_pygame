import pygame
import random

BOSS_ATTACK_INTERVAL = 2200
FURY_MULT = 1.4
ATTACK_ANIM_DELAY = 100

COXA_FALL_MIN_SPEED = 4
COXA_FALL_MAX_SPEED = 10
COXA_COUNT_PER_ATTACK = 6
COXA_SPREAD_PADDING = 60
COXA_WIDTH = 28
COXA_HEIGHT = 22
COXA_DAMAGE = 18
GRAVITY = 0.35
COXA_ROT_MIN = -8
COXA_ROT_MAX = 8

# escala de velocidade (1.0 = velocidade base passada no construtor)
SPEED_SCALE = 0.90


class BossGula(pygame.sprite.Sprite):
    def __init__(self, x, y, assets, hp=420, damage=16, patrol_min_x=100, patrol_max_x=None, speed=2):
        super().__init__()

        self.idle_frames = assets.get('gula_idle', []) if assets else []
        self.walk_frames = assets.get('gula_walk', []) if assets else []
        self.attack_frames = assets.get('gula_attack', []) if assets else []
        self.die_frames = assets.get('gula_die', []) if assets else []
        self.coxa_img = assets.get('gula_coxa') if assets else None

        # mantemos frames "originais" e usaremos flip na hora do draw
        self.facing = -1  # -1 = esquerda, 1 = direita (conceito lógico)
        self.image = self.idle_frames[0] if self.idle_frames else pygame.Surface((180, 180), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.hp = int(hp)
        self.base_hp = int(hp)
        self.base_damage = int(damage)
        self.damage = int(damage)
        self.alive_flag = True

        self.patrol_min_x = patrol_min_x
        self.patrol_max_x = patrol_max_x
        self.speed = float(speed)
        self.moving = True

        self.state = "idle"
        self.frame_idx = 0
        self.frame_timer = 0
        self.frame_delay = 200

        self.attack_timer = 0
        self.attack_interval = BOSS_ATTACK_INTERVAL
        self.attack_anim_idx = 0
        self.attack_anim_timer = 0
        self.attack_anim_delay = ATTACK_ANIM_DELAY

        self.is_dying = False
        self.die_index = 0
        self.die_timer = 0
        self.die_delay = 120

        self.coxas = []
        self.fury = False
        self.player_attacked_first = None

        self.atacando = False

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
        if not self.alive_flag:
            return
        self.hp -= amount
        if self.hp > 0:
            return
        if not self.is_dying:
            self.is_dying = True
            self.die_index = 0
            self.die_timer = 0
            self.coxas = []

    def gerar_coxas(self, window_width, ground_y, count=COXA_COUNT_PER_ATTACK):
        self.coxas = []
        now = pygame.time.get_ticks()
        ww = max(200, window_width or 800)
        for i in range(count):
            x = random.randint(COXA_SPREAD_PADDING, max(COXA_SPREAD_PADDING, ww - COXA_SPREAD_PADDING - COXA_WIDTH))
            y = - random.randint(20, 200)
            rect = pygame.Rect(x, y, COXA_WIDTH, COXA_HEIGHT)
            vel_y = random.uniform(COXA_FALL_MIN_SPEED, COXA_FALL_MAX_SPEED)
            img = self.coxa_img
            if isinstance(img, pygame.Surface):
                try:
                    img_s = pygame.transform.scale(img, (COXA_WIDTH, COXA_HEIGHT))
                except Exception:
                    img_s = img
            else:
                s = pygame.Surface((COXA_WIDTH, COXA_HEIGHT), pygame.SRCALPHA)
                pygame.draw.ellipse(s, (230, 120, 20), (0, 0, COXA_WIDTH, COXA_HEIGHT))
                img_s = s
            self.coxas.append({
                'rect': rect,
                'vel_y': vel_y,
                'img_orig': img_s,
                'angle': random.uniform(0, 360),
                'rot_speed': random.uniform(COXA_ROT_MIN, COXA_ROT_MAX),
                'dano': COXA_DAMAGE,
                'spawned_at': now,
            })
        # marca ciclo de ataque (para animação)
        self.atacando = True
        self.attack_anim_idx = 0
        self.attack_anim_timer = 0

    def atualizar_coxas(self, dt):
        if not self.coxas:
            return
        to_remove = []
        for c in self.coxas:
            c['vel_y'] += GRAVITY
            c['rect'].y += max(1, int(c['vel_y'] * (dt / (1000.0 / 60.0))))
            c['angle'] = (c['angle'] + c['rot_speed'] * (dt / (1000.0 / 60.0))) % 360
            if c['rect'].top > 900:
                to_remove.append(c)
        for r in to_remove:
            try:
                self.coxas.remove(r)
            except ValueError:
                pass

    def draw_traces(self, surface):
        for c in self.coxas:
            orig = c.get('img_orig')
            angle = c.get('angle', 0)
            rect = c.get('rect')
            try:
                rotated = pygame.transform.rotate(orig, angle)
                rotated_rect = rotated.get_rect(center=rect.center)
                surface.blit(rotated, rotated_rect.topleft)
                c['render_rect'] = rotated_rect
            except Exception:
                try:
                    surface.blit(orig, rect)
                    c['render_rect'] = rect
                except Exception:
                    pass

    def _select_frame_and_apply_flip(self, base_frames, dt):
        """Escolhe frame de base_frames (não flipadas) e aplica flip horizontal de acordo com self.facing."""
        if not base_frames:
            return None
        self.frame_timer += dt
        if self.frame_timer >= self.frame_delay:
            self.frame_timer -= self.frame_delay
            self.frame_idx = (self.frame_idx + 1) % len(base_frames)
        frame = base_frames[self.frame_idx]
        if self.facing == -1:
            try:
                return pygame.transform.flip(frame, True, False)
            except Exception:
                return frame
        else:
            return frame

    def update(self, dt, window_width=None, ground_y=None, player=None):
        if getattr(self, 'is_dying', False):
            self.die_timer += dt
            if self.die_timer >= self.die_delay:
                self.die_timer -= self.die_delay
                self.die_index += 1
                if self.die_index >= len(self.die_right):
                    self.is_dying = False
                    self.alive_flag = False
                    if self.die_right:
                        last = self.die_right[-1] if self.facing == 1 else self.die_left[-1]
                        anchor = self.rect.midbottom
                        self.image = last
                        self.rect = self.image.get_rect()
                        self.rect.midbottom = anchor
                    return
            if self.die_index < len(self.die_right):
                frame = self.die_right[self.die_index] if self.facing == 1 else self.die_left[self.die_index]
                anchor = self.rect.midbottom
                self.image = frame
                self.rect = self.image.get_rect()
                self.rect.midbottom = anchor
            return

        if not self.alive_flag:
            return

        # movimento: persegue o player se informado
        if player is not None and getattr(player, "rect", None) is not None:
            dx = player.rect.centerx - self.rect.centerx
            step = max(1, int(self.speed * SPEED_SCALE * (dt / (1000.0 / 60.0))))
            if dx > 8:
                self.rect.x += step
                self.facing = 1
                self.state = "walk"
            elif dx < -8:
                self.rect.x -= step
                self.facing = -1
                self.state = "walk"
            else:
                self.state = "idle"
        else:
            self.state = "idle"

        # escolha das frames base (sempre usar frames não-flipadas)
        if self.state == "walk":
            base = self.walk_frames if self.walk_frames else self.idle_frames
        else:
            base = self.idle_frames if self.idle_frames else self.walk_frames

        # aplica frame + flip
        frame_to_draw = self._select_frame_and_apply_flip(base, dt)
        if frame_to_draw is not None:
            anchor = self.rect.midbottom
            self.image = frame_to_draw
            self.rect = self.image.get_rect()
            self.rect.midbottom = anchor

        # ataque: só processa timer/geração quando player for passado
        if player is not None and getattr(player, "rect", None) is not None:
            distancia = abs(player.rect.centerx - self.rect.centerx)
            player_perto = distancia < 200
            if player_perto:
                self.attack_timer += dt
                if self.attack_timer >= self.attack_interval:
                    self.attack_timer = 0
                    if window_width is not None and ground_y is not None:
                        self.gerar_coxas(window_width, ground_y)
            else:
                self.attack_timer = 0

        # animação de ataque (se iniciou)
        frames_attack = self.attack_frames if self.attack_frames else None
        if self.atacando and frames_attack:
            if self.attack_anim_idx < len(frames_attack):
                self.attack_anim_timer += dt
                if self.attack_anim_timer >= self.attack_anim_delay:
                    self.attack_anim_timer -= self.attack_anim_delay
                    self.attack_anim_idx += 1
                if self.attack_anim_idx < len(frames_attack):
                    anchor = self.rect.midbottom
                    # aplica flip conforme facing
                    try:
                        attack_frame = frames_attack[self.attack_anim_idx]
                        if self.facing == -1:
                            attack_frame = pygame.transform.flip(attack_frame, True, False)
                        self.image = attack_frame
                        self.rect = self.image.get_rect()
                        self.rect.midbottom = anchor
                    except Exception:
                        pass
            else:
                self.atacando = False
                self.attack_anim_idx = 0
                self.attack_anim_timer = 0

        self.atualizar_coxas(dt)








