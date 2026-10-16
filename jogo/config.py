from functools import lru_cache
import pygame
LARGURA, ALTURA, FPS = 900, 400, 60
CHAO_Y = 345
MAX_VIDAS = 2  # Limite ja usado pela carta de vida extra.
BRANCO = (255,255,255)
ESCURO = (31,40,52)
OURO = (255,202,90)
VERMELHO = (185,49,42)
pygame.font.init()
FONTE = pygame.font.SysFont('arial',23,bold=True)
PEQUENA = pygame.font.SysFont('arial',17)
GRANDE = pygame.font.SysFont('arial',46,bold=True)


@lru_cache(maxsize=None)
def fonte_sistema(familias, tamanho, negrito=True):
    """Fonte do sistema criada uma única vez e reaproveitada nos quadros seguintes."""
    return pygame.font.SysFont(familias, tamanho, bold=negrito)
