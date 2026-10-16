"""HUD pixel art do Dino Upgrade.

Desenhado com primitivas do Pygame, sem assets/fontes adicionais.
A interface e renderizada em meia resolucao e ampliada por nearest-neighbor,
para que placas, icones e textos tenham pixels nitidos em 900 x 400.
"""

import pygame
from .config import LARGURA, ALTURA, MAX_VIDAS, fonte_sistema

ESCALA = 2
BASE_LARGURA = LARGURA // ESCALA
BASE_ALTURA = ALTURA // ESCALA

FUNDO = (19, 34, 42, 234)
SOMBRA = (7, 12, 19, 110)
BORDA = (207, 186, 143, 235)
CLARO = (250, 241, 210)
MUTED = (172, 190, 189)

# Cores do proprio mundo: os paineis conservam o mesmo acabamento,
# enquanto o detalhe e o icone acompanham o bioma.
BIOMAS = (
    ("FLORESTA", (126, 212, 113), (61, 119, 73)),
    ("DESERTO", (242, 189, 98), (157, 109, 54)),
    ("GELO", (117, 218, 244), (49, 130, 171)),
    ("VULCAO", (255, 142, 102), (184, 66, 48)),
)

CORACAO = (
    "..##.##..",
    ".########",
    "#########",
    "#########",
    ".#######.",
    "..#####..",
    "...###...",
    "....#....",
)


