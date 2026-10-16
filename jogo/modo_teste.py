"""Modo de teste curto do Dino Upgrade.

Ativado somente quando o jogo recebe `--teste` na linha de comando.
NÃO muda os parâmetros do jogo normal (`python main.py`).
"""
import sys

MODO_TESTE = '--teste' in sys.argv
PONTOS_POR_CHEFE_TESTE = 3000
VIDAS_INICIAIS_TESTE = 2
PRIMEIRA_CARTA_TESTE = 4200
INTERVALO_CARTA_TESTE = 8000
MULTIPLICADOR_PONTOS_TESTE = 60.0  
MULTIPLICADOR_VELOCIDADE_TESTE = 0.45
TEMPO_SPAWN_INICIAL_TESTE = 3.5
INTERVALO_SPAWN_TESTE = (7.0, 8.5)  
GERAR_OBSTACULOS_TESTE = False  
INVENCIBILIDADE_TESTE = 5.0


def pontos_para_o_proximo_chefe(pontos_bioma, fase):
    """Contagem regressiva para a próxima luta, só exibida no HUD de teste."""
    return max(0, (fase + 1) * PONTOS_POR_CHEFE_TESTE - int(pontos_bioma))
