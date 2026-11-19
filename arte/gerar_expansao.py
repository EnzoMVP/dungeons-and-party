"""Assets da expansão: o berserker, as ilustrações das cartas novas (passivas, descarte, roubo de vida
e habilidades), os ícones dos estados novos, o marcador de descarte e as relíquias novas."""
import math

import paleta as P
from pixelart import Tela
from gerar_sprites import _adaga, _anel, _corte, _faisca, _gota, _salvar_personagem


# ---------------------------------------------------------------- berserker

def _desenhar_berserker():
    t = Tela(48, 48)
    # manto de pele de lobo (atrás)
    t.poligono([(13, 19), (31, 19), (33, 39), (27, 37), (22, 40), (16, 37), (11, 40)], P.MARROM_ESCURO)
    t.poligono([(13, 19), (16, 19), (13, 38), (11, 40)], P.MARROM)
    for x, y in ((12, 40), (17, 38), (23, 41), (28, 38), (32, 40)):
        t.ponto(x, y, P.MARROM)
    # pernas: calça escura com faixas de couro cruzadas
    for x0 in (18, 25):
        t.ret(x0, 33, 5, 9, P.CINZA_ESCURO)
        t.ret(x0, 33, 1, 9, P.CINZA)
        for y in (35, 38):
            t.linha(x0, y, x0 + 4, y + 2, P.BEGE)
    # botas com borda de pele
    t.ret(17, 42, 6, 4, P.MARROM)
    t.ret(25, 42, 7, 4, P.MARROM)
    t.ret(17, 42, 6, 1, P.BEGE)
    t.ret(25, 42, 7, 1, P.BEGE)
    t.ret(17, 45, 6, 1, P.MARROM_ESCURO)
    t.ret(25, 45, 7, 1, P.MARROM_ESCURO)
    # tronco nu e musculoso (luz à esquerda, sombra à direita)
    t.ret(16, 20, 15, 13, P.BEGE)
    t.ret(29, 20, 2, 13, P.LARANJA)
    t.ret(16, 20, 1, 13, P.BRANCO)
    for y in range(22, 31, 2):
        t.ponto(23, y, P.LARANJA)
    for y in (25, 28):
        t.ret(19, y, 3, 1, P.LARANJA)
        t.ret(25, y, 3, 1, P.LARANJA)
    t.linha(18, 22, 20, 24, P.VERMELHO)  # cicatriz
    # cinto largo com fivela
    t.ret(16, 31, 15, 3, P.MARROM)
    t.ret(16, 31, 15, 1, P.BEGE)
    t.ret(21, 31, 4, 3, P.AMARELO)
    t.ponto(22, 32, P.MARROM_ESCURO)
    # braço de trás (esquerda), punho cerrado
    t.ret(12, 21, 4, 9, P.BEGE)
    t.ret(12, 21, 1, 9, P.BRANCO)
    t.ret(12, 25, 4, 2, P.MARROM)  # bracelete
    t.ret(11, 30, 5, 4, P.BEGE)
    t.ret(11, 33, 5, 1, P.LARANJA)
    # pele sobre os ombros
    t.elipse(15, 20, 4.5, 3, P.MARROM)
    t.elipse(31, 20, 4.5, 3, P.MARROM)
    t.elipse(14, 19, 2.5, 1.5, P.BEGE)
    t.elipse(30, 19, 2.5, 1.5, P.BEGE)
    t.ret(19, 18, 9, 2, P.MARROM)
    # cabeça, com a faixa de pintura azul nos olhos
    t.ret(19, 8, 10, 8, P.BEGE)
    t.ret(27, 8, 2, 8, P.LARANJA)
    t.ret(19, 10, 10, 2, P.AZUL)
    t.ponto(24, 10, P.BRANCO)
    t.ponto(27, 10, P.BRANCO)
    t.ponto(25, 10, P.PRETO)
    t.ponto(28, 10, P.PRETO)
    # barba ruiva trançada
    t.poligono([(19, 13), (29, 13), (28, 19), (25, 24), (21, 19)], P.LARANJA)
    t.poligono([(26, 13), (29, 13), (28, 19), (25, 24)], P.VERMELHO)
    t.ret(23, 14, 4, 1, P.VERMELHO)  # boca
    t.linha(21, 14, 23, 19, P.AMARELO)
    t.ponto(25, 24, P.AMARELO)
    t.ponto(25, 25, P.AMARELO)
    # elmo arredondado com chifres grossos
    for lado in (-1, 1):
        cx = 24 + lado * 6
        chifre = [(cx, 7), (cx + lado * 4, 6), (cx + lado * 6, 3), (cx + lado * 6, 0),
                  (cx + lado * 4, 2), (cx + lado * 3, 4), (cx, 4)]
        t.poligono(chifre, P.BEGE)
        t.linha(cx, 4, cx + lado * 3, 3, P.BRANCO)
        t.ponto(cx + lado * 6, 0, P.BRANCO)
        t.ponto(cx + lado * 6, 1, P.BRANCO)
        t.linha(cx + lado * 1, 7, cx + lado * 4, 6, P.MARROM)
    t.elipse(24, 6, 6.5, 4, P.CINZA)
    t.elipse(22, 4, 3, 1.5, P.CINZA_CLARO)
    t.ret(17, 8, 14, 2, P.CINZA)
    t.ret(17, 8, 14, 1, P.CINZA_CLARO)
    t.ret(28, 4, 3, 5, P.CINZA_ESCURO)
    t.ret(24, 8, 2, 4, P.CINZA_CLARO)  # proteção do nariz
    # braço da frente segurando o machado
    t.ret(30, 20, 4, 6, P.BEGE)
    t.ret(32, 20, 2, 6, P.LARANJA)
    t.ret(31, 24, 4, 2, P.MARROM)  # bracelete
    # machado barbado: cabo longo e lâmina larga
    t.linha(34, 44, 37, 4, P.MARROM)
    t.linha(35, 44, 38, 4, P.MARROM_ESCURO)
    t.ret(33, 17, 4, 4, P.BEGE)  # mão no cabo
    t.ret(33, 20, 4, 1, P.LARANJA)
    t.poligono([(38, 3), (45, 0), (47, 7), (46, 16), (42, 12), (38, 10)], P.CINZA_CLARO)
    t.poligono([(41, 3), (45, 1), (46, 15), (41, 10)], P.CINZA)
    t.linha(46, 2, 47, 8, P.BRANCO)
    t.linha(47, 8, 46, 15, P.BRANCO)
    t.ret(36, 3, 3, 8, P.CINZA_ESCURO)
    t.ponto(37, 5, P.AMARELO)
    t.ponto(37, 8, P.AMARELO)
    return t


