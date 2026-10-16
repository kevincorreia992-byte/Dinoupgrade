"""Dino Upgrade — um loop principal, telas independentes e pausa real.

Estados: titulo, identificacao, loja, configuracoes, jogando, boss,
cartas, revelando, pausa, controles_pausa, confirmar_saida, morte, vitoria.
O jogo só é atualizado em 'jogando' ou 'boss': pausar congela física,
contadores, inimigos, projéteis, cartas e avanço dos biomas.
"""
import pygame
from pathlib import Path
import shutil

from jogo.modo_teste import MODO_TESTE, pontos_para_o_proximo_chefe
from jogo.fases import LIMITE_POR_FASE
from jogo.config import LARGURA, ALTURA, FPS
from jogo.cenario import Cenario
from jogo.partida import Partida
from jogo.preferencias import Preferencias
from jogo.audio import Audio
from jogo.loja import Loja, ITENS, HABILIDADES
from jogo import telas


def executar():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption('Dino Upgrade - TESTE SUPER FACIL' if MODO_TESTE else 'Dino Upgrade')
    relogio = pygame.time.Clock()
    fonte_selo_teste = pygame.font.SysFont("consolas,monospace", 14, bold=True) if MODO_TESTE else None
    cenario = Cenario()
    if MODO_TESTE:
        
        pasta_jogo = Path(__file__).resolve().parent
        save_normal = pasta_jogo / 'progresso_jogador.json'
        save_teste = pasta_jogo / 'progresso_teste.json'
        if not save_teste.exists() and save_normal.is_file():
            try:
                shutil.copyfile(save_normal, save_teste)
            except OSError:
                pass
        loja = Loja(save_teste)
    else:
        loja = Loja()
    partida = Partida(loja)
    preferencias = Preferencias()
    audio = Audio(preferencias)

    estado = 'titulo'
    estado_antes_pausa = 'jogando'
    aba_loja = 'cosmeticos'
    nome_digitado = preferencias.ultimo_nome
    nome = ''
    recorde = loja.recorde
    aviso_loja = ''
    tempo_aviso_loja = 0.0
    foco_loja = 0
    tempo_vitoria = 0.0
    tempo_telas = 0.0
    aviso_nome = ''
    escolha_menu = -1
    foco_configuracoes = -1
    foco_pausa = 0
    arrastando = None
    carta_escolhida = None
    tempo_revelacao = 0.0

    def som(tipo='confirmar'):
        audio.efeito(tipo)

    def abrir_nome():
        nonlocal estado, nome_digitado, tempo_telas, aviso_nome
        nome_digitado = preferencias.ultimo_nome
        tempo_telas = 0.0
        aviso_nome = ''
        estado = 'identificacao'
        pygame.key.start_text_input()

    def voltar_titulo():
        nonlocal estado, arrastando, escolha_menu
        if estado == 'identificacao':
            pygame.key.stop_text_input()
        if estado in ('pausa', 'controles_pausa', 'confirmar_saida'):
            audio.retomar_musica()
        estado = 'titulo'
        arrastando = None
        escolha_menu = -1
        cenario.reiniciar()
        som('voltar')

    def iniciar_partida():
        nonlocal estado, nome, aviso_nome, arrastando
        novo_nome = nome_digitado.strip()
        if not novo_nome:
            aviso_nome = 'DIGITE UM NOME PARA COMECAR'
            som('voltar')
            return
        nome = novo_nome[:16]
        preferencias.guardar_nome(nome)
        pygame.key.stop_text_input()
        partida.reiniciar()
        cenario.reiniciar()
        arrastando = None
        estado = 'jogando'
        som()

    def abrir_loja():
        nonlocal estado, foco_loja, aviso_loja, tempo_aviso_loja, aba_loja
        estado = 'loja'
        foco_loja = 0
        aba_loja = 'cosmeticos'
        aviso_loja = ''
        tempo_aviso_loja = 0.0
        som()

    def mudar_aba(aba):
        nonlocal aba_loja, foco_loja, aviso_loja
        aba_loja = aba
        foco_loja = 0
        aviso_loja = ''
        som('voltar')

    def comprar_item(indice):
        nonlocal aviso_loja, tempo_aviso_loja, foco_loja
        foco_loja = indice
        if aba_loja == 'cosmeticos':
            sucesso, aviso_loja = loja.comprar_ou_equipar(ITENS[indice][0])
        else:
            sucesso, aviso_loja = loja.comprar_habilidade(HABILIDADES[indice][0])
        tempo_aviso_loja = 2.0
        som('comprar' if sucesso else 'voltar')

    def ajustar_volume(tipo, posicao, na_pausa=False, salvar=False):
        area = (telas.PAUSA_SLIDER_MUSICA if tipo == 'musica' else telas.PAUSA_SLIDER_EFEITOS) if na_pausa else (
            telas.SLIDER_MUSICA if tipo == 'musica' else telas.SLIDER_EFEITOS)
        valor = round(telas.slider_valor(area, posicao), 2)
        if tipo == 'musica':
            preferencias.volume_musica = valor
        else:
            preferencias.volume_efeitos = valor
        audio.aplicar_volumes()
        if salvar:
            preferencias.salvar()

    def pausar():
        nonlocal estado, estado_antes_pausa, foco_pausa, arrastando
        estado_antes_pausa = estado
        estado = 'pausa'
        foco_pausa = 0
        arrastando = None
        audio.pausar_musica()

    def continuar():
        nonlocal estado, arrastando
        arrastando = None
        estado = estado_antes_pausa
        audio.retomar_musica()
        som()

    def sair_da_partida():
        nonlocal recorde
        recorde = max(recorde, int(partida.pontos))
        loja.registrar_recorde(recorde)
        voltar_titulo()

    def executar_pausa(acao):
        nonlocal estado, foco_pausa
        if acao == 'continuar':
            continuar()
        elif acao == 'audio':
            preferencias.alternar_audio()
            audio.aplicar_volumes()
            som()
        elif acao == 'controles':
            estado = 'controles_pausa'
            som()
        elif acao == 'menu':
            estado = 'confirmar_saida'
            som('voltar')

    while True:
        dt = min(relogio.tick(FPS) / 1000.0, 0.04)
        if estado in ('titulo', 'identificacao', 'configuracoes', 'loja', 'vitoria'):
            tempo_telas += dt
        tempo_aviso_loja = max(0.0, tempo_aviso_loja - dt)
        mouse = pygame.mouse.get_pos()
        clique_pos = None

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                clique_pos = evento.pos
                sliders = []
                if estado == 'configuracoes':
                    sliders = [('musica', telas.SLIDER_MUSICA),
                               ('efeitos', telas.SLIDER_EFEITOS)]
                elif estado == 'pausa':
                    sliders = [('musica', telas.PAUSA_SLIDER_MUSICA),
                               ('efeitos', telas.PAUSA_SLIDER_EFEITOS)]
                for tipo, area in sliders:
                    if area.collidepoint(evento.pos):
                        arrastando = tipo
                        ajustar_volume(tipo, evento.pos[0], estado == 'pausa')
                        if estado == 'configuracoes':
                            foco_configuracoes = 0 if tipo == 'musica' else 1
                        else:
                            foco_pausa = 1 if tipo == 'musica' else 2
                        break

            if evento.type == pygame.MOUSEMOTION and arrastando:
                if estado in ('configuracoes', 'pausa'):
                    ajustar_volume(arrastando, evento.pos[0], estado == 'pausa')

            if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                if arrastando:
                    preferencias.salvar()
                    if arrastando == 'efeitos':
                        som()
                    arrastando = None

            if evento.type == pygame.TEXTINPUT and estado == 'identificacao':
                for letra in evento.text:
                    if letra.isprintable() and len(nome_digitado) < 16:
                        nome_digitado += letra
                        aviso_nome = ''

            if evento.type != pygame.KEYDOWN:
                continue

            if estado == 'titulo':
                if evento.key in (pygame.K_UP, pygame.K_w):
                    escolha_menu = (escolha_menu - 1) % 4
                    som('voltar')
                elif evento.key in (pygame.K_DOWN, pygame.K_s):
                    escolha_menu = (escolha_menu + 1) % 4
                    som('voltar')
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if escolha_menu in (-1, 0):
                        abrir_nome()
                    elif escolha_menu == 1:
                        abrir_loja()
                    elif escolha_menu == 2:
                        estado = 'configuracoes'
                        foco_configuracoes = -1
                    else:
                        pygame.quit()
                        return
                    som()

            elif estado == 'loja':
                itens_aba = ITENS if aba_loja == 'cosmeticos' else HABILIDADES
                deslocamento = 1  
                if evento.key == pygame.K_ESCAPE:
                    voltar_titulo()
                elif evento.key == pygame.K_TAB:
                    mudar_aba('habilidades' if aba_loja == 'cosmeticos' else 'cosmeticos')
                elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                    foco_loja = (foco_loja + 1) % len(itens_aba)
                elif evento.key in (pygame.K_LEFT, pygame.K_a):
                    foco_loja = (foco_loja - 1) % len(itens_aba)
                elif evento.key in (pygame.K_DOWN, pygame.K_s):
                    foco_loja = (foco_loja + deslocamento) % len(itens_aba)
                elif evento.key in (pygame.K_UP, pygame.K_w):
                    foco_loja = (foco_loja - deslocamento) % len(itens_aba)
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    comprar_item(foco_loja)

            elif estado == 'identificacao':
                if evento.key == pygame.K_BACKSPACE:
                    nome_digitado = nome_digitado[:-1]
                    aviso_nome = ''
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    iniciar_partida()
                elif evento.key == pygame.K_ESCAPE:
                    voltar_titulo()

            elif estado == 'configuracoes':
                if evento.key == pygame.K_ESCAPE:
                    voltar_titulo()
                elif evento.key in (pygame.K_TAB, pygame.K_UP, pygame.K_DOWN):
                    delta = -1 if evento.key == pygame.K_UP else 1
                    foco_configuracoes = (foco_configuracoes + delta) % 4
                elif evento.key in (pygame.K_LEFT, pygame.K_RIGHT) and foco_configuracoes in (0, 1):
                    tipo = 'musica' if foco_configuracoes == 0 else 'efeitos'
                    antigo = preferencias.volume_musica if tipo == 'musica' else preferencias.volume_efeitos
                    preferencias.ajustar(tipo, antigo + (-0.05 if evento.key == pygame.K_LEFT else 0.05))
                    audio.aplicar_volumes()
                    if tipo == 'efeitos':
                        som()
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    if foco_configuracoes == 2:
                        preferencias.alternar_audio()
                        audio.aplicar_volumes()
                        som()
                    elif foco_configuracoes == 3:
                        voltar_titulo()

            elif estado in ('jogando', 'boss'):
                if MODO_TESTE and estado == 'jogando' and evento.key == pygame.K_F8:
                    
                    marco = (partida.fase + 1) * LIMITE_POR_FASE
                    partida.pontos_bioma = max(partida.pontos_bioma, float(marco))
                    partida.pontos = max(partida.pontos, float(marco))
                    estado = partida._iniciar_chefe()
                    som('boss')
                elif MODO_TESTE and estado == 'boss' and evento.key == pygame.K_F9:
                    
                    
                    partida.chefe.vida = 0.0
                    som()
                elif evento.key == pygame.K_ESCAPE:
                    pausar()
                elif evento.key in (pygame.K_SPACE, pygame.K_UP):
                    if partida.dino.no_chao:
                        partida.dino.pular()
                        som('pulo')
                elif evento.key == pygame.K_q:
                    sucesso, _ = partida.ativar_habilidade('vida_extra')
                    som('habilidade' if sucesso else 'voltar')
                elif evento.key == pygame.K_e:
                    sucesso, _ = partida.ativar_habilidade('limpar_cenario')
                    som('habilidade' if sucesso else 'voltar')
                elif estado == 'boss' and evento.key in (pygame.K_f, pygame.K_j):
                    if partida.atirar():
                        som('ataque')

            elif estado == 'pausa':
                if evento.key == pygame.K_ESCAPE:
                    continuar()
                elif evento.key in (pygame.K_TAB, pygame.K_DOWN, pygame.K_UP):
                    delta = -1 if evento.key == pygame.K_UP else 1
                    foco_pausa = (foco_pausa + delta) % 6
                elif evento.key in (pygame.K_LEFT, pygame.K_RIGHT) and foco_pausa in (1, 2):
                    tipo = 'musica' if foco_pausa == 1 else 'efeitos'
                    antigo = preferencias.volume_musica if tipo == 'musica' else preferencias.volume_efeitos
                    preferencias.ajustar(tipo, antigo + (-0.05 if evento.key == pygame.K_LEFT else 0.05))
                    audio.aplicar_volumes()
                    if tipo == 'efeitos':
                        som()
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    executar_pausa({0: 'continuar', 3: 'audio', 4: 'controles',
                                    5: 'menu'}.get(foco_pausa))

            elif estado == 'controles_pausa':
                if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    estado = 'pausa'
                    som('voltar')

            elif estado == 'confirmar_saida':
                if evento.key == pygame.K_ESCAPE:
                    estado = 'pausa'
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    sair_da_partida()

            elif estado == 'morte' and evento.key == pygame.K_SPACE:
                partida.reiniciar()
                cenario.reiniciar()
                estado = 'jogando'
                som()

        
        if estado == 'revelando':
            tempo_revelacao += dt
            if tempo_revelacao >= 0.7:
                partida.escolher(carta_escolhida)
                carta_escolhida = None
                estado = 'jogando'

        
        
        if estado in ('jogando', 'boss'):
            
            
            if MODO_TESTE and estado == 'boss' and partida.chefe is not None:
                teclas = pygame.key.get_pressed()
                if (teclas[pygame.K_f] or teclas[pygame.K_j]) and partida.chefe.pode_disparar_contra_chefe():
                    if partida.atirar():
                        som('ataque')
            estado_novo = partida.atualizar(dt) if estado == 'jogando' else partida.atualizar_boss(dt)
            if partida.som_pendente:
                som(partida.som_pendente)
                partida.som_pendente = None
            if estado_novo in ('morte', 'vitoria'):
                recorde = max(recorde, int(partida.pontos))
                loja.registrar_recorde(recorde)
            if estado_novo == 'vitoria':
                tempo_vitoria = 0.0
                som()
            estado = estado_novo
        elif estado == 'vitoria':
            tempo_vitoria += dt
            if tempo_vitoria >= 5.5:
                voltar_titulo()

        if estado in ('titulo', 'identificacao', 'configuracoes', 'loja', 'vitoria'):
            audio.tocar('menu_title.ogg', repetir=True)
        elif estado in ('jogando', 'boss', 'cartas', 'revelando'):
            audio.tocar_bioma(partida.fase)
        elif estado == 'morte':
            audio.tocar('GameOver.ogg', repetir=False)

        na_abertura = estado in ('titulo', 'identificacao', 'configuracoes', 'loja')
        congelado = estado in ('pausa', 'controles_pausa', 'confirmar_saida')
        cenario.desenhar(tela,
                        dt if estado == 'jogando' else (dt if na_abertura else 0),
                        partida.velocidade() if estado == 'jogando' else (48 if na_abertura else 0),
                        0 if na_abertura else min(partida.fase, 3))

        if estado == 'titulo':
            partida.dino.definir_acessorio(loja.equipados.get('dino'))
            telas.titulo(tela, recorde, mouse, tempo_telas, partida.dino.frames,
                         escolha_menu, loja.moedas, loja.equipados.get('dino'))
            if clique_pos is not None:
                if telas.BOTAO_JOGAR.collidepoint(clique_pos):
                    abrir_nome()
                    som()
                elif telas.BOTAO_LOJA.collidepoint(clique_pos):
                    abrir_loja()
                elif telas.BOTAO_CONFIGURACOES.collidepoint(clique_pos):
                    estado = 'configuracoes'
                    foco_configuracoes = -1
                    som()
                elif telas.BOTAO_SAIR.collidepoint(clique_pos):
                    pygame.quit()
                    return

        elif estado == 'loja':
            telas.tela_loja(tela, loja, mouse, foco_loja,
                            aviso_loja if tempo_aviso_loja > 0 else '', aba_loja)
            if clique_pos is not None:
                if telas.BOTAO_VOLTAR_LOJA.collidepoint(clique_pos):
                    voltar_titulo()
                elif telas.ABA_COSMETICOS.collidepoint(clique_pos):
                    if aba_loja != 'cosmeticos':
                        mudar_aba('cosmeticos')
                elif telas.ABA_HABILIDADES.collidepoint(clique_pos):
                    if aba_loja != 'habilidades':
                        mudar_aba('habilidades')
                else:
                    areas = telas.BOTOES_ITENS if aba_loja == 'cosmeticos' else telas.BOTOES_HABILIDADES
                    for i, area in enumerate(areas):
                        if area.collidepoint(clique_pos):
                            comprar_item(i)
                            break

        elif estado == 'identificacao':
            telas.identificacao(tela, nome_digitado, mouse, tempo_telas, aviso_nome)
            if clique_pos is not None:
                if telas.BOTAO_COMECAR.collidepoint(clique_pos):
                    iniciar_partida()
                elif telas.BOTAO_VOLTAR_NOME.collidepoint(clique_pos):
                    voltar_titulo()

        elif estado == 'configuracoes':
            telas.configuracoes(tela, preferencias, mouse, audio.disponivel, foco_configuracoes)
            if clique_pos is not None:
                if telas.BOTAO_AUDIO.collidepoint(clique_pos):
                    preferencias.alternar_audio()
                    audio.aplicar_volumes()
                    som()
                elif telas.BOTAO_VOLTAR_CONFIG.collidepoint(clique_pos):
                    voltar_titulo()

        elif estado in ('jogando', 'boss'):
            partida.desenhar(tela, nome, dt)

        elif congelado:
            partida.desenhar(tela, nome, 0)
            if estado == 'pausa':
                telas.pausa(tela, preferencias, mouse, foco_pausa)
                if clique_pos is not None:
                    if telas.PAUSA_CONTINUAR.collidepoint(clique_pos):
                        executar_pausa('continuar')
                    elif telas.PAUSA_AUDIO.collidepoint(clique_pos):
                        executar_pausa('audio')
                    elif telas.PAUSA_CONTROLES.collidepoint(clique_pos):
                        executar_pausa('controles')
                    elif telas.PAUSA_MENU.collidepoint(clique_pos):
                        executar_pausa('menu')
            elif estado == 'controles_pausa':
                telas.controles_pausa(tela, mouse)
                if clique_pos is not None and telas.PAUSA_VOLTAR_CONTROLES.collidepoint(clique_pos):
                    estado = 'pausa'
                    som('voltar')
            elif estado == 'confirmar_saida':
                telas.confirmar_saida(tela, mouse)
                if clique_pos is not None:
                    if telas.CONFIRMAR_SAIR.collidepoint(clique_pos):
                        sair_da_partida()
                    elif telas.CANCELAR_SAIR.collidepoint(clique_pos):
                        estado = 'pausa'
                        som('voltar')

        elif estado == 'cartas':
            areas = telas.escolher_carta(tela, partida.cartas_atuais,
                                        partida.cartas_sistema.imagens, mouse)
            if clique_pos is not None:
                for i, area in enumerate(areas):
                    if area.collidepoint(clique_pos):
                        carta_escolhida = i
                        tempo_revelacao = 0.0
                        estado = 'revelando'
                        som()
                        break

        elif estado == 'revelando':
            telas.escolher_carta(tela, partida.cartas_atuais,
                                partida.cartas_sistema.imagens, mouse,
                                carta_escolhida, min(1.0, tempo_revelacao / 0.55))

        elif estado == 'vitoria':
            telas.cutscene_vitoria(tela, int(partida.pontos),
                                   partida.recompensa_final, tempo_vitoria, partida.dino.frames)

        elif estado == 'morte':
            partida.desenhar(tela, nome, 0)
            telas.morte(tela, partida.pontos, recorde, mouse)
            if clique_pos is not None:
                if telas.BOTAO_REINICIAR.collidepoint(clique_pos):
                    partida.reiniciar()
                    cenario.reiniciar()
                    estado = 'jogando'
                    som()
                elif telas.BOTAO_MENU.collidepoint(clique_pos):
                    voltar_titulo()

        if MODO_TESTE:
            
            if estado == 'jogando':
                restante = pontos_para_o_proximo_chefe(partida.pontos_bioma, partida.fase)
                legenda = f'TESTE | BOSS EM {restante} P'
            elif estado == 'boss':
                legenda = 'TESTE | BOSS SUPER FACIL'
            else:
                legenda = 'TESTE SUPER FACIL'
            texto = fonte_selo_teste.render(legenda, True, (245, 239, 190))
            area = texto.get_rect(bottomright=(LARGURA - 12, ALTURA - 11))
            fundo = area.inflate(18, 10)
            pygame.draw.rect(tela, (14, 34, 35), fundo)
            pygame.draw.rect(tela, (218, 192, 118), fundo, 2)
            tela.blit(texto, area)

        pygame.display.flip()


if __name__ == '__main__':
    executar()
