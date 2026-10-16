from pathlib import Path
import pygame
from .config import CHAO_Y
from .recursos import sequencia, tamanho_por_altura
from .colisoes import criar_mascara

PASTA_DINO = Path(__file__).resolve().parent.parent / 'assets' / 'Dinossauro'


def _sequencia_personalizada(pasta_relativa, total):
    pasta = PASTA_DINO / pasta_relativa
    frames = []
    for i in range(1, total + 1):
        frame = pygame.image.load(str(pasta / f'dinossauro_{i}.png')).convert_alpha()
        frames.append(tamanho_por_altura(frame, 59))
    return frames


def carregar_frames_dino(acessorio=None):
    """Carrega os quadros base ou os quadros já compostos com acessório."""
    if acessorio:
        pasta = Path('ComAcessorios') / acessorio
        try:
            return _sequencia_personalizada(pasta, 8)
        except (pygame.error, OSError, FileNotFoundError):
            pass
    return sequencia('Dinossauro', 'dinossauro', 8, 59)


def carregar_frames_fogo(acessorio=None):
    """Três frames de ataque enviados pelo usuário, com corpo ancorado nos pés.

    Os quadros são mais largos por conterem a chama: esse espaço extra precisa
    ficar à DIREITA do dino, sem mudar o retângulo usado nas colisões.
    """
    nome = acessorio if acessorio in ('chapeu', 'oculos', 'oculos_chapeu') else 'base'
    pasta = PASTA_DINO / 'AtaqueNovo' / nome
    frames = []
    escala = 0.60 if nome != 'base' else 0.59
    for indice in range(1, 4):
        caminho = pasta / f'frame_{indice:02d}.png'
        try:
            original = pygame.image.load(str(caminho)).convert_alpha()
            tamanho = (max(1, round(original.get_width() * escala)),
                       max(1, round(original.get_height() * escala)))
            frames.append(pygame.transform.scale(original, tamanho))
        except (pygame.error, OSError, FileNotFoundError):
            return []
    return frames


class Dinossauro:
    def __init__(self, acessorio=None):
        self.acessorio = None
        self.frames = []
        self.frames_fogo = []
        self.mascaras = []
        self.tempo_fogo = 0.0
        self.animacao_fogo = 0.0
        self.rect = pygame.Rect(0, 0, 1, 1)
        self.definir_acessorio(acessorio)
        self.rect = self.frames[0].get_rect(midbottom=(110, CHAO_Y))
        self.y = float(self.rect.y)
        self.vel_y = 0.0
        self.no_chao = True
        self.animacao = 0.0

    def definir_acessorio(self, acessorio):
        if acessorio == self.acessorio and self.frames:
            return
        midbottom = self.rect.midbottom if self.frames else (110, CHAO_Y)
        self.acessorio = acessorio
        self.frames = carregar_frames_dino(acessorio)
        self.frames_fogo = carregar_frames_fogo(acessorio)
        self.mascaras = [criar_mascara(frame) for frame in self.frames]
        self.rect = self.frames[0].get_rect(midbottom=midbottom)
        self.y = float(self.rect.y)

    def pular(self):
        if self.no_chao:
            self.vel_y = -720.0
            self.no_chao = False

    def disparar_fogo(self):
        self.tempo_fogo = 0.36
        self.animacao_fogo = 0.0

    def atualizar(self, dt):
        self.animacao += dt
        self.vel_y += 2100 * dt
        self.y += self.vel_y * dt
        self.rect.y = round(self.y)
        if self.rect.bottom >= CHAO_Y:
            self.rect.bottom = CHAO_Y
            self.y = float(self.rect.y)
            self.vel_y = 0.0
            self.no_chao = True
        self.tempo_fogo = max(0.0, self.tempo_fogo - dt)
        if self.tempo_fogo > 0:
            self.animacao_fogo += dt

    def indice_frame(self):
        return int(self.animacao * 10) % len(self.frames) if self.no_chao else 0

    def mascara_colisao(self):
        indice = self.indice_frame()
        ret = self.frames[indice].get_rect(midbottom=self.rect.midbottom)
        return self.mascaras[indice], ret

    def _frame_visual(self):
        if self.tempo_fogo > 0 and self.frames_fogo:
            indice = min(len(self.frames_fogo) - 1, int(self.animacao_fogo / 0.12))
            return self.frames_fogo[indice]
        return self.frames[self.indice_frame()]

    def desenhar(self, tela):
        frame = self._frame_visual()
        if self.tempo_fogo > 0 and self.frames_fogo:
            # Animação larga: a boca/chama se estende para a direita, sem
            # deslocar o corpo do dino nem modificar a sua hitbox.
            ret_base = self.frames[self.indice_frame()].get_rect(midbottom=self.rect.midbottom)
            tela.blit(frame, frame.get_rect(bottomleft=ret_base.bottomleft))
        else:
            ret = frame.get_rect(midbottom=self.rect.midbottom)
            tela.blit(frame, ret)

    def colisao(self):
        return self.mascara_colisao()[1]
