"""Quatro bosses, exatamente dois ataques animados por bioma.

Ataques em assets/AtaquesBoss/<Bioma>/<Nome>/frame_01..06.png.
O boss do Vulcão usa APENAS meteoro e pilar de fogo. O pilar é avisado
antes de causar dano e os padrões nunca aparecem simultaneamente.
"""
import math
from pathlib import Path
import pygame
from .config import CHAO_Y, LARGURA, fonte_sistema
from .modo_teste import MODO_TESTE

PASTA_ASSETS = Path(__file__).resolve().parent.parent / 'assets'
PASTAS = ('Floresta', 'Deserto', 'Gelo', 'Vulcao')
NOMES = ('GUARDIÃO DA FLORESTA', 'FARAÓ DAS DUNAS',
         'ESPÍRITO GLACIAL', 'TITÃ DO VULCÃO')
# O Vulcão tem a maior vida nos DOIS modos. O teste permanece rápido.
VIDAS_CHEFE = (1, 1, 1, 2) if MODO_TESTE else (4, 5, 6, 10)
# O fogo ataca com maior frequência que os outros bosses.
TEMPO_ATAQUE = (6.5, 6.0, 5.8, 3.2) if MODO_TESTE else (1.85, 1.70, 1.55, 1.10)
TEMPO_BLINDADO = (0.5, 0.5, 0.6, 0.7) if MODO_TESTE else (4.1, 3.8, 3.5, 2.9)
TEMPO_VULNERAVEL = (7.0, 7.0, 7.0, 7.0) if MODO_TESTE else (1.85, 1.70, 1.60, 1.6)
CORES = ((105, 179, 79), (216, 166, 85), (107, 213, 255), (246, 109, 64))
COR_ESCUDO = (73, 92, 103)

# Nomes exatos das pastas incluídas pelo usuário.
ATAQUES = (
    ('ataque1_folhas_cortantes', 'ataque2_raizes_espinhosas'),
    ('ataque1_tornado_de_areia', 'ataque2_bola_de_cacto'),
    ('ataque1_lanca_de_gelo', 'ataque2_espinhos_de_gelo'),
    ('ataque1_meteoro', 'ataque2_pilar_de_fogo'),
)
# As armadilhas surgem no solo, mas só atingem DEPOIS do aviso.
ARMADILHAS = {(0, 1), (2, 1), (3, 1)}
# Golpes pesados seguem fatais no modo normal e causam 1 dano no teste.
ATAQUES_PESADOS = {(0, 1), (1, 1), (2, 1), (3, 0)}
TAMANHOS_ATAQUES = ((37, 58), (68, 39), (67, 57), (56, 72))
# (para ataques 1 e 2 por bioma)
AVISO_ARMADILHA = 1.25 if MODO_TESTE else 1.12
DURACAO_ARMADILHA = 0.70
_CACHE_CHEFES = {}
_CACHE_TIROS = {}


def _carregar_chefes(fase):
    if fase not in _CACHE_CHEFES:
        pasta = PASTA_ASSETS / 'Chefes' / PASTAS[fase]
        frames = []
        for indice in range(1, 5):
            origem = pygame.image.load(str(pasta / f'frame_{indice:02d}.png')).convert_alpha()
            frames.append(pygame.transform.flip(origem, True, False))
        if len({f.get_size() for f in frames}) != 1:
            raise ValueError(f'Frames de boss inconsistentes: {pasta}')
        _CACHE_CHEFES[fase] = frames
    return _CACHE_CHEFES[fase]


def _carregar_tiro(fase, tipo):
    # tipo é o identificador da pasta (um dos dois ataques de cada boss).
    chave = (fase, tipo)
    if chave in _CACHE_TIROS:
        return _CACHE_TIROS[chave]
    pasta = PASTA_ASSETS / 'AtaquesBoss' / PASTAS[fase] / tipo
    idx = ATAQUES[fase].index(tipo)
    maior_lado = TAMANHOS_ATAQUES[fase][idx]
    frames = []
    for num in range(1, 7):
        original = pygame.image.load(str(pasta / f'frame_{num:02d}.png')).convert_alpha()
        escala = maior_lado / max(original.get_size())
        tam = (max(1, round(original.get_width() * escala)),
               max(1, round(original.get_height() * escala)))
        sprite = pygame.transform.scale(original, tam)  # pixel art: vizinho próximo
        # O meteoro enviado está orientado à direita; o boss mira à esquerda.
        if fase == 3 and idx == 0:
            sprite = pygame.transform.flip(sprite, True, False)
        frames.append(sprite)
    if len({f.get_size() for f in frames}) != 1:
        raise ValueError(f'Frames do ataque com tamanhos diferentes: {pasta}')
    masks = [pygame.mask.from_surface(f, 145) for f in frames]
    _CACHE_TIROS[chave] = (frames, masks)
    return frames, masks