def _extra_berserker(t):
    # os olhos brilham em vermelho no segundo quadro (coordenadas já descidas 1 pixel)
    t.ponto(25, 11, P.VERMELHO)
    t.ponto(28, 11, P.VERMELHO)


def gerar_berserker():
    _salvar_personagem(_desenhar_berserker(), "herois/berserker", corte=33, extra=_extra_berserker)


# ---------------------------------------------------------------- peças de desenho

def _salvar_ilustracao(t, nome):
    t.contornar(P.PRETO)
    t.salvar(f"cartas/ilustracao_{nome}.png")


def _machado(t, cabo, topo, largura_lamina, altura_lamina, dupla=False):
    """Machado com o cabo de `cabo` até `topo` e a lâmina (voltada para a direita) presa no topo."""
    (x0, y0), (x1, y1) = cabo, topo
    t.linha(x0, y0, x1, y1, P.MARROM)
    t.linha(x0 + 1, y0, x1 + 1, y1, P.MARROM_ESCURO)
    meia = altura_lamina / 2
    for lado in ((1, -1) if dupla else (1,)):
        borda = x1 + lado * largura_lamina
        t.poligono([(x1, y1 - 2), (borda, y1 - meia - 1), (borda + lado, y1), (borda, y1 + meia + 1),
                    (x1, y1 + 3)], P.CINZA_CLARO)
        t.poligono([(x1 + lado * 2, y1 - 1), (borda - lado * 2, y1 - meia + 1), (borda - lado * 2, y1 + meia - 1),
                    (x1 + lado * 2, y1 + 2)], P.CINZA)
        t.linha(borda, y1 - meia - 1, borda + lado, y1, P.BRANCO)
        t.linha(borda + lado, y1, borda, y1 + meia + 1, P.BRANCO)
    t.ret(x1 - 1, y1 - 2, 3, 6, P.CINZA_ESCURO)
    t.ponto(x1, y1, P.AMARELO)


def _coracao(t, cx, cy, raio, cor=P.VERMELHO, luz=P.LARANJA):
    t.elipse(cx - raio * 0.55, cy - raio * 0.3, raio * 0.6, raio * 0.6, cor)
    t.elipse(cx + raio * 0.55, cy - raio * 0.3, raio * 0.6, raio * 0.6, cor)
    t.poligono([(cx - raio * 1.12, cy - raio * 0.1), (cx + raio * 1.12, cy - raio * 0.1), (cx, cy + raio * 1.1)], cor)
    t.elipse(cx - raio * 0.6, cy - raio * 0.45, raio * 0.22, raio * 0.22, luz)


def _orbe(t, cx, cy, raio):
    """Orbe de energia laranja (como o indicador de energia)."""
    t.elipse(cx, cy, raio, raio, P.LARANJA)
    t.elipse(cx - raio * 0.2, cy - raio * 0.2, raio * 0.65, raio * 0.65, P.AMARELO)
    t.ponto(round(cx - raio * 0.45), round(cy - raio * 0.45), P.BRANCO)


