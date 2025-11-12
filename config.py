from os import path

# RESOLUÇÃO
LARGURA = 1280
ALTURA = 720

# Caminho base (ajuste se sua estrutura mudar)
IMG_DIR = path.join(path.dirname(__file__), 'assets', 'imagens')

FPS = 60
GRAVIDADE = 1

#Pasta que contem os sons

SND_DIR = path.join(path.dirname(__file__), 'assets', 'sounds')


#Controle de fluxos

MENU_STATE=0
GAME_STATE=1
EXIT_STATE=2
GAME_OVER_STATE=3
VICTORY_STATE=4


