"""Biomas em ordem fixa. Cada chefe aparece a cada 5.000 pontos de progressão.
A fase seguinte só é liberada após derrotá-lo em partida.py.
"""

from .modo_teste import MODO_TESTE, PONTOS_POR_CHEFE_TESTE

FASES = ("Floresta", "Deserto", "Gelo", "Vulcão")
PASTAS_FASES = ("01_Floresta", "02_Deserto", "03_Gelo", "04_Vulcao")
LIMITE_POR_FASE = PONTOS_POR_CHEFE_TESTE if MODO_TESTE else 5000
