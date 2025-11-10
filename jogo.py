# jogo.py (modificado: adiciona Gula e mantém Ira)
import pygame
import os
from config import LARGURA, ALTURA, FPS,  IMG_DIR, SND_DIR
from assets import load_assets
from ira import BossIra
from classes import Dante
import random
from gula import BossGula

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

# player
dante = Dante(groups=[all_sprites], assets=assets)

# cria Gula no começo do jogo
bx = LARGURA // 2 + 100
by = ALTURA - 10
gula = BossGula(bx, by, assets=assets, patrol_min_x=120, patrol_max_x=LARGURA-120, speed=2.0)
enemies.add(gula)
all_sprites.add(gula)

# Ira será criada quando o Dante chegar ao fim da tela
ira = None

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
                # Notifica qualquer inimigo presente que suporte notify_player_attack
                for e in enemies:
                    if hasattr(e, 'notify_player_attack'):
                        try:
                            e.notify_player_attack()
                        except Exception:
                            pass

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

    # spawn da Ira quando Dante alcançar o final da tela (mantém Gula que já existe)
    if ira is None and dante.rect.centerx >= LARGURA - 120:
        # teletransporta o player para o começo da segunda janela
        dante.rect.midbottom = (140, ALTURA - 10)
        dante.parar()
        # cria a Ira na cena:
        bx = LARGURA // 2 + 100
        by = ALTURA - 10
        ira = BossIra(bx, by, assets=assets)
        enemies.add(ira)
        all_sprites.add(ira)

    # atualiza todos os sprites (player + inimigos)
    all_sprites.update(dt)

    # atualiza cada inimigo (passando window params quando possível) e checa colisões com traços
    now = pygame.time.get_ticks()
    for e in list(enemies):  # list() permite remoção durante o loop
        # tenta chamar update com window params; se assinatura for diferente, cai para fallback
        try:
            e.update(dt, window_width=LARGURA, ground_y=ALTURA)
        except TypeError:
            try:
                e.update(dt)
            except Exception:
                pass
        except Exception:
            # protege contra outros erros de atualização para não travar o jogo
            pass

        # se o inimigo tem traços, checa colisão com os pés do Dante
        if hasattr(e, 'traces') and getattr(e, 'traces'):
            for t in list(e.traces):
                # dano ocorre durante a fase ACTIVE (mesma lógica original)
                if now >= t['warn_until'] and now < t['active_until']:
                    feet_h = 12                         # altura da caixa dos pés
                    feet_w = max(24, int(dante.rect.width * 0.3))  # largura dos pés (mesma lógica original)
                    feet_x = dante.rect.centerx - feet_w // 2
                    feet_y = dante.rect.bottom - feet_h
                    feet_rect = pygame.Rect(feet_x, feet_y, feet_w, feet_h)

                    if feet_rect.colliderect(t['rect']):
                        try:
                            dante.dano(amount=e.damage)
                        except Exception:
                            dante.dano(amount=20)
                        t['active_until'] = now - 1

    # remove Ira se ela morreu (não esvazia enemies: mantém Gula)
    if ira is not None and not ira.alive_flag:
        try:
            ira.kill()
        except Exception:
            pass
        ira = None

    # remove Gula se ela morreu (mantém Ira se ainda existir)
    if gula is not None and not gula.alive_flag:
        try:
            gula.kill()
        except Exception:
            pass
        gula = None
        # também remove de enemies (caso não tenha sido removida automaticamente)
        try:
            enemies.remove(gula)
        except Exception:
            pass

    # desenha fundo
    if bg:
        window.blit(bg, (0,0))
    else:
        window.fill((30,30,30))

    # desenha traços de cada inimigo (caso tenham)
    for e in enemies:
        if hasattr(e, 'draw_traces'):
            try:
                e.draw_traces(window)
            except Exception:
                pass

    # desenha sprites
    all_sprites.draw(window)

    # --- HUD do boss: escolhe Ira se existir, senão Gula ---
    boss_for_hud = None
    if ira is not None:
        boss_for_hud = ira
    elif gula is not None:
        boss_for_hud = gula

    if boss_for_hud is not None:
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
        boss_name = "IRA" if isinstance(boss_for_hud, BossIra) else "GULA"
        name_surf = name_font.render(boss_name, True, (230,230,230))
        name_pos = (x + (bar_w - name_surf.get_width())//2, y - 2)
        window.blit(name_surf, name_pos)

        # barra de vida (proporcional)
        hp_pct = max(0.0, boss_for_hud.hp) / max(1, boss_for_hud.base_hp)
        hp_w = int(bar_w * hp_pct)
        bar_rect = pygame.Rect(x, y + 18, bar_w, bar_h)
        hp_rect = pygame.Rect(x, y + 18, hp_w, bar_h)

        # desenha background da barra
        pygame.draw.rect(window, (60,60,60), bar_rect)
        # desenha vida restante
        pygame.draw.rect(window, (200,40,40), hp_rect)
        # borda
        pygame.draw.rect(window, (20,20,20), bar_rect, 2)

    # HUD de corações do Dante
    hearts = "♥ " * max(0, dante.lives)
    if hearts:
        heart_surf = font.render(hearts, True, HEART_COLOR)
        window.blit(heart_surf, (10, 10))

    pygame.display.flip()

pygame.quit()

