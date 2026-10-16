"""Preferencias locais leves para o menu, sem dependencias externas."""
import json
import math
from pathlib import Path

CAMINHO = Path(__file__).resolve().parent.parent / 'configuracoes.json'
PADRAO = {'volume_musica': 0.35, 'volume_efeitos': 0.60,
          'audio_ativo': True, 'ultimo_nome': ''}


def _volume(valor, padrao):
    
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return padrao
    if not math.isfinite(valor):
        return padrao
    return round(max(0.0, min(1.0, float(valor))), 2)


class Preferencias:
    def __init__(self, caminho=CAMINHO):
        self.caminho = Path(caminho)
        self.volume_musica = PADRAO['volume_musica']
        self.volume_efeitos = PADRAO['volume_efeitos']
        self.audio_ativo = PADRAO['audio_ativo']
        self.ultimo_nome = PADRAO['ultimo_nome']
        self.carregar()

    def carregar(self):
        try:
            with self.caminho.open('r', encoding='utf-8') as arquivo:
                dados = json.load(arquivo)
            if not isinstance(dados, dict):
                return
        except (OSError, ValueError, TypeError):
            return
        self.volume_musica = _volume(dados.get('volume_musica'), self.volume_musica)
        self.volume_efeitos = _volume(dados.get('volume_efeitos'), self.volume_efeitos)
        if isinstance(dados.get('audio_ativo'), bool):
            self.audio_ativo = dados['audio_ativo']
        if isinstance(dados.get('ultimo_nome'), str):
            self.ultimo_nome = dados['ultimo_nome'].strip()[:16]

    def salvar(self):
        dados = {
            'volume_musica': self.volume_musica,
            'volume_efeitos': self.volume_efeitos,
            'audio_ativo': self.audio_ativo,
            'ultimo_nome': self.ultimo_nome,
        }
        try:
            
            temporario = self.caminho.with_suffix('.json.tmp')
            temporario.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
            temporario.replace(self.caminho)
        except OSError as erro:
            print('Nao foi possivel salvar configuracoes:', erro)

    def ajustar(self, tipo, valor):
        if tipo == 'musica':
            self.volume_musica = _volume(valor, self.volume_musica)
        elif tipo == 'efeitos':
            self.volume_efeitos = _volume(valor, self.volume_efeitos)
        else:
            return
        self.salvar()

    def alternar_audio(self):
        self.audio_ativo = not self.audio_ativo
        self.salvar()

    def guardar_nome(self, nome):
        self.ultimo_nome = str(nome).strip()[:16]
        self.salvar()
