"""Ícones PNG das habilidades da loja, reutilizados na partida e nos menus."""
from pathlib import Path
import pygame

PASTA = Path(__file__).resolve().parent.parent / 'assets' / 'Habilidades'
CACHE = {}


def imagem_icone(chave, escala=1):
    chave_cache = (chave, escala)
    if chave_cache not in CACHE:
        caminho = PASTA / f'{chave}.png'
        sprite = pygame.image.load(str(caminho)).convert_alpha()
        if escala != 1:
            sprite = pygame.transform.scale(sprite,
                    (round(sprite.get_width()*escala), round(sprite.get_height()*escala)))
        CACHE[chave_cache] = sprite
    return CACHE[chave_cache]


def desenhar_icone(tela, chave, centro, escala=1):
    imagem = imagem_icone(chave, escala)
    tela.blit(imagem, imagem.get_rect(center=centro))