def _chama(t, cx, base, altura, largura):
    """Chama de três camadas com a base em (cx, base)."""
    for escala, cor in ((1.0, P.VERMELHO), (0.68, P.LARANJA), (0.38, P.AMARELO)):
        a, l = altura * escala, largura * escala
        t.poligono([(cx - l, base), (cx - l * 1.1, base - a * 0.45), (cx - l * 0.3, base - a * 0.7),
                    (cx, base - a), (cx + l * 0.5, base - a * 0.6), (cx + l * 1.1, base - a * 0.4),
                    (cx + l, base)], cor)


def _cartinha(t, x, y, moldura=P.VERMELHO, luz=P.LARANJA, apagada=False):
    """Carta miniatura 9x12 com canto superior esquerdo em (x, y)."""
    t.ret(x, y, 9, 12, P.PRETO)
    t.ret(x + 1, y + 1, 7, 10, P.CINZA if apagada else moldura)
    t.ret(x + 1, y + 1, 7, 1, P.CINZA_CLARO if apagada else luz)
    t.ret(x + 2, y + 2, 5, 4, P.CINZA_ESCURO if apagada else P.AZUL_ESCURO)
    t.ret(x + 2, y + 7, 5, 3, P.CINZA_CLARO if apagada else P.BEGE)


def _seta(t, x0, y0, x1, y1, cor):
    t.linha(x0, y0, x1, y1, cor)
    t.linha(x0, y0 + 1, x1, y1 + 1, cor)
    t.poligono([(x1 + 1, y1 - 3), (x1 + 5, y1 + 0.5), (x1 + 1, y1 + 4)], cor)


# ---------------------------------------------------------------- ilustrações: guerreiro, mago e ladino

