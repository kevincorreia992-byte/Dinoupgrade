"""Destaque discreto para sprites sobre cenários coloridos.

Esta superfície é usada SOMENTE no desenho. A imagem original permanece
responsável pela máscara de colisão, tamanho e posicionamento do objeto.
"""
import pygame

MARGEM = 3


CORES_HALO = (
    (255, 231, 160),  
    (255, 245, 190),  
    (187, 237, 255),  
    (255, 219, 136),  
)


def destacar_sprite(imagem, fase):
    largura, altura = imagem.get_size()
    superficie = pygame.Surface(
        (largura + 2 * MARGEM, altura + 2 * MARGEM), pygame.SRCALPHA
    )
    mascara = pygame.mask.from_surface(imagem, 105)
    if mascara.count() == 0:
        superficie.blit(imagem, (MARGEM, MARGEM))
        return superficie

    cor_halo = CORES_HALO[max(0, min(int(fase), len(CORES_HALO) - 1))]
    
    
    vulcao = fase == 3
    halo = mascara.to_surface(
        setcolor=(*cor_halo, 130 if vulcao else 64),
        unsetcolor=(0, 0, 0, 0),
    )
    contorno = mascara.to_surface(
        setcolor=(255, 227, 142, 215) if vulcao else (18, 29, 40, 200),
        unsetcolor=(0, 0, 0, 0),
    )

    
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        superficie.blit(halo, (MARGEM + dx, MARGEM + dy))
    for dx, dy in (
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),            (0, 1),
        (1, -1),  (1, 0),   (1, 1),
    ):
        superficie.blit(contorno, (MARGEM + dx, MARGEM + dy))
    superficie.blit(imagem, (MARGEM, MARGEM))
    return superficie
