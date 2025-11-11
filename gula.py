import pygame
import random
import math

# ===== CONFIGURAÇÕES DO BOSS =====
BOSS_ATTACK_INTERVAL = 1500  # NÃO USADO (sistema de tiro substitui)
FURY_MULT = 1.4
ATTACK_ANIM_DELAY = 100

# ===== CONFIGURAÇÕES DOS TIROS (COXAS) =====
COXA_DAMAGE = 18
COXA_SPEED = 350  # pixels por segundo (velocidade do tiro)
COXA_WIDTH = 40
COXA_HEIGHT = 20
COXA_LIFETIME = 5000  # ms até desaparecer
COXA_SHOOT_DELAY = 1200  # ms entre cada tiro ← CONTROLE AQUI O DELAY

SPEED_SCALE = 0.90


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
        
        # Carrega a imagem da coxa
        self.coxa_img = assets.get('gula_coxa') if assets else None
        if not self.coxa_img:
            # Fallback: cria uma coxa genérica
            temp_w = 50
            temp_h = 20
            self.coxa_img = pygame.Surface((temp_w, temp_h), pygame.SRCALPHA)
            pygame.draw.ellipse(self.coxa_img, (230, 120, 20), (0, 0, temp_w, temp_h))
        
        # Escala a coxa para o tamanho desejado
        self.coxa_weapon = pygame.transform.scale(self.coxa_img, (COXA_WIDTH, COXA_HEIGHT))

        self.facing = 1  # 1 = direita, -1 = esquerda
        
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

        # Sistema de tiro
        self.shoot_timer = 0

        self.is_dying = False
        self.die_index = 0
        self.die_timer = 0
        self.die_delay = 120

        self.coxas = []  # Lista de projéteis (tiros)
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

    def atirar_coxa(self):
        """Dispara uma coxa de frango na direção que o boss está olhando"""
        try:
            # Prepara a imagem do projétil (flipada se olhando para esquerda)
            img = self.coxa_weapon.copy()
            if self.facing == -1:
                img = pygame.transform.flip(img, True, False)
            
            w, h = img.get_size()

            # Posição inicial: na frente do boss
            if self.facing == 1:  # Olhando para direita
                sx = self.rect.right + 10
            else:  # Olhando para esquerda
                sx = self.rect.left - w - 10
            
            sy = self.rect.centery - h // 2

            rect = pygame.Rect(sx, sy, w, h)

            # Velocidade: positiva para direita, negativa para esquerda
            vel = COXA_SPEED * self.facing

            proj = {
                'rect': rect,
                'vel': vel,
                'image': img,
                'lifetime': COXA_LIFETIME,
                'damage': COXA_DAMAGE
            }
            self.coxas.append(proj)
            
            # Inicia animação de ataque
            self.atacando = True
            self.attack_anim_idx = 0
            self.attack_anim_timer = 0
            
        except Exception as e:
            print(f"Erro ao atirar coxa: {e}")

    def atualizar_coxas(self, dt, window_width):
        """Atualiza posição dos projéteis e remove os que saíram da tela"""
        if not self.coxas:
            return
        
        to_remove = []
        for p in self.coxas:
            # Move o projétil
            dx = int(p['vel'] * (dt / 1000.0))
            p['rect'].x += dx
            p['lifetime'] -= dt

            # Remove se saiu da tela ou acabou o lifetime
            off_left = p['rect'].right < 0
            off_right = window_width is not None and p['rect'].left > window_width
            if p['lifetime'] <= 0 or off_left or off_right:
                to_remove.append(p)

        for p in to_remove:
            try:
                self.coxas.remove(p)
            except ValueError:
                pass

    def draw_traces(self, surface):
        """Desenha os projéteis (coxas) na tela"""
        for p in self.coxas:
            try:
                surface.blit(p['image'], p['rect'])
            except Exception:
                # Fallback: desenha um retângulo
                pygame.draw.rect(surface, (230, 120, 20), p['rect'])

    def _select_frame_and_apply_flip(self, base_frames, dt):
        if not base_frames:
            return None
            
        self.frame_timer += dt
        if self.frame_timer >= self.frame_delay:
            self.frame_timer -= self.frame_delay
            self.frame_idx = (self.frame_idx + 1) % len(base_frames)
        
        frame = base_frames[self.frame_idx]
        
        # Aplica flip quando facing == -1 (olhando para esquerda)
        if self.facing == -1:
            try:
                return pygame.transform.flip(frame, True, False)
            except Exception:
                return frame
        else:
            return frame

    def update(self, dt, window_width=None, ground_y=None, player=None):
        # === ANIMAÇÃO DE MORTE ===
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

        # === LÓGICA DE COMPORTAMENTO ===
        if player is not None and getattr(player, "rect", None) is not None:
            dx = player.rect.centerx - self.rect.centerx
            step = max(1, int(self.speed * SPEED_SCALE * (dt / (1000.0 / 60.0))))
            
            ATTACK_RANGE = 350  # Distância para começar a atirar
            MELEE_RANGE = 120   # Distância mínima (para de andar)
            
            # === FACING: Sempre olha PARA o jogador ===
            if dx > 0:
                self.facing = 1  # Jogador à direita → olha para direita
            else:
                self.facing = -1  # Jogador à esquerda → olha para esquerda
            
            # === MOVIMENTO ===
            if abs(dx) > ATTACK_RANGE:
                # Muito longe: anda em direção ao jogador
                if dx > 0:
                    self.rect.x += step
                else:
                    self.rect.x -= step
                self.state = "walk"
                self.shoot_timer = 0  # Reseta o timer de tiro
            elif abs(dx) > MELEE_RANGE:
                # Distância ideal: para e atira
                self.state = "idle"
                
                # Sistema de tiro
                self.shoot_timer += dt
                if self.shoot_timer >= COXA_SHOOT_DELAY:
                    self.shoot_timer = 0
                    self.atirar_coxa()
            else:
                # Muito perto: para
                self.state = "idle"
                self.shoot_timer = 0
        else:
            self.state = "idle"
            self.shoot_timer = 0

        # === ANIMAÇÃO VISUAL (walk/idle) ===
        if self.state == "walk":
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

        # === ANIMAÇÃO DE ATAQUE ===
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

        # === ATUALIZA PROJÉTEIS ===
        self.atualizar_coxas(dt, window_width)