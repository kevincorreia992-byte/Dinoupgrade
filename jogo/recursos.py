from pathlib import Path
import pygame
PASTA_ASSETS = Path(__file__).resolve().parent.parent / 'assets'
def imagem(caminho):
    return pygame.image.load(str(PASTA_ASSETS / caminho)).convert_alpha()
def tamanho_por_altura(surface, altura):
    largura = max(1,round(surface.get_width()*altura/surface.get_height()))
    return pygame.transform.scale(surface,(largura,altura))
def sequencia(pasta, prefixo, total, altura):
    return [tamanho_por_altura(imagem(f'{pasta}/{prefixo}_{i}.png'),altura) for i in range(1,total+1)]