def gerar_ilustracoes_classes():
    # DISCIPLINA (passiva: +energia): estandarte com um orbe de energia no topo
    t = Tela(40, 28)
    t.ret(15, 5, 2, 23, P.MARROM)
    t.ret(16, 5, 1, 23, P.MARROM_ESCURO)
    t.poligono([(17, 7), (31, 7), (29, 13), (31, 19), (17, 19)], P.VERMELHO)
    t.poligono([(17, 7), (31, 7), (30, 9), (17, 9)], P.LARANJA)
    t.ret(17, 17, 13, 2, P.ROXO)
    t.poligono([(22, 10), (25, 10), (25, 12), (23.5, 16), (22, 12)], P.AMARELO)
    t.ret(21, 11, 5, 1, P.AMARELO)
    _orbe(t, 16, 4, 3.5)
    for x, y in ((9, 6), (23, 2), (8, 14), (35, 4)):
        _faisca(t, x, y, P.BRANCO, P.AMARELO)
    _salvar_ilustracao(t, "disciplina")

    # VETERANO (cresce a cada uso): espada gasta e marcas de contagem entalhadas
    t = Tela(40, 28)
    t.linha(15, 22, 33, 4, P.BRANCO)
    t.linha(16, 22, 34, 4, P.CINZA_CLARO)
    t.linha(15, 23, 33, 5, P.CINZA)
    for x, y in ((22, 15), (27, 10)):  # dentes na lâmina
        t.ponto(x, y, None)
        t.ponto(x + 1, y, P.CINZA)
    t.linha(12, 19, 18, 25, P.AMARELO)
    t.linha(12, 20, 17, 25, P.LARANJA)
    t.linha(10, 26, 13, 23, P.MARROM)
    for i in range(4):
        t.ret(4 + i * 3, 13, 1, 9, P.BEGE)
    t.linha(3, 21, 14, 14, P.AMARELO)
    for x, y in ((36, 11), (30, 19), (24, 5)):
        t.ponto(x, y, P.AMARELO)
    _salvar_ilustracao(t, "veterano")

    # ESCUDADA (dano igual ao bloqueio): escudo avançando com rastro e estrela de impacto
    t = Tela(40, 28)
    for y in (8, 13, 18):
        t.linha(2, y, 9, y, P.CIANO)
    t.poligono([(10, 3), (24, 3), (24, 14), (17, 24), (10, 14)], P.CINZA_CLARO)
    t.poligono([(12, 5), (22, 5), (22, 14), (17, 21), (12, 14)], P.AZUL)
    t.ret(18, 5, 4, 12, P.AZUL_ESCURO)
    t.ret(16, 5, 2, 15, P.CIANO)
    t.ret(12, 10, 10, 2, P.CIANO)
    t.ponto(11, 4, P.BRANCO)
    estrela = []
    for k in range(16):
        ang = math.radians(k * 22.5)
        raio = 9 if k % 2 == 0 else 4
        estrela.append((31 + math.cos(ang) * raio, 13 + math.sin(ang) * raio))
    t.poligono(estrela, P.AMARELO)
    t.elipse(31, 13, 3, 3, P.BRANCO)
    _salvar_ilustracao(t, "escudada")

    # SABEDORIA (passiva: +cartas): coruja de olhos arregalados sobre um livro
    t = Tela(40, 28)
    t.poligono([(9, 23), (20, 20), (31, 23), (31, 27), (20, 25), (9, 27)], P.BEGE)
    t.linha(20, 20, 20, 25, P.MARROM)
    t.ret(9, 26, 22, 1, P.MARROM)
    t.elipse(20, 13, 8, 9, P.MARROM)
    t.elipse(20, 15, 5, 6, P.BEGE)
    for x in (17, 20, 23):
        t.ponto(x, 16, P.MARROM)
        t.ponto(x + 1, 19, P.MARROM)
    t.poligono([(12, 5), (15, 7), (13, 9)], P.MARROM)
    t.poligono([(28, 5), (25, 7), (27, 9)], P.MARROM)
    for cx in (16.5, 23.5):
        t.elipse(cx, 10, 3.2, 3.2, P.AMARELO)
        t.elipse(cx, 10, 1.4, 1.4, P.PRETO)
        t.ponto(round(cx - 1), 9, P.BRANCO)
    t.poligono([(19, 12), (21, 12), (20, 15)], P.LARANJA)
    for x, y in ((6, 8), (34, 7), (35, 17), (5, 17)):
        _faisca(t, x, y, P.BRANCO, P.CIANO)
    _salvar_ilustracao(t, "sabedoria")

    # TRANSMUTAR (descarta 1, compra 2): carta apagada vira duas cartas novas
    t = Tela(40, 28)
    _cartinha(t, 5, 10, apagada=True)
    t.linha(6, 11, 13, 21, P.PRETO)
    _seta(t, 16, 15, 20, 15, P.CIANO)
    _cartinha(t, 26, 5, P.AZUL, P.AZUL_CLARO)
    _cartinha(t, 30, 13, P.AZUL, P.AZUL_CLARO)
    _anel(t, 19.5, 15.5, 7.5, 1, P.AZUL_CLARO)
    for x, y in ((19, 3), (37, 4), (24, 25)):
        _faisca(t, x, y, P.BRANCO, P.CIANO)
    _salvar_ilustracao(t, "transmutar")

    # DRENAR (dano que vira vida): coração do inimigo vertendo sangue até um orbe arcano
    t = Tela(40, 28)
    _coracao(t, 30, 13, 6)
    t.elipse(10, 17, 5, 5, P.AZUL)
    t.elipse(9, 16, 3, 3, P.AZUL_CLARO)
    t.ponto(8, 15, P.BRANCO)
    for i in range(9):
        s = i / 8
        x = 24 - s * 11
        y = 14 + math.sin(s * math.pi) * -6 + s * 2
        t.elipse(x, y, 1.2, 1.2, P.VERMELHO)
    t.ponto(19, 9, P.LARANJA)
    _anel(t, 10, 17, 7, 1, P.CIANO)
    _salvar_ilustracao(t, "drenar")

    # RAJADA (dano igual à velocidade): adaga cortando o vento, com rajadas acima e abaixo
    t = Tela(40, 28)
    for y, x0, x1 in ((5, 14, 36), (22, 6, 26), (26, 16, 34)):
        _corte(t, (x0, y), (x1, y - 2), 1.2, 0.5)
    for y, x0, x1 in ((11, 3, 11), (16, 2, 9)):
        t.linha(x0, y, x1, y, P.CIANO)
    _adaga(t, (12, 17), (35, 11))
    _adaga(t, (13, 18), (36, 12))
    t.ponto(38, 11, P.BRANCO)
    _salvar_ilustracao(t, "rajada")

    # ACELERAR (velocidade x2): bota alada com rastro de velocidade
    t = Tela(40, 28)
    for y in (9, 14, 19):
        t.linha(3, y, 11, y, P.VERDE_CLARO)
    t.ret(17, 5, 8, 14, P.MARROM)
    t.poligono([(17, 17), (25, 17), (33, 20), (34, 24), (17, 24)], P.MARROM)
    t.ret(17, 5, 2, 19, P.BEGE)
    t.ret(16, 4, 10, 3, P.MARROM_ESCURO)
    t.ret(17, 23, 17, 2, P.MARROM_ESCURO)
    t.poligono([(25, 8), (31, 3), (37, 3), (33, 6), (38, 7), (33, 10), (26, 12)], P.BRANCO)
    t.linha(27, 9, 35, 5, P.CINZA_CLARO)
    t.linha(27, 11, 35, 8, P.CINZA_CLARO)
    _salvar_ilustracao(t, "acelerar")

    # TRAPAÇA (descarta 1, +2 energia): carta marcada virando e dois orbes de energia
    t = Tela(40, 28)
    t.poligono([(9, 6), (21, 4), (24, 22), (12, 24)], P.BEGE)
    t.poligono([(10, 7), (20, 5), (22, 20), (13, 22)], P.BRANCO)
    t.poligono([(15, 10), (18, 12), (16, 16), (13, 14)], P.VERMELHO)
    t.ponto(11, 8, P.VERMELHO)
    t.ponto(21, 20, P.VERMELHO)
    _orbe(t, 30, 8, 4)
    _orbe(t, 32, 20, 4)
    for x, y in ((26, 14), (37, 13), (6, 16)):
        _faisca(t, x, y, P.BRANCO, P.AMARELO)
    _salvar_ilustracao(t, "trapaca")

    # PEÇONHA (passiva: ataques envenenam): serpente dando o bote com presas pingando
    t = Tela(40, 28)
    pontos = [(4 + i, 22 + math.sin(i / 3.2) * 3) for i in range(0, 20)]
    for x, y in pontos:
        t.elipse(x, y, 2, 2, P.VERDE)
    for x, y in pontos[::3]:
        t.ponto(round(x), round(y) - 1, P.VERDE_CLARO)
    t.poligono([(21, 20), (24, 11), (30, 7), (36, 9), (34, 13), (28, 13), (25, 21)], P.VERDE)
    t.poligono([(24, 11), (30, 7), (36, 9), (30, 9)], P.VERDE_CLARO)
    t.poligono([(28, 13), (35, 13), (33, 17), (29, 16)], P.VERMELHO)
    t.ret(29, 13, 1, 3, P.BRANCO)
    t.ret(33, 13, 1, 3, P.BRANCO)
    t.ponto(31, 9, P.AMARELO)
    t.ponto(32, 9, P.PRETO)
    _gota(t, 29, 18, "pequena")
    _gota(t, 34, 21, "pequena")
    _salvar_ilustracao(t, "peconha")


