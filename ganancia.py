
# ganancia.py
import pygame
import random
from classes import Dante
from config import LARGURA, ALTURA, FPS

class BossGanancia(pygame.sprite.Sprite):
    """
    Classe que representa o boss Ganância (Avareza) do jogo.
    Este boss é um inimigo voador que se move pelo ar, atira projéteis em forma de moedas
    e possui animações de idle, ataque e morte.
    """
    
    def __init__(self, x, y, assets=None, groups=None):
        """
        Inicializa o Boss Ganância com sua posição inicial, sprites e configurações.
        
        Recebe:
            x (int): Posição X inicial do boss
            y (int): Posição Y inicial do boss
            assets (dict): Dicionário contendo os frames de animação do boss
            groups (iterable): Grupos de sprites aos quais o boss deve ser adicionado
        
        Faz:
            - Inicializa o sprite base do Pygame
            - Adiciona o boss aos grupos fornecidos
            - Define HP base, dano e estado inicial
            - Carrega os frames de animação dos assets
            - Cria a imagem de projétil (moeda dourada)
            - Define limites de movimento e posição alvo aleatória
            - Inicializa variáveis de animação e controle
        
        Retorna:
            Nada (construtor)
        """
        # Inicializa o sprite sem passar `groups` diretamente
        super().__init__()

        # Se o chamador passou um iterable de groups, adiciona o sprite a eles
        if groups:
            try:
                for g in groups:
                    g.add(self)
            except Exception:
                pass

        self.base_hp = 300
        self.hp = self.base_hp
        self.alive_flag = True
        self.damage = 10

        self.idle_frames = assets.get('ganancia_idle', [])
        self.attack_frames = assets.get('ganancia_attack', [])
        self.die_frames = assets.get('ganancia_die', [])

        self.state = 'idle'
        self.image = self.idle_frames[0] if self.idle_frames else pygame.Surface([50, 50])
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.projectiles = []
        self.shoot_delay = 2500  # ms entre disparos
        self.shoot_timer = 0
        self.projectile_speed = 5
        self.projectile_img = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.projectile_img, (255, 215, 0), (8, 8), 8)  # moeda dourada simples

        self.speed = 2.0
        self.max_x = LARGURA - 100
        self.min_x = 100
        self.max_y = ALTURA // 2
        self.min_y = 100
        self.target_pos = pygame.math.Vector2(random.randint(self.min_x, self.max_x), random.randint(self.min_y, self.max_y))
        self.pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)

        self.facing = 1
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_delay = 150
        
        self.is_attacking = False
        self.is_dying = False

    def set_state(self, new_state):
        """
        Altera o estado do boss e reseta os contadores de animação.
        
        Recebe:
            new_state (str): Novo estado a ser definido ('idle', 'attack' ou 'die')
        
        Faz:
            - Verifica se o novo estado é diferente do atual
            - Se for diferente, atualiza o estado
            - Reseta o índice do frame de animação para 0
            - Reseta o timer de animação para 0
        
        Retorna:
            Nada (void)
        """
        if new_state == self.state: return
        self.state = new_state
        self.frame_index = 0
        self.frame_timer = 0

    def take_damage(self, amount):
        """
        Aplica dano ao boss e inicia um ataque como reação.
        
        Recebe:
            amount (int): Quantidade de dano a ser aplicada ao HP do boss
        
        Faz:
            - Verifica se o boss está vivo e não está morrendo
            - Subtrai o dano do HP atual (não permite HP negativo)
            - Muda o estado do boss para 'attack' como reação ao dano
        
        Retorna:
            Nada (void)
        """
        if self.alive_flag and not self.is_dying:
            self.hp = max(0, self.hp - amount)
            self.set_state('attack') # Reage ao dano iniciando um ataque

    def notify_player_attack(self):
        """
        Notifica o boss que o jogador está atacando.
        
        Recebe:
            Nada
        
        Faz:
            - Muda o estado do boss para 'attack'
        
        Retorna:
            Nada (void)
        """
        self.set_state('attack')

    def _animate(self, dt):
        """
        Gerencia a animação do boss baseada no estado atual.
        
        Recebe:
            dt (int): Delta time em milissegundos desde o último frame
        
        Faz:
            - Incrementa o timer de animação com o delta time
            - Seleciona os frames corretos baseado no estado (dying, attack ou idle)
            - Avança para o próximo frame quando o delay é atingido
            - Gerencia o fim das animações (morte para no último frame, ataque volta ao idle, idle faz loop)
            - Aplica flip horizontal na sprite se o boss estiver olhando para a esquerda
            - Atualiza a imagem e o rect mantendo a posição central
        
        Retorna:
            Nada (void)
        """
        self.frame_timer += dt
        
        frames = []
        if self.is_dying:
            frames = self.die_frames
        elif self.state == 'attack':
            frames = self.attack_frames
        elif self.state == 'idle':
            frames = self.idle_frames

        if not frames:
            return

        if self.frame_timer >= self.frame_delay:
            self.frame_timer -= self.frame_delay
            self.frame_index += 1

            # Lógica de fim de animação (Ataque/Morte)
            if self.frame_index >= len(frames):
                if self.is_dying:
                    self.alive_flag = False
                    self.frame_index = len(frames) - 1 # Para manter o último frame
                elif self.state == 'attack':
                    self.set_state('idle')
                else:
                    self.frame_index = 0 # Loop para idle

        self.frame_index = min(self.frame_index, len(frames) - 1)
        
        new_image = frames[self.frame_index]
        if self.facing == -1:
            new_image = pygame.transform.flip(new_image, True, False)
        
        anchor = self.rect.center
        self.image = new_image
        self.rect = self.image.get_rect(center=anchor)

    def update(self, dt, **kwargs):
        """
        Atualiza o boss a cada frame do jogo.
        
        Recebe:
            dt (int): Delta time em milissegundos desde o último frame
            **kwargs: Argumentos adicionais, especialmente 'player' (objeto Dante) para referência ao jogador
        
        Faz:
            - Verifica se o HP chegou a zero e inicia animação de morte
            - Retorna imediatamente se o boss já morreu
            - Move o boss em direção a uma posição alvo aleatória (voo)
            - Escolhe nova posição alvo quando alcança a atual
            - Atualiza a direção que o boss está olhando baseado no movimento
            - Chama a função de animação
            - Gerencia o timer de disparo de projéteis
            - Cria novos projéteis (moedas) direcionados ao jogador a cada intervalo
            - Atualiza a posição de todos os projéteis ativos
            - Remove projéteis que expiraram ou colidiram com o jogador
            - Aplica dano ao jogador quando um projétil o atinge
        
        Retorna:
            Nada (void)
        """
        if self.hp <= 0 and not self.is_dying:
            self.is_dying = True
            self.set_state('die')
        
        if not self.alive_flag:
            return

        if not self.is_dying:
            # 1. Movimento de voo (ocorre apenas em estado 'idle' ou 'attack')
            direction = self.target_pos - self.pos
            distance = direction.length()
            
            if distance < self.speed:
                self.target_pos.x = random.randint(self.min_x, self.max_x)
                self.target_pos.y = random.randint(self.min_y, self.max_y)
            else:
                move_vector = direction.normalize() * self.speed
                self.pos += move_vector
                self.rect.center = (int(self.pos.x), int(self.pos.y))

                if move_vector.x > 0.1:
                    self.facing = 1
                elif move_vector.x < -0.1:
                    self.facing = -1
        
        self._animate(dt)

        # 2. Ataque à distância (atira moedas)
        self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_delay and not self.is_dying:
            self.shoot_timer = 0
            if 'player' in kwargs:
                player = kwargs['player']
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
                vx = self.projectile_speed * dx / dist
                vy = self.projectile_speed * dy / dist
                rect = self.projectile_img.get_rect(center=self.rect.center)
                self.projectiles.append({'rect': rect, 'vx': vx, 'vy': vy, 'life': 4000})



        # 3. Colisão com Dante - SEM dano por contato (apenas projéteis do boss podem ferir o jogador)
        if 'player' in kwargs and self.alive_flag and not self.is_dying:
            dante = kwargs['player']
            pass

        
        # Atualiza projéteis
        for p in list(self.projectiles):
            p['rect'].x += p['vx']
            p['rect'].y += p['vy']
            p['life'] -= dt
            if p['life'] <= 0:
                self.projectiles.remove(p)
            elif 'player' in kwargs and p['rect'].colliderect(kwargs['player'].rect):
                kwargs['player'].dano(amount=self.damage // 2)
                try:
                    self.projectiles.remove(p)
                except ValueError:
                    pass

    def draw_traces(self, surface):
        """
        Desenha todos os projéteis do boss na tela.
        
        Recebe:
            surface (pygame.Surface): Superfície do Pygame onde os projéteis serão desenhados
        
        Faz:
            - Itera por todos os projéteis ativos na lista
            - Desenha (blit) cada imagem de projétil na sua posição atual
        
        Retorna:
            Nada (void)
        """
        for p in self.projectiles:
            surface.blit(self.projectile_img, p['rect'])