def _carregar_fogo_jogador():
    chave = ('jogador', 'fogo')
    if chave in _CACHE_TIROS:
        return _CACHE_TIROS[chave]
    pasta = PASTA_ASSETS / 'Tiros' / 'Dinossauro'
    frames = []
    for num in range(1, 7):
        origem = pygame.image.load(str(pasta / f'fogo_{num:02d}.png')).convert_alpha()
        escala = 39 / max(origem.get_size())
        tam = (max(1, round(origem.get_width() * escala)),
               max(1, round(origem.get_height() * escala)))
        frames.append(pygame.transform.scale(origem, tam))
    masks = [pygame.mask.from_surface(frame, 120) for frame in frames]
    _CACHE_TIROS[chave] = (frames, masks)
    return frames, masks


class Projetil:
    def __init__(self, x, y, vx, vy, especie, aliado=False, tipo=None):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.especie = int(especie)
        self.aliado = bool(aliado)
        self.tempo = 0.0
        self.tipo = tipo if tipo is not None else (None if aliado else ATAQUES[self.especie][0])
        self.indice_ataque = (-1 if aliado else ATAQUES[self.especie].index(self.tipo))
        self.armadilha = (not self.aliado and (self.especie, self.indice_ataque) in ARMADILHAS)
        self.pesado = (not self.aliado and (self.especie, self.indice_ataque) in ATAQUES_PESADOS)
        self.frames, self.mascaras = (_carregar_fogo_jogador() if aliado
                                      else _carregar_tiro(self.especie, self.tipo))
        self.frame = 0
        self.imagem = self.frames[0]
        self.mascara = self.mascaras[0]

    def esta_perigoso(self):
        if not self.armadilha:
            return True
        return AVISO_ARMADILHA <= self.tempo < AVISO_ARMADILHA + DURACAO_ARMADILHA

    def atualizar(self, dt):
        self.tempo += dt
        if not self.armadilha:
            self.x += self.vx * dt
            self.y += self.vy * dt
            self.frame = int(self.tempo * 11) % len(self.frames)
        elif self.tempo < AVISO_ARMADILHA:
            self.frame = 0
        else:
            progresso = max(0, self.tempo - AVISO_ARMADILHA) / DURACAO_ARMADILHA
            self.frame = min(len(self.frames) - 1, int(progresso * len(self.frames)))
        self.imagem = self.frames[self.frame]
        self.mascara = self.mascaras[self.frame]

    def _ret_sprite(self):
        if self.armadilha:
            return self.imagem.get_rect(midbottom=(round(self.x), CHAO_Y))
        return self.imagem.get_rect(center=(round(self.x), round(self.y)))

    def retangulo(self):
        if self.armadilha and not self.esta_perigoso():
            return pygame.Rect(-200, -200, 1, 1)  # aviso não colide
        rect = self._ret_sprite()
        rect.inflate_ip(-min(max(2, round(rect.width * .12)), rect.width - 1),
                        -min(max(2, round(rect.height * .10)), rect.height - 1))
        return rect

    def mascara_colisao(self):
        if self.armadilha and not self.esta_perigoso():
            return pygame.mask.Mask((1, 1)), pygame.Rect(-200, -200, 1, 1)
        return self.mascara, self._ret_sprite()

    def fora(self):
        if self.armadilha:
            return self.tempo >= AVISO_ARMADILHA + DURACAO_ARMADILHA
        margem = 75
        return self.x < -margem or self.x > LARGURA + margem or self.y < -margem or self.y > CHAO_Y + margem

    def desenhar(self, tela):
        ret = self._ret_sprite()
        if self.armadilha and not self.esta_perigoso():
            if self.tempo < AVISO_ARMADILHA:
                # Uma marca no chão pulsante e sem hitbox, para o jogador pular.
                cor = (255, 222, 89) if int(self.tempo * 5) % 2 else (255, 134, 70)
                pygame.draw.rect(tela, (44, 33, 24), (round(self.x) - 35, CHAO_Y - 6, 70, 7))
                pygame.draw.rect(tela, cor, (round(self.x) - 31, CHAO_Y - 5, 62, 4))
                pygame.draw.polygon(tela, cor, [(round(self.x), CHAO_Y - 27),
                                                (round(self.x) - 7, CHAO_Y - 12),
                                                (round(self.x) + 7, CHAO_Y - 12)])
            return
        tela.blit(self.imagem, ret)
        if self.pesado and not self.aliado and int(self.tempo * 6) % 2 == 0:
            placa = pygame.Rect(ret.centerx - 6, ret.top - 15, 12, 12)
            pygame.draw.rect(tela, (36, 22, 21), placa)
            pygame.draw.rect(tela, (250, 199, 80), placa, 2)
            pygame.draw.rect(tela, (255, 246, 206), (placa.centerx - 1, placa.y + 2, 2, 5))
            pygame.draw.rect(tela, (255, 246, 206), (placa.centerx - 1, placa.y + 9, 2, 2))


