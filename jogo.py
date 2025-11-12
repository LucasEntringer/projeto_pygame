import pygame
import os
from config import LARGURA, ALTURA, FPS, IMG_DIR, SND_DIR, MENU_STATE, GAME_STATE, EXIT_STATE, GAME_OVER_STATE, VICTORY_STATE, COMMAND_STATE
from assets import load_assets
from ira import BossIra
from classes import Dante
from gula import BossGula
import random
from ganancia import BossGanancia

def menu_screen(window, clock, assets):
    """
    Exibe e gerencia a tela de menu principal.

    O que faz:
        - Renderiza o background do menu.
        - Mostra botões (Iniciar, Comandos, Sair) e trata hover/click.
        - Toca a trilha sonora do menu.

    Recebe:
        window (pygame.Surface): Superfície principal onde o menu será desenhado.
        clock (pygame.time.Clock): Relógio para controle de FPS.
        assets (dict): Dicionário contendo imagens e sons necessários.

    Retorna:
        int: Um dos estados (GAME_STATE, COMMAND_STATE, EXIT_STATE) dependendo da interação do usuário.
    """
    TAMANHO_NORMAL = 60
    TAMANHO_HOVER = 65

    font_normal = pygame.font.SysFont("Bookman Old Style", TAMANHO_NORMAL, bold=True)
    font_hover = pygame.font.SysFont("Bookman Old Style", TAMANHO_HOVER, bold=True)

    COLOR_NORMAL = (204, 153, 0)
    COLOR_HOVER = (255, 255, 153)

    #fontes e cores
    font_menu = pygame.font.SysFont("Bookman Old Style", 50)
    BTN_COLOR = (100, 100, 100)
    BTN_HOVER_COLOR = (150, 150, 150)
    TEXT_COLOR = (255, 255, 255)
    PRETO = (0, 0, 0)

    # Definição dos botões
    btn_w, btn_h = 300, 60
    btn_x = (LARGURA - btn_w) // 2

    start_btn = pygame.Rect(btn_x, 250, btn_w, btn_h) # Botão "Iniciar"
    command_btn = pygame.Rect(btn_x, 350, btn_w, btn_h) #Botão "comandos"
    exit_btn = pygame.Rect(btn_x, 450, btn_w, btn_h)  # Botão "Sair"

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
                    
                    if command_btn.collidepoint(mouse_pos):
                        return COMMAND_STATE
            
                    if exit_btn.collidepoint(mouse_pos):
                        return EXIT_STATE
        
        window.blit(background,(0,0))

        if start_btn.collidepoint(mouse_pos):
            text_surf = font_hover.render("INICIAR", True, COLOR_HOVER)
        else:
            text_surf = font_normal.render("INICIAR", True, COLOR_NORMAL)
        
        text_rect = text_surf.get_rect(center=start_btn.center)
        window.blit(text_surf, text_rect)

        if command_btn.collidepoint(mouse_pos):
            text_surf = font_hover.render("COMANDOS", True, COLOR_HOVER)
        else:
            text_surf = font_normal.render("COMANDOS", True, COLOR_NORMAL)
        text_rect = text_surf.get_rect(center=command_btn.center)
        window.blit(text_surf, text_rect)
        
        if exit_btn.collidepoint(mouse_pos):
            text_surf = font_hover.render("SAIR", True, COLOR_HOVER)
        else:
            text_surf = font_normal.render("SAIR", True, COLOR_NORMAL)
            
        text_rect = text_surf.get_rect(center=exit_btn.center)
        window.blit(text_surf, text_rect)

        pygame.display.flip()

def command_screen(window, clock, assets):
    """
    Exibe a tela de comandos/controles do jogo.

    O que faz:
        - Renderiza a imagem com os comandos.
        - Aguarda a tecla ESC para retornar ao menu.

    Recebe:
        window (pygame.Surface): Superfície principal onde a tela será desenhada.
        clock (pygame.time.Clock): Relógio para controle de FPS.
        assets (dict): Dicionário contendo imagens (deve conter 'command_scr').

    Retorna:
        int: MENU_STATE quando o usuário pressionar ESC, ou EXIT_STATE se fechar a janela.
    """
    command_img = assets["command_scr"]

    running_commands = True
    while running_commands:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return EXIT_STATE
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MENU_STATE
                
        window.blit(command_img, (0, 0))

        pygame.display.flip()


