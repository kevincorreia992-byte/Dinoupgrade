"""Telas pixel art do Dino Upgrade, mantendo as cartas e o Game Over existentes.

Coordenadas dos botoes e sliders sao centralizadas aqui para que o desenho
sempre corresponda exatamente as areas clicaveis.
"""
import pygame
from .config import LARGURA, ALTURA, BRANCO, ESCURO, OURO, FONTE, PEQUENA, GRANDE

AREIA = (247, 214, 145)
CREME = (253, 242, 212)
VERDE = (135, 210, 134)
AZUL_ESCURO = (15, 34, 41)
PAINEL = (19, 38, 43)
CONTORNO = (215, 186, 126)

BOTAO_JOGAR = pygame.Rect(488, 139, 258, 40)
BOTAO_LOJA = pygame.Rect(488, 185, 258, 40)
BOTAO_CONFIGURACOES = pygame.Rect(488, 231, 258, 40)
BOTAO_SAIR = pygame.Rect(488, 277, 258, 40)
BOTOES_ITENS = [pygame.Rect(x, 146, 220, 155) for x in (90, 340, 590)]
BOTOES_HABILIDADES = [pygame.Rect(x, 123, 222, 180) for x in (88, 339, 590)]
ABA_COSMETICOS = pygame.Rect(252, 76, 190, 28)
ABA_HABILIDADES = pygame.Rect(460, 76, 190, 28)
BOTAO_VOLTAR_LOJA = pygame.Rect(365, 348, 170, 37)
BOTAO_COMECAR = pygame.Rect(258, 259, 184, 48)
BOTAO_VOLTAR_NOME = pygame.Rect(458, 259, 184, 48)
BOTAO_VOLTAR_CONFIG = pygame.Rect(620, 342, 166, 36)
BOTAO_AUDIO = pygame.Rect(111, 259, 354, 39)
SLIDER_MUSICA = pygame.Rect(254, 133, 185, 27)
SLIDER_EFEITOS = pygame.Rect(254, 195, 185, 27)
PAUSA_CONTINUAR = pygame.Rect(316, 73, 268, 35)
PAUSA_SLIDER_MUSICA = pygame.Rect(346, 142, 214, 25)
PAUSA_SLIDER_EFEITOS = pygame.Rect(346, 196, 214, 25)
PAUSA_AUDIO = pygame.Rect(317, 235, 266, 31)
PAUSA_CONTROLES = pygame.Rect(317, 274, 266, 31)
PAUSA_MENU = pygame.Rect(317, 313, 266, 34)
PAUSA_VOLTAR_CONTROLES = pygame.Rect(354, 333, 192, 39)
CONFIRMAR_SAIR = pygame.Rect(250, 243, 193, 47)
CANCELAR_SAIR = pygame.Rect(457, 243, 193, 47)
BOTAO_REINICIAR = pygame.Rect(310, 198, 280, 52)
BOTAO_MENU = pygame.Rect(310, 268, 280, 52)

_FONTES = {}


def _fonte_pixel(tamanho, negrito=True):
    # Renderização em resolução final, com antialias. A tipografia fica muito
    # mais legível do que ampliar um texto originalmente feito em 7 pixels.
    chave = (int(tamanho), negrito)
    if chave not in _FONTES:
        _FONTES[chave] = pygame.font.SysFont(
            'dejavusansmono,consolas,couriernew,monospace', max(10, int(tamanho)),
            bold=negrito)
    return _FONTES[chave]


def pixel(tela, mensagem, centro, tamanho=12, cor=CREME, escala=2,
          sombra=True, max_largura=None):
    """Texto retrô nítido com ajuste limitado à largura do painel."""
    mensagem = str(mensagem)
    tam = max(11, int(tamanho * escala))
    fonte = _fonte_pixel(tam)
    if max_largura is not None:
        while tam > 12 and fonte.size(mensagem)[0] > max_largura:
            tam -= 1
            fonte = _fonte_pixel(tam)
        if fonte.size(mensagem)[0] > max_largura:
            while mensagem and fonte.size(mensagem + '…')[0] > max_largura:
                mensagem = mensagem[:-1]
            mensagem += '…'
    imagem = fonte.render(mensagem, True, cor)
    destino = imagem.get_rect(center=centro)
    if sombra:
        silhueta = fonte.render(mensagem, True, (5, 15, 20))
        tela.blit(silhueta, destino.move(1, 2))
    tela.blit(imagem, destino)
    return destino