class Chefe:
    def __init__(self, fase):
        self.fase = int(fase)
        self.vida_max = VIDAS_CHEFE[self.fase]
        self.vida = self.vida_max
        self.x_base = 710
        self.y_base = CHAO_Y + 3
        self.tempo = 0.0
        self.contador_ataques = 0
        self.proximo_ataque = 2.6 if MODO_TESTE else 1.4
        self.projeteis = []
        self.piscar = 0.0
        self.frames = _carregar_chefes(self.fase)
        self.frame = 0
        self.estado = 'blindado'
        self.tempo_estado = TEMPO_BLINDADO[self.fase]
        self.dano_nesta_abertura = False
        self.animacao_ataque = 0.0

    def rect_sprite(self):
        recuo = round(abs(math.sin(self.tempo * 2.3)) * 22)
        flutuar = round(math.sin(self.tempo * 2.7) * 2)
        return self.frames[self.frame].get_rect(midbottom=(self.x_base + recuo, self.y_base + flutuar))

    def retangulo(self):
        area = self.frames[self.frame].get_bounding_rect(min_alpha=125)
        if area.width <= 0 or area.height <= 0:
            area = self.frames[self.frame].get_rect()
        area.inflate_ip(-2 * min(18, area.width // 8), -2 * min(13, area.height // 10))
        return area.move(self.rect_sprite().topleft)

    def pode_receber_dano(self):
        return self.estado == 'vulneravel' and not self.dano_nesta_abertura and self.vida > 0

    def pode_disparar_contra_chefe(self):
        return self.pode_receber_dano()

    def mensagem_estado(self):
        return 'ABERTURA! ATAQUE O CHEFE!' if self.pode_receber_dano() else 'CHEFE BLINDADO - DESVIE DOS ATAQUES!'

    def receber_dano(self, dano=1.0):
        if not self.pode_receber_dano():
            return False
        self.vida = max(0.0, self.vida - max(0.0, float(dano)))
        self.piscar = 0.22
        self.dano_nesta_abertura = True
        self.estado = 'blindado'
        self.tempo_estado = TEMPO_BLINDADO[self.fase]
        return True

    def _disparar(self, y, velocidade, tipo, desvio=0):
        fator = 0.38 if MODO_TESTE else 1.0
        self.projeteis.append(Projetil(self.retangulo().left - 16, y, -velocidade * fator,
                                       desvio * fator, self.fase, tipo=tipo))

    def atacar(self):
        self.contador_ataques += 1
        rodada = self.contador_ataques
        idx = (rodada - 1) % 2
        tipo = ATAQUES[self.fase][idx]
        self.animacao_ataque = 0.24
        if (self.fase, idx) in ARMADILHAS:
            # Nasce perto do jogador, com alerta e tempo para saltar.
            self.projeteis.append(Projetil(118, CHAO_Y, 0, 0, self.fase, tipo=tipo))
        elif self.fase == 0:
            self._disparar(CHAO_Y - (95 if rodada % 4 == 3 else 22), 285, tipo)
        elif self.fase == 1:
            # Tornado alto: passar por baixo; cacto baixo: saltar por cima.
            altura = CHAO_Y - (98 if idx == 0 else 19)
            self._disparar(altura, 306, tipo)
        elif self.fase == 2:
            self._disparar(CHAO_Y - 22, 324, tipo)
        else:
            # APENAS meteoro e pilar de fogo. Nunca há uma rajada dupla.
            altura = CHAO_Y - (96 if rodada % 4 == 3 else 24)
            self._disparar(altura, 368, tipo)
        return idx

    def _atualizar_estado(self, dt):
        self.tempo_estado -= dt
        if self.tempo_estado > 0:
            return
        if self.estado == 'blindado':
            self.estado = 'vulneravel'
            self.tempo_estado = TEMPO_VULNERAVEL[self.fase]
            self.dano_nesta_abertura = False
        else:
            self.estado = 'blindado'
            self.tempo_estado = TEMPO_BLINDADO[self.fase]
            self.dano_nesta_abertura = False

    def atualizar(self, dt):
        self.tempo += dt
        self.piscar = max(0.0, self.piscar - dt)
        self.animacao_ataque = max(0.0, self.animacao_ataque - dt)
        self.proximo_ataque -= dt
        self._atualizar_estado(dt)
        if self.proximo_ataque <= 0:
            if self.fase == 3 and self.projeteis:
                # Nunca sobrepor um meteoro à armadilha de chão (nem vice-versa):
                # esse era o padrão que impedia pular ou permanecer no solo.
                self.proximo_ataque = 0.16
            else:
                indice = self.atacar()
                ritmo = TEMPO_ATAQUE[self.fase] * (0.92 if self.estado == 'vulneravel' else 1.0)
                if (self.fase, indice) in ARMADILHAS:
                    # Não lançar outro projétil antes de a armadilha desaparecer.
                    ritmo = max(ritmo, AVISO_ARMADILHA + DURACAO_ARMADILHA + 0.40)
                self.proximo_ataque += ritmo
        if self.animacao_ataque > 0:
            self.frame = 3
        elif self.proximo_ataque <= 0.33:
            self.frame = 2
        else:
            self.frame = int(self.tempo * 3.2) % 2
        for projetil in self.projeteis[:]:
            projetil.atualizar(dt)
            if projetil.fora():
                self.projeteis.remove(projetil)

    def desenhar(self, tela):
        ret = self.rect_sprite()
        tela.blit(self.frames[self.frame], ret)
        cor = CORES[self.fase] if self.estado == 'vulneravel' else COR_ESCUDO
        simbolo = ((ret.centerx, ret.top - 13), (ret.centerx + 6, ret.top - 7),
                   (ret.centerx, ret.top - 1), (ret.centerx - 6, ret.top - 7))
        pygame.draw.polygon(tela, (19, 29, 36), simbolo)
        pygame.draw.rect(tela, cor, (ret.centerx - 2, ret.top - 9, 4, 5))
        for proj in self.projeteis:
            proj.desenhar(tela)
        if self.piscar > 0 and int(self.piscar * 35) % 2:
            pygame.draw.rect(tela, (255, 248, 236), (ret.centerx - 5, ret.top - 17, 10, 3))

    def _barra_vida(self, tela):
        px, py, largura = 255, 135, 390
        pygame.draw.rect(tela, (18, 26, 30), (px - 5, py - 6, largura + 10, 29))
        pygame.draw.rect(tela, (221, 187, 127), (px - 3, py - 3, largura + 6, 20), 2)
        pygame.draw.rect(tela, (71, 63, 62), (px, py, largura, 14))
        if self.vida > 0:
            pygame.draw.rect(tela, CORES[self.fase],
                             (px + 1, py + 1, round((largura - 2) * self.vida / self.vida_max), 12))
        fonte = fonte_sistema('consolas,couriernew,monospace', 13)
        vida_legenda = (str(int(self.vida)) if self.vida == int(self.vida)
                        else f'{self.vida:.1f}')
        legenda = fonte.render(f'{NOMES[self.fase]}   {vida_legenda}/{self.vida_max}', True, (249, 243, 220))
        tela.blit(legenda, legenda.get_rect(center=(450, 124)))

    def _barra_abertura(self, tela):
        px, py, largura = 300, 177, 300
        pygame.draw.rect(tela, (12, 20, 24), (px - 4, py - 4, largura + 8, 20))
        pygame.draw.rect(tela, (211, 178, 116), (px - 2, py - 2, largura + 4, 16), 2)
        pygame.draw.rect(tela, (57, 60, 68), (px, py, largura, 12))
        total = TEMPO_VULNERAVEL[self.fase] if self.estado == 'vulneravel' else TEMPO_BLINDADO[self.fase]
        frac = max(0.0, min(1.0, self.tempo_estado / max(0.1, total)))
        cor = CORES[self.fase] if self.estado == 'vulneravel' else COR_ESCUDO
        pygame.draw.rect(tela, cor, (px, py, round(largura * frac), 12))
        fonte = fonte_sistema('consolas,couriernew,monospace', 12)
        txt = 'ABERTURA DE ATAQUE' if self.estado == 'vulneravel' else 'ESCUDO RECARREGANDO'
        legenda = fonte.render(txt, False, (245, 236, 205))
        tela.blit(legenda, legenda.get_rect(center=(450, 168)))
        if any(proj.pesado for proj in self.projeteis):
            aviso_pesado = ('!  ATAQUE PESADO: -1 VIDA (TESTE)  !' if MODO_TESTE
                            else '!  ATAQUE PESADO: GAME OVER AO TOCAR  !')
            alerta = fonte.render(aviso_pesado, False, (255, 208, 109))
            box = alerta.get_rect(center=(450, 269))
            pygame.draw.rect(tela, (75, 27, 28), box.inflate(20, 11))
            pygame.draw.rect(tela, (247, 161, 70), box.inflate(20, 11), 2)
            tela.blit(alerta, box)
