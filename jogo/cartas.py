import random
from .recursos import imagem, tamanho_por_altura
from .config import MAX_VIDAS
NOMES=['Vida extra','Pontos 2x','Sorte','Velocidade 1.5x','Pontos pela metade','Azar']
class Cartas:
    def __init__(self):
        self.imagens=[tamanho_por_altura(imagem(f'Cartas/carta_{i}.png'),112) for i in range(1,7)]
    def sortear(self,boa=False,ruim=False):
        if boa: return [0,1,2]
        if ruim: return [3,4,5]
        return random.sample(range(6),3)
    def aplicar(self,indice,jogo):
        jogo.boa_proxima=jogo.ruim_proxima=False
        if indice==0: jogo.vidas=min(MAX_VIDAS,jogo.vidas+1)
        elif indice==1: jogo.mult_pontos=2
        elif indice==2: jogo.boa_proxima=True
        elif indice==3: jogo.mult_velocidade=1.5
        elif indice==4: jogo.mult_pontos=0.5
        elif indice==5: jogo.ruim_proxima=True
        jogo.mensagem=NOMES[indice]
        jogo.tempo_mensagem=1.8
