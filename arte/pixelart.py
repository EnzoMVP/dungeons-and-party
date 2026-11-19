"""Helper de produção de pixel art.

Monta mapas de pixels em memória e os renderiza para PNG com Pillow
(cada pixel de arte vira um bloco de ESCALA x ESCALA pixels).
Não faz parte do jogo: o jogo só carrega os PNGs gerados.
"""
import os

from PIL import Image, ImageColor

PASTA_ARTE = os.path.dirname(os.path.abspath(__file__))
PASTA_IMAGENS = os.path.join(PASTA_ARTE, "..", "dungeons_and_party", "images")

# 1 pixel de arte = ESCALA pixels no canvas virtual 960x540 do jogo.
ESCALA = 3

# Matriz de Bayer 4x4 para dithering.
BAYER4 = [
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5],
]


def dither(x, y, intensidade):
    """True se o pixel (x, y) deve receber a cor 'b' numa mistura de intensidade 0..1."""
    return (BAYER4[y % 4][x % 4] + 0.5) / 16 < intensidade


class Tela:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        self.px = [[None] * largura for _ in range(altura)]

    # ---------- primitivas ----------
    def dentro(self, x, y):
        return 0 <= x < self.largura and 0 <= y < self.altura

    def ponto(self, x, y, cor):
        x, y = int(x), int(y)
        if self.dentro(x, y):
            self.px[y][x] = cor

    def get(self, x, y):
        if self.dentro(x, y):
            return self.px[y][x]
        return None

    def ret(self, x, y, w, h, cor):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                self.ponto(xx, yy, cor)

    def ret_contorno(self, x, y, w, h, cor):
        for xx in range(x, x + w):
            self.ponto(xx, y, cor)
            self.ponto(xx, y + h - 1, cor)
        for yy in range(y, y + h):
            self.ponto(x, yy, cor)
            self.ponto(x + w - 1, yy, cor)

    def linha(self, x0, y0, x1, y1, cor):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.ponto(x0, y0, cor)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def elipse(self, cx, cy, rx, ry, cor):
        for yy in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for xx in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if rx > 0 and ry > 0 and ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0:
                    self.ponto(xx, yy, cor)

    def poligono(self, pontos, cor):
        ys = [p[1] for p in pontos]
        for yy in range(int(min(ys)), int(max(ys)) + 1):
            cy = yy + 0.5
            cruzamentos = []
            for i in range(len(pontos)):
                (xa, ya), (xb, yb) = pontos[i], pontos[(i + 1) % len(pontos)]
                if (ya <= cy < yb) or (yb <= cy < ya):
                    cruzamentos.append(xa + (cy - ya) * (xb - xa) / (yb - ya))
            cruzamentos.sort()
            for i in range(0, len(cruzamentos) - 1, 2):
                for xx in range(round(cruzamentos[i]), round(cruzamentos[i + 1])):
                    self.ponto(xx, yy, cor)

    def ascii(self, linhas, mapa, x=0, y=0):
        """Desenha arte ASCII; caracteres fora do mapa são transparentes."""
        for dy, linha in enumerate(linhas):
            for dx, ch in enumerate(linha):
                if ch in mapa:
                    self.ponto(x + dx, y + dy, mapa[ch])

    def colar(self, outra, x, y):
        for yy in range(outra.altura):
            for xx in range(outra.largura):
                cor = outra.px[yy][xx]
                if cor is not None:
                    self.ponto(x + xx, y + yy, cor)

    def contornar(self, cor):
        """Adiciona contorno (vizinhança 4) ao redor de todos os pixels preenchidos."""
        novos = []
        for yy in range(self.altura):
            for xx in range(self.largura):
                if self.px[yy][xx] is None:
                    for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        if self.get(xx + ox, yy + oy) not in (None, cor):
                            novos.append((xx, yy))
                            break
        for xx, yy in novos:
            self.px[yy][xx] = cor

    def substituir(self, mapa):
        for yy in range(self.altura):
            for xx in range(self.largura):
                if self.px[yy][xx] in mapa:
                    self.px[yy][xx] = mapa[self.px[yy][xx]]

    def silhueta(self, cor):
        """Nova tela com todos os pixels preenchidos pintados de uma única cor (ex.: flash de dano)."""
        copia = Tela(self.largura, self.altura)
        for yy in range(self.altura):
            for xx in range(self.largura):
                if self.px[yy][xx] is not None:
                    copia.px[yy][xx] = cor
        return copia

    # ---------- saída ----------
    def salvar(self, caminho_relativo, escala=ESCALA, fundo="transparent", pasta=PASTA_IMAGENS):
        """Renderiza a tela para PNG, ampliando cada pixel de arte para escala x escala."""
        cor_fundo = (0, 0, 0, 0) if fundo == "transparent" else ImageColor.getcolor(fundo, "RGBA")
        img = Image.new("RGBA", (self.largura, self.altura), cor_fundo)
        cores = {}
        for yy in range(self.altura):
            for xx in range(self.largura):
                cor = self.px[yy][xx]
                if cor is None:
                    continue
                if cor not in cores:
                    cores[cor] = (0, 0, 0, 0) if cor == "transparent" else ImageColor.getcolor(cor, "RGBA")
                img.putpixel((xx, yy), cores[cor])
        if escala != 1:
            img = img.resize((self.largura * escala, self.altura * escala), Image.NEAREST)
        saida = os.path.normpath(os.path.join(pasta, caminho_relativo))
        os.makedirs(os.path.dirname(saida), exist_ok=True)
        img.save(saida)
        return saida
