import pygame
import random
import math
from config import GRAVIDADE # Importa a gravidade para o projétil

BOSS_ATTACK_INTERVAL = 1500
FURY_MULT = 1.4
ATTACK_ANIM_DELAY = 100

COXA_VELOCITY_X = 8           # Velocidade horizontal da coxa
COXA_VELOCITY_Y = -15         # Velocidade vertical inicial da coxa
COXA_DAMAGE = 18              # Dano da coxa
COXA_LIFESPAN = 3000          # ms antes de desaparecer

SPEED_SCALE = 0.90


class CoxaDeFrango(pygame.sprite.Sprite):
    def __init__(self, x, y, facing, assets, groups=None):
        super().__init__(groups)
        
        self.image_base = assets.get('gula_coxa') # Usa a chave do assets.py
        if self.image_base:
            # ALTURA é 720, importada de config
            self.image_base = pygame.transform.scale(self.image_base, (40, 20)) 
        else:
            # Fallback visual se a imagem faltar
            self.image_base = pygame.Surface((40, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image_base, (230, 120, 20), (0, 0, 40, 20))
            
        self.facing = facing
        self.image = self.image_base if facing == 1 else pygame.transform.flip(self.image_base, True, False)
        
        self.rect = self.image.get_rect(center=(x, y))
        
        # Inverte a velocidade horizontal se estiver virado para a esquerda
        self.speedx = COXA_VELOCITY_X * facing
        self.speedy = COXA_VELOCITY_Y 
        self.damage = COXA_DAMAGE
        self.spawn_time = pygame.time.get_ticks()

    def update(self, dt):
        # Aplica Gravidade
        self.speedy += GRAVIDADE
        
        # Movimento
        self.rect.x += int(self.speedx)
        self.rect.y += int(self.speedy)
        
        # Rotação do projétil (opcional)
        if self.speedx != 0:
            # Calcula o ângulo de voo
            angle = math.degrees(math.atan2(-self.speedy, self.speedx))
            temp_image = pygame.transform.rotate(self.image_base, angle)
            
            # Se for left (-1), flipa o resultado
            if self.facing == -1:
                # Rotaciona o frame flipado
                temp_image = pygame.transform.flip(temp_image, True, False) 
            
            # Preserva o centro ao trocar a imagem para evitar jitter
            center = self.rect.center
            self.image = temp_image
            self.rect = self.image.get_rect(center=center)
        
        # Remoção do projétil (expira ou sai da tela)
        now = pygame.time.get_ticks()
        # ALTURA (720) é a constante definida em config.py
        if now - self.spawn_time > COXA_LIFESPAN or self.rect.bottom > 720 + 20: 
            self.kill()


class BossGula(pygame.sprite.Sprite):
    def __init__(self, x, y, assets, hp=420, damage=16, patrol_min_x=100, patrol_max_x=None, speed=2):
        super().__init__()

        self.idle_frames = assets.get('gula_idle', []) if assets else []
        self.walk_frames = assets.get('gula_walk', []) if assets else []
        self.attack_frames = assets.get('gula_attack', []) if assets else []
        self.die_frames = assets.get('gula_die', []) if assets else []
        self.die_right = list(self.die_frames)
        try:
            self.die_left = [pygame.transform.flip(f, True, False) for f in self.die_right]
        except Exception:
            self.die_left = list(self.die_right)
        self.coxa_img = assets.get('gula_coxa') if assets else None
        
        if not self.coxa_img:
            temp_w = 50
            temp_h = 20
            self.coxa_img = pygame.Surface((temp_w, temp_h), pygame.SRCALPHA)
            pygame.draw.ellipse(self.coxa_img, (230, 120, 20), (0, 0, temp_w, temp_h))
        
        self.facing = -1
        
        self.image = self.idle_frames[0] if self.idle_frames else pygame.Surface((180, 180), pygame.SRCALPHA)
        if not self.idle_frames and not self.walk_frames:
            self.image.fill((0, 150, 0))
            
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

        self.fury = False
        self.player_attacked_first = None

        self.atacando = False
        self.assets = assets # Guarda assets para instanciar o projétil

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

    def gerar_coxas(self, projectiles_group): # CORRIGIDO: Removeu o argumento 'assets'
        """Instancia e retorna o projétil CoxaDeFrango."""
        self.atacando = True
        self.attack_anim_idx = 0
        self.attack_anim_timer = 0
        
        # Ponto de lançamento (ajustado para a mão do boss)
        launch_x = self.rect.centerx + (self.rect.width // 4) * self.facing 
        launch_y = self.rect.centery - 30 
        
        # Cria o projétil (usando self.assets)
        new_coxa = CoxaDeFrango(launch_x, launch_y, self.facing, self.assets, groups=None)
        
        return new_coxa

    def draw_traces(self, surface):
        """Mantido para compatibilidade com Ira, mas não desenha a coxa."""
        pass


    def _select_frame_and_apply_flip(self, base_frames, dt):
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
            # Lógica de morte
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
                    return []
            if self.die_index < len(self.die_right):
                frame = self.die_right[self.die_index] if self.facing == 1 else self.die_left[self.die_index]
                anchor = self.rect.midbottom
                self.image = frame
                self.rect = self.image.get_rect()
                self.rect.midbottom = anchor
            return []

        if not self.alive_flag:
            return []
        
        projectile_to_add = None 

        if player is not None and getattr(player, "rect", None) is not None:
            dx = player.rect.centerx - self.rect.centerx
            step = max(1, int(self.speed * SPEED_SCALE * (dt / (1000.0 / 60.0))))
            
            MELEE_RANGE = 100
            
            if abs(dx) > MELEE_RANGE: 
                if dx > 0:
                    self.rect.x += step
                    self.facing = 1
                else:
                    self.rect.x -= step
                    self.facing = -1
                self.state = "walk"
            else: 
                self.state = "idle"
                self.facing = 1 if dx > 0 else -1 
                
                if not self.atacando:
                    self.attack_timer += dt
                    if self.attack_timer >= self.attack_interval:
                        self.attack_timer = 0
                        # CORRIGIDO: Gera e captura o projétil, chamando sem o argumento 'assets'
                        projectile_to_add = self.gerar_coxas(None) 
                else:
                    self.attack_timer = self.attack_interval 

        else:
            self.state = "idle"
            self.attack_timer = 0

        new_state = self.state
        if new_state == "walk":
            base = self.walk_frames if self.walk_frames else self.idle_frames
        else:
            base = self.idle_frames if self.idle_frames else self.walk_frames

        if base and self.frame_idx >= len(base):
             self.frame_idx = 0
             self.frame_timer = 0
             
        frame_to_draw = self._select_frame_and_apply_flip(base, dt)
        if frame_to_draw is not None:
            anchor = self.rect.midbottom
            self.image = frame_to_draw
            self.rect = self.image.get_rect()
            self.rect.midbottom = anchor

        frames_attack = self.attack_frames if self.attack_frames else None
        if self.atacando and frames_attack:
            if self.attack_anim_idx < len(frames_attack):
                self.attack_anim_timer += dt
                if self.attack_anim_timer >= self.attack_anim_delay:
                    self.attack_anim_timer -= self.attack_anim_delay
                    self.attack_anim_idx += 1
                if self.attack_anim_idx < len(frames_attack):
                    anchor = self.rect.midbottom
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
        
        # Retorna o projétil (se gerado) para o game_screen
        return [projectile_to_add] if projectile_to_add else []

