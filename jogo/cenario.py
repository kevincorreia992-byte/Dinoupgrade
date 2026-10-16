"""Cenário em movimento: paralaxe e piso próprio de cada bioma."""
import pygame
from .config import LARGURA, ALTURA, CHAO_Y
from .recursos import PASTA_ASSETS
from .fases import PASTAS_FASES


class Cenario:
    def __init__(self):
        self.fundos = []
        self.fundos_espelhados = []
        self.pisos = []
        for indice, pasta_fase in enumerate(PASTAS_FASES):
            pasta = PASTA_ASSETS / 'Fases' / pasta_fase / 'Cenario'
            candidatos = [pasta / 'fundo_1200x640.png', pasta / 'cenariofundo.png']
            caminho = next((p for p in candidatos if p.is_file()), None)
            if caminho is None:
                raise FileNotFoundError(f'Sem fundo para {pasta_fase}')
            original = pygame.image.load(str(caminho)).convert()
            # Gelo/Vulcao: o fundo 1200x640 era comprimido em 900x420,
            # alongando montanhas e arvores na horizontal. Redimensionar
            # proporcionalmente sem interpolacao evita essa distorcao.
            altura = 420
            largura = max(LARGURA, round(original.get_width() * altura / original.get_height()))
            if indice in (2, 3):
                fator = max(LARGURA / original.get_width(), altura / original.get_height())
                largura = max(LARGURA, round(original.get_width() * fator))
                altura = max(420, round(original.get_height() * fator))
            fundo = pygame.transform.scale(original, (largura, altura))
            self.fundos.append(fundo)
            self.fundos_espelhados.append(pygame.transform.flip(fundo, True, False))
            caminho_piso = PASTA_ASSETS / 'Fases' / pasta_fase / 'Cenario' / 'piso_repetivel.png'
            self.pisos.append(pygame.image.load(str(caminho_piso)).convert())
        self.reiniciar()

    def reiniciar(self):
        self.fase_atual = 0
        self.fase_anterior = 0
        self.progresso_transicao = 1.0
        self.deslocamento_fundo = 0.0
        self.deslocamento_piso = 0.0

    def _camada(self, tela, fase):
        fundo = self.fundos[fase]
        invertido = self.fundos_espelhados[fase]
        largura = fundo.get_width()
        # Sequência A, A espelhado, A, A espelhado: sem cortes bruscos nas bordas.
        deslocamento = int(self.deslocamento_fundo)
        indice = deslocamento // largura
        x = -(deslocamento % largura)
        while x < LARGURA:
            tela.blit(fundo if indice % 2 == 0 else invertido, (x, 0))
            x += largura
            indice += 1
        # Piso repetível e móvel, em sincronia com os obstáculos.
        piso = self.pisos[fase]
        largura_piso = piso.get_width()
        x = -(int(self.deslocamento_piso) % largura_piso)
        while x < LARGURA:
            tela.blit(piso, (x, CHAO_Y))
            x += largura_piso

    def desenhar(self, tela, dt=0, velocidade=0, fase=0):
        fase = max(0, min(int(fase), len(self.fundos) - 1))
        if fase != self.fase_atual:
            self.fase_anterior = self.fase_atual
            self.fase_atual = fase
            self.progresso_transicao = 0.0
        self.deslocamento_fundo += max(0, velocidade) * dt * 0.23
        self.deslocamento_piso += max(0, velocidade) * dt
        self.progresso_transicao = min(1.0, self.progresso_transicao + dt / 1.4)
        if self.progresso_transicao < 1.0:
            self._camada(tela, self.fase_anterior)
            camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            self._camada(camada, self.fase_atual)
            camada.set_alpha(round(255 * self.progresso_transicao))
            tela.blit(camada, (0, 0))
        else:
            self._camada(tela, self.fase_atual)
