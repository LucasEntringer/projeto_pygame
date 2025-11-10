
import pygame
import random

# Comportamento
BOSS_ATTACK_INTERVAL = 2200
TRACE_COUNT = 5
TRACE_WARNING_DURATION = 1200
TRACE_ACTIVE_DURATION = 1800
FURY_MULT = 1.4
TRACE_WIDTH = 76
TRACE_HEIGHT = 18
TRACE_MARGIN_BOTTOM = 10
ATTACK_ANIM_DELAY = 100


class BossGula(pygame.sprite.Sprite):
    def __init__(self, x, y, assets, hp=420, damage=16, patrol_min_x=100, patrol_max_x=None, speed=2):
        super().__init__()
  
        self.idle_frames = assets.get('gula_idle', [])
        self.walk_frames = assets.get('gula_walk', [])
        self.attack_frames = assets.get('gula_attack', [])
        self.die_frames = assets.get('gula_die', [])

    
        self.idle_right = self.idle_frames
        self.idle_left = [pygame.transform.flip(f, True, False) for f in self.idle_frames]

        self.walk_right = self.walk_frames
        self.walk_left = [pygame.transform.flip(f, True, False) for f in self.walk_frames]

        self.attack_right = self.attack_frames
        self.attack_left = [pygame.transform.flip(f, True, False) for f in self.attack_frames]

        self.die_right = self.die_frames
        self.die_left = [pygame.transform.flip(f, True, False) for f in self.die_frames]

  
        self.facing = -1
        self.image = self.idle_right[0] if self.idle_right else pygame.Surface((180,180), pygame.SRCALPHA)
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

        # Timers e animações 
        self.state = "idle"
        self.frame_idx = 0
        self.frame_timer = 0
        self.frame_delay = 200  

        self.attack_timer = 0
        self.attack_interval = BOSS_ATTACK_INTERVAL
        self.attack_anim_idx = 0
        self.attack_anim_timer = 0
        self.attack_anim_delay = ATTACK_ANIM_DELAY

        #Morte 
        self.is_dying = False
        self.die_index = 0
        self.die_timer = 0
        self.die_delay = 120

        #Efeitos no chão
        self.traces = []

        # Fúria
        self.fury = False
        self.player_attacked_first = None

    # COMPORTAMENTO 

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
            self.traces = []

    # ATAQUE 
    def spawn_traces(self, window_width, ground_y, count=TRACE_COUNT):
        self.traces = []
        now = pygame.time.get_ticks()
        for i in range(count):
            w = TRACE_WIDTH
            h = TRACE_HEIGHT
            x = random.randint(100, max(100, window_width - 100 - w))
            y = ground_y - h - TRACE_MARGIN_BOTTOM
            pad_x = 10
            pad_y = 4
            hit_rect = pygame.Rect(x + pad_x, y + pad_y, max(4, w - 2 * pad_x), max(4, h - 2 * pad_y))
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
        # --- Animação de morte ---
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

        # Define limite direito se não houver
        if self.patrol_max_x is None and window_width is not None:
            self.patrol_max_x = max(self.patrol_min_x + 100, window_width - 100)

        # Movimento 
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

        #Atualiza animação
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

        # Ataque
        self.attack_timer += dt
        if self.attack_timer >= self.attack_interval:
            self.attack_timer = 0
            if window_width is not None and ground_y is not None:
                self.spawn_traces(window_width, ground_y)
            self.attack_anim_idx = 0
            self.attack_anim_timer = 0

        # Animação do ataque
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


        now = pygame.time.get_ticks()
        self.traces = [t for t in self.traces if t['active_until'] > now]

    def draw_traces(self, surface):
        now = pygame.time.get_ticks()
        for t in self.traces:
            vr = t.get('visual', t['rect'])
            if now < t['warn_until']:
                blink_period = 120
                show = ((now // blink_period) % 2) == 0
                if show:
                    alpha = 140 + int(80 * ((now % blink_period) / blink_period))
                    s = pygame.Surface((vr.w, vr.h), pygame.SRCALPHA)
                    s.fill((255, 180, 40, alpha))
                    surface.blit(s, (vr.x, vr.y))
            elif now < t['active_until']:
                s = pygame.Surface((vr.w, vr.h), pygame.SRCALPHA)
                s.fill((255, 160, 40, 200))
                surface.blit(s, (vr.x, vr.y))

