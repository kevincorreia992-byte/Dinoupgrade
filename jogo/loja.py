"""Loja, moedas, acessórios do dinossauro e habilidades persistentes."""
import json
from pathlib import Path
import pygame

ARQUIVO = Path(__file__).resolve().parent.parent / 'progresso_jogador.json'
PASTA_ASSETS = Path(__file__).resolve().parent.parent / 'assets' / 'Cosmeticos'

ITENS = (
    ('chapeu', 'CHAPEU', 6, 'dino', 'Novo visual com chapeu'),
    ('oculos', 'OCULOS', 5, 'dino', 'Novo visual com oculos'),
    ('oculos_chapeu', 'CHAPEU + OCULOS', 8, 'dino', 'Substitui a antiga mascara'),
)
MAPA_ITENS = {item[0]: item for item in ITENS}


HABILIDADES = (
    ('vida_extra', 'VIDA EXTRA', 8, 'consumivel', 'Q: recupera 1 coracao (maximo 2)'),
    ('limpar_cenario', 'LIMPAR CENARIO', 10, 'consumivel', 'E: remove perigos visiveis agora'),
    ('arma_antiboss', 'ARMA ANTIBOSS', 28, 'permanente', 'Ataques causam +50% de dano aos bosses'),
)
MAPA_HABILIDADES = {h[0]: h for h in HABILIDADES}
LIMITE_ESTOQUE = 5

_CACHE_SPRITES = {}
_SUBPASTA = {'dino': 'Dino'}


