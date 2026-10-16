"""Obstáculos com tamanhos proporcionais e inimigos por bioma."""
from pathlib import Path
import random
import pygame
from .config import CHAO_Y, LARGURA
from .recursos import PASTA_ASSETS
from .fases import PASTAS_FASES
from .passaros import Passaro
from .colisoes import criar_mascara
from .visibilidade import destacar_sprite, MARGEM


TAMANHOS = {
    'pedra': (32, 58), 'rocha': (39, 61),
    'bloco_gelo': (39, 50), 'bloco': (47, 55),
    'cacto': (58, 43), 'cogumelo': (35, 39), 'toco': (47, 52),
    'tronco': (28, 76), 'arbusto': (31, 66), 'cristais': (55, 47),
    'estalactites': (36, 62), 'neve': (29, 59), 'chamas': (34, 83),
    'lava': (29, 52), 'tartaruga': (43, 62), 'escorpiao': (43, 59),
    'lobo': (50, 70), 'dino': (55, 69),
}


def tamanho_para(nome, inimigo=False):
    nome = nome.lower()
    for chave, tamanho in TAMANHOS.items():
        if chave in nome:
            return tamanho
    return (48, 66) if inimigo else (45, 60)


def preparar_sprite(caminho, inimigo=False):
    original = pygame.image.load(str(caminho)).convert_alpha()
    area = original.get_bounding_rect(min_alpha=30)
    if 'dino_vermelho' in caminho.stem.lower():
        
        
        corpo = criar_mascara(original, caminho.stem)
        retangulos = corpo.get_bounding_rects()
        if retangulos:
            area = retangulos[0]
    if area.width < 3 or area.height < 3:
        return None
    original = original.subsurface(area).copy()
    
    if 'estalactites' in caminho.stem.lower():
        original = pygame.transform.flip(original, False, True)
    altura, largura = tamanho_para(caminho.stem, inimigo)
    escala = min(altura / original.get_height(), largura / original.get_width())
    tamanho = (max(1, round(original.get_width() * escala)),
               max(1, round(original.get_height() * escala)))
    return pygame.transform.scale(original, tamanho)


class Obstaculo:
    cache = {}
    cache_mascaras = {}
    cache_desenhos = {}

    @classmethod
    def _imagens(cls, fase, inimigo):
        chave = (fase, inimigo)
        if chave in cls.cache:
            return cls.cache[chave]
        base = PASTA_ASSETS / 'Fases' / PASTAS_FASES[fase]
        pasta = base / ('Inimigos' if inimigo else 'Obstaculos')
        arquivos = sorted(pasta.glob('*.png')) if pasta.exists() else []
        
        arquivos = [a for a in arquivos if not a.stem.lower().startswith(('tile_', 'sheet_', 'sprite_'))]
        
        if inimigo:
            
            if fase == 0:
                arquivos = [a for a in arquivos if 'tartaruga' not in a.stem.lower()]
            arquivos = [a for a in arquivos if not any(
                palavra in a.stem.lower() for palavra in ('passaro', 'coruja', 'dragao', 'ptero', 'voador'))]
        if not arquivos and not inimigo:
            arquivos = sorted((PASTA_ASSETS / 'Obstaculos').glob('obstaculo_*.png'))
        imagens = []
        for arquivo in arquivos:
            try:
                imagem = preparar_sprite(arquivo, inimigo)
                if imagem is not None:
                    imagens.append(imagem)
                    cls.cache_mascaras[id(imagem)] = criar_mascara(imagem, arquivo.stem)
                    cls.cache_desenhos[id(imagem)] = destacar_sprite(imagem, fase)
            except (pygame.error, OSError, ValueError):
                continue
        cls.cache[chave] = imagens
        return imagens

    def __init__(self, x, fase=0, inimigo=False):
        imagens = self._imagens(fase, inimigo)
        if not imagens:
            imagens = self._imagens(fase, False)
        if not imagens:
            raise RuntimeError(f'Sem obstáculos para a fase {fase}')
        self.imagem = random.choice(imagens)
        self.mascara = self.cache_mascaras[id(self.imagem)]
        self.x = float(x)

    def rect(self):
        return self.imagem.get_rect(midbottom=(round(self.x), CHAO_Y))

    def mascara_colisao(self):
        return self.mascara, self.rect()

    def atualizar(self, dt, velocidade):
        self.x -= velocidade * dt

    def desenhar(self, tela):
        ret = self.rect()
        tela.blit(self.cache_desenhos[id(self.imagem)], (ret.x - MARGEM, ret.y - MARGEM))


Rocha = Obstaculo


def novo_obstaculo(fase=0):
    if random.random() < 0.34:
        altura = random.choice([CHAO_Y - 65, CHAO_Y - 95, CHAO_Y - 125])
        return Passaro(LARGURA + 80, altura, 0, fase)
    
    usar_inimigo = fase not in (2, 3) and bool(Obstaculo._imagens(fase, True)) and random.random() < 0.27
    return Obstaculo(LARGURA + 80, fase, inimigo=usar_inimigo)
