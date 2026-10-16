"""Partida Dino Upgrade: cartas, biomas, chefes e cosméticos."""
import random
import pygame
from .dinossauro import Dinossauro
from .obstaculos import novo_obstaculo
from .cartas import Cartas
from .hud import Hud
from .colisoes import colidir
from .fases import FASES, LIMITE_POR_FASE
from .chefes import Chefe, Projetil
from .config import MAX_VIDAS
from .modo_teste import (MODO_TESTE, VIDAS_INICIAIS_TESTE,
                        PRIMEIRA_CARTA_TESTE, INTERVALO_CARTA_TESTE,
                        MULTIPLICADOR_PONTOS_TESTE, MULTIPLICADOR_VELOCIDADE_TESTE,
                        TEMPO_SPAWN_INICIAL_TESTE, INTERVALO_SPAWN_TESTE,
                        INVENCIBILIDADE_TESTE, GERAR_OBSTACULOS_TESTE)


class Partida:
    def __init__(self, loja=None):
        self.cartas_sistema = Cartas()
        self.loja = loja
        self.reiniciar()

    def reiniciar(self):
        self.hud = Hud()
        self.dino = Dinossauro(self.loja.equipados.get('dino') if self.loja is not None else None)
        self.fase = 0
        self.obstaculos = []
        self.pontos = 0.0
        self.pontos_bioma = 0.0
        self.moedas_por_pontos = 0  
        self.vidas = VIDAS_INICIAIS_TESTE if MODO_TESTE else 1
        self.mult_pontos = 1
        self.mult_velocidade = 1
        self.proxima_carta = PRIMEIRA_CARTA_TESTE if MODO_TESTE else 1000
        self.cartas_atuais = []
        self.boa_proxima = False
        self.ruim_proxima = False
        self.tempo_spawn = TEMPO_SPAWN_INICIAL_TESTE if MODO_TESTE else 1.0
        self.invencivel = 0.0
        self.mensagem = ''
        self.tempo_mensagem = 0.0
        self.biomas_visitados = {0}
        self.mensagem_bioma = ''
        self.tempo_mensagem_bioma = 0.0
        self.chefe = None
        self.tiros = []
        self.tempo_tiro = 0.0
        self.recompensa_final = 0
        self.tempo_limpando = 0.0
        self.som_pendente = None

    def ativar_habilidade(self, identificador):
        """Ativação das habilidades compradas: Q (vida) e E (limpeza).

        Não consome estoque quando a ação seria inválida (por exemplo, vida
        cheia). O efeito de limpeza remove também projéteis hostis do boss,
        mas nunca remove o boss, o personagem ou os elementos decorativos.
        """
        if self.loja is None:
            return False, 'LOJA INDISPONIVEL'
        if identificador not in ('vida_extra', 'limpar_cenario'):
            return False, 'HABILIDADE INVALIDA'
        if self.loja.quantidade_habilidade(identificador) <= 0:
            self.mensagem = 'COMPRE ESSA HABILIDADE NA LOJA'
            self.tempo_mensagem = 1.5
            return False, self.mensagem
        if identificador == 'vida_extra':
            if self.vidas >= MAX_VIDAS or self.vidas <= 0:
                self.mensagem = 'VIDAS JA ESTAO NO LIMITE'
                self.tempo_mensagem = 1.5
                return False, self.mensagem
            if not self.loja.consumir_habilidade(identificador):
                return False, 'ESTOQUE INDISPONIVEL'
            self.vidas = min(MAX_VIDAS, self.vidas + 1)
            self.mensagem = 'VIDA EXTRA ATIVADA!'
        else:
            perigos = len(self.obstaculos)
            if self.chefe is not None:
                perigos += len(self.chefe.projeteis)
            if perigos == 0:
                self.mensagem = 'NENHUM PERIGO PARA LIMPAR'
                self.tempo_mensagem = 1.5
                return False, self.mensagem
            if not self.loja.consumir_habilidade(identificador):
                return False, 'ESTOQUE INDISPONIVEL'
            self.obstaculos.clear()
            if self.chefe is not None:
                self.chefe.projeteis.clear()
            self.tempo_limpando = 0.45
            self.mensagem = 'CENARIO LIMPO!'
        self.tempo_mensagem = 1.8
        return True, self.mensagem

    def velocidade(self):
        velocidade_base = 290 + min(self.pontos / 14, 230)
        return velocidade_base * (MULTIPLICADOR_VELOCIDADE_TESTE if MODO_TESTE else 1.0) * self.mult_velocidade

    def _tempo(self, dt):
        self.invencivel = max(0.0, self.invencivel - dt)
        self.tempo_mensagem = max(0.0, self.tempo_mensagem - dt)
        self.tempo_mensagem_bioma = max(0.0, self.tempo_mensagem_bioma - dt)
        self.tempo_limpando = max(0.0, self.tempo_limpando - dt)

    def _ferir(self):
        if self.invencivel > 0:
            return False
        self.vidas -= 1
        self.som_pendente = 'colisao'
        self.invencivel = INVENCIBILIDADE_TESTE if MODO_TESTE else 1.5
        return self.vidas <= 0

    def _recompensa_fase(self):
        if self.loja is not None:
            self.loja.adicionar(5)
        self.mensagem = '+5 MOEDAS - BOSS LIBERADO!'
        self.tempo_mensagem = 2.2

    def _iniciar_chefe(self):
        self.chefe = Chefe(self.fase)
        self.obstaculos.clear()
        self.tiros.clear()
        self.tempo_tiro = 0.0
        self.invencivel = max(self.invencivel, INVENCIBILIDADE_TESTE if MODO_TESTE else 1.0)
        self._recompensa_fase()
        return 'boss'

    def atualizar(self, dt):
        self.dino.atualizar(dt)
        ganho_base = dt * (42 + min(self.pontos / 140, 35))
        
        
        ganho = ganho_base * (MULTIPLICADOR_PONTOS_TESTE if MODO_TESTE else 1.0)
        
        self.pontos += ganho * self.mult_pontos
        self.pontos_bioma += ganho if self.mult_pontos == 2 else ganho * self.mult_pontos
        
        
        marcos = int(self.pontos // 1000)
        if marcos > self.moedas_por_pontos:
            quantidade = marcos - self.moedas_por_pontos
            self.moedas_por_pontos = marcos
            if self.loja is not None:
                self.loja.adicionar(quantidade)
            self.mensagem = f'+{quantidade} MOEDA' + ('S' if quantidade != 1 else '') + ' POR PONTOS!'
            self.tempo_mensagem = 1.65
        self._tempo(dt)

        
        if self.pontos_bioma >= (self.fase + 1) * LIMITE_POR_FASE:
            return self._iniciar_chefe()

        if self.pontos >= self.proxima_carta:
            self.cartas_atuais = self.cartas_sistema.sortear(self.boa_proxima, self.ruim_proxima)
            self.boa_proxima = self.ruim_proxima = False
            self.mult_pontos = self.mult_velocidade = 1
            return 'cartas'

        
        
        
        if MODO_TESTE and not GERAR_OBSTACULOS_TESTE:
            self.obstaculos.clear()
        else:
            self.tempo_spawn -= dt
            if self.tempo_spawn <= 0:
                self.obstaculos.append(novo_obstaculo(self.fase))
                self.tempo_spawn = (random.uniform(*INTERVALO_SPAWN_TESTE) if MODO_TESTE else
                                    random.uniform(1.0, 1.5) * (290 / self.velocidade()) + 0.25)
        for obj in self.obstaculos[:]:
            obj.atualizar(dt, self.velocidade())
            if obj.rect().right < 0:
                self.obstaculos.remove(obj)
                continue
            if self.invencivel <= 0 and colidir(self.dino, obj):
                self.obstaculos.remove(obj)
                if self._ferir():
                    return 'morte'
                break
        return 'jogando'

    def atirar(self):
        """Tiro do jogador: só funciona quando o chefe abre a janela de vulnerabilidade."""
        if self.chefe is None or self.tempo_tiro > 0:
            return False
        if not self.chefe.pode_disparar_contra_chefe():
            self.mensagem = self.chefe.mensagem_estado()
            self.tempo_mensagem = max(self.tempo_mensagem, 0.9)
            self.tempo_tiro = 0.12
            return False
        ret = self.dino.rect
        self.tiros.append(Projetil(ret.right + 8, ret.centery - 4, 525, 0, self.fase, aliado=True))
        self.dino.disparar_fogo()
        self.tempo_tiro = 0.34
        return True

    def _colisao_projetil_dino(self, projetil):
        mascara, rect_dino = self.dino.mascara_colisao()
        r = projetil.retangulo()
        if not rect_dino.colliderect(r):
            return False
        mascara_proj, ret_imagem = projetil.mascara_colisao()
        return mascara.overlap(mascara_proj,
                              (ret_imagem.left - rect_dino.left,
                               ret_imagem.top - rect_dino.top)) is not None

    def atualizar_boss(self, dt):
        if self.chefe is None:
            return 'jogando'
        self.dino.atualizar(dt)
        self._tempo(dt)
        self.tempo_tiro = max(0.0, self.tempo_tiro - dt)
        ataques_antes = self.chefe.contador_ataques
        self.chefe.atualizar(dt)
        if self.chefe.contador_ataques != ataques_antes:
            self.som_pendente = 'boss'

        
        if self.chefe.pode_disparar_contra_chefe():
            self.mensagem = self.chefe.mensagem_estado()
            self.tempo_mensagem = max(self.tempo_mensagem, 0.2)

        for tiro in self.tiros[:]:
            tiro.atualizar(dt)
            if tiro.fora():
                self.tiros.remove(tiro)
                continue
            if tiro.retangulo().colliderect(self.chefe.retangulo()):
                self.tiros.remove(tiro)
                dano = 1.5 if self.loja is not None and self.loja.arma_antiboss else 1.0
                if self.chefe.receber_dano(dano):
                    self.mensagem = 'ARMA ANTIBOSS +50%!' if dano > 1 else 'BOSS ATINGIDO!'
                    self.tempo_mensagem = 0.85

        if self.chefe.vida <= 0:
            self.chefe = None
            self.tiros.clear()
            self.fase += 1
            if self.fase >= len(FASES):
                self.recompensa_final = 15
                if self.loja is not None:
                    self.loja.adicionar(self.recompensa_final)
                return 'vitoria'
            self.mensagem_bioma = f'NOVO BIOMA: {FASES[self.fase].upper()}!'
            self.tempo_mensagem_bioma = 3.0
            self.biomas_visitados.add(self.fase)
            self.obstaculos.clear()
            self.tempo_spawn = TEMPO_SPAWN_INICIAL_TESTE if MODO_TESTE else 1.5
            self.invencivel = max(INVENCIBILIDADE_TESTE if MODO_TESTE else 1.4, self.invencivel)
            self.mensagem = ''
            self.tempo_mensagem = 0
            return 'jogando'

        for ataque in self.chefe.projeteis[:]:
            
            
            
            if ataque.pesado and not MODO_TESTE:
                if self._colisao_projetil_dino(ataque):
                    self.vidas = 0
                    self.som_pendente = 'colisao'
                    self.chefe.projeteis.remove(ataque)
                    return 'morte'
            elif self.invencivel <= 0 and self._colisao_projetil_dino(ataque):
                self.chefe.projeteis.remove(ataque)
                if self._ferir():
                    return 'morte'
                break
        return 'boss'

    def escolher(self, indice):
        self.cartas_sistema.aplicar(self.cartas_atuais[indice], self)
        self.proxima_carta += INTERVALO_CARTA_TESTE if MODO_TESTE else 3000
        self.obstaculos.clear()
        self.tempo_spawn = TEMPO_SPAWN_INICIAL_TESTE if MODO_TESTE else 1.5
        self.invencivel = INVENCIBILIDADE_TESTE if MODO_TESTE else 1.0

    def desenhar(self, tela, nome, dt=0):
        if self.loja is not None:
            self.dino.definir_acessorio(self.loja.equipados.get('dino'))
        self.dino.desenhar(tela)
        for obj in self.obstaculos:
            obj.desenhar(tela)
        if self.chefe is not None:
            self.chefe.desenhar(tela)
            for tiro in self.tiros:
                tiro.desenhar(tela)
        if self.tempo_limpando > 0:
            
            for faixa in range(0, 900, 42):
                intensidade = int(110 * self.tempo_limpando / 0.45)
                camada = pygame.Surface((18, 345), pygame.SRCALPHA)
                camada.fill((144, 236, 225, intensidade))
                tela.blit(camada, (faixa + int((0.45 - self.tempo_limpando) * 65), 0))
        if self.loja is not None:
            fonte_habilidade = pygame.font.SysFont('consolas,dejavusansmono,monospace', 14, bold=True)
            info = (('Q', 'VIDA', 'vida_extra'), ('E', 'LIMPAR', 'limpar_cenario'))
            for i, (tecla, descricao, chave) in enumerate(info):
                x, y = 12 + 137 * i, 361
                area = pygame.Rect(x, y, 130, 25)
                pygame.draw.rect(tela, (12, 28, 34), area)
                pygame.draw.rect(tela, (214, 183, 119), area, 2)
                qtd = self.loja.quantidade_habilidade(chave)
                cor = (255, 230, 168) if qtd else (135, 153, 150)
                msg = fonte_habilidade.render(f'{tecla} {descricao} x{qtd}', True, cor)
                tela.blit(msg, msg.get_rect(center=area.center))
        self.hud.desenhar(
            tela, nome, min(self.fase, len(FASES) - 1), self.vidas, self.pontos,
            self.mult_pontos, self.mult_velocidade,
            self.mensagem if self.chefe is None else '',
            self.tempo_mensagem if self.chefe is None else 0,
            self.mensagem_bioma, self.tempo_mensagem_bioma, dt,
        )
        if self.chefe is not None:
            
            self.chefe._barra_vida(tela)
            self.chefe._barra_abertura(tela)
            if self.tempo_mensagem > 0 and self.mensagem:
                fonte_aviso = pygame.font.SysFont('consolas,dejavusansmono,monospace', 13, bold=True)
                aviso = fonte_aviso.render(self.mensagem.upper(), True, (255, 228, 156))
                r_aviso = aviso.get_rect(center=(450, 223))
                painel_aviso = r_aviso.inflate(20, 10)
                pygame.draw.rect(tela, (18, 34, 40), painel_aviso)
                pygame.draw.rect(tela, (193, 160, 95), painel_aviso, 2)
                tela.blit(aviso, r_aviso)
            fonte = pygame.font.SysFont('consolas,couriernew,monospace', 12, bold=True)
            linha = fonte.render('F / J: ATACAR NA ABERTURA     ESPACO / CIMA: PULAR', False, (250, 236, 188))
            r = linha.get_rect(center=(450, 388))
            pygame.draw.rect(tela, (15, 29, 36), r.inflate(15, 8))
            tela.blit(linha, r)
