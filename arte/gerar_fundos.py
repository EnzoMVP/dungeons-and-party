"""Gera os cenários 320x180 (masmorra de combate e entrada do menu)."""
import math
import random

import paleta as P
from pixelart import Tela, dither

LARGURA, ALTURA = 320, 180
HORIZONTE = 80  # linha onde a parede encontra o chão

LUZ_QUENTE = {
    P.PRETO: P.MARROM_ESCURO,
    P.AZUL_ESCURO: P.MARROM_ESCURO,
    P.CINZA_ESCURO: P.MARROM,
    P.CINZA: P.BEGE,
}


def _parede(t, rng):
    tons = {}
    for y in range(HORIZONTE):
        linha = y // 8
        desloc = 8 if linha % 2 else 0
        by = y % 8
        for x in range(LARGURA):
            bx = (x + desloc) % 16
            tijolo = (linha, (x + desloc) // 16)
            if tijolo not in tons:
                tons[tijolo] = rng.choice([P.CINZA_ESCURO] * 5 + [P.AZUL_ESCURO] * 2)
            if by == 7 or bx == 15:
                cor = P.PRETO
            elif by == 0 and dither(x, y, 0.6):
                cor = P.CINZA
            elif bx == 0 and dither(x, y, 0.3):
                cor = P.CINZA
            else:
                cor = tons[tijolo]
            # escurece em direção ao teto
            if dither(x, y, (1 - y / HORIZONTE) * 0.75):
                cor = P.PRETO if cor != P.CINZA else P.CINZA_ESCURO
            t.ponto(x, y, cor)


def _chao(t):
    fx = LARGURA / 2
    fy = HORIZONTE - 60  # ponto de fuga
    for y in range(HORIZONTE, ALTURA):
        prof = (y - HORIZONTE) / (ALTURA - HORIZONTE)
        # linhas horizontais em perspectiva
        k = math.sqrt(prof) * 9
        horizontal = (k % 1) < (0.09 + 0.03 * prof)
        for x in range(LARGURA):
            u = (x - fx) / (y - fy) * 160
            vertical = (u % 32) < 1.6 * (y - fy) / 160 * 1.2
            if horizontal or vertical:
                cor = P.PRETO
            else:
                cor = P.CINZA_ESCURO
                if dither(x, y, 0.15 * (1 - prof)):
                    cor = P.CINZA
            if dither(x, y, prof * 0.65):
                cor = P.PRETO if cor != P.CINZA_ESCURO else P.AZUL_ESCURO
            t.ponto(x, y, cor)
    t.ret(0, HORIZONTE, LARGURA, 1, P.PRETO)
    for x in range(LARGURA):
        if dither(x, HORIZONTE + 1, 0.5):
            t.ponto(x, HORIZONTE + 1, P.PRETO)


def _luz_tocha(t, cx, cy, raio):
    for y in range(max(0, cy - raio), min(ALTURA, cy + raio)):
        for x in range(max(0, cx - raio), min(LARGURA, cx + raio)):
            d = math.hypot(x - cx, (y - cy) * 1.2)
            intensidade = max(0.0, 1 - d / raio) * 0.9
            cor = t.get(x, y)
            if cor in LUZ_QUENTE and dither(x, y, intensidade):
                if cor == P.CINZA and intensidade < 0.55:
                    continue
                t.ponto(x, y, LUZ_QUENTE[cor])


def _tocha(t, cx, cy):
    t.ret(cx - 2, cy + 3, 5, 2, P.MARROM_ESCURO)
    t.ret(cx - 1, cy + 5, 3, 4, P.MARROM_ESCURO)
    t.ret(cx - 1, cy + 5, 1, 4, P.MARROM)
    t.ret(cx - 3, cy + 2, 7, 1, P.PRETO)
    t.elipse(cx, cy - 2, 2.5, 5, P.VERMELHO)
    t.elipse(cx, cy - 1, 2, 3.5, P.LARANJA)
    t.elipse(cx, cy, 1, 2, P.AMARELO)
    t.ponto(cx, cy - 6, P.LARANJA)
    t.ponto(cx, cy + 1, P.BRANCO)


def _arco(t, cx, topo, rx, base, degraus):
    cy = topo + rx
    # vão escuro
    for y in range(topo, base):
        for x in range(cx - rx, cx + rx + 1):
            dentro = y >= cy or ((x - cx) / rx) ** 2 + ((y - cy) / rx) ** 2 <= 1
            if dentro:
                borda = min(x - (cx - rx), (cx + rx) - x) / rx
                t.ponto(x, y, P.AZUL_ESCURO if dither(x, y, 0.35 * (1 - borda * 3)) else P.PRETO)
    # degraus descendo para a escuridão
    for i in range(degraus):
        y = base - 2 - i * 4
        largura = rx - i * 3
        if largura <= 2:
            break
        for x in range(cx - largura, cx + largura + 1):
            if dither(x, y, 0.8 - i * 0.12):
                t.ponto(x, y, P.CINZA_ESCURO)
    # aduelas de pedra
    for ang in range(0, 181, 1):
        a = math.radians(ang)
        for r in range(rx + 1, rx + 6):
            x = round(cx + math.cos(a) * r)
            y = round(cy - math.sin(a) * r)
            junta = (ang % 20) < 2 or r == rx + 5
            t.ponto(x, y, P.PRETO if junta else (P.CINZA if r <= rx + 2 else P.CINZA_ESCURO))
    for lado in (-1, 1):
        x0 = cx + lado * (rx + 1) if lado > 0 else cx - rx - 5
        for y in range(cy, base):
            for x in range(x0, x0 + 5):
                junta = (y - cy) % 8 == 7 or x == (x0 + 4 if lado > 0 else x0)
                t.ponto(x, y, P.PRETO if junta else (P.CINZA if (x - x0 < 2) == (lado < 0) else P.CINZA_ESCURO))


def _pilar(t, x0, largura):
    for y in range(0, HORIZONTE + 6):
        for x in range(x0, x0 + largura):
            rel = (x - x0) / largura
            if rel < 0.2:
                cor = P.CINZA
            elif rel > 0.8:
                cor = P.PRETO
            else:
                cor = P.CINZA_ESCURO
            if y % 24 == 23:
                cor = P.PRETO
            if dither(x, y, (1 - y / HORIZONTE) * 0.6):
                cor = P.PRETO if cor != P.CINZA else P.CINZA_ESCURO
            t.ponto(x, y, cor)
    t.ret(x0 - 2, HORIZONTE, largura + 4, 6, P.CINZA_ESCURO)
    t.ret(x0 - 2, HORIZONTE, largura + 4, 1, P.CINZA)
    t.ret(x0 - 2, HORIZONTE + 6, largura + 4, 1, P.PRETO)


def _nevoa(t, rng, centro_y, espessura, forca):
    fase = rng.random() * 10
    for y in range(max(0, centro_y - espessura * 2), min(ALTURA, centro_y + espessura * 2)):
        for x in range(LARGURA):
            onda = 0.55 + 0.3 * math.sin(x / 17 + fase) + 0.15 * math.sin(x / 7 + fase * 2)
            intensidade = forca * math.exp(-((y - centro_y) / espessura) ** 2) * onda
            if dither(x, y, intensidade):
                cor = t.get(x, y)
                t.ponto(x, y, P.CINZA if cor in (P.PRETO, P.AZUL_ESCURO, P.MARROM_ESCURO) else P.CINZA_CLARO)


def _vinheta(t, forca):
    for y in range(ALTURA):
        for x in range(LARGURA):
            d = math.hypot((x - LARGURA / 2) / (LARGURA / 2), (y - ALTURA / 2) / (ALTURA / 2))
            if dither(x, y, max(0.0, d - 0.75) * forca):
                t.ponto(x, y, P.PRETO)


def gerar_masmorra():
    rng = random.Random(7)
    t = Tela(LARGURA, ALTURA)
    _parede(t, rng)
    _chao(t)
    _arco(t, 160, 22, 26, HORIZONTE, 5)
    for x in (0, 302):
        _pilar(t, x, 18)
    for x in (92, 228):
        _luz_tocha(t, x, 38, 34)
        _tocha(t, x, 38)
    _nevoa(t, rng, HORIZONTE + 4, 7, 0.28)
    _vinheta(t, 1.4)
    t.salvar("fundos/masmorra.png")


def gerar_menu():
    rng = random.Random(21)
    t = Tela(LARGURA, ALTURA)
    _parede(t, rng)
    _chao(t)
    _arco(t, 160, 8, 44, HORIZONTE, 9)
    for x in (58, 262):
        _luz_tocha(t, x, 46, 40)
        _tocha(t, x, 46)
    _nevoa(t, rng, HORIZONTE + 2, 9, 0.3)
    _nevoa(t, rng, 150, 12, 0.12)
    _vinheta(t, 2.0)
    t.salvar("fundos/menu.png")


def gerar_nevoa():
    """Camadas de névoa (320x40, fundo transparente) que deslizam em paralaxe sobre os cenários."""
    for nome, semente, densidade, cor in (("nevoa_longe", 5, 0.30, P.CINZA), ("nevoa_perto", 9, 0.22, P.CINZA_CLARO)):
        rng = random.Random(semente)
        fases = [rng.random() * 10 for _ in range(3)]
        t = Tela(LARGURA, 40)
        for y in range(40):
            for x in range(LARGURA):
                # ondas com período que divide a largura, para a camada repetir sem emenda
                onda = (0.5 + 0.3 * math.sin(2 * math.pi * x / 160 + fases[0])
                        + 0.2 * math.sin(2 * math.pi * x / 40 + fases[1]))
                perfil = math.exp(-((y - 20) / (9 + 4 * math.sin(2 * math.pi * x / 80 + fases[2]))) ** 2)
                if dither(x, y, densidade * onda * perfil * 2):
                    t.ponto(x, y, cor)
        t.salvar(f"fundos/{nome}.png")


def gerar():
    gerar_masmorra()
    gerar_menu()
    gerar_nevoa()


if __name__ == "__main__":
    gerar()