def texto_cabendo(tela, mensagem, area, tamanho=17, cor=CREME, alinhar='center'):
    """Desenha uma linha inteira respeitando as margens do retângulo."""
    area = pygame.Rect(area)
    tam = tamanho
    fonte = _fonte_pixel(tam)
    while tam > 12 and fonte.size(mensagem)[0] > area.width:
        tam -= 1
        fonte = _fonte_pixel(tam)
    img = fonte.render(mensagem, True, cor)
    destino = img.get_rect(midleft=(area.left, area.centery) if alinhar == 'left'
                           else (area.centerx - img.get_width() // 2, area.centery))
    tela.blit(img, destino)
    return destino


def quebrar_texto(texto, largura, fonte):
    """Quebra em palavras sem ultrapassar a largura fornecida."""
    linhas, atual = [], ''
    for palavra in str(texto).split():
        candidata = (atual + ' ' + palavra).strip()
        if atual and fonte.size(candidata)[0] > largura:
            linhas.append(atual)
            atual = palavra
        else:
            atual = candidata
    if atual:
        linhas.append(atual)
    return linhas


def texto(tela, mensagem, fonte, cor, centro):
    imagem = fonte.render(str(mensagem), True, cor)
    tela.blit(imagem, imagem.get_rect(center=centro))


def escurecer(tela, opacidade=176):
    camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    camada.fill((8, 20, 27, opacidade))
    tela.blit(camada, (0, 0))


def placa(tela, rect, realce=VERDE, opacidade=235):
    """Moldura quadrada em camadas com cantos chanfrados por pixels."""
    rect = pygame.Rect(rect)
    sombra = pygame.Surface((rect.w + 9, rect.h + 9), pygame.SRCALPHA)
    pygame.draw.rect(sombra, (3, 10, 14, 135), (5, 6, rect.w, rect.h))
    tela.blit(sombra, (rect.x - 1, rect.y - 1))
    painel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(painel, (*CONTORNO, 245), painel.get_rect())
    pygame.draw.rect(painel, (*PAINEL, opacidade), (3, 3, rect.w - 6, rect.h - 6))
    pygame.draw.rect(painel, (*realce, 255), (8, 6, max(0, rect.w - 16), 3))
    pygame.draw.rect(painel, (65, 92, 88, 255), (8, rect.h - 9, max(0, rect.w - 16), 2))
    for x in (0, rect.w - 3):
        for y in (0, rect.h - 3):
            pygame.draw.rect(painel, (0, 0, 0, 0), (x, y, 3, 3))
    tela.blit(painel, rect)


def botao_pixel(tela, legenda, retangulo, mouse, selecionado=False, ativo=True):
    foco = ativo and (selecionado or retangulo.collidepoint(mouse))
    borda = AREIA if foco else CONTORNO
    fundo = (61, 104, 78) if foco else (30, 66, 66)
    pygame.draw.rect(tela, (8, 23, 28), retangulo.move(4, 5))
    pygame.draw.rect(tela, borda, retangulo)
    pygame.draw.rect(tela, fundo, retangulo.inflate(-6, -6))
    pygame.draw.rect(tela, VERDE if foco else (79, 134, 107),
                     (retangulo.x + 11, retangulo.y + 7, retangulo.w - 22, 3))
    # Duas marcas nas extremidades reforcam o estilo de botoes retrô.
    for x in (retangulo.x + 12, retangulo.right - 16):
        pygame.draw.rect(tela, borda, (x, retangulo.centery - 2, 4, 4))
    pixel(tela, legenda, retangulo.center, 11 if len(legenda) <= 17 else 10,
          CREME if ativo else (157, 164, 158), max_largura=retangulo.width - 29)
    return foco


def botao(tela, legenda, retangulo, mouse):
    """Compatibilidade para as telas de Game Over e vitoria antigas."""
    return botao_pixel(tela, legenda, retangulo, mouse)


def titulo(tela, recorde, mouse, tempo, frames_dino, escolha_teclado=0, moedas=0, cosmetico=None):
    """Primeira tela do jogo: o mundo da Floresta aparece ao fundo."""
    escurecer(tela, 91)
    placa(tela, (172, 18, 556, 105), AREIA, 236)
    pixel(tela, 'DINO UPGRADE', (LARGURA // 2, 65), 25, AREIA)
    pixel(tela, 'SOBREVIVA  •  EVOLUA  •  VENÇA OS CHEFES', (LARGURA // 2, 102), 8, VERDE)

    placa(tela, (114, 156, 270, 182), VERDE, 180)
    pygame.draw.rect(tela, (118, 159, 103), (131, 309, 231, 5))
    pygame.draw.rect(tela, (75, 107, 70), (141, 315, 211, 6))
    if frames_dino:
        frame = frames_dino[int(tempo * 7) % len(frames_dino)]
        # Aumenta por nearest-neighbor, preservando os pixels originais.
        ampliado = pygame.transform.scale(frame, (frame.get_width() * 2,
                                                  frame.get_height() * 2))
        tela.blit(ampliado, ampliado.get_rect(midbottom=(251, 307)))
    pixel(tela, 'UMA NOVA AVENTURA', (247, 175), 10, CREME)

    for i, (rotulo, area) in enumerate((('JOGAR', BOTAO_JOGAR),
                                       ('LOJA', BOTAO_LOJA),
                                       ('CONFIGURAÇÕES', BOTAO_CONFIGURACOES),
                                       ('SAIR', BOTAO_SAIR))):
        botao_pixel(tela, rotulo, area, mouse, selecionado=escolha_teclado == i)
    placa(tela, (260, 345, 380, 37), AREIA)
    pixel(tela, f'RECORDE {int(recorde):,}  |  MOEDAS {int(moedas)}'.replace(',', '.'),
          (450, 364), 9, AREIA)


def identificacao(tela, nome, mouse, tempo=0, aviso=''):
    escurecer(tela, 150)
    placa(tela, (133, 31, 634, 326), AREIA)
    pixel(tela, 'QUAL É O SEU NOME, AVENTUREIRO?', (450, 94), 15, AREIA)
    pixel(tela, 'ESCREVA SEU NOME PARA COMEÇAR', (450, 139), 9, CREME)
    rect = pygame.Rect(205, 170, 490, 62)
    pygame.draw.rect(tela, (7, 20, 26), rect)
    pygame.draw.rect(tela, VERDE, rect, 3)
    pygame.draw.rect(tela, (32, 65, 65), rect.inflate(-10, -10))
    conteudo = nome if nome else 'SEU NOME AQUI'
    pixel(tela, conteudo, (450, 199), 14, CREME if nome else (146, 166, 155))
    if int(tempo * 2) % 2 == 0:
        largura = _fonte_pixel(14).size(nome)[0] * 2
        x = min(650, 450 + largura // 2 + 5)
        pygame.draw.rect(tela, AREIA, (x, 183, 3, 30))
    botao_pixel(tela, 'COMEÇAR', BOTAO_COMECAR, mouse)
    botao_pixel(tela, 'VOLTAR', BOTAO_VOLTAR_NOME, mouse)
    pixel(tela, aviso if aviso else 'ATÉ 16 CARACTERES  •  ENTER PARA COMEÇAR',
          (450, 326), 8, AREIA if aviso else (192, 209, 196))


def _slider(tela, area, valor, mouse, selecionado=False):
    trilho = pygame.Rect(area.x, area.centery - 5, area.w, 10)
    pygame.draw.rect(tela, (9, 25, 30), trilho.inflate(4, 4))
    pygame.draw.rect(tela, (87, 114, 99), trilho)
    largura = round(trilho.w * max(0, min(1, valor)))
    if largura:
        pygame.draw.rect(tela, VERDE, (trilho.x, trilho.y, largura, trilho.h))
    x = round(trilho.x + trilho.w * max(0, min(1, valor)))
    pygame.draw.rect(tela, AREIA if selecionado or area.collidepoint(mouse) else CONTORNO,
                     (x - 5, area.y + 1, 10, area.h - 2))
    pygame.draw.rect(tela, (49, 77, 67), (x - 2, area.y + 5, 4, area.h - 10))


def _painel_controles(tela, area, compacto=False):
    """Legenda das teclas: mesmas teclas realmente tratadas no main.py."""
    area = pygame.Rect(area)
    placa(tela, area, AREIA)
    pixel(tela, 'CONTROLES', (area.centerx, area.y + 21), 11, AREIA,
          max_largura=area.w - 16)
    linhas = (
        ('ESPAÇO / SETA CIMA', 'PULAR'),
        ('F / J', 'ATIRAR NO BOSS ABERTO'),
        ('Q', 'USAR VIDA EXTRA'),
        ('E', 'LIMPAR CENÁRIO'),
        ('MOUSE', 'ESCOLHER CARTAS'),
        ('ESC', 'PAUSAR / CONTINUAR'),
        ('ESPAÇO NO GAME OVER', 'REINICIAR PARTIDA'),
    )
    topo = area.y + 43
    passo = 25 if compacto else 30
    for i, (tecla, descricao) in enumerate(linhas):
        y = topo + i * passo
        fonte = _fonte_pixel(13 if compacto else 15)
        largura = area.width - 28
        if not compacto:
            linha = f'{tecla}  —  {descricao}'
            texto_cabendo(tela, linha, (area.x + 13, y - 11, largura, 24), 15, CREME, 'left')
        else:
            # A coluna estreita usa duas áreas bem definidas: tecla e função.
            texto_cabendo(tela, tecla, (area.x + 13, y - 10, largura, 17), 14, VERDE, 'left')
            texto_cabendo(tela, descricao, (area.x + 13, y + 4, largura, 15), 12, CREME, 'left')


def configuracoes(tela, opcoes, mouse, audio_disponivel=True, foco=0):
    escurecer(tela, 166)
    placa(tela, (65, 15, 770, 372), AREIA)
    pixel(tela, 'CONFIGURAÇÕES', (450, 47), 18, AREIA)
    placa(tela, (89, 88, 395, 228), VERDE)
    pixel(tela, 'ÁUDIO', (290, 109), 11, VERDE)
    pixel(tela, 'MÚSICA', (165, 150), 9, CREME)
    pixel(tela, 'EFEITOS', (165, 212), 9, CREME)
    _slider(tela, SLIDER_MUSICA, opcoes.volume_musica, mouse, foco == 0)
    _slider(tela, SLIDER_EFEITOS, opcoes.volume_efeitos, mouse, foco == 1)
    pixel(tela, f'{round(opcoes.volume_musica * 100)}%', (421, 170), 8, CREME)
    pixel(tela, f'{round(opcoes.volume_efeitos * 100)}%', (421, 232), 8, CREME)
    botao_pixel(tela, 'SOM: LIGADO' if opcoes.audio_ativo else 'SOM: SILENCIADO',
                BOTAO_AUDIO, mouse, selecionado=foco == 2)
    if not audio_disponivel:
        pixel(tela, 'ÁUDIO INDISPONÍVEL', (290, 308), 8, AREIA)

    _painel_controles(tela, (496, 88, 310, 228), compacto=True)
    botao_pixel(tela, 'VOLTAR', BOTAO_VOLTAR_CONFIG, mouse, selecionado=foco == 3)
    pixel(tela, 'TAB: NAVEGAR    SETAS: AJUSTAR    ESC: VOLTAR',
          (304, 358), 8, CREME, max_largura=438)


def slider_valor(area, x):
    return max(0.0, min(1.0, (x - area.left) / area.width))


def morte(tela, pontos, recorde, mouse):
    escurecer(tela)
    texto(tela, 'GAME OVER', GRANDE, BRANCO, (LARGURA // 2, 95))
    texto(tela, f'Pontuação: {int(pontos)} | Recorde: {recorde}', FONTE,
          BRANCO, (LARGURA // 2, 153))
    botao(tela, 'JOGAR NOVAMENTE', BOTAO_REINICIAR, mouse)
    botao(tela, 'VOLTAR AO MENU', BOTAO_MENU, mouse)


def escolher_carta(tela, cartas, imagens, mouse, escolhida=None, progresso=0):
    escurecer(tela)
    texto(tela, 'ESCOLHA UMA CARTA', GRANDE, BRANCO, (LARGURA // 2, 65))
    texto(tela, 'Clique em uma carta para revelar seu efeito', PEQUENA,
          BRANCO, (LARGURA // 2, 105))
    areas = []
    for i, indice in enumerate(cartas):
        rect = pygame.Rect(125 + i * 255, 155, 140, 160)
        revelada = escolhida == i and progresso >= 0.5
        largura = max(2, int(rect.width * (abs(1 - 2 * progresso) if escolhida == i else 1)))
        visual = pygame.Rect(0, 0, largura, rect.height)
        visual.center = rect.center
        pygame.draw.rect(tela, ESCURO, visual, border_radius=12)
        pygame.draw.rect(tela, OURO, visual, 3, border_radius=12)
        if revelada:
            img = imagens[indice]
            if progresso < 1:
                img = pygame.transform.smoothscale(img, (max(1, int(img.get_width() * (2 * progresso - 1))), img.get_height()))
            tela.blit(img, img.get_rect(center=(rect.centerx, rect.centery - 12)))
        elif escolhida != i or progresso < 0.5:
            if largura > 35:
                pygame.draw.rect(tela, (58, 83, 112), visual.inflate(-14, -14), border_radius=9)
                pygame.draw.rect(tela, OURO, visual.inflate(-30, -30), 2, border_radius=8)
                texto(tela, '?', GRANDE, BRANCO, (rect.centerx, rect.centery - 8))
        if largura > 35:
            texto(tela, str(i + 1), PEQUENA, BRANCO, (rect.centerx, rect.bottom - 15))
        areas.append(rect)
    return areas


# Duas abas: 3 acessórios do dinossauro + 3 habilidades.
def tela_loja(tela, loja, mouse, foco=0, aviso='', aba='cosmeticos'):
    from .loja import ITENS, HABILIDADES, desenhar_preview_item
    from .habilidades_visuais import desenhar_icone
    escurecer(tela, 155)
    placa(tela, (44, 10, 812, 380), AREIA)
    pixel(tela, 'LOJA DINO UPGRADE', (450, 28), 15, AREIA)
    pixel(tela, f'SALDO: {loja.moedas} MOEDAS', (450, 57), 9, (255, 230, 129))
    botao_pixel(tela, 'COSMÉTICOS', ABA_COSMETICOS, mouse, selecionado=aba == 'cosmeticos')
    botao_pixel(tela, 'HABILIDADES', ABA_HABILIDADES, mouse, selecionado=aba == 'habilidades')
    if aba == 'cosmeticos':
        for i, ((identificador, nome, preco, _categoria, descricao), rect) in enumerate(zip(ITENS, BOTOES_ITENS)):
            ativo = loja.equipados['dino'] == identificador
            comprado = identificador in loja.comprados
            realce = VERDE if ativo else AREIA if i == foco or rect.collidepoint(mouse) else (134, 170, 151)
            placa(tela, rect, realce)

            # Miniatura independente: a imagem fica inteiramente contida no espaço 64x64.
            miniatura = pygame.Rect(rect.x + 13, rect.y + 33, 64, 64)
            pygame.draw.rect(tela, (17, 31, 38), miniatura)
            pygame.draw.rect(tela, (235, 213, 149), miniatura, 2)
            desenhar_preview_item(tela, identificador, miniatura.center, tamanho_maximo=47)

            # Título, nome e descrição numa coluna que não encontra a imagem.
            centro_texto = (rect.x + 148)
            pixel(tela, 'ACESSÓRIO DINO', (centro_texto, rect.y + 26), 7, VERDE, max_largura=128)
            pixel(tela, nome, (centro_texto, rect.y + 55), 9, CREME, max_largura=130)
            for n, linha in enumerate(quebrar_texto(descricao, 130, _fonte_pixel(12))[:2]):
                pixel(tela, linha, (centro_texto, rect.y + 78 + n * 16), 6, (194, 210, 191), max_largura=130)
            pygame.draw.rect(tela, (74, 105, 98), (rect.x + 13, rect.bottom - 47, rect.w - 26, 2))
            if ativo:
                status, cor = 'EQUIPADO - DESEQUIPAR', VERDE
            elif comprado:
                status, cor = 'COMPRADO - EQUIPAR', VERDE
            else:
                status, cor = f'COMPRAR: {preco} MOEDAS', AREIA
            pixel(tela, status, (rect.centerx, rect.bottom - 24), 8, cor, max_largura=rect.w - 20)
    else:
        for i, (chave, nome, preco, tipo, descricao) in enumerate(HABILIDADES):
            rect = BOTOES_HABILIDADES[i]
            ativo = i == foco or rect.collidepoint(mouse)
            placa(tela, rect, AREIA if ativo else VERDE)
            desenhar_icone(tela, chave, (rect.centerx, rect.y + 42), escala=2)
            pixel(tela, nome, (rect.centerx, rect.y + 82), 9, CREME, max_largura=rect.w - 16)
            fonte = _fonte_pixel(14)
            for n, linha in enumerate(quebrar_texto(descricao, rect.w - 24, fonte)[:2]):
                pixel(tela, linha, (rect.centerx, rect.y + 111 + n * 17), 7, (198, 218, 208),
                      max_largura=rect.w - 18)
            if tipo == 'permanente':
                status = 'ADQUIRIDO - PERMANENTE' if loja.arma_antiboss else f'COMPRAR: {preco} MOEDAS'
                cor = VERDE if loja.arma_antiboss else AREIA
            else:
                status = f'COMPRAR: {preco} | ESTOQUE: {loja.quantidade_habilidade(chave)}/5'
                cor = AREIA
            pixel(tela, status, (rect.centerx, rect.bottom - 17), 8, cor, max_largura=rect.w - 14)
        placa(tela, (112, 311, 678, 26), VERDE)
        pixel(tela, 'Q = VIDA EXTRA   |   E = LIMPAR CENÁRIO   |   ARMA = +50% NO BOSS',
              (450, 324), 8, CREME, max_largura=652)
    botao_pixel(tela, 'VOLTAR', BOTAO_VOLTAR_LOJA, mouse)
    if aviso:
        pixel(tela, aviso, (450, 321 if aba == 'cosmeticos' else 111), 8, AREIA, max_largura=690)
    elif aba == 'cosmeticos':
        pixel(tela, 'TAB: MUDAR ABA  |  SETAS: SELECIONAR  |  ENTER: COMPRAR',
              (450, 321), 7, CREME, max_largura=700)


def cutscene_vitoria(tela, pontos, moedas_ganhas, tempo, frames_dino):
    """Celebracao temporizada; o loop principal volta ao menu apos 5,5 s."""
    import math
    escurecer(tela, 157)
    placa(tela, (154, 24, 592, 342), AREIA)
    # Confetes pixelados com trajetorias previsiveis, sem arquivos ou objetos extras.
    cores = ((255, 189, 91), (126, 218, 139), (115, 216, 243), (244, 115, 102))
    for i in range(50):
        x = 164 + (i * 131 + round(math.sin(tempo * 0.8 + i) * 9)) % 572
        y = 37 + (i * 53 + int(tempo * (29 + i % 5 * 12))) % 303
        pygame.draw.rect(tela, cores[i % len(cores)], (x, y, 5, 7))
    pixel(tela, 'VITÓRIA!', (450, 81), 26, AREIA)
    pixel(tela, 'VOCÊ DERROTOU O TITÃ DO VULCÃO!', (450, 119), 11, CREME)
    if frames_dino:
        img = frames_dino[int(tempo * 8) % len(frames_dino)]
        img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
        tela.blit(img, img.get_rect(midbottom=(450, 288)))
    pixel(tela, f'PONTOS: {int(pontos):,}'.replace(',', '.'), (450, 297), 10, CREME)
    pixel(tela, f'+{moedas_ganhas} MOEDAS DE PRÊMIO', (450, 322), 10, AREIA)
    pixel(tela, 'RETORNANDO AO MENU...', (450, 353), 8, VERDE)


# Todos os controles de pausa correspondem a áreas clicáveis reais do main.py.
def pausa(tela, opcoes, mouse, foco=0):
    escurecer(tela, 192)
    placa(tela, (189, 12, 522, 373), AREIA)
    pixel(tela, 'JOGO PAUSADO', (450, 42), 20, AREIA)
    botao_pixel(tela, 'CONTINUAR (ESC)', PAUSA_CONTINUAR, mouse, selecionado=foco == 0)
    pixel(tela, 'MÚSICA', (283, 151), 9, CREME)
    _slider(tela, PAUSA_SLIDER_MUSICA, opcoes.volume_musica, mouse, foco == 1)
    pixel(tela, f'{int(opcoes.volume_musica * 100)}%', (582, 151), 8, CREME)
    pixel(tela, 'EFEITOS', (283, 206), 9, CREME)
    _slider(tela, PAUSA_SLIDER_EFEITOS, opcoes.volume_efeitos, mouse, foco == 2)
    pixel(tela, f'{int(opcoes.volume_efeitos * 100)}%', (582, 206), 8, CREME)
    botao_pixel(tela, 'ÁUDIO LIGADO' if opcoes.audio_ativo else 'ÁUDIO DESLIGADO',
                PAUSA_AUDIO, mouse, selecionado=foco == 3)
    botao_pixel(tela, 'VER CONTROLES', PAUSA_CONTROLES, mouse, selecionado=foco == 4)
    botao_pixel(tela, 'VOLTAR AO MENU', PAUSA_MENU, mouse, selecionado=foco == 5)
    pixel(tela, 'O JOGO FICA CONGELADO ENQUANTO ESTE MENU ESTIVER ABERTO',
          (450, 361), 7, VERDE, max_largura=475)


def controles_pausa(tela, mouse):
    escurecer(tela, 198)
    placa(tela, (175, 13, 550, 375), AREIA)
    _painel_controles(tela, (225, 49, 450, 276), compacto=False)
    botao_pixel(tela, 'VOLTAR (ESC)', PAUSA_VOLTAR_CONTROLES, mouse)


def confirmar_saida(tela, mouse):
    escurecer(tela, 206)
    placa(tela, (174, 85, 552, 230), AREIA)
    pixel(tela, 'SAIR DA PARTIDA?', (450, 126), 18, AREIA)
    fonte = _fonte_pixel(17)
    frases = ('A pontuação da partida atual será encerrada.',
              'Moedas e compras já salvas serão mantidas.')
    for i, frase in enumerate(frases):
        texto_cabendo(tela, frase, (225, 160 + 28 * i, 450, 24), 17, CREME)
    botao_pixel(tela, 'SAIR', CONFIRMAR_SAIR, mouse)
    botao_pixel(tela, 'CANCELAR', CANCELAR_SAIR, mouse)