# ---------------------------------------------------------------- ilustrações: berserker

def gerar_ilustracoes_berserker():
    # MACHADADA: machado de uma lâmina, em diagonal (canto superior direito livre para o ícone de combo)
    t = Tela(40, 28)
    _machado(t, (9, 26), (23, 9), 8, 12)
    for x, y in ((31, 22), (6, 12), (15, 3)):
        t.ponto(x, y, P.CIANO)
    _salvar_ilustracao(t, "machado")

    # BROQUEL: escudo redondo de tábuas com umbo de ferro
    t = Tela(40, 28)
    t.elipse(20, 14, 12, 12, P.CINZA)
    t.elipse(20, 14, 10.5, 10.5, P.MARROM)
    for x in range(11, 30, 4):
        t.linha(x, 4, x, 24, P.MARROM_ESCURO)
    t.poligono([(20, 4), (24, 14), (20, 24), (16, 14)], P.AZUL)
    t.poligono([(10, 14), (20, 11), (30, 14), (20, 17)], P.AZUL)
    t.elipse(20, 14, 3.5, 3.5, P.CINZA_CLARO)
    t.elipse(19, 13, 1.5, 1.5, P.BRANCO)
    t.linha(12, 5, 16, 3, P.CINZA_CLARO)
    for ang in range(0, 360, 45):
        t.ponto(round(20 + math.cos(math.radians(ang)) * 11), round(14 + math.sin(math.radians(ang)) * 11), P.CINZA_CLARO)
    _salvar_ilustracao(t, "broquel")

    # BRUTAL: machado de duas lâminas manchado de sangue
    t = Tela(40, 28)
    _machado(t, (10, 27), (20, 10), 9, 13, dupla=True)
    for x, y in ((28, 14), (26, 20), (13, 13), (30, 5)):
        t.ret(x, y, 1, 2, P.VERMELHO)
    _salvar_ilustracao(t, "machado_duplo")

    # SANGRIA (vida vira energia): gota de sangue passando para um orbe de energia
    t = Tela(40, 28)
    t.poligono([(12, 4), (18, 14), (6, 14)], P.VERMELHO)
    t.elipse(12, 16, 6.3, 6.3, P.VERMELHO)
    t.elipse(10, 15, 2, 2.5, P.LARANJA)
    t.ponto(9, 14, P.BRANCO)
    _seta(t, 20, 15, 23, 15, P.AMARELO)
    _orbe(t, 32, 15, 5.5)
    for x, y in ((25, 5), (37, 6), (27, 24)):
        _faisca(t, x, y, P.BRANCO, P.AMARELO)
    _salvar_ilustracao(t, "sangria")

    # SEDE (buff de roubo de vida): chifre de beber curvo transbordando sangue
    t = Tela(40, 28)
    caminho = [(6 + 25 * k / 30, 25 - 5 * k / 30 - 12 * (k / 30) ** 2, 0.6 + 4.2 * k / 30) for k in range(31)]
    for x, y, r in caminho:
        t.elipse(x, y + 1, r, r, P.MARROM)
    for x, y, r in caminho:
        t.elipse(x, y, r, r * 0.8, P.BEGE)
    for k in (15, 24):
        x, y, r = caminho[k]
        t.linha(round(x), round(y - r), round(x), round(y + r), P.AMARELO)
    x, y, r = caminho[-1]
    t.elipse(x, y - 1, 2, r, P.VERMELHO)
    t.elipse(x - 0.5, y - 2, 1, r * 0.5, P.LARANJA)
    t.poligono([(x - 1, y + 2), (x + 2, y + 1), (x + 1, y + 8), (x - 1, y + 6)], P.VERMELHO)
    t.ret(round(x), round(y) + 10, 1, 2, P.VERMELHO)
    t.ret(round(x) + 3, round(y) + 6, 1, 2, P.VERMELHO)
    _salvar_ilustracao(t, "sede")

    # SANGRAR (marca o inimigo): três garras vermelhas com gotas
    t = Tela(40, 28)
    for i, x in enumerate((12, 19, 26)):
        for k in range(18):
            s = k / 17
            px = x + s * 6 - math.sin(s * math.pi) * 2
            py = 3 + s * 21
            largura = 1.8 * math.sin(s * math.pi) + 0.3
            t.elipse(px, py, largura, 0.8, P.VERMELHO)
        t.linha(x + 1, 6, x + 4, 18, P.LARANJA)
    for x, y in ((8, 20), (34, 9), (35, 22)):
        t.ret(x, y, 1, 2, P.VERMELHO)
    _salvar_ilustracao(t, "sangrar")

    # IMORTAL (passiva: volta com 1 de vida): caveira de olhos em brasa sobre uma aura de fúria
    t = Tela(40, 28)
    for k in range(12):
        ang = math.radians(k * 30)
        t.linha(20, 13, round(20 + math.cos(ang) * 16), round(13 + math.sin(ang) * 12),
                P.VERMELHO if k % 2 else P.ROXO)
    t.elipse(20, 12, 8, 7.5, P.BRANCO)
    t.ret(15, 16, 10, 7, P.BRANCO)
    t.ret(15, 21, 10, 2, P.CINZA_CLARO)
    t.elipse(22, 10, 5, 4, P.CINZA_CLARO)
    t.elipse(20, 10, 6.5, 6, P.BRANCO)
    for cx in (17, 23):
        t.elipse(cx, 13, 2.2, 2.2, P.PRETO)
        t.ponto(cx, 13, P.VERMELHO)
        t.ponto(cx - 1, 13, P.LARANJA)
    t.poligono([(19, 16), (21, 16), (20, 18)], P.PRETO)
    for x in (16, 18, 20, 22):
        t.ret(x, 20, 1, 3, P.CINZA)
    _salvar_ilustracao(t, "imortal")

    # IRA (+dano a cada rodada): chamas crescendo da esquerda para a direita
    t = Tela(40, 28)
    _chama(t, 9, 26, 9, 3)
    _chama(t, 19, 26, 15, 4.5)
    _chama(t, 31, 26, 24, 6.5)
    t.ret(3, 26, 34, 2, P.MARROM_ESCURO)
    _salvar_ilustracao(t, "ira")

    # DESVARIO (descarta 2, golpe forte): redemoinho vermelho com duas cartas rasgadas e um corte
    t = Tela(40, 28)
    for i in range(40):
        ang = i * 0.42
        raio = 2 + i * 0.3
        t.elipse(20 + math.cos(ang) * raio * 1.3, 14 + math.sin(ang) * raio * 0.9, 1, 1,
                 P.VERMELHO if i % 3 else P.ROXO)
    _cartinha(t, 4, 3, apagada=True)
    _cartinha(t, 28, 14, apagada=True)
    t.linha(4, 5, 12, 14, P.VERMELHO)
    t.linha(28, 16, 36, 25, P.VERMELHO)
    _corte(t, (8, 25), (35, 2), 2.5, 1.2)
    _salvar_ilustracao(t, "desvario")

    # VINGANÇA (dano igual à vida perdida): coração partido atravessado por uma espada
    t = Tela(40, 28)
    _coracao(t, 20, 13, 10)
    t.linha(20, 4, 18, 9, P.PRETO)
    t.linha(18, 9, 22, 14, P.PRETO)
    t.linha(22, 14, 19, 19, P.PRETO)
    t.linha(19, 19, 20, 24, P.PRETO)
    t.linha(3, 25, 36, 2, P.BRANCO)
    t.linha(4, 25, 37, 2, P.CINZA_CLARO)
    t.linha(6, 20, 10, 25, P.AMARELO)
    t.linha(2, 27, 5, 24, P.MARROM)
    for x, y in ((31, 18), (8, 7), (34, 25)):
        t.ret(x, y, 1, 2, P.VERMELHO)
    _salvar_ilustracao(t, "vinganca")

    # SELVAGERIA (passiva: +roubo de vida): cabeça de lobo rosnando, com a boca vermelha
    t = Tela(40, 28)
    t.poligono([(8, 26), (10, 12), (14, 5), (17, 10), (22, 9), (25, 4), (28, 11), (35, 16), (36, 20),
                (30, 22), (26, 26)], P.CINZA)
    t.poligono([(10, 12), (14, 5), (17, 10), (15, 14)], P.CINZA_CLARO)
    t.poligono([(14, 8), (15, 11), (13, 11)], P.ROXO)
    t.poligono([(25, 7), (27, 11), (24, 11)], P.ROXO)
    t.poligono([(26, 17), (36, 20), (30, 22), (26, 22)], P.VERMELHO)
    for x in (28, 31, 34):
        t.poligono([(x, 18), (x + 1, 18), (x + 0.5, 20.5)], P.BRANCO)
    t.ponto(29, 22, P.BRANCO)
    t.ponto(32, 21, P.BRANCO)
    t.ret(34, 15, 2, 2, P.PRETO)
    t.ret(22, 12, 3, 2, P.AMARELO)
    t.ponto(24, 12, P.PRETO)
    t.linha(19, 16, 24, 22, P.CINZA_ESCURO)
    t.linha(12, 18, 16, 25, P.CINZA_ESCURO)
    _salvar_ilustracao(t, "selvageria")

    # RAGNAROK (especial): machado de duas lâminas sobre um mar de chamas, sob um céu partido por raios
    t = Tela(40, 28)
    for cx, altura, largura in ((6, 13, 4), (15, 18, 5), (25, 16, 5), (34, 12, 4)):
        _chama(t, cx, 28, altura, largura)
    t.poligono([(31, 0), (37, 0), (33, 7), (36, 7), (29, 15), (31, 9), (28, 9)], P.AZUL_CLARO)
    t.linha(33, 1, 30, 8, P.BRANCO)
    t.poligono([(2, 12), (6, 12), (4, 16), (6, 16), (1, 22), (2, 17), (0, 17)], P.AZUL_CLARO)
    _machado(t, (13, 27), (21, 7), 9, 14, dupla=True)
    for x, y in ((14, 2), (38, 18), (7, 7)):
        _faisca(t, x, y, P.BRANCO, P.AMARELO)
    _salvar_ilustracao(t, "ragnarok")


