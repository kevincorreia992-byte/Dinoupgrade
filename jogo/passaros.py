"""Animação estável dos pássaros normais de cada bioma."""
import random
import pygame
from .recursos import PASTA_ASSETS
from .fases import PASTAS_FASES
from .colisoes import criar_mascara
from .visibilidade import destacar_sprite, MARGEM





ESCALA_CORUJA = 1.20


def ajustar_tamanho_coruja(imagem):
    largura, altura = imagem.get_size()
    ampliada = pygame.transform.scale(
        imagem,
        (round(largura * ESCALA_CORUJA), round(altura * ESCALA_CORUJA)),
    )  
    quadro = pygame.Surface((largura, altura), pygame.SRCALPHA)
    quadro.blit(ampliada, (
        (largura - ampliada.get_width()) // 2,
        (altura - ampliada.get_height()) // 2,
    ))
    return quadro


ESPECIES = {
    0: ('passaro_marrom',),
    1: ('azul', 'cinza', 'roxo', 'vermelho'),
    2: ('coruja',),
    3: ('dragao',),
}


class Passaro:
    cache = {}

    @classmethod
    def carregar(cls, fase):
        chave = fase
        if chave in cls.cache:
            return cls.cache[chave]
        base = PASTA_ASSETS / 'Fases' / PASTAS_FASES[fase] / 'Passaros'
        pasta_anim = base / 'Animacoes'
        grupos = []
        for especie in ESPECIES.get(fase, ()):  
            caminhos = sorted((pasta_anim / especie).glob('frame_*.png'))
            frames = []
            for caminho in caminhos:
                try:
                    img = pygame.image.load(str(caminho)).convert_alpha()
                    if fase == 2 and especie == 'coruja':
                        img = ajustar_tamanho_coruja(img)
                    
                    img = pygame.transform.flip(img, True, False)
                    frames.append(img)
                except (pygame.error, OSError):
                    pass
            if frames:
                grupos.append((
                    especie, frames, [criar_mascara(frame) for frame in frames],
                    [frame if fase == 3 else destacar_sprite(frame, fase) for frame in frames],
                ))
        if not grupos:
            raise RuntimeError(f'Não há sprites de voo em {base}.')
        cls.cache[chave] = grupos
        return grupos

    def __init__(self, x, altura, animacao_inicial=0, fase=0):
        self.especie, self.frames, self.mascaras, self.frames_visuais = random.choice(self.carregar(fase))
        self.x = float(x)
        self.altura = float(altura)
        self.tempo_animacao = 0.0
        self.frame = int(animacao_inicial) % len(self.frames)
        self.fps_animacao = 11
        self.margem_visual = 0 if fase == 3 else MARGEM

    def imagem_atual(self):
        return self.frames[self.frame]

    def rect(self):
        
        return self.frames[0].get_rect(center=(round(self.x), round(self.altura)))

    def mascara_colisao(self):
        return self.mascaras[self.frame], self.rect()

    def atualizar(self, dt, velocidade):
        self.x -= velocidade * 1.2 * dt
        self.tempo_animacao += dt
        duracao = 1.0 / self.fps_animacao
        while self.tempo_animacao >= duracao:
            self.tempo_animacao -= duracao
            self.frame = (self.frame + 1) % len(self.frames)

    def desenhar(self, tela):
        ret = self.rect()
        tela.blit(self.frames_visuais[self.frame], (ret.x - self.margem_visual, ret.y - self.margem_visual))
