import pygame
import os
from config import LARGURA, ALTURA, FPS, IMG_DIR, SND_DIR, MENU_STATE, GAME_STATE, EXIT_STATE, GAME_OVER_STATE
from assets import load_assets
from ira import BossIra
from classes import Dante
# Importa apenas BossGula (CoxaDeFrango removida)
from gula import BossGula
import random

def menu_screen(window, clock, assets):
    assets = load_assets()

    TAMANHO_NORMAL = 50
    TAMANHO_HOVER = 55

    font_normal = pygame.font.SysFont("Times New Roman", TAMANHO_NORMAL, bold=True)
    font_hover = pygame.font.SysFont("Times New Roman", TAMANHO_HOVER, bold=True)

    COLOR_NORMAL = (180, 180, 180)
    COLOR_HOVER = (255, 255, 255)

    #fontes e cores
    font_menu = pygame.font.SysFont("Times New Roman", 50)
    BTN_COLOR = (100, 100, 100)
    BTN_HOVER_COLOR = (150, 150, 150)
    TEXT_COLOR = (255, 255, 255)
    PRETO = (0, 0, 0)

    # Definição dos botões
    btn_w, btn_h = 300, 60
    btn_x = (LARGURA - btn_w) // 2

    start_btn = pygame.Rect(btn_x, 250, btn_w, btn_h) # Botão "Iniciar"
    exit_btn = pygame.Rect(btn_x, 350, btn_w, btn_h)  # Botão "Sair"

    background = assets['menu_back']

    menu_music_path = os.path.join(SND_DIR, 'menu_soundtrack.wav')
    pygame.mixer.music.load(menu_music_path)
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(0.5)

    running_menu = True
    while running_menu:
        clock.tick(FPS) 
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return EXIT_STATE

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # 1 é o Clique esquerdo
                    # Verifica se o clique foi em cima do botão "Iniciar"
                    assets['atk_sound'].play()
                    if start_btn.collidepoint(mouse_pos):
                        return GAME_STATE
            
                    if exit_btn.collidepoint(mouse_pos):
                        return EXIT_STATE
        
        window.blit(background,(0,0))

        if start_btn.collidepoint(mouse_pos):
            text_surf = font_hover.render("Iniciar", True, COLOR_HOVER)
        else:
            text_surf = font_normal.render("Iniciar", True, COLOR_NORMAL)
        
        text_rect = text_surf.get_rect(center=start_btn.center)
        window.blit(text_surf, text_rect)
        
        if exit_btn.collidepoint(mouse_pos):
            text_surf = font_hover.render("Sair", True, COLOR_HOVER)
        else:
            text_surf = font_normal.render("Sair", True, COLOR_NORMAL)
            
        text_rect = text_surf.get_rect(center=exit_btn.center)
        window.blit(text_surf, text_rect)

        pygame.display.flip()


