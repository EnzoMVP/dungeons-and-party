"""Gera os assets do mapa de nós: fundo de pergaminho, ícones dos nós, anéis de seleção, trilha e marcador."""
import math
import random

import paleta as P
from pixelart import Tela, dither

LARGURA, ALTURA = 320, 180


def gerar_fundo():
    rng = random.Random(3)
    t = Tela(LARGURA, ALTURA)
    manchas = [(rng.uniform(0, LARGURA), rng.uniform(0, ALTURA), rng.uniform(10, 40)) for _ in range(14)]
    for y in range(ALTURA):
        for x in range(LARGURA):
            cor = P.BEGE
            # manchas de envelhecimento
            mancha = max((1 - math.hypot(x - mx, y - my) / r) for mx, my, r in manchas)
            if dither(x, y, max(0.0, mancha) * 0.45):
                cor = P.MARROM
            # grade tênue de cartógrafo
            if (x % 40 == 0 or y % 40 == 0) and dither(x, y, 0.35):
                cor = P.MARROM
            # bordas queimadas
            borda = min(x, y, LARGURA - 1 - x, ALTURA - 1 - y)
            ruido = 3 * math.sin(x * 0.21 + y * 0.13) + 2 * math.sin(x * 0.07 - y * 0.29)
            d = borda + ruido
            if d < 3:
                cor = P.PRETO
            elif d < 6:
                cor = P.MARROM_ESCURO
            elif d < 12 and dither(x, y, (12 - d) / 6):
                cor = P.MARROM
            t.ponto(x, y, cor)
    # rosa dos ventos no canto inferior direito
    cx, cy = 290, 150
    t.poligono([(cx, cy - 16), (cx + 3, cy), (cx, cy + 16), (cx - 3, cy)], P.MARROM_ESCURO)
    t.poligono([(cx - 16, cy), (cx, cy - 3), (cx + 16, cy), (cx, cy + 3)], P.MARROM_ESCURO)
    t.poligono([(cx, cy - 16), (cx + 3, cy), (cx, cy)], P.VERMELHO)
    t.elipse(cx, cy, 2, 2, P.AMARELO)
    t.salvar("mapa/fundo.png")


def _medalhao(t, cx, cy, raio, fundo, luz):
    t.elipse(cx, cy, raio + 1, raio + 1, P.PRETO)
    t.elipse(cx, cy, raio, raio, fundo)
    t.elipse(cx - 1, cy - 1, raio - 2, raio - 2, luz)
    t.elipse(cx, cy, raio - 3, raio - 3, fundo)


def gerar_icones():
    # combate: espadas cruzadas
    t = Tela(20, 20)
    _medalhao(t, 9.5, 9.5, 9, P.CINZA_ESCURO, P.CINZA)
    for (x0, y0, x1, y1) in ((5, 14, 14, 5), (14, 14, 5, 5)):
        t.linha(x0, y0, x1, y1, P.BRANCO)
    t.linha(4, 12, 7, 15, P.AMARELO)
    t.linha(12, 15, 15, 12, P.AMARELO)
    t.salvar("mapa/no_combate.png")

    # recrutamento: aventureiro com sinal de mais
    t = Tela(20, 20)
    _medalhao(t, 9.5, 9.5, 9, P.VERDE_ESCURO, P.VERDE)
    t.elipse(8, 7, 2.5, 2.5, P.BEGE)
    t.poligono([(3, 16), (4, 11), (12, 11), (13, 16)], P.AZUL_CLARO)
    t.ret(13, 4, 5, 1, P.AMARELO)
    t.ret(15, 2, 1, 5, P.AMARELO)
    t.salvar("mapa/no_recrutamento.png")

    # chefe: caveira coroada
    t = Tela(28, 28)
    _medalhao(t, 13.5, 13.5, 13, P.ROXO, P.VERMELHO)
    t.elipse(13.5, 14, 6.5, 6, P.BRANCO)
    t.ret(10, 18, 8, 4, P.BRANCO)
    t.elipse(11, 14, 1.5, 1.5, P.PRETO)
    t.elipse(16, 14, 1.5, 1.5, P.PRETO)
    t.ponto(11, 14, P.VERMELHO)
    t.ponto(16, 14, P.VERMELHO)
    for x in range(10, 18, 2):
        t.ponto(x, 20, P.PRETO)
    t.ret(8, 6, 12, 2, P.AMARELO)
    for x in (8, 12, 16):
        t.poligono([(x, 6), (x + 4, 6), (x + 2, 2)], P.AMARELO)
    t.salvar("mapa/no_chefe.png")

    # evento: interrogação
    t = Tela(20, 20)
    _medalhao(t, 9.5, 9.5, 9, P.AZUL_ESCURO, P.AZUL)
    t.ascii(["..###..", ".##.##.", ".....##", "....##.", "...##..", "...##..", ".......", "...##.."],
            {"#": P.AMARELO}, 6, 5)
    t.salvar("mapa/no_evento.png")

    # descanso: fogueira
    t = Tela(20, 20)
    _medalhao(t, 9.5, 9.5, 9, P.MARROM_ESCURO, P.MARROM)
    t.linha(5, 15, 14, 12, P.BEGE)
    t.linha(5, 12, 14, 15, P.BEGE)
    t.poligono([(6, 13), (9.5, 3), (13, 13)], P.LARANJA)
    t.poligono([(8, 13), (9.5, 7), (11, 13)], P.AMARELO)
    t.salvar("mapa/no_descanso.png")

    # tesouro: baú
    t = Tela(20, 20)
    _medalhao(t, 9.5, 9.5, 9, P.ROXO, P.VERMELHO)
    t.ret(4, 9, 12, 7, P.MARROM)
    t.poligono([(4, 9), (5, 5), (15, 5), (16, 9)], P.MARROM)
    t.ret(4, 9, 12, 1, P.AMARELO)
    t.ret(9, 8, 2, 4, P.AMARELO)
    t.salvar("mapa/no_tesouro.png")

    # anéis de seleção (frame 0 = alcançável, frame 1 = sob o mouse)
    for nome, tamanho in (("anel", 26), ("anel_chefe", 34)):
        folha = Tela(tamanho * 2, tamanho)
        centro = (tamanho - 1) / 2
        for i, (cor, espessura) in enumerate(((P.VERMELHO, 1.6), (P.VERMELHO, 2.6))):
            for y in range(tamanho):
                for x in range(tamanho):
                    d = math.hypot(x - centro, y - centro)
                    if centro - espessura <= d <= centro:
                        pontilhado = i == 1 or (math.degrees(math.atan2(y - centro, x - centro)) % 30) < 18
                        if pontilhado:
                            folha.ponto(i * tamanho + x, y, cor)
        folha.salvar(f"mapa/{nome}.png")

    # pontos da trilha
    for nome, cor in (("trilha", P.MARROM_ESCURO), ("trilha_percorrida", P.VERMELHO)):
        t = Tela(2, 2)
        t.ret(0, 0, 2, 2, cor)
        t.salvar(f"mapa/{nome}.png")

    # marcador do grupo (bandeira)
    t = Tela(10, 14)
    t.ret(1, 0, 1, 14, P.MARROM_ESCURO)
    t.poligono([(2, 1), (10, 3.5), (2, 7)], P.VERMELHO)
    t.ret(2, 1, 5, 1, P.LARANJA)
    t.contornar(P.PRETO)
    t.salvar("mapa/marcador.png")


def gerar():
    gerar_fundo()
    gerar_icones()


if __name__ == "__main__":
    gerar()
