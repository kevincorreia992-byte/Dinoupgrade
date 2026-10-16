"""Musicas originais dos biomas e efeitos curtos do menu com volume independente."""
from array import array
from math import pi, sin
from pathlib import Path
import pygame
from .fases import PASTAS_FASES

BASE = Path(__file__).resolve().parent.parent / 'assets'
PASTA = BASE / 'musicas'
NOMES_BIOMAS = (
    'musica_floresta.ogg',
    'musica_deserto.ogg',
    'musica_gelo.ogg',
    'musica_vulcao.ogg',
)


class Audio:
    def __init__(self, preferencias=None):
        self.atual = None
        self.em_pausa = False
        self.disponivel = True
        self.preferencias = preferencias
        self.sons = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._criar_efeitos()
            self.aplicar_volumes()
        except (pygame.error, OSError) as erro:
            print('Audio indisponivel:', erro)
            self.disponivel = False

    def _criar_efeitos(self):
        """Dois bipes curtos 8-bit. Nenhum arquivo ou biblioteca extra."""
        formato = pygame.mixer.get_init()
        if not formato or formato[1] != -16:
            return  
        taxa, _, canais = formato
        for nome, frequencia in (('confirmar', 720), ('voltar', 420),
                                 ('pulo', 560), ('ataque', 870), ('colisao', 170),
                                 ('comprar', 920), ('habilidade', 1100), ('boss', 290)):
            amostras = array('h')
            duracao = int(taxa * 0.075)
            for i in range(duracao):
                decaimento = (1 - i / duracao) ** 2
                
                onda = 0.65 * sin(2 * pi * frequencia * i / taxa)
                onda += 0.35 * (1 if sin(2 * pi * frequencia * i / taxa) >= 0 else -1)
                valor = int(4400 * decaimento * onda)
                for _ in range(canais):
                    amostras.append(valor)
            self.sons[nome] = pygame.mixer.Sound(buffer=amostras.tobytes())

    def aplicar_volumes(self):
        if not self.disponivel:
            return
        opcoes = self.preferencias
        ligado = (opcoes is None or opcoes.audio_ativo)
        musica = (opcoes.volume_musica if opcoes else 0.35) if ligado else 0.0
        pygame.mixer.music.set_volume(musica)

    def efeito(self, nome='confirmar'):
        if not self.disponivel or nome not in self.sons:
            return
        opcoes = self.preferencias
        if opcoes is not None and not opcoes.audio_ativo:
            return
        volume = opcoes.volume_efeitos if opcoes else 0.60
        if volume <= 0:
            return
        canal = pygame.mixer.find_channel()
        if canal is not None:
            canal.set_volume(volume)
            canal.play(self.sons[nome])

    def tocar_caminho(self, caminho, repetir=True):
        if not self.disponivel:
            return
        caminho = Path(caminho)
        if not caminho.is_file():
            return
        chave = (str(caminho.resolve()), repetir)
        if self.atual == chave:
            return
        try:
            pygame.mixer.music.load(str(caminho))
            self.aplicar_volumes()
            pygame.mixer.music.play(-1 if repetir else 0, fade_ms=250)
            self.atual = chave
            self.em_pausa = False
        except (pygame.error, OSError) as erro:
            print(f'Falha ao tocar {caminho.name}: {erro}')

    def tocar(self, nome, repetir=True):
        self.tocar_caminho(PASTA / nome, repetir)

    def tocar_bioma(self, fase):
        fase = max(0, min(int(fase), len(PASTAS_FASES) - 1))
        pasta = BASE / 'Fases' / PASTAS_FASES[fase] / 'Musica'
        caminho = pasta / NOMES_BIOMAS[fase]
        if not caminho.is_file():
            caminho = PASTA / 'musicajogo.ogg'
        self.tocar_caminho(caminho, repetir=True)

    def pausar_musica(self):
        if self.disponivel and not self.em_pausa:
            pygame.mixer.music.pause()
            self.em_pausa = True

    def retomar_musica(self):
        if self.disponivel and self.em_pausa:
            pygame.mixer.music.unpause()
            self.em_pausa = False

    def parar(self):
        if self.disponivel:
            pygame.mixer.music.stop()
        self.atual = None