class Hud:
    def __init__(self):
        # Fonte monoespacada fica pixelada pelo desenho sem antialias + escala 2x.
        self.fonte_mini = fonte_sistema('consolas,couriernew,monospace', 9)
        self.fonte_normal = fonte_sistema('consolas,couriernew,monospace', 12)
        self.fonte_pontos = fonte_sistema('consolas,couriernew,monospace', 16)
        self.coracoes_desbloqueados = 1
        self.marco_pontos = 0
        self.pulso_pontos = 0.0

    @staticmethod
    def _placa(superficie, area, destaque):
        """Moldura retangular com cantos recortados, sem bordas arredondadas."""
        x, y, largura, altura = area
        pygame.draw.rect(superficie, SOMBRA, (x + 2, y + 3, largura, altura))
        pygame.draw.rect(superficie, BORDA, (x, y, largura, altura))
        pygame.draw.rect(superficie, FUNDO, (x + 1, y + 1, largura - 2, altura - 2))
        # Cantos em degraus e filete superior fazem parte da linguagem pixel art.
        for canto_x in (x, x + largura - 1):
            for canto_y in (y, y + altura - 1):
                superficie.fill((0, 0, 0, 0), (canto_x, canto_y, 1, 1))
        pygame.draw.rect(superficie, destaque, (x + 5, y + 3, largura - 10, 1))
        pygame.draw.rect(superficie, (76, 94, 93, 255),
                         (x + 5, y + altura - 4, largura - 10, 1))
        # Rebites quadrados, nao circulos.
        for canto_x in (x + 3, x + largura - 4):
            superficie.fill(BORDA, (canto_x, y + 4, 1, 1))
            superficie.fill(BORDA, (canto_x, y + altura - 5, 1, 1))

    @staticmethod
    def _escrever(superficie, fonte, frase, cor, centro, limite=None):
        frase = str(frase)
        imagem = fonte.render(frase, False, cor)
        if limite is not None and imagem.get_width() > limite:
            # Nao invadir os paineis adjacentes com nomes compridos.
            while frase and imagem.get_width() > limite:
                frase = frase[:-1]
                imagem = fonte.render(frase + '...', False, cor)
        superficie.blit(imagem, imagem.get_rect(center=centro))

    @staticmethod
    def _coracao(superficie, x, y, preenchido):
        # Um pixel do sprite corresponde a 2x2 pixels na tela intermediaria.
        borda = (31, 17, 29, 255)
        vermelho = (240, 84, 90, 255)
        luz = (255, 171, 145, 255)
        vazio = (71, 85, 88, 255)
        for lin, linha in enumerate(CORACAO):
            for col, char in enumerate(linha):
                if char == '#':
                    pygame.draw.rect(superficie, borda, (x + col * 2 - 1, y + lin * 2 - 1, 4, 4))
        for lin, linha in enumerate(CORACAO):
            for col, char in enumerate(linha):
                if char == '#':
                    cor = (luz if (lin <= 2 and col in (2, 3)) else vermelho) if preenchido else vazio
                    pygame.draw.rect(superficie, cor, (x + col * 2, y + lin * 2, 2, 2))
        if not preenchido:
            # Centro escuro diferencia visualmente vida perdida de vida ativa.
            pygame.draw.rect(superficie, FUNDO, (x + 6, y + 4, 6, 4))

    @staticmethod
    def _icone_bioma(superficie, x, y, fase):
        fase %= 4
        verde = (131, 222, 118)
        marrom = (145, 98, 66)
        azul = (127, 218, 255)
        laranja = (255, 133, 71)
        if fase == 0:  # arvore
            pygame.draw.rect(superficie, marrom, (x + 5, y + 7, 3, 5))
            pygame.draw.rect(superficie, verde, (x + 3, y + 1, 6, 8))
            pygame.draw.rect(superficie, verde, (x + 1, y + 4, 10, 4))
            pygame.draw.rect(superficie, (76, 156, 80), (x + 8, y + 5, 3, 2))
        elif fase == 1:  # cacto
            pygame.draw.rect(superficie, verde, (x + 5, y + 1, 3, 11))
            pygame.draw.rect(superficie, verde, (x + 1, y + 4, 3, 6))
            pygame.draw.rect(superficie, verde, (x + 9, y + 3, 3, 6))
            pygame.draw.rect(superficie, verde, (x + 3, y + 8, 7, 2))
        elif fase == 2:  # cristal congelado
            pygame.draw.polygon(superficie, (49, 117, 173),
                                [(x + 6, y), (x + 12, y + 8), (x + 6, y + 12), (x, y + 8)])
            pygame.draw.polygon(superficie, azul,
                                [(x + 6, y + 1), (x + 9, y + 8), (x + 6, y + 11), (x + 3, y + 8)])
            pygame.draw.line(superficie, (235, 252, 255), (x + 6, y + 3), (x + 6, y + 8))
        else:  # vulcao
            pygame.draw.polygon(superficie, (111, 73, 75),
                                [(x, y + 12), (x + 5, y + 4), (x + 8, y + 5), (x + 13, y + 12)])
            pygame.draw.rect(superficie, (58, 41, 49), (x, y + 11, 13, 2))
            pygame.draw.polygon(superficie, laranja,
                                [(x + 5, y + 4), (x + 6, y + 1), (x + 7, y + 5),
                                 (x + 9, y + 4), (x + 8, y + 8), (x + 6, y + 10)])

    def desenhar(self, tela, nome, fase, vidas, pontos, mult_pontos=1, mult_velocidade=1,
                mensagem='', tempo_mensagem=0, mensagem_bioma='', tempo_mensagem_bioma=0, dt=0):
        fase = max(0, min(int(fase), len(BIOMAS) - 1))
        nome_bioma, destaque, detalhe = BIOMAS[fase]
        # O numero de coracoes desbloqueados e APENAS visual: o jogo continua
        # usando o atributo vidas original como fonte de verdade.
        quantidade = max(0, min(MAX_VIDAS, int(vidas)))
        self.coracoes_desbloqueados = max(self.coracoes_desbloqueados, quantidade)
        visiveis = max(1, min(MAX_VIDAS, self.coracoes_desbloqueados))

        marco = max(0, int(pontos)) // 100
        if marco > self.marco_pontos:
            self.pulso_pontos = 0.18
        self.marco_pontos = marco
        self.pulso_pontos = max(0.0, self.pulso_pontos - max(0.0, dt))

        layer = pygame.Surface((BASE_LARGURA, BASE_ALTURA), pygame.SRCALPHA)
        # Areas fixas em 900x400: esquerdo x16-200,
        # central x280-620, direito x700-886.
        self._placa(layer, (8, 8, 92, 38), (237, 116, 113))
        self._placa(layer, (140, 8, 170, 47), destaque)
        self._placa(layer, (350, 8, 92, 42), (242, 192, 98))

        self._escrever(layer, self.fonte_mini, '♥  VIDAS', CLARO, (54, 17))
        for indice in range(visiveis):
            inicio = 44 if visiveis == 1 else 33
            self._coracao(layer, inicio + indice * 23, 23, indice < quantidade)

        self._escrever(layer, self.fonte_mini, 'EXPLORADOR', MUTED, (225, 16))
        self._escrever(layer, self.fonte_normal, nome or 'JOGADOR', CLARO, (225, 27), 152)
        pygame.draw.line(layer, (80, 104, 97), (154, 35), (296, 35))
        self._icone_bioma(layer, 180, 38, fase)
        self._escrever(layer, self.fonte_mini, f'{fase + 1:02d} / {nome_bioma}', destaque, (236, 44))

        self._escrever(layer, self.fonte_mini, 'PONTOS', MUTED, (395, 17))
        pontos_texto = f'{max(0, int(pontos)):,}'.replace(',', '.')
        cor_pontos = (255, 246, 173) if self.pulso_pontos > 0 else CLARO
        # Reduz a fonte apenas em pontuacoes extremamente grandes.
        fonte = self.fonte_pontos if self.fonte_pontos.size(pontos_texto)[0] <= 78 else self.fonte_normal
        self._escrever(layer, fonte, pontos_texto, cor_pontos, (396, 33), 80)

        # Status temporario independente do nome, do bioma e dos avisos.
        bonus = []
        if mult_pontos != 1:
            bonus.append(f'PONTOS x{mult_pontos:g}')
        if mult_velocidade != 1:
            bonus.append(f'VELOCIDADE x{mult_velocidade:g}')
        if bonus:
            legenda = '  |  '.join(bonus)
            largura = min(210, max(100, self.fonte_mini.size(legenda)[0] + 24))
            self._placa(layer, (BASE_LARGURA // 2 - largura // 2, 60, largura, 16), (241, 192, 95))
            self._escrever(layer, self.fonte_mini, legenda, (255, 222, 140), (225, 68), largura - 12)

        avisos = []
        if tempo_mensagem > 0 and mensagem:
            avisos.append((mensagem.upper(), (248, 209, 119)))
        if tempo_mensagem_bioma > 0 and mensagem_bioma:
            avisos.append((mensagem_bioma.upper(), destaque))
        for i, (aviso, cor) in enumerate(avisos):
            largura = min(310, max(130, self.fonte_normal.size(aviso)[0] + 34))
            pos_y = 84 + i * 22
            self._placa(layer, (BASE_LARGURA // 2 - largura // 2, pos_y, largura, 19), cor)
            self._escrever(layer, self.fonte_normal, aviso, CLARO, (225, pos_y + 10), largura - 14)

        # Scale sem suavizacao: cada pixel do HUD ocupa um quadrado 2x2.
        tela.blit(pygame.transform.scale(layer, (LARGURA, ALTURA)), (0, 0))
