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


class BossGula(pygame.sprite.Sprite):
    def __init__(self, x, y, assets, hp=420, damage=16, patrol_min_x=100, patrol_max_x=None, speed=2):
        super().__init__()

        self.idle_frames = assets.get('gula_idle', []) if assets else []
        self.walk_frames = assets.get('gula_walk', []) if assets else []
        self.attack_frames = assets.get('gula_attack', []) if assets else []
        self.die_frames = assets.get('gula_die', []) if assets else []
        self.coxa_img = assets.get('gula_coxa') if assets else None

        self.idle_right = self.idle_frames
        self.idle_left = [pygame.transform.flip(f, True, False) for f in self.idle_frames]
        self.walk_right = self.walk_frames
        self.walk_left = [pygame.transform.flip(f, True, False) for f in self.walk_frames]
        self.attack_right = self.attack_frames
        self.attack_left = [pygame.transform.flip(f, True, False) for f in self.attack_frames]
        self.die_right = self.die_frames
        self.die_left = [pygame.transform.flip(f, True, False) for f in self.die_frames]

        self.facing = -1
        self.image = self.idle_right[0] if self.idle_right else pygame.Surface((180, 180), pygame.SRCALPHA)
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
        for i in range(count):
            x = random.randint(COXA_SPREAD_PADDING, max(COXA_SPREAD_PADDING, window_width - COXA_SPREAD_PADDING - COXA_WIDTH))
            y = - random.randint(20, 200)
            rect = pygame.Rect(x, y, COXA_WIDTH, COXA_HEIGHT)
            vel_y = random.uniform(COXA_FALL_MIN_SPEED, COXA_FALL_MAX_SPEED)
            img = self.coxa_img
            if isinstance(img, pygame.Surface):
                img_s = pygame.transform.scale(img, (COXA_WIDTH, COXA_HEIGHT))
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

    def atualizar_coxas(self, dt):
        if not self.coxas:
            return
        to_remove = []
        for c in self.coxas:
            c['vel_y'] += GRAVITY
            c['rect'].y += int(c['vel_y'] * (dt / (1000 / 60)))
            c['angle'] = (c['angle'] + c['rot_speed'] * (dt / (1000 / 60))) % 360
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

        if self.patrol_max_x is None and window_width is not None:
            self.patrol_max_x = max(self.patrol_min_x + 100, window_width - 100)

        if self.moving and (self.patrol_min_x is not None and self.patrol_max_x is not None):
            self.rect.x += int(self.speed * self.facing)
            if self.rect.centerx <= self.patrol_min_x:
                self.rect.centerx = self.patrol_min_x
                self.facing = 1
            elif self.rect.centerx >= self.patrol_max_x:
                self.rect.centerx = self.patrol_max_x
                self.facing = -1

        desired_state = "walk" if self.moving else "idle"
        if self.state != desired_state:
            self.state = desired_state
            self.frame_idx = 0
            self.frame_timer = 0

        frames = []
        if self.state == "walk":
            frames = self.walk_right if self.facing == 1 else self.walk_left
        elif self.state == "idle":
            frames = self.idle_right if self.facing == 1 else self.idle_left

        if frames:
            self.frame_timer += dt
            if self.frame_timer >= self.frame_delay:
                self.frame_timer -= self.frame_delay
                self.frame_idx = (self.frame_idx + 1) % len(frames)
            anchor = self.rect.midbottom
            self.image = frames[self.frame_idx]
            self.rect = self.image.get_rect()
            self.rect.midbottom = anchor

        player_perto = False
        if player is not None:
            distancia = abs(player.rect.centerx - self.rect.centerx)
            player_perto = distancia < 280

        # se o player estiver perto e o intervalo passou, atacar novamente
        if player_perto:
            self.attack_timer += dt
            if self.attack_timer >= self.attack_interval:
                self.attack_timer = 0
                if window_width is not None and ground_y is not None:
                    self.gerar_coxas(window_width, ground_y)
                self.attack_anim_idx = 0
                self.attack_anim_timer = 0
        else:
            self.attack_timer = 0  # reseta se o jogador se afastar

        frames_attack = self.attack_right if self.facing == 1 else self.attack_left
        if frames_attack:
            if self.attack_anim_idx < len(frames_attack):
                self.attack_anim_timer += dt
                if self.attack_anim_timer >= self.attack_anim_delay:
                    self.attack_anim_timer -= self.attack_anim_delay
                    self.attack_anim_idx += 1
                if self.attack_anim_idx < len(frames_attack):
                    anchor = self.rect.midbottom
                    self.image = frames_attack[self.attack_anim_idx]
                    self.rect = self.image.get_rect()
                    self.rect.midbottom = anchor

        self.atualizar_coxas(dt)





