"""Gera trilhas e efeitos sonoros chiptune em WAV (16 bits, mono) para dungeons_and_party/sounds/.

Não faz parte do jogo: usa só a biblioteca padrão (wave, struct, math, random) para sintetizar
ondas quadradas, triangulares e ruído, como nos consoles de 8 bits. Rode: python gerar_audio.py
"""
import math
import os
import random
import struct
import wave

TAXA = 22050
PASTA_SONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dungeons_and_party", "sounds")
NOTAS = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1,
         "A": 0, "A#": 1, "B": 2}


def freq(nota):
    """'A4' -> 440 Hz; None ou '-' -> pausa."""
    if nota in (None, "-"):
        return 0.0
    nome, oitava = nota[:-1], int(nota[-1])
    return 440.0 * 2 ** ((NOTAS[nome] + 12 * (oitava - 4)) / 12)


# ---------------------------------------------------------------- osciladores

def _envelope(i, total, ataque=0.005, soltura=0.03):
    t = i / TAXA
    duracao = total / TAXA
    if t < ataque:
        return t / ataque
    if t > duracao - soltura:
        return max(0.0, (duracao - t) / soltura)
    return 1.0


def quadrada(f_inicio, duracao, volume=0.25, ciclo=0.5, f_fim=None, decaimento=0.0):
    total = int(duracao * TAXA)
    f_fim = f_inicio if f_fim is None else f_fim
    fase = 0.0
    amostras = []
    for i in range(total):
        f = f_inicio + (f_fim - f_inicio) * i / max(1, total)
        fase = (fase + f / TAXA) % 1.0
        valor = 1.0 if fase < ciclo else -1.0
        queda = math.exp(-decaimento * i / TAXA)
        amostras.append(valor * volume * queda * _envelope(i, total) if f > 0 else 0.0)
    return amostras


def triangular(f_inicio, duracao, volume=0.35, f_fim=None, decaimento=0.0):
    total = int(duracao * TAXA)
    f_fim = f_inicio if f_fim is None else f_fim
    fase = 0.0
    amostras = []
    for i in range(total):
        f = f_inicio + (f_fim - f_inicio) * i / max(1, total)
        fase = (fase + f / TAXA) % 1.0
        valor = 4 * abs(fase - 0.5) - 1
        queda = math.exp(-decaimento * i / TAXA)
        amostras.append(valor * volume * queda * _envelope(i, total) if f > 0 else 0.0)
    return amostras


def ruido(duracao, volume=0.2, decaimento=20.0, passo=1, rng=random.Random(1)):
    """Ruído branco; `passo` > 1 repete amostras e deixa o som mais grave."""
    total = int(duracao * TAXA)
    amostras = []
    valor = 0.0
    for i in range(total):
        if i % passo == 0:
            valor = rng.uniform(-1, 1)
        amostras.append(valor * volume * math.exp(-decaimento * i / TAXA) * _envelope(i, total, 0.001, 0.01))
    return amostras


def silencio(duracao):
    return [0.0] * int(duracao * TAXA)


def mixar(trilha, amostras, inicio_seg):
    inicio = int(inicio_seg * TAXA)
    if len(trilha) < inicio + len(amostras):
        trilha.extend([0.0] * (inicio + len(amostras) - len(trilha)))
    for i, valor in enumerate(amostras):
        trilha[inicio + i] += valor


def salvar(nome, amostras, volume_final=0.9):
    os.makedirs(PASTA_SONS, exist_ok=True)
    pico = max(1e-6, max(abs(a) for a in amostras))
    escala = volume_final / pico if pico > volume_final else 1.0
    caminho = os.path.join(PASTA_SONS, f"{nome}.wav")
    with wave.open(caminho, "wb") as arquivo:
        arquivo.setnchannels(1)
        arquivo.setsampwidth(2)
        arquivo.setframerate(TAXA)
        dados = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, a * escala)) * 32767)) for a in amostras)
        arquivo.writeframes(dados)
    print(f"  {nome}.wav ({len(amostras) / TAXA:.1f} s)")


# ---------------------------------------------------------------- trilhas

def _acorde(raiz, tipo):
    """Notas (nomes com oitava) de uma tríade a partir da raiz, ex.: ('A3', 'm')."""
    semitons = [0, 3, 7] if tipo == "m" else [0, 4, 7]
    nomes = list(NOTAS.keys())
    nome, oitava = raiz[:-1], int(raiz[-1])
    base = nomes.index(nome)
    notas = []
    for s in semitons:
        indice = base + s
        notas.append(f"{nomes[indice % 12]}{oitava + indice // 12}")
    return notas


