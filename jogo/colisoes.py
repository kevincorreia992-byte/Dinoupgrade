"""Colisões por pixels visíveis, independentes das margens dos sprites.

As máscaras são criadas apenas quando os recursos são carregados, não a
cada quadro. Isso evita hitboxes enormes em animações com fundo transparente.
"""
import pygame

# Ignora transparência parcial e halos suaves ao redor dos pixels desenhados.
ALFA_COLISAO = 160


def _maior_componente(mascara):
    """Elimina elementos isolados que não fazem parte do corpo do inimigo."""
    partes = mascara.connected_components()
    return max(partes, key=lambda parte: parte.count()) if partes else mascara


def criar_mascara(imagem, nome=''):
    """Gera a máscara de colisão a partir do conteúdo VISÍVEL do sprite."""
    if 'lobo' in nome.lower():
        # O PNG do lobo contém um fundo escuro OPACO: seu canal alfa não
        # distingue o personagem do cenário. Só os pixels claros do lobo
        # devem contar como colisão, descartando o fundo e artefatos.
        mascara = pygame.mask.Mask(imagem.get_size())
        for y in range(imagem.get_height()):
            for x in range(imagem.get_width()):
                r, g, b, a = imagem.get_at((x, y))
                if a >= ALFA_COLISAO and max(r, g, b) >= 105:
                    mascara.set_at((x, y), 1)
        return _maior_componente(mascara)

    mascara = pygame.mask.from_surface(imagem, ALFA_COLISAO)
    if 'dino_vermelho' in nome.lower():
        # A arte original possui pequenas letras abaixo dos pés.
        # Essas letras não podem causar colisão.
        return _maior_componente(mascara)
    return mascara


def colidir(dinossauro, obstaculo):
    """Testa sobreposição real dos desenhos, incluindo o frame animado atual."""
    mascara_dino, ret_dino = dinossauro.mascara_colisao()
    mascara_obj, ret_obj = obstaculo.mascara_colisao()
    if not ret_dino.colliderect(ret_obj):
        return False
    deslocamento = (ret_obj.x - ret_dino.x, ret_obj.y - ret_dino.y)
    return mascara_dino.overlap(mascara_obj, deslocamento) is not None