class Loja:
    def __init__(self, caminho=ARQUIVO):
        self.caminho = Path(caminho)
        self.moedas = 0
        self.recorde = 0
        self.comprados = set()
        self.equipados = {'dino': None}
        self.habilidades = {'vida_extra': 0, 'limpar_cenario': 0}
        self.melhorias = set()
        self.carregar()

    def carregar(self):
        try:
            dados = json.loads(self.caminho.read_text(encoding='utf-8'))
            if not isinstance(dados, dict):
                return
            moedas = dados.get('moedas', 0)
            recorde = dados.get('recorde', 0)
            if isinstance(moedas, int) and not isinstance(moedas, bool):
                self.moedas = max(0, min(9999999, moedas))
            if isinstance(recorde, int) and not isinstance(recorde, bool):
                self.recorde = max(0, recorde)
            itens = dados.get('comprados', [])
            itens_brutos = itens if isinstance(itens, list) else []
            if isinstance(itens, list):
                self.comprados = {i for i in itens if isinstance(i, str) and i in MAPA_ITENS}
                
                if 'mascara' in itens_brutos:
                    self.comprados.add('oculos_chapeu')
            equips = dados.get('equipados', {})
            if isinstance(equips, dict):
                item = equips.get('dino')
                if item == 'mascara':
                    item = 'oculos_chapeu'
                if isinstance(item, str) and item in self.comprados and MAPA_ITENS[item][3] == 'dino':
                    self.equipados['dino'] = item
            habilidade_dados = dados.get('habilidades', {})
            if isinstance(habilidade_dados, dict):
                for chave in self.habilidades:
                    valor = habilidade_dados.get(chave, 0)
                    if isinstance(valor, int) and not isinstance(valor, bool):
                        self.habilidades[chave] = max(0, min(LIMITE_ESTOQUE, valor))
            melhorias = dados.get('melhorias', [])
            if isinstance(melhorias, list):
                self.melhorias = {chave for chave in melhorias
                                  if chave == 'arma_antiboss'}
        except (OSError, ValueError, TypeError):
            return

    def salvar(self):
        dados = {'moedas': self.moedas, 'recorde': self.recorde,
                 'comprados': sorted(self.comprados), 'equipados': self.equipados,
                 'habilidades': self.habilidades, 'melhorias': sorted(self.melhorias)}
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            temporario = self.caminho.with_suffix('.json.tmp')
            temporario.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
            temporario.replace(self.caminho)
        except OSError as erro:
            print('Nao foi possivel salvar progresso:', erro)

    def adicionar(self, quantidade):
        if isinstance(quantidade, int) and quantidade > 0:
            self.moedas = min(9999999, self.moedas + quantidade)
            self.salvar()

    def registrar_recorde(self, pontos):
        if int(pontos) > self.recorde:
            self.recorde = int(pontos)
            self.salvar()

    def comprar_ou_equipar(self, identificador):
        """Retorna (sucesso, mensagem). Um clique nunca gasta duas vezes."""
        item = MAPA_ITENS.get(identificador)
        if item is None:
            return False, 'ITEM DESCONHECIDO'
        _, nome, preco, categoria, _ = item
        if identificador not in self.comprados:
            if self.moedas < preco:
                return False, 'MOEDAS INSUFICIENTES'
            self.moedas -= preco
            self.comprados.add(identificador)
        if self.equipados[categoria] == identificador:
            self.equipados[categoria] = None
            mensagem = 'ITEM DESEQUIPADO'
        else:
            self.equipados[categoria] = identificador
            mensagem = f'{nome} EQUIPADO!'
        self.salvar()
        return True, mensagem

    @property
    def arma_antiboss(self):
        return 'arma_antiboss' in self.melhorias

    def quantidade_habilidade(self, nome):
        return self.habilidades.get(nome, 0)

    def comprar_habilidade(self, identificador):
        """Compra consumíveis empilháveis ou a melhoria permanente uma única vez."""
        item = MAPA_HABILIDADES.get(identificador)
        if item is None:
            return False, 'HABILIDADE DESCONHECIDA'
        _, nome, preco, tipo, _ = item
        if tipo == 'permanente' and identificador in self.melhorias:
            return False, 'MELHORIA JA ADQUIRIDA'
        if tipo == 'consumivel' and self.habilidades[identificador] >= LIMITE_ESTOQUE:
            return False, 'ESTOQUE CHEIO (MAX. 5)'
        if self.moedas < preco:
            return False, 'MOEDAS INSUFICIENTES'
        self.moedas -= preco
        if tipo == 'permanente':
            self.melhorias.add(identificador)
        else:
            self.habilidades[identificador] += 1
        self.salvar()
        return True, f'{nome} COMPRADA!'

    def consumir_habilidade(self, identificador):
        """Consome somente sob autorização da Partida, após validar o efeito."""
        if identificador not in self.habilidades or self.habilidades[identificador] <= 0:
            return False
        self.habilidades[identificador] -= 1
        self.salvar()
        return True


def _carregar_icone(identificador):
    """Carrega SOMENTE o PNG do acessório — nunca um frame inteiro do Dino."""
    if identificador in _CACHE_SPRITES:
        return _CACHE_SPRITES[identificador]
    caminho = PASTA_ASSETS / 'Dino' / f'{identificador}.png'
    try:
        imagem = pygame.image.load(str(caminho)).convert_alpha()
    except (pygame.error, OSError, FileNotFoundError):
        imagem = None
    _CACHE_SPRITES[identificador] = imagem
    return imagem


def desenhar_preview_item(tela, identificador, centro, tamanho_maximo=48):
    """Miniatura proporcional, limitada a um quadrado; sem sobrepor os textos."""
    if identificador not in MAPA_ITENS:
        return None
    sprite = _carregar_icone(identificador)
    if sprite is None:
        return None
    limite = max(8, min(56, int(tamanho_maximo)))
    fator = min(limite / sprite.get_width(), limite / sprite.get_height(), 1.0)
    tamanho = (max(1, round(sprite.get_width() * fator)),
               max(1, round(sprite.get_height() * fator)))
    miniatura = pygame.transform.scale(sprite, tamanho)
    destino = miniatura.get_rect(center=(int(centro[0]), int(centro[1])))
    tela.blit(miniatura, destino)
    return destino
