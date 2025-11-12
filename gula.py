import pygame
import random
import math

# ===== CONFIGURAÇÕES DOS TIROS (COXAS) =====
COXA_DAMAGE = 10
COXA_SPEED = 300  # pixels por segundo (velocidade do tiro)
COXA_WIDTH = 40
COXA_HEIGHT = 20
COXA_LIFETIME = 5000  # ms até desaparecer
COXA_SHOOT_DELAY = 3000  # ms entre cada tiro ← CONTROLE AQUI O DELAY

SPEED_SCALE = 0.90
ATTACK_ANIM_DELAY = 100


class BossGula(pygame.sprite.Sprite):
    def __init__(self, x, y, assets, hp=420, damage=16, patrol_min_x=100, patrol_max_x=None, speed=2):
        """
        Inicializa o chefe 'Gula', configurando sprites, atributos de movimento e combate.

        Parâmetros:
            x (int): Posição horizontal inicial.
            y (int): Posição vertical inicial.
            assets (dict): Dicionário contendo sprites e imagens.
            hp (int): Vida total do chefe.
            damage (int): Dano causado ao jogador.
            patrol_min_x (int): Limite esquerdo de movimentação.
            patrol_max_x (int): Limite direito de movimentação.
            speed (float): Velocidade de deslocamento.

        Retorna:
            None
        """
        super().__init__()

        self.idle_frames = assets.get('gula_idle', []) if assets else []
        self.walk_frames = assets.get('gula_walk', []) if assets else []
        self.attack_frames = assets.get('gula_attack', []) if assets else []
        self.die_frames = assets.get('gula_die', []) if assets else []

        self.die_right = list(self.die_frames)
        self.die_left = [pygame.transform.flip(f, True, False) for f in self.die_right] if self.die_right else []

        self.coxa_img = assets.get('gula_coxa') if assets else None
        if not self.coxa_img:
            temp_w = 50
            temp_h = 20
            self.coxa_img = pygame.Surface((temp_w, temp_h), pygame.SRCALPHA)
            pygame.draw.ellipse(self.coxa_img, (230, 120, 20), (0, 0, temp_w, temp_h))

        self.coxa_weapon = pygame.transform.scale(self.coxa_img, (COXA_WIDTH, COXA_HEIGHT))
        self.facing = -1
        self.image = self.idle_frames[0] if self.idle_frames else pygame.Surface((180, 180), pygame.SRCALPHA)
        if not self.idle_frames and not self.walk_frames:
            self.image.fill((0, 150, 0))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.hp = int(hp)
        self.base_hp = int(hp)
        self.damage = int(damage)
        self.alive_flag = True
        self.patrol_min_x = patrol_min_x
        self.patrol_max_x = patrol_max_x
        self.speed = float(speed)
        self.state = "idle"
        self.frame_idx = 0
        self.frame_timer = 0
        self.frame_delay = 200
        self.attack_anim_idx = 0
        self.attack_anim_timer = 0
        self.attack_anim_delay = ATTACK_ANIM_DELAY
        self.shoot_timer = 0
        self.is_dying = False
        self.die_index = 0
        self.die_timer = 0
        self.die_delay = 120
        self.coxas = []
        self.atacando = False

    def take_damage(self, amount):
        """
        Aplica dano ao chefe. Se o HP chegar a 0, inicia a animação de morte.

        Parâmetros:
            amount (int): Quantidade de dano recebido.

        Retorna:
            None
        """
        if not self.alive_flag:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.is_dying = True
            self.die_index = 0
            self.die_timer = 0
            self.coxas = []

    def atirar_coxa(self):
        """
        Cria e dispara um projétil (coxa de frango) na direção que o chefe está virado.

        Parâmetros:
            None

        Retorna:
            None
        """
        img = self.coxa_weapon.copy()
        if self.facing == 1:
            img = pygame.transform.flip(img, True, False)
        w, h = img.get_size()
        sx = self.rect.right + 10 if self.facing == 1 else self.rect.left - w - 10
        sy = self.rect.centery - h // 2
        rect = pygame.Rect(sx, sy, w, h)
        vel = COXA_SPEED * self.facing
        proj = {
            'rect': rect,
            'vel': vel,
            'image': img,
            'lifetime': COXA_LIFETIME,
            'damage': COXA_DAMAGE
        }
        self.coxas.append(proj)
        self.atacando = True
        self.attack_anim_idx = 0
        self.attack_anim_timer = 0

    def atualizar_coxas(self, dt, window_width):
        """
        Atualiza a posição dos projéteis disparados e remove os que saíram da tela.

        Parâmetros:
            dt (float): Tempo decorrido desde o último quadro (ms).
            window_width (int): Largura da janela do jogo.

        Retorna:
            None
        """
        if not self.coxas:
            return
        to_remove = []
        for p in self.coxas:
            dx = int(p['vel'] * (dt / 1000.0))
            p['rect'].x += dx
            p['lifetime'] -= dt
            if p['lifetime'] <= 0 or p['rect'].right < 0 or (window_width and p['rect'].left > window_width):
                to_remove.append(p)
        for p in to_remove:
            self.coxas.remove(p)

    def draw_traces(self, surface):
        """
        Desenha os projéteis (coxas) na tela.

        Parâmetros:
            surface (pygame.Surface): Superfície onde os projéteis serão desenhados.

        Retorna:
            None
        """
        for p in self.coxas:
            surface.blit(p['image'], p['rect'])

    def _select_frame_and_apply_flip(self, base_frames, dt):
        """
        Seleciona o frame de animação apropriado e aplica flip se necessário.

        Parâmetros:
            base_frames (list): Lista de frames da animação.
            dt (float): Tempo decorrido desde o último frame (ms).

        Retorna:
            pygame.Surface: Frame de animação ajustado.
        """
        if not base_frames:
            return None
        self.frame_timer += dt
        if self.frame_timer >= self.frame_delay:
            self.frame_timer -= self.frame_delay
            self.frame_idx = (self.frame_idx + 1) % len(base_frames)
        frame = base_frames[self.frame_idx]
        return pygame.transform.flip(frame, True, False) if self.facing == 1 else frame

    def update(self, dt, window_width=None, ground_y=None, player=None):
        """
        Atualiza o comportamento do chefe, controlando movimento, ataque, animações e estado de vida.

        Parâmetros:
            dt (float): Tempo decorrido desde o último quadro (ms).
            window_width (int): Largura da janela do jogo.
            ground_y (int): Posição do chão (altura de referência).
            player (obj): Instância do jogador (para rastrear posição).

        Retorna:
            None
        """
        if self.is_dying:
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

        if player and getattr(player, "rect", None):
            dx = player.rect.centerx - self.rect.centerx
            step = max(1, int(self.speed * SPEED_SCALE * (dt / (1000.0 / 60.0))))
            ATTACK_RANGE = 350
            if dx > 0:
                self.facing = 1
            else:
                self.facing = -1
            if abs(dx) > ATTACK_RANGE:
                if dx > 0:
                    self.rect.x += step
                else:
                    self.rect.x -= step
                self.state = "walk"
                self.shoot_timer = 0
            else:
                self.state = "idle"
                self.shoot_timer += dt
                if self.shoot_timer >= COXA_SHOOT_DELAY:
                    self.shoot_timer = 0
                    self.atirar_coxa()
        else:
            self.state = "idle"
            self.shoot_timer = 0

        base = self.walk_frames if self.state == "walk" else self.idle_frames
        if base and self.frame_idx >= len(base):
            self.frame_idx = 0
            self.frame_timer = 0
        frame_to_draw = self._select_frame_and_apply_flip(base, dt)
        if frame_to_draw:
            anchor = self.rect.midbottom
            self.image = frame_to_draw
            self.rect = self.image.get_rect()
            self.rect.midbottom = anchor

        frames_attack = self.attack_frames
        if self.atacando and frames_attack:
            if self.attack_anim_idx < len(frames_attack):
                self.attack_anim_timer += dt
                if self.attack_anim_timer >= self.attack_anim_delay:
                    self.attack_anim_timer -= self.attack_anim_delay
                    self.attack_anim_idx += 1
                if self.attack_anim_idx < len(frames_attack):
                    anchor = self.rect.midbottom
                    attack_frame = frames_attack[self.attack_anim_idx]
                    if self.facing == 1:
                        attack_frame = pygame.transform.flip(attack_frame, True, False)
                    self.image = attack_frame
                    self.rect = self.image.get_rect()
                    self.rect.midbottom = anchor
            else:
                self.atacando = False
                self.attack_anim_idx = 0
                self.attack_anim_timer = 0

        self.atualizar_coxas(dt, window_width)