def game_screen(window, clock, assets):
    """
    Executa o loop principal do jogo (tela de jogo).

    O que faz:
        - Inicializa sprites, bosses e lógica de salas.
        - Processa entradas (movimento, pulo, ataque).
        - Atualiza entidades, projéteis e checa colisões/dano.
        - Controla transições entre salas e estados (GAME_OVER, VICTORY, MENU).

    Recebe:
        window (pygame.Surface): Superfície principal onde o jogo será desenhado.
        clock (pygame.time.Clock): Relógio para controle de FPS.
        assets (dict): Dicionário contendo imagens, sons e outros recursos.

    Retorna:
        int: Próximo estado do jogo (MENU_STATE, GAME_OVER_STATE, VICTORY_STATE ou EXIT_STATE).
    """
    font = pygame.font.SysFont("Bookman Old Style", 40)
    HEART_COLOR = (220, 20, 60)

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
        """
        Cria instâncias dos bosses necessários para a sala atual (lazy instantiation).

        O que faz:
            - Instancia BossGula, BossGanancia (luxuria) e BossIra quando a sala correspondente for acessada.

        Recebe:
            room (int): Número da sala atual.

        Retorna:
            None
        """
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
        """
        Carrega e redimensiona um arquivo de background a partir da pasta de imagens.

        O que faz:
            - Monta o caminho a partir de IMG_DIR e carrega a imagem via pygame.
            - Redimensiona para (LARGURA, ALTURA).

        Recebe:
            filename (str): Nome do arquivo dentro de IMG_DIR/inferno.

        Retorna:
            pygame.Surface ou None: A superfície carregada e escalada, ou None se não existir.
        """
        path = os.path.join(IMG_DIR, 'inferno', filename)
        if not os.path.isfile(path):
            return None
        try:
            img = pygame.image.load(path)
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

    PLATFORM_Y = ALTURA - 110
    dante.rect.midbottom = (LARGURA // 2, PLATFORM_Y)

    while running:
        dt = clock.tick(FPS)
        bg = bg_cache.get(current_room)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
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
            dante.parar()

        boss_vivo = False
        bosses_por_sala = {
            2: gula,
            4: luxuria,
            6: ira
        }

        boss_atual = bosses_por_sala.get(current_room)
        if boss_atual is not None and getattr(boss_atual, "alive_flag", False):
            boss_vivo = True

        if dante.rect.right >= LARGURA:
            if boss_vivo:
                dante.rect.right = LARGURA - 2
                if dante.speedx > 0:
                    dante.parar()
            elif current_room < ROOM_COUNT:
                current_room += 1
                dante.rect.left = 10
                dante.rect.midbottom = (dante.rect.centerx, PLATFORM_Y)
                dante.parar()
                spawn_bosses_for_room(current_room)
                if gula and current_room == 2 and gula not in enemies:
                    enemies.add(gula)
                if luxuria and current_room == 4 and luxuria not in enemies:
                    enemies.add(luxuria)
                if ira and current_room == 6 and ira not in enemies:
                    enemies.add(ira)
                for sala, boss in bosses_por_sala.items():
                    if boss and current_room != sala and boss in enemies:
                        try: enemies.remove(boss)
                        except Exception: pass
            else:
                dante.rect.right = LARGURA - 2
                if dante.speedx > 0:
                    dante.parar()

        if dante.rect.left <= 0:
            if boss_vivo:
                dante.rect.left = 2
                if dante.speedx < 0:
                    dante.parar()
            elif current_room > 1:
                current_room -= 1
                dante.rect.right = LARGURA - 10
                dante.rect.midbottom = (dante.rect.centerx, PLATFORM_Y)
                dante.parar()
                spawn_bosses_for_room(current_room)
                if gula and current_room == 2 and gula not in enemies:
                    enemies.add(gula)
                if ira and current_room == 6 and ira not in enemies:
                    enemies.add(ira)
                if "luxuria" in globals():
                    luxuria = globals()["luxuria"]
                    if luxuria and current_room == 4 and luxuria not in enemies:
                        enemies.add(luxuria)
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
                        # versão alinhada: deixa a área dos pés maior e "encaixa" verticalmente com o hitbox do trace
                        # só aplica a verificação se o jogador estiver no chão (evita dano no ar)
                        if not getattr(dante, 'no_chao', False):
                            continue

                        feet_h = 28
                        feet_w = max(32, int(dante.rect.width * 0.45))
                        feet_x = dante.rect.centerx - feet_w // 2

                        # alinha verticalmente: coloca os pés um pouco acima de PLATFORM_Y e
                        # também permite que a área encaixe com o topo do trace (t['rect'].top)
                        feet_y = min(PLATFORM_Y - feet_h, t['rect'].top + 4)

                        feet_rect = pygame.Rect(feet_x, feet_y, feet_w, feet_h)
                        if feet_rect.colliderect(t['rect']):
                            try:
                                dante.dano(amount=e.damage)
                            except Exception:
                                dante.dano(amount=20)
                            assets['hurt_sound'].play()
                            t['active_until'] = now - 1

            if hasattr(e, 'coxas') and getattr(e, 'coxas'):
                for c in list(e.coxas):
                    c_rect = c.get('render_rect') if c.get('render_rect') else c['rect']
                    if dante.rect.colliderect(c_rect):
                        try:
                            dante.dano(amount=c.get('dano', 18))
                        except Exception:
                            dante.dano(amount=18)
                        assets['hurt_sound'].play()
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
            return VICTORY_STATE

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
        if dante.lives <= 0:
            if not getattr(dante, 'is_dying', False) and not getattr(dante, 'die_played', False):
                dante.morrer()
                assets['hurt_sound'].play()

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
            if isinstance(boss_for_hud, BossIra):
                boss_name = "IRA"
            elif isinstance(boss_for_hud, BossGanancia):
                boss_name = "LUXÚRIA"
            else:
                boss_name = "GULA"

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
            hp_text = f"{boss_for_hud.hp}/{boss_for_hud.base_hp}"
            hp_font = pygame.font.SysFont(None, 26, bold=True)
            hp_surf = hp_font.render(hp_text, True, (255, 255, 255))
            hp_rect = hp_surf.get_rect(center=(x + bar_w // 2, y + 18 + bar_h // 2))
            window.blit(hp_surf, hp_rect)

        hearts = "♥ " * max(0, dante.lives)
        if hearts:
            heart_surf = font.render(hearts, True, HEART_COLOR)
            window.blit(heart_surf, (10, 10))

        pygame.display.flip()

        if dante.lives <= 0 and getattr(dante, 'die_played', False):
            return GAME_OVER_STATE
            
    return MENU_STATE

def game_over_screen(window, clock, assets): 
    """
    Exibe a tela de Game Over.

    O que faz:
        - Renderiza background de Game Over.
        - Pisca instrução "PRESSIONE ESC PARA VOLTAR AO MENU".
        - Aguarda ESC para retornar ao menu ou fechar a janela.

    Recebe:
        window (pygame.Surface): Superfície principal.
        clock (pygame.time.Clock): Relógio para controle de FPS.
        assets (dict): Dicionário de assets (deve conter 'game_over_back').

    Retorna:
        int: MENU_STATE quando ESC for pressionado, ou EXIT_STATE se a janela for fechada.
    """
    font_titulo = pygame.font.SysFont("Bookman Old Style", 100)
    font_instrucao = pygame.font.SysFont("Bookman Old Style", 40)
    VERMELHO = (200, 0, 0)
    BRANCO = (255, 255, 255)
    PRETO = (0, 0, 0)
    background_over = assets['game_over_back']
    show_text = True
    BLINK_INTERVAL = 400
    last_update = pygame.time.get_ticks()

    running_game_over = True
    while running_game_over:
        window.blit(background_over, (0,0))
        now = pygame.time.get_ticks()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return EXIT_STATE
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MENU_STATE
        
        if now - last_update > BLINK_INTERVAL:
            show_text = not show_text
            last_update = now

        text_go = font_titulo.render("GAME OVER", True, BRANCO)
        text_go_rect = text_go.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50))
        window.blit(text_go, text_go_rect)
        if show_text: 
            text_inst = font_instrucao.render("PRESSIONE ESC PARA VOLTAR AO MENU", True, BRANCO)
            text_inst_rect = text_inst.get_rect(center=(LARGURA // 2, ALTURA // 2 + 50))
            window.blit(text_inst, text_inst_rect)
        

        pygame.display.flip()


def victory_screen(window, clock, assets):
    """
    Exibe a tela de vitória do jogo.

    O que faz:
        - Toca a trilha de vitória (se existir).
        - Carrega e exibe background de vitória a partir de IMG_DIR/imagem_da_tela_final.
        - Exibe título com efeito fade-in e instrução piscante para retornar ao menu.
        - Aguarda ESC para retornar ao menu ou fechar a janela.

    Recebe:
        window (pygame.Surface): Superfície principal.
        clock (pygame.time.Clock): Relógio para controle de FPS.
        assets (dict): Dicionário de assets (opcionalmente usado para ícones e sons).

    Retorna:
        int: MENU_STATE quando ESC for pressionado, ou EXIT_STATE se a janela for fechada.
    """
    font_titulo = pygame.font.SysFont("Georgia", 90, bold=True)
    font_instrucao = pygame.font.SysFont("Segoe UI Symbol", 35, bold=True)
    COR_TITULO = (255, 215, 0)
    COR_SOMBRA = (20, 20, 20)
    COR_INSTRUCAO = (245, 245, 245)

    victory_music_path = os.path.join(SND_DIR, 'victory_theme.wav')
    if os.path.isfile(victory_music_path):
        try:
            pygame.mixer.music.load(victory_music_path)
            pygame.mixer.music.play(loops=-1)
            pygame.mixer.music.set_volume(0.5)
        except Exception:
            pass

    victory_bg_img = None
    try:
        folder = os.path.join(IMG_DIR, 'imagem_da_tela_final')
        if os.path.isdir(folder):
            imagens = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if imagens:
                img_path = os.path.join(folder, imagens[0])
                img = pygame.image.load(img_path)
                img = img.convert_alpha() if img.get_alpha() else img.convert()
                victory_bg_img = pygame.transform.scale(img, (LARGURA, ALTURA))
    except Exception:
        victory_bg_img = None

    running_victory = True
    alpha = 0
    fade_in = True

    show_text = True
    BLINK_INTERVAL = 400
    last_update = pygame.time.get_ticks()

    while running_victory:
        now = pygame.time.get_ticks()
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return EXIT_STATE
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MENU_STATE
        
        if now - last_update > BLINK_INTERVAL:
            show_text = not show_text 
            last_update = now

        if victory_bg_img:
            window.blit(victory_bg_img, (0, 0))
        else:
            window.fill((0, 0, 0))

        if fade_in:
            alpha += int(300 * (dt / 1000.0))
            if alpha >= 255:
                alpha = 255
                fade_in = False

        title_text = "VOCÊ VENCEU!"
        title_surf = font_titulo.render(title_text, True, COR_TITULO)
        shadow_surf = font_titulo.render(title_text, True, COR_SOMBRA)

        title_surf_alpha = title_surf.copy().convert_alpha()
        shadow_surf_alpha = shadow_surf.copy().convert_alpha()
        title_surf_alpha.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        shadow_surf_alpha.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)

        title_rect = title_surf_alpha.get_rect(center=(LARGURA // 2, ALTURA // 2 - 80))
        window.blit(shadow_surf_alpha, (title_rect.x + 4, title_rect.y + 4))
        window.blit(title_surf_alpha, title_rect)

        if show_text: 
            text_inst = font_instrucao.render("PRESSIONE ESC PARA VOLTAR AO MENU", True, COR_INSTRUCAO)
            text_inst_rect = text_inst.get_rect(center=(LARGURA // 2, ALTURA // 2 + 50))
            window.blit(text_inst, text_inst_rect)

        pygame.display.flip()


def main():
    """
    Inicializa o Pygame e gerencia o loop principal de estados do jogo.

    O que faz:
        - Inicializa pygame/mixer e cria a janela.
        - Carrega assets e define o ícone.
        - Controla a máquina de estados (MENU, GAME, GAME_OVER, VICTORY, COMMAND).
        - Encerra o Pygame ao sair.

    Recebe:
        None (usa variáveis e constantes importadas).

    Retorna:
        None
    """
    pygame.init()
    pygame.mixer.init()
    window = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("HELLFIRE")
    clock = pygame.time.Clock()
    
    # Carrega os assets
    assets = load_assets()

    pygame.display.set_icon(assets['game_icon'])

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

        elif current_state == VICTORY_STATE:
            current_state = victory_screen(window, clock, assets)

        elif current_state == COMMAND_STATE:
            current_state = command_screen(window, clock, assets)

    pygame.quit()

if __name__ == "__main__":
    main()