def trilha_exploracao():
    """Tema calmo em Lá menor (Am-F-C-G), 96 bpm, 8 compassos em loop."""
    bpm = 96
    tempo = 60 / bpm
    progressao = [("A2", "m"), ("F2", "M"), ("C3", "M"), ("G2", "M")] * 2
    melodia = [
        "E5", "-", "C5", "D5", "E5", "-", "D5", "C5",
        "A4", "-", "C5", "-", "F5", "E5", "D5", "-",
        "E5", "-", "G5", "-", "E5", "D5", "C5", "D5",
        "D5", "-", "B4", "-", "G4", "-", "-", "-",
        "A4", "C5", "E5", "-", "A5", "-", "G5", "E5",
        "F5", "-", "E5", "D5", "C5", "-", "A4", "-",
        "G4", "C5", "E5", "-", "G5", "F5", "E5", "D5",
        "D5", "-", "-", "B4", "C5", "-", "-", "-",
    ]
    trilha = silencio(8 * 4 * tempo)
    for compasso, (raiz, tipo) in enumerate(progressao):
        inicio = compasso * 4 * tempo
        notas = _acorde(raiz, tipo)
        # baixo em mínimas
        for batida in (0, 2):
            mixar(trilha, triangular(freq(raiz), tempo * 1.9, 0.30), inicio + batida * tempo)
        # arpejo em colcheias, uma oitava acima
        arpejo = [notas[0], notas[1], notas[2], notas[1]] * 2
        for k, nota in enumerate(arpejo):
            nome, oitava = nota[:-1], int(nota[-1]) + 1
            mixar(trilha, quadrada(freq(f"{nome}{oitava}"), tempo / 2 * 0.9, 0.06, ciclo=0.25, decaimento=6),
                  inicio + k * tempo / 2)
    for k, nota in enumerate(melodia):
        if nota != "-":
            mixar(trilha, quadrada(freq(nota), tempo / 2 * 0.95, 0.09, ciclo=0.5, decaimento=2.5), k * tempo / 2)
    salvar("musica_exploracao", trilha)


def trilha_combate():
    """Tema tenso em Ré menor (Dm-Bb-C-A), 144 bpm, 8 compassos em loop com bateria."""
    bpm = 144
    tempo = 60 / bpm
    progressao = [("D2", "m"), ("A#1", "M"), ("C2", "M"), ("A1", "M")] * 2
    melodia = [
        "D5", "D5", "-", "F5", "E5", "-", "D5", "C5",
        "A#4", "-", "D5", "-", "F5", "-", "A5", "G5",
        "E5", "E5", "-", "G5", "F5", "-", "E5", "D5",
        "C#5", "-", "E5", "-", "A5", "-", "-", "-",
        "D5", "F5", "A5", "-", "D6", "-", "C6", "A5",
        "A#5", "-", "A5", "G5", "F5", "-", "D5", "-",
        "C5", "E5", "G5", "-", "C6", "A#5", "A5", "G5",
        "A5", "-", "C#6", "-", "E6", "-", "-", "-",
    ]
    trilha = silencio(8 * 4 * tempo)
    for compasso, (raiz, _tipo) in enumerate(progressao):
        inicio = compasso * 4 * tempo
        nome, oitava = raiz[:-1], int(raiz[-1])
        # baixo pulsante em oitavas (colcheias)
        for k in range(8):
            nota = f"{nome}{oitava + (k % 2)}"
            mixar(trilha, triangular(freq(nota), tempo / 2 * 0.8, 0.30), inicio + k * tempo / 2)
        # bateria: bumbo nos tempos 1 e 3, caixa no 2 e 4, chimbal nos contratempos
        for batida in range(4):
            momento = inicio + batida * tempo
            if batida % 2 == 0:
                mixar(trilha, triangular(150, 0.12, 0.45, f_fim=45, decaimento=18), momento)
            else:
                mixar(trilha, ruido(0.12, 0.22, decaimento=28, passo=2), momento)
            mixar(trilha, ruido(0.03, 0.07, decaimento=90), momento + tempo / 2)
    for k, nota in enumerate(melodia):
        if nota != "-":
            mixar(trilha, quadrada(freq(nota), tempo / 2 * 0.9, 0.08, ciclo=0.125, decaimento=3), k * tempo / 2)
    salvar("musica_combate", trilha)


# ---------------------------------------------------------------- efeitos

