import pygame
import os
from config import LARGURA, ALTURA, FPS, IMG_DIR, SND_DIR, MENU_STATE, GAME_STATE, EXIT_STATE, GAME_OVER_STATE
from assets import load_assets
from ira import BossIra
from classes import Dante
from gula import BossGula
import random
from ganancia import BossGanancia

def menu_screen(window, clock, assets):
    assets = load_assets()

    TAMANHO_NORMAL = 70
    TAMANHO_HOVER = 75

    font_normal = pygame.font.SysFont("Dark Hell Font", TAMANHO_NORMAL, bold=True)
    font_hover = pygame.font.SysFont("Dark Hell Font", TAMANHO_HOVER, bold=True)

    COLOR_NORMAL = (180, 180, 180)
    COLOR_HOVER = (255, 255, 255)

    #fontes e cores
    font_menu = pygame.font.SysFont("Dark Hell Font", 50)
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

    assets = load_assets()
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    dante = Dante(groups=[all_sprites], assets=assets)

    # SISTEMA DE SALAS
    ROOM_COUNT = 6
    current_room = 1

    # Nós guardamos referências aos bosses, mas só os adicionamos ao Group quando
    # estiverem na sala correta.
    gula = None
    ira = None
    luxuria = None

    def spawn_bosses_for_room(room):
        nonlocal gula, ira, luxuria
        # Remove bosses que estão no grupo se não pertencerem à sala atual
        # (a remoção do Group é feita no loop principal abaixo)
        # Cria instâncias apenas se necessário (lazy)
        if room == 2 and gula is None:
            bx = LARGURA // 2 + 100
            by = PLATFORM_Y
            gula = BossGula(bx, by, assets=assets, patrol_min_x=120, patrol_max_x=LARGURA - 120, speed=2.0)
        if room == 4 and luxuria is None:
            bx = LARGURA // 2
            by = PLATFORM_Y
            # adapte os argumentos de BossGanancia conforme quiser (x,y,assets,groups...)
            luxuria = BossGanancia(bx, by, assets=assets)
        if room == 6 and ira is None:
            bx = LARGURA // 2 + 100
            by = PLATFORM_Y
            ira = BossIra(bx, by, assets=assets)

    # certifica-se de criar possíveis bosses da sala inicial (se for sala 1 não faz nada)
    spawn_bosses_for_room(current_room)

    running = True
    pygame.mixer.music.play(loops=-1)

    # --- PRELOAD BACKGROUNDS (evita carregar a imagem a cada frame) ---
    # salas: 1,3,5 -> inferno ; 2 -> gula ; 4 -> ganancia ; 6 -> ira
    bg_cache = {}
    def _load_bg_file(filename):
        path = os.path.join(IMG_DIR, 'inferno', filename)
        if not os.path.isfile(path):
            return None
        try:
            img = pygame.image.load(path)
            # convert/convert_alpha adequados dependendo do alpha
            img = img.convert_alpha() if img.get_alpha() else img.convert()
            img = pygame.transform.scale(img, (LARGURA, ALTURA))
            return img
        except Exception as e:
            print("Erro carregando bg:", path, e)
            return None

    bg_cache[1] = _load_bg_file('Cenário_inferno.png')
    bg_cache[2] = _load_bg_file('Cenário_gula.png')
    bg_cache[3] = _load_bg_file('Cenário_inferno.png')
    bg_cache[4] = _load_bg_file('Cenário_ganancia.png')
    bg_cache[5] = _load_bg_file('Cenário_inferno.png')
    bg_cache[6] = _load_bg_file('Cenário_ira.png')

    # --- ALTURA FIXA DA PLATAFORMA (ajuste conforme a arte do fundo) ---
    # experimente valores como ALTURA - 60, ALTURA - 72, ALTURA - 90 até ficar perfeito
    PLATFORM_Y = ALTURA - 110

    # posicionamento inicial do jogador exatamente sobre a plataforma
    dante.rect.midbottom = (LARGURA // 2, PLATFORM_Y)

    while running:
        dt = clock.tick(FPS)

        # Seleciona o background pré-carregado para a sala atual
        bg = bg_cache.get(current_room)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Bloqueia controles se estiver morrendo
                if not getattr(dante, 'is_dying', False):
                    if event.key == pygame.K_w:
                        dante.pular()
                    if event.key == pygame.K_SPACE:
                        assets['atk_sound'].play()
                        dante.attack(enemies)
                        for e in enemies:
                            if hasattr(e, 'notify_player_attack'):
                                try:
                                    e.notify_player_attack()
                                except Exception:
                                    pass

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

        # --- MOVIMENTO ENTRE SALAS (borda direita / esquerda) ---
        # detecta se há algum boss vivo na sala atual
        boss_vivo = False

        # checagem para cada boss existente (expande fácil pra futuros)
        bosses_por_sala = {
            2: gula,
            4: luxuria,
            6: ira
        }

        boss_atual = bosses_por_sala.get(current_room)
        if boss_atual is not None and getattr(boss_atual, "alive_flag", False):
            boss_vivo = True

        # --- Borda direita ---
        if dante.rect.right >= LARGURA:
            if boss_vivo:
                # boss ainda está vivo — impede sair, mas permite andar pra dentro
                dante.rect.right = LARGURA - 2
                if dante.speedx > 0:
                    dante.parar()
            elif current_room < ROOM_COUNT:
                current_room += 1
                dante.rect.left = 10
                # garante y alinhado com a plataforma
                dante.rect.midbottom = (dante.rect.centerx, PLATFORM_Y)
                dante.parar()
                spawn_bosses_for_room(current_room)

                # adiciona/remover bosses conforme sala
                if gula and current_room == 2 and gula not in enemies:
                    enemies.add(gula)
                if luxuria and current_room == 4 and luxuria not in enemies:
                    enemies.add(luxuria)
                if ira and current_room == 6 and ira not in enemies:
                    enemies.add(ira)

                # remove bosses fora da sala
                for sala, boss in bosses_por_sala.items():
                    if boss and current_room != sala and boss in enemies:
                        try: enemies.remove(boss)
                        except Exception: pass
            else:
                dante.rect.right = LARGURA - 2
                if dante.speedx > 0:
                    dante.parar()

        # --- Borda esquerda ---
        if dante.rect.left <= 0:
            if boss_vivo:
                dante.rect.left = 2
                if dante.speedx < 0:
                    dante.parar()
            elif current_room > 1:
                current_room -= 1
                dante.rect.right = LARGURA - 10
                # garante y alinhado com a plataforma
                dante.rect.midbottom = (dante.rect.centerx, PLATFORM_Y)
                dante.parar()
                spawn_bosses_for_room(current_room)

                if gula and current_room == 2 and gula not in enemies:
                    enemies.add(gula)
                if ira and current_room == 6 and ira not in enemies:
                    enemies.add(ira)
                # futuro boss (sala 4)
                if "luxuria" in globals():
                    luxuria = globals()["luxuria"]
                    if luxuria and current_room == 4 and luxuria not in enemies:
                        enemies.add(luxuria)

                # remove bosses fora da sala
                for sala, boss in bosses_por_sala.items():
                    if boss and current_room != sala and boss in enemies:
                        try: enemies.remove(boss)
                        except Exception: pass
            else:
                dante.rect.left = 2
                if dante.speedx < 0:
                    dante.parar()

        all_sprites.update(dt)

        now = pygame.time.get_ticks()
        for e in list(enemies):
            try:
                # passa ground_y = PLATFORM_Y para consistência com a linha da plataforma
                e.update(dt, window_width=LARGURA, ground_y=PLATFORM_Y, player=dante)
            except TypeError:
                try:
                    e.update(dt, window_width=LARGURA, ground_y=PLATFORM_Y)
                except Exception:
                    try:
                        e.update(dt)
                    except Exception:
                        pass
            except Exception:
                pass

            if hasattr(e, 'traces') and getattr(e, 'traces'):
                for t in list(e.traces):
                    if now >= t['warn_until'] and now < t['active_until']:
                        feet_h = 12
                        feet_w = max(24, int(dante.rect.width * 0.3))
                        feet_x = dante.rect.centerx - feet_w // 2
                        # usar PLATFORM_Y para a checagem dos pés (base na plataforma)
                        feet_y = PLATFORM_Y - feet_h
                        feet_rect = pygame.Rect(feet_x, feet_y, feet_w, feet_h)
                        if feet_rect.colliderect(t['rect']):
                            try:
                                dante.dano(amount=e.damage)
                            except Exception:
                                dante.dano(amount=20)
                            t['active_until'] = now - 1

            if hasattr(e, 'coxas') and getattr(e, 'coxas'):
                for c in list(e.coxas):
                    c_rect = c.get('render_rect') if c.get('render_rect') else c['rect']
                    if dante.rect.colliderect(c_rect):
                        try:
                            dante.dano(amount=c.get('dano', 18))
                        except Exception:
                            dante.dano(amount=18)
                        try:
                            e.coxas.remove(c)
                        except ValueError:
                            pass

        if ira is not None and not ira.alive_flag:
            try:
                ira.kill()
            except Exception:
                pass
            ira = None

        if gula is not None and not gula.alive_flag:
            try:
                gula.kill()
            except Exception:
                pass
            try:
                enemies.remove(gula)
            except Exception:
                pass
            gula = None

        if luxuria is not None and not luxuria.alive_flag:
            try:
                luxuria.kill()
            except Exception:
                pass
            try:
                enemies.remove(luxuria)
            except Exception:
                pass
            luxuria = None
        # CORREÇÃO: Inicia a animação de morte, mas NÃO retorna ainda
        if dante.lives <= 0:
            if not getattr(dante, 'is_dying', False) and not getattr(dante, 'die_played', False):
                dante.morrer()
                assets['hurt_sound'].play()  # Toca som de morte (opcional)

        if bg:
            window.blit(bg, (0, 0))
        else:
            window.fill((30, 30, 30))

        for e in enemies:
            if hasattr(e, 'draw_traces'):
                try:
                    e.draw_traces(window)
                except Exception:
                    pass

        all_sprites.draw(window)

        try:
            enemies.draw(window)
        except Exception:
            for e in enemies:
                try:
                    window.blit(e.image, e.rect)
                except Exception:
                    pass

        boss_for_hud = None
        if ira is not None:
            boss_for_hud = ira
        elif gula is not None:
            boss_for_hud = gula
        elif luxuria is not None:
            boss_for_hud = luxuria

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
            boss_name = "IRA" if isinstance(boss_for_hud, BossIra) else "GULA"
            name_surf = name_font.render(boss_name, True, (230, 230, 230))
            name_pos = (x + (bar_w - name_surf.get_width()) // 2, y - 2)
            window.blit(name_surf, name_pos)

            hp_pct = max(0.0, boss_for_hud.hp) / max(1, boss_for_hud.base_hp)
            hp_w = int(bar_w * hp_pct)
            bar_rect = pygame.Rect(x, y + 18, bar_w, bar_h)
            hp_rect = pygame.Rect(x, y + 18, hp_w, bar_h)
            pygame.draw.rect(window, (60, 60, 60), bar_rect)
            pygame.draw.rect(window, (200, 40, 40), hp_rect)
            pygame.draw.rect(window, (20, 20, 20), bar_rect, 2)
            # Mostrar número de vida do boss (HP atual / total)
            hp_text = f"{boss_for_hud.hp}/{boss_for_hud.base_hp}"
            hp_font = pygame.font.SysFont(None, 26, bold=True)
            hp_surf = hp_font.render(hp_text, True, (255, 255, 255))
            hp_rect = hp_surf.get_rect(center=(x + bar_w // 2, y + 18 + bar_h // 2))
            window.blit(hp_surf, hp_rect)

        # Mostra corações (agora atualiza corretamente)
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
    clock = pygame.time.Clock()
    
    # Carrega os assets
    assets = load_assets()

    # Define o estado inicial
    current_state = MENU_STATE

    while current_state != EXIT_STATE:
        
        if current_state == MENU_STATE:
            # Chama a função do menu
            current_state = menu_screen(window, clock, assets)
            
        elif current_state == GAME_STATE:
            # Chama a função do jogo (seu código original)
            current_state = game_screen(window, clock, assets)
        
        elif current_state == GAME_OVER_STATE:
            current_state = game_over_screen(window, clock, assets)

    pygame.quit()

if __name__ == "__main__":
    main()
