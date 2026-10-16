"""Biomas em ordem fixa. Cada chefe aparece a cada 5.000 pontos de progressão.
A fase seguinte só é liberada após derrotá-lo em partida.py.
"""

from .modo_teste import MODO_TESTE, PONTOS_POR_CHEFE_TESTE

FASES = ("Floresta", "Deserto", "Gelo", "Vulcao")
PASTAS_FASES = ("02_Floresta", "01_Deserto", "03_Gelo", "04_Vulcao")
LIMITE_POR_FASE = PONTOS_POR_CHEFE_TESTE if MODO_TESTE else 5000


def indice_fase(pontos):
    """Consulta legada por pontos; nao decide a fase durante o combate."""
    etapa = max(0, int(pontos // LIMITE_POR_FASE))
    return min(etapa, len(FASES) - 1)


def nome_fase(pontos):
    return FASES[indice_fase(pontos)]