def efeitos():
    salvar("comprar", ruido(0.05, 0.25, decaimento=60, passo=1) + quadrada(1400, 0.03, 0.12, ciclo=0.25))
    ataque = ruido(0.14, 0.5, decaimento=25, passo=2)
    mixar(ataque, quadrada(520, 0.10, 0.2, f_fim=140, ciclo=0.5), 0)
    salvar("carta_ataque", ataque)
    defesa = triangular(880, 0.18, 0.4, decaimento=14)
    mixar(defesa, quadrada(1320, 0.12, 0.10, ciclo=0.25, decaimento=20), 0.01)
    salvar("carta_defesa", defesa)
    magia = silencio(0.3)
    for k, nota in enumerate(("C6", "E6", "G6", "C7")):
        mixar(magia, quadrada(freq(nota), 0.08, 0.14, ciclo=0.125, decaimento=12), k * 0.05)
    salvar("carta_magia", magia)
    dano = triangular(200, 0.16, 0.5, f_fim=55)
    mixar(dano, ruido(0.10, 0.35, decaimento=30, passo=3), 0)
    salvar("dano", dano)
    dano_forte = triangular(160, 0.32, 0.6, f_fim=40)
    mixar(dano_forte, ruido(0.25, 0.45, decaimento=12, passo=4), 0)
    salvar("dano_forte", dano_forte)
    salvar("bloqueio", triangular(1500, 0.12, 0.35, decaimento=25))
    salvar("buff", quadrada(300, 0.28, 0.18, f_fim=950, ciclo=0.25))
    morte = quadrada(420, 0.5, 0.2, f_fim=55, ciclo=0.5)
    mixar(morte, ruido(0.45, 0.25, decaimento=6, passo=5), 0)
    salvar("morte", morte)
    vitoria = silencio(1.1)
    for momento, nota, duracao in ((0, "C5", 0.12), (0.13, "E5", 0.12), (0.26, "G5", 0.12), (0.4, "C6", 0.6)):
        mixar(vitoria, quadrada(freq(nota), duracao, 0.2, ciclo=0.5, decaimento=1.5), momento)
        mixar(vitoria, triangular(freq(nota) / 2, duracao, 0.25), momento)
    salvar("vitoria", vitoria)
    derrota = silencio(1.6)
    for k, nota in enumerate(("G4", "F#4", "F4", "E4")):
        mixar(derrota, triangular(freq(nota), 0.38 if k < 3 else 0.7, 0.4), k * 0.35)
        mixar(derrota, quadrada(freq(nota) / 2, 0.38 if k < 3 else 0.7, 0.07, ciclo=0.5), k * 0.35)
    salvar("derrota", derrota)
    recrutar = silencio(0.6)
    for k, nota in enumerate(("G5", "B5", "D6", "G6")):
        mixar(recrutar, quadrada(freq(nota), 0.1 if k < 3 else 0.3, 0.16, ciclo=0.25, decaimento=4), k * 0.08)
    salvar("recrutar", recrutar)
    cura = silencio(0.5)
    for k, nota in enumerate(("E5", "G#5", "B5", "E6")):
        mixar(cura, triangular(freq(nota), 0.18, 0.35, decaimento=8), k * 0.07)
    salvar("cura", cura)
    salvar("clique", quadrada(900, 0.04, 0.18, ciclo=0.5, decaimento=40))
    passo = quadrada(660, 0.06, 0.16, ciclo=0.25)
    mixar(passo, quadrada(880, 0.08, 0.16, ciclo=0.25, decaimento=15), 0.07)
    salvar("passo_mapa", passo)
    # duas cartas se fundindo: dois tons convergem num acorde brilhante, com um brilho no final
    combinar = silencio(0.55)
    mixar(combinar, quadrada(freq("C5"), 0.25, 0.12, ciclo=0.25, f_fim=freq("G5")), 0)
    mixar(combinar, quadrada(freq("C6"), 0.25, 0.10, ciclo=0.125, f_fim=freq("G5")), 0)
    for nota in ("G5", "B5", "D6"):
        mixar(combinar, quadrada(freq(nota), 0.28, 0.10, ciclo=0.25, decaimento=6), 0.25)
    mixar(combinar, triangular(freq("G4"), 0.28, 0.25, decaimento=5), 0.25)
    mixar(combinar, ruido(0.08, 0.12, decaimento=35, passo=1), 0.25)
    salvar("combinar", combinar)
    # carta especial: impacto grave + estouro de ruído + acorde maior ascendente
    especial = silencio(0.7)
    mixar(especial, triangular(180, 0.35, 0.55, f_fim=40), 0)
    mixar(especial, ruido(0.3, 0.45, decaimento=10, passo=4), 0)
    for k, nota in enumerate(("C5", "E5", "G5", "C6")):
        mixar(especial, quadrada(freq(nota), 0.12 if k < 3 else 0.35, 0.14, ciclo=0.5, decaimento=4),
              0.08 + k * 0.08)
    salvar("carta_especial", especial)
    # imortal: o herói se recusa a cair (duas batidas de coração graves e um urro menor ascendente)
    # (fica por último: o ruído usa um gerador compartilhado e os sons anteriores não mudam)
    renascer = silencio(0.95)
    for momento in (0, 0.2):
        mixar(renascer, triangular(95, 0.14, 0.6, f_fim=45), momento)
    mixar(renascer, ruido(0.45, 0.3, decaimento=5, passo=6), 0.38)
    for k, nota in enumerate(("A3", "C4", "E4", "A4")):
        mixar(renascer, quadrada(freq(nota), 0.14 if k < 3 else 0.4, 0.15, ciclo=0.5, decaimento=3), 0.38 + k * 0.08)
    salvar("renascer", renascer)


if __name__ == "__main__":
    print("Gerando sons em dungeons_and_party/sounds/")
    trilha_exploracao()
    trilha_combate()
    efeitos()