# ---------------------------------------------------------------- ícones

def _icone(nome, largura, altura, desenhar):
    t = Tela(largura, altura)
    desenhar(t)
    t.contornar(P.PRETO)
    t.salvar(f"{nome}.png")


def gerar_icones_estados():
    """Ícones 11x11 dos estados novos (sobre a barra de vida), do atributo de roubo e do marcador de descarte."""
    def sede(t):  # gota de sangue com duas presas
        t.poligono([(5.5, 0.5), (9, 6), (2, 6)], P.VERMELHO)
        t.elipse(5.5, 7, 3.5, 3.2, P.VERMELHO)
        t.elipse(4.3, 6.3, 1, 1.2, P.LARANJA)
        t.poligono([(3, 8), (5, 8), (4, 10)], P.BRANCO)
        t.poligono([(6, 8), (8, 8), (7, 10)], P.BRANCO)

    def acelerado(t):  # seta dupla verde
        for dx in (0, 4):
            t.poligono([(1 + dx, 1), (4 + dx, 1), (8 + dx, 5.5), (4 + dx, 10), (1 + dx, 10), (5 + dx, 5.5)],
                       P.VERDE_CLARO if dx else P.VERDE)

    def marcado(t):  # mira vermelha
        _anel(t, 5, 5, 5, 1.3, P.VERMELHO)
        t.ret(5, 0, 1, 11, P.VERMELHO)
        t.ret(0, 5, 11, 1, P.VERMELHO)
        t.ponto(5, 5, P.AMARELO)

    def bonus_energia(t):
        _orbe(t, 5, 5, 4.6)

    def bonus_compra(t):  # duas cartas azuis
        for ox, oy, moldura in ((3, 0, P.AZUL), (0, 2, P.AZUL_CLARO)):
            t.ret(ox, oy, 7, 9, P.PRETO)
            t.ret(ox + 1, oy + 1, 5, 7, moldura)
            t.ret(ox + 2, oy + 2, 3, 3, P.AZUL_ESCURO)

    def peconha(t):  # presa pingando veneno
        t.poligono([(1, 0), (8, 0), (3, 8)], P.BRANCO)
        t.poligono([(5, 0), (8, 0), (3, 8)], P.CINZA_CLARO)
        _gota(t, 6, 6, "pequena")

    def selvageria(t):  # boca de lobo com presas
        t.elipse(5, 6, 5, 4, P.VERMELHO)
        for x in (1, 4, 7):
            t.poligono([(x, 2), (x + 2, 2), (x + 1, 6)], P.BRANCO)
        t.poligono([(3, 10), (4, 7), (5, 10)], P.BRANCO)
        t.poligono([(6, 10), (7, 7), (8, 10)], P.BRANCO)

    def imortal(t):  # caveira de olhos vermelhos
        t.elipse(5.5, 4.5, 4.5, 4, P.BRANCO)
        t.ret(3, 7, 6, 3, P.BRANCO)
        t.ret(3, 4, 2, 2, P.VERMELHO)
        t.ret(7, 4, 2, 2, P.VERMELHO)
        t.ponto(5, 7, P.PRETO)
        t.ponto(4, 9, P.CINZA)
        t.ponto(6, 9, P.CINZA)

    def frenesi(t):  # explosão vermelha
        pontos = []
        for k in range(16):
            ang = math.radians(k * 22.5 + 11)
            raio = 5.4 if k % 2 == 0 else 2.6
            pontos.append((5.5 + math.cos(ang) * raio, 5.5 + math.sin(ang) * raio))
        t.poligono(pontos, P.VERMELHO)
        t.elipse(5.5, 5.5, 2, 2, P.LARANJA)
        t.ponto(5, 5, P.AMARELO)

    for nome, funcao in (("sede", sede), ("acelerado", acelerado), ("marcado", marcado),
                         ("bonus_energia", bonus_energia), ("bonus_compra", bonus_compra), ("peconha", peconha),
                         ("selvageria", selvageria), ("imortal", imortal), ("frenesi", frenesi)):
        _icone(f"icones/{nome}", 11, 11, funcao)

    def roubo(t):  # atributo: gota de sangue
        t.poligono([(4.5, 0), (8, 5), (1, 5)], P.VERMELHO)
        t.elipse(4.5, 5.6, 3.4, 3.2, P.VERMELHO)
        t.elipse(3.3, 5, 0.9, 1.1, P.LARANJA)
    _icone("icones/atr_roubo", 9, 9, roubo)

    def descartar(t):  # carta que vai para o descarte: círculo vermelho com X
        t.elipse(7.5, 7.5, 7.5, 7.5, P.VERMELHO)
        t.elipse(7, 7, 5.5, 5.5, P.LARANJA)
        t.elipse(7.5, 7.5, 5, 5, P.VERMELHO)
        for d in (-1, 0, 1):
            t.linha(4 + d, 4, 11 + d, 11, P.BRANCO)
            t.linha(11 + d, 4, 4 + d, 11, P.BRANCO)
    _icone("icones/descartar", 16, 16, descartar)