def game_screen(window, clock, assets):
    font = pygame.font.SysFont("Segoe UI Symbol", 40)
    HEART_COLOR = (220, 20, 60)

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    # projectiles = pygame.sprite.Group() # REMOVIDO: Não há mais projéteis
    
    dante = Dante(groups=[all_sprites], assets=assets)

    # Inicia com o Boss Gula
    bx = LARGURA // 2 + 100
    by = ALTURA - 10
    gula = BossGula(bx, by, assets=assets, patrol_min_x=120, patrol_max_x=LARGURA - 120, speed=2.0)
    enemies.add(gula)
    all_sprites.add(gula) 
    
    # Ira começa como None
    ira = None

    running = True
    pygame.mixer.music.stop()
    game_music_path = os.path.join(SND_DIR, 'Verdi_s-Requiem_-II.-Dies-Irae-_CUGMZlvrR4c_.ogg') 
    pygame.mixer.music.load(game_music_path)
    pygame.mixer.music.play(loops=-1)

    while running:
        dt = clock.tick(FPS) 

        bg_path = os.path.join(IMG_DIR, 'inferno', 'Cenario_inferno.png')
        try:
            bg = pygame.image.load(bg_path).convert()
            bg = pygame.transform.scale(bg, (LARGURA, ALTURA))
        except pygame.error:
            bg = None
        except FileNotFoundError:
            bg = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return EXIT_STATE
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Bloqueia controles se estiver morrendo
                if not getattr(dante, 'is_dying', False):
                    if event.key == pygame.K_SPACE:
                        dante.pular()
                    if event.key == pygame.K_z:
                        assets['atk_sound'].play()
                        dante.attack(enemies)
                        for e in enemies:
                            # Notifica o boss sobre o ataque (se tiver o método)
                            if hasattr(e, 'notify_player_attack'):
                                e.notify_player_attack()

        # Bloqueia movimentação se estiver morrendo
        if not getattr(dante, 'is_dying', False):
            keys = pygame.key.get_pressed()
            left = keys[pygame.K_a] or keys[pygame.K_LEFT]
            right = keys[pygame.K_d] or keys[pygame.K_RIGHT]

            if left and right:
                dante.parar()
            elif left:
                dante.mover_esquerda()
            elif right:
                dante.mover_direita()
            else:
                dante.parar()
        else:
            # Garante que pare de se mover durante a morte
            dante.parar()

        # --- Limite de Movimento de Dante ---
        dante.rect.left = max(dante.rect.left, 0)
        # --------------------------------------

        # --- LÓGICA DE TRANSIÇÃO DE FASE: GULA -> IRA ---
        if gula is None and ira is None and dante.rect.centerx >= LARGURA - 120:
            
            # Reposiciona Dante para o início da nova "tela"
            dante.rect.midbottom = (140, ALTURA - 10)
            dante.parar()
            
            # Instancia o novo boss, Ira
            bx = LARGURA // 2 + 100
            by = ALTURA - 10
            ira = BossIra(bx, by, assets=assets)
            enemies.add(ira)
            all_sprites.add(ira)
        # -------------------------------------------------


        all_sprites.update(dt)
        # projectiles.update(dt) # REMOVIDO: Não há mais projéteis

        now = pygame.time.get_ticks()
        for e in list(enemies):
            # --- Atualização do Inimigo ---
            if hasattr(e, 'update'):
                if isinstance(e, BossGula):
                    # Gula.update agora NÃO retorna projéteis
                    e.update(dt, window_width=LARGURA, ground_y=ALTURA, player=dante)
                elif isinstance(e, BossIra):
                    e.update(dt, window_width=LARGURA, ground_y=ALTURA)
                else:
                    e.update(dt)

            # Lógica de colisão para ataques no chão do Ira (traces)
            if hasattr(e, 'traces') and getattr(e, 'traces'):
                for t in list(e.traces):
                    if now >= t['warn_until'] and now < t['active_until']:
                        feet_h = 12
                        feet_w = max(24, int(dante.rect.width * 0.3))
                        feet_x = dante.rect.centerx - feet_w // 2
                        feet_y = dante.rect.bottom - feet_h
                        feet_rect = pygame.Rect(feet_x, feet_y, feet_w, feet_h)
                        if feet_rect.colliderect(t['rect']):
                            damage_amount = getattr(e, 'damage', 20)
                            dante.dano(amount=damage_amount)
                            t['active_until'] = now - 1

            # --- Remoção de Inimigos Mortos ---
            if not getattr(e, 'alive_flag', True):
                if e is ira:
                    if ira is not None:
                        ira.kill()
                        ira = None
                elif e is gula:
                    if gula is not None:
                        gula.kill()
                        enemies.remove(gula)
                        gula = None
        
        # --- REMOVIDO: Lógica de Colisão Projétil (Coxa) vs Dante ---
        # Removido bloco que verificava hit_coxas.

        # Inicia a animação de morte, mas NÃO retorna ainda
        if dante.lives <= 0:
            if not getattr(dante, 'is_dying', False) and not getattr(dante, 'die_played', False):
                dante.morrer()
                assets['hurt_sound'].play()

        if bg:
            window.blit(bg, (0, 0))
        else:
            window.fill((30, 30, 30))

        # --- Desenho de Traços/Coxas ---
        for e in enemies:
            if hasattr(e, 'draw_traces'):
                e.draw_traces(window)
        # --------------------------------

        all_sprites.draw(window)

        # Lógica HUD
        boss_for_hud = None
        if ira is not None:
            boss_for_hud = ira
        elif gula is not None:
            boss_for_hud = gula

        if boss_for_hud is not None:
            bar_w = 420
            bar_h = 18
            margin_top = 8
            x = (LARGURA - bar_w) // 2
            y = margin_top

            bg_rect = pygame.Rect(x - 4, y - 6, bar_w + 8, bar_h + 28)
            s_bg = pygame.Surface((bg_rect.w, bg_rect.h), pygame.SRCALPHA)
            s_bg.fill((10, 10, 10, 180))
            window.blit(s_bg, (bg_rect.x, bg_rect.y))

            name_font = pygame.font.SysFont(None, 28)
            # Verifica o tipo de boss explicitamente
            if isinstance(boss_for_hud, BossIra):
                boss_name = "IRA"
                boss_base_hp = boss_for_hud.base_hp
            elif isinstance(boss_for_hud, BossGula):
                boss_name = "GULA"
                boss_base_hp = boss_for_hud.base_hp
            else:
                boss_name = "BOSS"
                boss_base_hp = 1 # Evita divisão por zero

            name_surf = name_font.render(boss_name, True, (230, 230, 230))
            name_pos = (x + (bar_w - name_surf.get_width()) // 2, y - 2)
            window.blit(name_surf, name_pos)

            hp_pct = max(0.0, boss_for_hud.hp) / max(1, boss_base_hp)
            hp_w = int(bar_w * hp_pct)
            bar_rect = pygame.Rect(x, y + 18, bar_w, bar_h)
            hp_rect = pygame.Rect(x, y + 18, hp_w, bar_h)
            pygame.draw.rect(window, (60, 60, 60), bar_rect)
            pygame.draw.rect(window, (200, 40, 40), hp_rect)
            pygame.draw.rect(window, (20, 20, 20), bar_rect, 2)


        # Mostra corações 
        hearts = "♥ " * max(0, dante.lives)
        if hearts:
            heart_surf = font.render(hearts, True, HEART_COLOR)
            window.blit(heart_surf, (10, 10))

        pygame.display.flip()

        # SÓ VAI PARA GAME OVER quando a animação de morte terminar
        if dante.lives <= 0 and getattr(dante, 'die_played', False):
            return GAME_OVER_STATE
            
    return MENU_STATE

def game_over_screen(window, clock, assets):
    font_titulo = pygame.font.SysFont("Arial", 70)
    font_instrucao = pygame.font.SysFont("Arial", 30)
    VERMELHO = (200, 0, 0)
    BRANCO = (255, 255, 255)
    PRETO = (0, 0, 0)

    running_game_over = True
    while running_game_over:
        clock.tick(FPS) 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return EXIT_STATE
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MENU_STATE
    
        window.fill(PRETO)

        text_go = font_titulo.render("GAME OVER", True, VERMELHO)
        text_go_rect = text_go.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50))
        window.blit(text_go, text_go_rect)

        text_inst = font_instrucao.render("Pressione ESC para voltar ao Menu", True, BRANCO)
        text_inst_rect = text_inst.get_rect(center=(LARGURA // 2, ALTURA // 2 + 50))
        window.blit(text_inst, text_inst_rect)

        pygame.display.flip()


def main():
    pygame.init()
    pygame.mixer.init()
    window = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Meu inferninho")
    
    # CORREÇÃO: Cria a instância do Clock corretamente
    clock = pygame.time.Clock()
    
    # Carrega os assets
    assets = load_assets()

    # Define o estado inicial
    current_state = MENU_STATE

    while current_state != EXIT_STATE:
        
        if current_state == MENU_STATE:
            # Passa o objeto clock
            current_state = menu_screen(window, clock, assets)
            
        elif current_state == GAME_STATE:
            # Passa o objeto clock
            current_state = game_screen(window, clock, assets)
        
        elif current_state == GAME_OVER_STATE:
            current_state = game_over_screen(window, clock, assets)

    pygame.quit()

if __name__ == "__main__":
    main()