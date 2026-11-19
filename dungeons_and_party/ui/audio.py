"""Trilhas e efeitos sonoros via Sound/Music do PPlay (arquivos gerados por audio/gerar_audio.py).

Os volumes (0–100) ficam salvos em config.json, na pasta do jogo.
"""
import json
import os

from PPlay.sound import Music, Sound, SoundManager

ARQUIVO_CONFIG = "config.json"
PADRAO = {"volume_musica": 40, "volume_efeitos": 70}

_efeitos = {}
_musica_atual = None
_audio_disponivel = True
_inicializado = False
_config = None


def _carregar_config():
    global _config
    if _config is None:
        _config = dict(PADRAO)
        if os.path.exists(ARQUIVO_CONFIG):
            try:
                with open(ARQUIVO_CONFIG, encoding="utf-8") as arquivo:
                    _config.update(json.load(arquivo))
            except (OSError, ValueError):
                pass
    return _config


def _salvar_config():
    try:
        with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as arquivo:
            json.dump(_config, arquivo, indent=2)
    except OSError:
        pass


def _inicializar():
    global _audio_disponivel, _inicializado
    if _inicializado:
        return
    _inicializado = True
    config = _carregar_config()
    try:
        SoundManager.inicializar()
        SoundManager.set_music_volume(config["volume_musica"])
        SoundManager.set_sfx_volume(config["volume_efeitos"])
    except Exception:  # máquina sem dispositivo de áudio: o jogo segue mudo
        _audio_disponivel = False


def volume(tipo):
    """tipo: 'musica' ou 'efeitos'."""
    return _carregar_config()[f"volume_{tipo}"]


def definir_volume(tipo, valor):
    _inicializar()
    config = _carregar_config()
    config[f"volume_{tipo}"] = max(0, min(100, valor))
    _salvar_config()
    if not _audio_disponivel:
        return
    if tipo == "musica":
        SoundManager.set_music_volume(config["volume_musica"])
    else:
        SoundManager.set_sfx_volume(config["volume_efeitos"])


def tocar_efeito(nome):
    _inicializar()
    if not _audio_disponivel:
        return
    if nome not in _efeitos:
        _efeitos[nome] = Sound(f"sounds/{nome}.wav")
    _efeitos[nome].play()


def tocar_musica(nome):
    """Troca a trilha em loop; não reinicia se a mesma trilha já estiver tocando."""
    global _musica_atual
    _inicializar()
    if not _audio_disponivel or nome == _musica_atual:
        return
    Music(f"sounds/{nome}.wav").play(loops=-1, fade_in_ms=600)
    SoundManager.set_music_volume(_carregar_config()["volume_musica"])
    _musica_atual = nome


def parar_musica():
    global _musica_atual
    if _audio_disponivel and _musica_atual is not None:
        Music("").stop(fade_out_ms=500)
    _musica_atual = None