def gerar_reliquias():
    def calice(t):  # cálice dourado cheio de sangue
        t.poligono([(2, 2), (14, 2), (12, 8), (8, 10), (4, 8)], P.AMARELO)
        t.poligono([(3, 2), (13, 2), (12, 4), (4, 4)], P.VERMELHO)
        t.ret(10, 4, 2, 4, P.LARANJA)
        t.ret(7, 10, 2, 3, P.AMARELO)
        t.ret(4, 13, 8, 2, P.AMARELO)
        t.ret(10, 13, 2, 2, P.LARANJA)
        t.ret(4, 5, 1, 2, P.BRANCO)
        t.ret(13, 4, 1, 2, P.VERMELHO)

    def bolsa(t):  # bolsa de couro com uma carta saindo
        t.ret(8, 1, 6, 8, P.PRETO)
        t.ret(9, 2, 4, 6, P.VERMELHO)
        t.ret(10, 3, 2, 2, P.AMARELO)
        t.elipse(7.5, 10.5, 6, 4.5, P.MARROM)
        t.poligono([(3, 7), (12, 7), (10, 5), (5, 5)], P.MARROM)
        t.ret(3, 7, 10, 1, P.AMARELO)
        t.elipse(5, 10, 1.5, 1.5, P.BEGE)
        t.ret(10, 12, 3, 2, P.MARROM_ESCURO)

    for nome, funcao in (("calice_de_sangue", calice), ("bolsa_de_truques", bolsa)):
        _icone(f"reliquias/{nome}", 16, 16, funcao)


def gerar():
    gerar_berserker()
    gerar_ilustracoes_classes()
    gerar_ilustracoes_berserker()
    gerar_icones_estados()
    gerar_reliquias()


if __name__ == "__main__":
    gerar()
