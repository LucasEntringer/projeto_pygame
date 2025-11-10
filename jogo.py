# jogo.py (trecho relevante)
import pygame
import os
from config import LARGURA, ALTURA, FPS,  IMG_DIR, SND_DIR
from assets import load_assets
from ira import BossIra
from classes import Dante
import random

pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((LARGURA, ALTURA))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Segoe UI Symbol", 40)  # o número ajusta o tamanho do coração
# cor dos corações:
HEART_COLOR = (220, 20, 60)

assets = load_assets()
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()

#player
dante = Dante(groups=[all_sprites], assets=assets)

boss = None

running = True

pygame.mixer.music.play(loops=-1)
while running:
    dt = clock.tick(FPS)  # dt em ms

    bg = None
    bg_path = os.path.join(IMG_DIR, 'inferno', 'Cenario_inferno.png')
    try:
        bg = pygame.image.load(bg_path).convert()     # convert() é mais rápido para fundos sem alpha
        # escala a imagem para a resolução do jogo (opcional mas recomendado)
        bg = pygame.transform.scale(bg, (LARGURA, ALTURA))
    except Exception as e:
        print('Erro ao carregar background', bg_path, e)
        bg = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                dante.pular()
            if event.key == pygame.K_z:
                assets['atk_sound'].play()
                dante.attack(enemies)
                #Identifica se atacou antes do boss:
                if boss is not None:
                    boss.notify_player_attack()
                
    keys = pygame.key.get_pressed()
    left = keys[pygame.K_a] or keys[pygame.K_LEFT]
    right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

    if left and right:
        dante.parar()
    elif left:
        dante.mover_esquerda()
    elif right:
        dante.mover_direita()
    else:
        dante.parar()

    if boss is None and dante.rect.centerx >= LARGURA - 120:
        #teletransporta o player para o começo da segunda janela
        dante.rect.midbottom = (140, ALTURA - 10)
        dante.parar()
        #cria o boss na cena:
        bx = LARGURA // 2 + 100
        by = ALTURA - 10
        boss = BossIra(bx, by, assets=assets)
        enemies.add(boss)

    all_sprites.update(dt)

    #checa se há colisão entre os traços do boss e o dante
    if boss is not None:
        boss.update(dt, window_width=LARGURA, ground_y= ALTURA)
    
    if boss is not None:
        now = pygame.time.get_ticks()
        for t in list(boss.traces):
            if now >= t['warn_until'] and now < t['active_until']:
                # cria a hitbox dos pés do Dante (ajuste offsets conforme seu sprite)
                feet_h = 12                         # altura da caixa dos pés
                feet_w = max(24, int(dante.rect.width * 0.5))  # largura dos pés
                feet_x = dante.rect.centerx - feet_w // 2
                feet_y = dante.rect.bottom - feet_h
                feet_rect = pygame.Rect(feet_x, feet_y, feet_w, feet_h)

                if feet_rect.colliderect(t['rect']):
                    dante.dano(amount=boss.damage)
                    t['active_until'] = now - 1
        
    #Se o boss morreu, limpa e permite continuar
    if boss is not None and not boss.alive_flag:
        #remove o boss:
        try:
            boss.kill()
        except Exception:
            pass
        boss = None
        enemies.empty()
        
    if bg:
        window.blit(bg, (0,0))
    else:
        window.fill((30,30,30))
    
    if boss is not None:
        boss.draw_traces(window)
    
    all_sprites.draw(window)
    if boss is not None:
        window.blit(boss.image, boss.rect)

    # --- HUD do boss: nome e barra de vida ---
    if boss is not None:
        # parâmetros visuais
        bar_w = 420
        bar_h = 18
        margin_top = 8
        x = (LARGURA - bar_w) // 2
        y = margin_top

        # fundo (caixa escura)
        bg_rect = pygame.Rect(x-4, y-6, bar_w+8, bar_h+28)
        s_bg = pygame.Surface((bg_rect.w, bg_rect.h), pygame.SRCALPHA)
        s_bg.fill((10, 10, 10, 180))
        window.blit(s_bg, (bg_rect.x, bg_rect.y))

        # nome do boss
        name_font = pygame.font.SysFont(None, 28)  # usa fonte do sistema; ajuste se quiser
        name_surf = name_font.render("IRA", True, (230,230,230))
        name_pos = (x + (bar_w - name_surf.get_width())//2, y - 2)
        window.blit(name_surf, name_pos)

        # barra de vida (proporcional)
        hp_pct = max(0.0, boss.hp) / max(1, boss.base_hp)
        hp_w = int(bar_w * hp_pct)
        bar_rect = pygame.Rect(x, y + 18, bar_w, bar_h)
        hp_rect = pygame.Rect(x, y + 18, hp_w, bar_h)

        # desenha background da barra
        pygame.draw.rect(window, (60,60,60), bar_rect)
        # desenha vida restante
        pygame.draw.rect(window, (200,40,40), hp_rect)
        # borda
        pygame.draw.rect(window, (20,20,20), bar_rect, 2)

    hearts = "♥ " * max(0, dante.lives)
    if hearts:
        heart_surf = font.render(hearts, True, HEART_COLOR)
        window.blit(heart_surf, (10, 10))
    pygame.display.flip()

pygame.quit()
