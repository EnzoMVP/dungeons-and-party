"""Gera sprites de entidades, ícones, cartas e elementos de UI."""
import math

import paleta as P
from pixelart import Tela, dither
from gerar_fonte import mascara_do_caractere


# ---------------------------------------------------------------- entidades

def gerar_guerreiro():
    t = Tela(48, 48)
    # penacho
    t.elipse(19, 6, 6, 3, P.VERMELHO)
    t.elipse(13, 9, 3, 2, P.VERMELHO)
    t.linha(15, 5, 22, 4, P.LARANJA)
    t.ponto(11, 9, P.ROXO)
    t.ponto(12, 10, P.ROXO)
    # pernas e botas
    for x0 in (17, 25):
        t.ret(x0, 34, 5, 9, P.CINZA)
        t.ret(x0, 34, 1, 9, P.CINZA_CLARO)
        t.ret(x0 + 4, 34, 1, 9, P.CINZA_ESCURO)
        t.ret(x0, 38, 5, 2, P.CINZA_CLARO)
    t.ret(16, 42, 6, 4, P.MARROM_ESCURO)
    t.ret(25, 42, 7, 4, P.MARROM_ESCURO)
    t.ret(16, 42, 6, 1, P.MARROM)
    t.ret(25, 42, 7, 1, P.MARROM)
    # tronco (couraça)
    t.ret(15, 20, 17, 14, P.CINZA)
    t.ret(15, 20, 3, 14, P.CINZA_CLARO)
    t.ret(29, 20, 3, 14, P.CINZA_ESCURO)
    t.ret(18, 21, 4, 3, P.BRANCO)
    # tabardo
    t.ret(19, 24, 9, 14, P.VERMELHO)
    t.ret(26, 24, 2, 14, P.ROXO)
    t.ret(19, 24, 1, 14, P.LARANJA)
    for x in range(19, 28, 2):
        t.ponto(x, 38, P.VERMELHO)
    # cinto
    t.ret(15, 31, 17, 2, P.MARROM)
    t.ret(22, 31, 3, 2, P.AMARELO)
    # braço de trás + espada
    t.linha(15, 22, 11, 28, P.CINZA)
    t.linha(16, 22, 12, 28, P.CINZA)
    t.linha(14, 23, 10, 28, P.CINZA_CLARO)
    t.ret(10, 6, 3, 18, P.CINZA_CLARO)
    t.ret(10, 6, 1, 18, P.BRANCO)
    t.ret(12, 6, 1, 18, P.CINZA)
    t.ponto(11, 5, P.BRANCO)
    t.ret(7, 24, 9, 2, P.AMARELO)
    t.ret(7, 25, 9, 1, P.LARANJA)
    t.ret(10, 26, 3, 4, P.MARROM)
    t.ret(10, 30, 3, 1, P.AMARELO)
    # ombreiras
    t.elipse(15, 21, 4, 3, P.CINZA)
    t.elipse(14, 20, 2, 1, P.CINZA_CLARO)
    t.elipse(31, 21, 4, 3, P.CINZA)
    t.elipse(30, 20, 2, 1, P.CINZA_CLARO)
    # elmo
    t.elipse(23, 12, 7, 6, P.CINZA)
    t.ret(16, 12, 15, 8, P.CINZA)
    t.elipse(21, 9, 3, 2, P.CINZA_CLARO)
    t.ret(16, 12, 2, 8, P.CINZA_CLARO)
    t.ret(28, 12, 3, 8, P.CINZA_ESCURO)
    t.ret(22, 14, 9, 2, P.PRETO)
    t.ponto(26, 17, P.PRETO)
    t.ponto(28, 17, P.PRETO)
    t.ret(23, 7, 1, 12, P.CINZA_CLARO)
    # escudo (frente)
    externo = [(30, 20), (42, 20), (42, 31), (36, 40), (30, 31)]
    interno = [(32, 22), (40, 22), (40, 31), (36, 37), (32, 31)]
    t.poligono(externo, P.CINZA_CLARO)
    t.poligono(interno, P.VERMELHO)
    t.ret(38, 22, 2, 10, P.ROXO)
    t.ret(35, 22, 2, 14, P.AMARELO)
    t.ret(32, 25, 8, 2, P.AMARELO)
    t.ponto(31, 21, P.BRANCO)
    _salvar_personagem(t, "herois/guerreiro", corte=34)


def _salvar_personagem(t, caminho_sem_extensao, corte=None, extra=None, quadro2=None):
    """Salva a folha de 2 quadros (96x48) do personagem, que o jogo alterna para dar vida ao sprite,
    e a folha com as silhuetas brancas (flash ao receber dano).

    O 2º quadro é `quadro2`, se dado; senão é a "respiração" de `t`: tudo acima da linha `corte`
    desce 1 pixel, e `extra(tela)` pinta detalhes próprios (chamas, olhos...) por cima.
    Os quadros chegam sem contorno; o contorno é aplicado aqui.
    """
    if quadro2 is None:
        quadro2 = _respirar(t, corte)
        if extra:
            extra(quadro2)
    folha = Tela(t.largura * 2, t.altura)
    flash = Tela(t.largura * 2, t.altura)
    for i, quadro in enumerate((t, quadro2)):
        quadro.contornar(P.PRETO)
        folha.colar(quadro, i * t.largura, 0)
        flash.colar(quadro.silhueta(P.BRANCO), i * t.largura, 0)
    folha.salvar(f"{caminho_sem_extensao}.png")
    flash.salvar(f"{caminho_sem_extensao}_flash.png")


def _respirar(t, corte):
    """Cópia de `t` com as linhas acima de `corte` descidas 1 pixel (as de baixo ficam paradas)."""
    nova = Tela(t.largura, t.altura)
    for y in range(t.altura - 1, -1, -1):
        for x in range(t.largura):
            cor = t.px[y][x]
            if cor is not None:
                nova.ponto(x, y + 1 if y < corte else y, cor)
    return nova


def _trocar_pontos(t, apagar, acender):
    """Apaga os pontos de `apagar` e pinta os de `acender` [(x, y, cor)] (brilhos que piscam)."""
    for x, y in apagar:
        t.ponto(x, y, None)
    for x, y, cor in acender:
        t.ponto(x, y, cor)


def _extra_cultista(t):
    # a chama do cajado tremula (coordenadas já descidas 1 pixel pela respiração)
    t.elipse(9, 7, 3, 3.5, P.VERMELHO)
    t.elipse(9, 8, 2, 2.5, P.LARANJA)
    t.ponto(9, 8, P.AMARELO)
    t.ponto(9, 7, P.AMARELO)
    _trocar_pontos(t, [(12, 2), (5, 4)], [(6, 1, P.LARANJA), (12, 4, P.AMARELO), (10, 0, P.LARANJA)])


def _extra_mago(t):
    # o orbe pulsa e as faíscas mudam de lugar
    t.elipse(38, 6, 2.5, 2.5, P.CIANO)
    t.ponto(38, 6, P.BRANCO)
    _trocar_pontos(t, [(43, 3), (33, 2), (44, 10)], [(42, 1, P.CIANO), (34, 5, P.CIANO), (43, 7, P.BRANCO)])


def _extra_rei_esqueleto(t):
    # os olhos arcanos brilham mais forte
    for x in (20, 26):
        t.ponto(x, 12, P.BRANCO)
        t.ponto(x - 1, 12, P.CIANO)
        t.ponto(x + 1, 12, P.CIANO)


def _osso(t, x0, y0, x1, y1, cor=P.BRANCO, sombra=P.CINZA_CLARO):
    t.linha(x0, y0, x1, y1, cor)
    t.linha(x0 + 1, y0, x1 + 1, y1, sombra)


def _desenhar_esqueleto(t):
    # espada enferrujada (braço da frente, voltado para a esquerda)
    t.linha(9, 26, 3, 7, P.CINZA_CLARO)
    t.linha(10, 26, 4, 7, P.CINZA)
    t.ponto(5, 12, P.MARROM)
    t.ponto(7, 19, P.MARROM)
    t.ponto(4, 9, P.LARANJA)
    t.linha(6, 26, 12, 24, P.MARROM_ESCURO)
    t.linha(9, 27, 10, 30, P.MARROM)
    # braço da frente
    _osso(t, 15, 21, 12, 27)
    _osso(t, 12, 27, 9, 26)
    # braço de trás
    _osso(t, 31, 21, 34, 28)
    _osso(t, 34, 28, 35, 34)
    t.ret(34, 34, 3, 2, P.CINZA_CLARO)
    # pernas
    _osso(t, 20, 35, 19, 44)
    _osso(t, 27, 35, 28, 44)
    t.ret(18, 39, 4, 2, P.BRANCO)
    t.ret(27, 39, 4, 2, P.BRANCO)
    t.ret(15, 44, 7, 2, P.BRANCO)
    t.ret(25, 44, 7, 2, P.BRANCO)
    t.ret(15, 45, 7, 1, P.CINZA_CLARO)
    t.ret(25, 45, 7, 1, P.CINZA_CLARO)
    # coluna e costelas
    t.ret(23, 20, 2, 15, P.CINZA_CLARO)
    for y, (xa, xb) in zip((22, 25, 28, 31), ((16, 31), (16, 31), (17, 30), (19, 28))):
        t.ret(xa, y, xb - xa + 1, 1, P.BRANCO)
        t.ponto(xb, y, P.CINZA_CLARO)
    t.ret(15, 21, 18, 1, P.BRANCO)
    # tanga esfarrapada
    t.ret(18, 33, 12, 4, P.ROXO)
    t.ret(18, 33, 12, 1, P.VERMELHO)
    for x in range(18, 30, 3):
        t.ret(x, 37, 2, 2, P.ROXO)
    # crânio
    t.elipse(24, 10, 7, 6, P.BRANCO)
    t.ret(19, 14, 10, 5, P.BRANCO)
    t.ret(27, 8, 3, 10, P.CINZA_CLARO)
    t.ret(19, 18, 10, 1, P.CINZA_CLARO)
    t.elipse(20, 11, 2, 2, P.PRETO)
    t.elipse(26, 11, 2, 2, P.PRETO)
    t.ponto(20, 11, P.VERMELHO)
    t.ponto(26, 11, P.VERMELHO)
    t.ret(22, 14, 2, 2, P.PRETO)
    for x in range(19, 29, 2):
        t.ponto(x, 17, P.PRETO)


def gerar_esqueleto():
    t = Tela(48, 48)
    _desenhar_esqueleto(t)
    _salvar_personagem(t, "inimigos/esqueleto", corte=35)


def gerar_rei_esqueleto():
    t = Tela(48, 48)
    # manto real atrás do corpo
    t.poligono([(14, 19), (34, 19), (40, 46), (8, 46)], P.ROXO)
    t.poligono([(29, 19), (34, 19), (40, 46), (33, 46)], P.PRETO)
    t.ret(8, 45, 33, 1, P.VERMELHO)
    _desenhar_esqueleto(t)
    # gola de pele e ombreiras douradas
    t.ret(14, 19, 20, 3, P.BRANCO)
    for x in range(14, 34, 3):
        t.ponto(x, 21, P.CINZA_CLARO)
    t.elipse(14, 21, 3, 2, P.AMARELO)
    t.elipse(33, 21, 3, 2, P.AMARELO)
    # olhos arcanos
    t.ponto(20, 11, P.CIANO)
    t.ponto(26, 11, P.CIANO)
    # coroa
    t.ret(17, 2, 15, 3, P.AMARELO)
    for x in (17, 21, 25, 29):
        t.poligono([(x, 2), (x + 3, 2), (x + 1.5, -2)], P.AMARELO)
    t.ret(17, 4, 15, 1, P.LARANJA)
    t.ponto(24, 3, P.VERMELHO)
    t.ponto(19, 3, P.CIANO)
    t.ponto(29, 3, P.CIANO)
    # espada grande reluzente (substitui a enferrujada)
    t.linha(9, 26, 3, 5, P.BRANCO)
    t.linha(10, 26, 4, 5, P.CINZA_CLARO)
    t.linha(4, 23, 13, 21, P.AMARELO)
    _salvar_personagem(t, "inimigos/rei_esqueleto", corte=35, extra=_extra_rei_esqueleto)


# ---------------------------------------------------------------- ícones

def gerar_icones():
    # intenção: ataque
    t = Tela(16, 16)
    t.linha(4, 11, 12, 3, P.BRANCO)
    t.linha(5, 11, 13, 3, P.CINZA_CLARO)
    t.linha(4, 12, 12, 4, P.CINZA_CLARO)
    t.linha(2, 9, 6, 13, P.AMARELO)
    t.linha(2, 13, 3, 14, P.MARROM)
    t.linha(3, 12, 4, 13, P.MARROM)
    t.contornar(P.PRETO)
    t.salvar("icones/intencao_ataque.png")

    # intenção: defesa
    t = Tela(16, 16)
    t.poligono([(3, 2), (13, 2), (13, 9), (8, 14), (3, 9)], P.CIANO)
    t.poligono([(5, 4), (11, 4), (11, 9), (8, 12), (5, 9)], P.AZUL)
    t.ret(8, 4, 3, 7, P.AZUL_ESCURO)
    t.ponto(4, 3, P.BRANCO)
    t.contornar(P.PRETO)
    t.salvar("icones/intencao_defesa.png")

    # marcadores sobre personagens: alvo do inimigo (vermelho) e seleção do jogador (dourado)
    for nome, cor, luz in (("alvo", P.VERMELHO, P.LARANJA), ("selecao", P.AMARELO, P.BRANCO)):
        t = Tela(13, 11)
        t.poligono([(1, 1), (12, 1), (6.5, 10)], cor)
        t.ret(2, 1, 9, 1, luz)
        t.contornar(P.PRETO)
        t.salvar(f"icones/{nome}.png")

    # bloqueio (ao lado da barra de vida)
    t = Tela(12, 13)
    t.poligono([(1, 1), (11, 1), (11, 7), (6, 12), (1, 7)], P.CIANO)
    t.poligono([(3, 3), (9, 3), (9, 7), (6, 10), (3, 7)], P.AZUL)
    t.ponto(2, 2, P.BRANCO)
    t.contornar(P.PRETO)
    t.salvar("icones/bloqueio.png")


# ---------------------------------------------------------------- cartas

CORES_CLASSE = {
    # classe: (base, luz, sombra)
    "guerreiro": (P.VERMELHO, P.LARANJA, P.ROXO),
    "mago": (P.AZUL, P.AZUL_CLARO, P.AZUL_ESCURO),
    "ladino": (P.VERDE, P.VERDE_CLARO, P.VERDE_ESCURO),
    "berserker": (P.CINZA, P.CINZA_CLARO, P.CINZA_ESCURO),
}


def gerar_moldura_carta(classe):
    base, luz, sombra = CORES_CLASSE[classe]
    t = Tela(48, 64)
    # corpo da moldura (o contorno final arredonda os cantos)
    t.ret(1, 1, 46, 62, base)
    t.ret(1, 1, 45, 1, luz)
    t.ret(1, 1, 1, 61, luz)
    t.ret(2, 62, 45, 1, sombra)
    t.ret(46, 2, 1, 61, sombra)
    # janela da ilustração (fundo com degradê pontilhado)
    for y in range(4, 32):
        for x in range(4, 44):
            t.ponto(x, y, P.ROXO if dither(x, y, (y - 4) / 30) else P.AZUL_ESCURO)
    t.ret_contorno(3, 3, 42, 30, P.PRETO)
    # faixa do nome
    t.ret(3, 33, 42, 10, P.MARROM)
    t.ret(3, 33, 42, 1, P.BEGE)
    t.ret(3, 42, 42, 1, P.MARROM_ESCURO)
    t.ret_contorno(2, 32, 44, 12, P.PRETO)
    # área de descrição (pergaminho)
    t.ret(4, 45, 40, 16, P.BEGE)
    t.ret(4, 59, 40, 2, P.BEGE)
    for x in range(4, 44):
        if dither(x, 60, 0.5):
            t.ponto(x, 60, P.MARROM)
    t.ret_contorno(3, 44, 42, 18, P.PRETO)
    # gema de custo
    t.elipse(7, 7, 6.5, 6.5, P.PRETO)
    t.elipse(7, 7, 5.5, 5.5, P.LARANJA)
    t.elipse(6.5, 6.5, 4, 4, P.AMARELO)
    t.ponto(4, 4, P.BRANCO)
    # contorno externo
    t.contornar(P.PRETO)
    t.salvar(f"cartas/moldura_{classe}.png")


def gerar_ilustracoes():
    # espada (Golpe)
    t = Tela(40, 28)
    t.linha(12, 21, 28, 5, P.BRANCO)
    t.linha(13, 21, 29, 5, P.CINZA_CLARO)
    t.linha(12, 22, 28, 6, P.CINZA_CLARO)
    t.linha(13, 22, 29, 6, P.CINZA)
    t.linha(29, 4, 30, 4, P.BRANCO)
    t.linha(9, 18, 15, 24, P.AMARELO)
    t.linha(9, 19, 14, 24, P.LARANJA)
    t.linha(8, 24, 11, 21, P.MARROM)
    t.linha(8, 25, 11, 22, P.MARROM_ESCURO)
    t.ponto(7, 26, P.AMARELO)
    for (x, y) in ((31, 10), (33, 8), (26, 3), (22, 6)):
        t.ponto(x, y, P.CIANO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_espada.png")

    # escudo (Defender)
    t = Tela(40, 28)
    t.poligono([(11, 3), (29, 3), (29, 15), (20, 26), (11, 15)], P.CINZA_CLARO)
    t.poligono([(13, 5), (27, 5), (27, 15), (20, 23), (13, 15)], P.VERMELHO)
    t.ret(21, 5, 6, 12, P.ROXO)
    t.ret(19, 5, 3, 18, P.AMARELO)
    t.ret(13, 10, 14, 3, P.AMARELO)
    t.ret(12, 4, 2, 1, P.BRANCO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_escudo.png")

    # martelo de guerra (Esmagar)
    t = Tela(40, 28)
    t.linha(10, 25, 24, 8, P.MARROM)
    t.linha(11, 25, 25, 8, P.MARROM_ESCURO)
    t.poligono([(17, 2), (33, 10), (29, 18), (13, 10)], P.CINZA)
    t.poligono([(18, 3), (31, 10), (30, 12), (16, 6)], P.CINZA_CLARO)
    t.linha(17, 3, 23, 6, P.BRANCO)
    t.linha(14, 10, 29, 18, P.CINZA_ESCURO)
    for (x, y) in ((35, 6), (36, 13), (8, 5), (34, 20)):
        t.ponto(x, y, P.AMARELO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_martelo.png")


# ---------------------------------------------------------------- UI

def gerar_ui():
    # barra de vida: moldura e preenchimento (escalado em x pelo jogo)
    t = Tela(46, 6)
    t.ret(0, 0, 46, 6, P.PRETO)
    t.ret(1, 1, 44, 4, P.MARROM_ESCURO)
    t.ret(1, 4, 44, 1, P.PRETO)
    t.salvar("ui/barra_moldura.png")

    t = Tela(44, 4)
    t.ret(0, 0, 44, 1, P.LARANJA)
    t.ret(0, 1, 44, 2, P.VERMELHO)
    t.ret(0, 3, 44, 1, P.ROXO)
    t.salvar("ui/barra_preenchimento.png")

    # orbe de energia: frame 0 = com energia, frame 1 = vazio
    t = Tela(64, 32)
    for i, (base, luz, sombra) in enumerate(((P.LARANJA, P.AMARELO, P.VERMELHO),
                                              (P.CINZA_ESCURO, P.CINZA, P.PRETO))):
        ox = i * 32
        t.elipse(ox + 16, 16, 15.5, 15.5, P.PRETO)
        t.elipse(ox + 16, 16, 14.5, 14.5, sombra)
        t.elipse(ox + 15, 15, 12.5, 12.5, base)
        t.elipse(ox + 14, 14, 8.5, 8.5, luz)
        t.elipse(ox + 10, 9, 2.5, 1.5, P.BRANCO if i == 0 else P.CINZA_CLARO)
    t.salvar("ui/orbe_energia.png")

    # botão: frame 0 = normal, frame 1 = hover
    t = Tela(140, 16)
    for i, (corpo, luz, sombra, borda) in enumerate(((P.MARROM, P.BEGE, P.MARROM_ESCURO, P.PRETO),
                                                     (P.VERMELHO, P.AMARELO, P.ROXO, P.PRETO))):
        ox = i * 70
        t.ret(ox + 1, 0, 68, 16, borda)
        t.ret(ox, 1, 70, 14, borda)
        t.ret(ox + 1, 1, 68, 14, corpo)
        t.ret(ox + 1, 1, 68, 1, luz)
        t.ret(ox + 1, 13, 68, 2, sombra)
    t.salvar("ui/botao.png")

    # pixel preto para sobreposições (escala 1, esticado via set_scale)
    t = Tela(1, 1)
    t.ponto(0, 0, P.PRETO)
    t.salvar("ui/pixel_preto.png", escala=1)


def _verso_carta(t, ox, oy, moldura, luz, interior, emblema):
    """Verso de carta 20x28 com borda preta própria (para empilhar)."""
    t.ret(ox, oy, 20, 28, P.PRETO)
    t.ret(ox + 1, oy + 1, 18, 26, moldura)
    t.ret(ox + 1, oy + 1, 18, 1, luz)
    t.ret(ox + 1, oy + 1, 1, 26, luz)
    t.ret(ox + 3, oy + 3, 14, 22, interior)
    t.poligono([(ox + 10, oy + 7), (ox + 15, oy + 14), (ox + 10, oy + 21), (ox + 5, oy + 14)], emblema)
    t.ret(ox + 9, oy + 13, 2, 2, luz)


def gerar_pilhas():
    cores_compra = (P.MARROM, P.BEGE, P.ROXO, P.AMARELO)
    cores_descarte = (P.CINZA_ESCURO, P.CINZA, P.PRETO, P.CINZA)

    t = Tela(20, 28)
    _verso_carta(t, 0, 0, *cores_compra)
    t.salvar("cartas/verso_mini.png")

    for nome, cores in (("compra", cores_compra), ("descarte", cores_descarte)):
        folha = Tela(48, 32)
        for i, contorno in enumerate((P.PRETO, P.AMARELO)):
            quadro = Tela(24, 32)
            for off in (3, 2, 1):
                _verso_carta(quadro, off, off, *cores)
            quadro.contornar(contorno)
            folha.colar(quadro, i * 24, 0)
        folha.salvar(f"ui/pilha_{nome}.png")


def gerar_titulo():
    linhas = ["DUNGEONS", "& PARTY"]
    fator = 3
    avanco = 6 * fator
    altura_linha = 8 * fator
    largura = max(len(l) for l in linhas) * avanco + 4
    t = Tela(largura, len(linhas) * altura_linha + 6)
    for n, texto in enumerate(linhas):
        ox = 2 + (largura - 4 - (len(texto) * avanco - fator)) // 2
        oy = 2 + n * altura_linha
        for i, ch in enumerate(texto):
            m = mascara_do_caractere(ch)
            for gy in range(2, 9):
                for gx in range(5):
                    if not m[gy][gx]:
                        continue
                    for sy in range(fator):
                        for sx in range(fator):
                            x = ox + i * avanco + gx * fator + sx
                            y = oy + (gy - 2) * fator + sy
                            prog = ((gy - 2) * fator + sy) / (7 * fator)
                            cor = P.LARANJA if dither(x, y, prog * 1.2 - 0.2) else P.AMARELO
                            if prog < 0.12:
                                cor = P.BRANCO
                            t.ponto(x, y, cor)
    sombra = Tela(t.largura, t.altura)
    for y in range(t.altura):
        for x in range(t.largura):
            if t.get(x, y) is not None:
                sombra.ponto(x + 1, y + 2, P.ROXO)
    sombra.colar(t, 0, 0)
    sombra.contornar(P.PRETO)
    sombra.salvar("ui/titulo.png")


def gerar_mago():
    t = Tela(48, 48)
    # manto
    t.poligono([(16, 19), (31, 19), (35, 46), (11, 46)], P.AZUL)
    t.poligono([(26, 19), (31, 19), (35, 46), (29, 46)], P.AZUL_ESCURO)
    t.poligono([(16, 19), (18, 19), (14, 46), (11, 46)], P.AZUL_CLARO)
    t.ret(12, 44, 23, 2, P.AMARELO)
    t.ret(15, 30, 17, 2, P.AMARELO)
    t.ret(22, 30, 3, 2, P.LARANJA)
    # botas
    t.ret(15, 46, 6, 2, P.MARROM_ESCURO)
    t.ret(26, 46, 6, 2, P.MARROM_ESCURO)
    # rosto e barba
    t.ret(19, 14, 10, 6, P.BEGE)
    t.ret(19, 14, 2, 6, P.LARANJA)
    t.ponto(26, 16, P.PRETO)
    t.ponto(29, 17, P.LARANJA)
    t.poligono([(18, 18), (30, 18), (26, 31), (22, 31)], P.BRANCO)
    t.poligono([(26, 18), (30, 18), (26, 31), (25, 31)], P.CINZA_CLARO)
    # chapéu pontudo com a ponta caída para trás
    t.elipse(23, 13, 11, 2.5, P.AZUL)
    t.ret(12, 13, 23, 1, P.AZUL_ESCURO)
    t.poligono([(16, 12), (30, 12), (24, 2), (21, 2)], P.AZUL)
    t.poligono([(21, 3), (24, 2), (18, 0), (15, 1)], P.AZUL)
    t.poligono([(24, 12), (30, 12), (24, 2)], P.AZUL_ESCURO)
    t.ret(16, 10, 14, 2, P.AMARELO)
    t.ponto(21, 6, P.AMARELO)
    t.ponto(20, 7, P.AMARELO)
    t.ponto(22, 7, P.AMARELO)
    # cajado e orbe
    t.ret(37, 8, 2, 39, P.MARROM)
    t.ret(38, 8, 1, 39, P.MARROM_ESCURO)
    t.linha(30, 21, 36, 25, P.AZUL)
    t.linha(30, 22, 36, 26, P.AZUL_ESCURO)
    t.ret(35, 24, 4, 3, P.BEGE)
    t.elipse(38, 5, 3.5, 3.5, P.AZUL_CLARO)
    t.elipse(38, 5, 2, 2, P.CIANO)
    t.ponto(37, 4, P.BRANCO)
    for x, y in ((43, 2), (33, 1), (44, 9)):
        t.ponto(x, y, P.CIANO)
    _salvar_personagem(t, "herois/mago", corte=30, extra=_extra_mago)


def gerar_ladino():
    t = Tela(48, 48)
    # capa esvoaçante atrás
    t.poligono([(15, 17), (27, 17), (30, 40), (22, 38), (15, 43), (8, 41)], P.VERDE_ESCURO)
    t.poligono([(15, 17), (17, 17), (11, 41), (8, 41)], P.VERDE)
    # pernas e botas
    t.ret(18, 33, 4, 9, P.CINZA_ESCURO)
    t.ret(25, 33, 4, 9, P.CINZA_ESCURO)
    t.ret(18, 33, 1, 9, P.CINZA)
    t.ret(17, 41, 6, 4, P.MARROM_ESCURO)
    t.ret(25, 41, 7, 4, P.MARROM_ESCURO)
    # tronco de couro
    t.ret(17, 19, 13, 15, P.MARROM)
    t.ret(26, 19, 4, 15, P.MARROM_ESCURO)
    t.ret(17, 19, 1, 15, P.BEGE)
    t.linha(17, 20, 29, 30, P.MARROM_ESCURO)
    t.ret(17, 29, 13, 2, P.MARROM_ESCURO)
    t.ret(22, 29, 2, 2, P.AMARELO)
    t.ret(26, 30, 3, 3, P.BEGE)
    # capuz
    t.elipse(23, 11, 7, 7, P.VERDE_ESCURO)
    t.poligono([(16, 10), (20, 5), (15, 2)], P.VERDE_ESCURO)
    t.elipse(21, 9, 3, 3, P.VERDE)
    t.elipse(26, 13, 4, 3, P.PRETO)
    t.ponto(25, 12, P.AMARELO)
    t.ponto(28, 12, P.AMARELO)
    t.ret(21, 16, 9, 3, P.VERDE_ESCURO)
    # adaga da frente (apontando para a direita)
    t.linha(29, 21, 33, 26, P.MARROM)
    t.ret(32, 25, 3, 3, P.BEGE)
    t.linha(35, 27, 42, 31, P.BRANCO)
    t.linha(35, 28, 42, 32, P.CINZA_CLARO)
    t.linha(34, 24, 33, 29, P.AMARELO)
    # adaga de trás (erguida)
    t.linha(17, 21, 13, 26, P.MARROM)
    t.ret(11, 25, 3, 3, P.BEGE)
    t.linha(11, 24, 6, 17, P.BRANCO)
    t.linha(12, 24, 7, 17, P.CINZA_CLARO)
    t.linha(9, 25, 14, 23, P.AMARELO)
    _salvar_personagem(t, "herois/ladino", corte=33)


def _anel(t, cx, cy, raio, espessura, cor):
    for y in range(int(cy - raio) - 1, int(cy + raio) + 2):
        for x in range(int(cx - raio) - 1, int(cx + raio) + 2):
            d = math.hypot(x - cx, y - cy)
            if raio - espessura <= d <= raio:
                t.ponto(x, y, cor)


def _adaga(t, cabo, ponta):
    """Adaga reta do cabo até a ponta, com guarda perpendicular."""
    (x0, y0), (x1, y1) = cabo, ponta
    comprimento = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / comprimento, (y1 - y0) / comprimento
    gx, gy = x0 + ux * 4, y0 + uy * 4
    t.linha(x0, y0, round(x0 + ux * 3), round(y0 + uy * 3), P.MARROM)
    t.linha(round(gx - uy * 3), round(gy + ux * 3), round(gx + uy * 3), round(gy - ux * 3), P.AMARELO)
    t.linha(round(gx + ux), round(gy + uy), x1, y1, P.BRANCO)
    t.linha(round(gx + ux + 1), round(gy + uy), x1 + 1, y1, P.CINZA_CLARO)


def gerar_ilustracoes_mago():
    # faísca
    t = Tela(40, 28)
    t.poligono([(23, 1), (13, 15), (19, 15), (14, 27), (28, 10), (21, 10), (27, 1)], P.AMARELO)
    t.poligono([(23, 3), (16, 14), (20, 14), (18, 21), (25, 11), (20, 11)], P.BRANCO)
    for x, y in ((9, 8), (31, 18), (33, 5), (7, 20), (30, 24)):
        t.ponto(x, y, P.CIANO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_faisca.png")

    # barreira arcana
    t = Tela(40, 28)
    _anel(t, 20, 14, 12.5, 2, P.AZUL_CLARO)
    _anel(t, 20, 14, 10.5, 1, P.AZUL)
    t.poligono([(20, 6), (27, 10), (27, 18), (20, 22), (13, 18), (13, 10)], P.AZUL)
    t.poligono([(20, 6), (27, 10), (20, 14), (13, 10)], P.CIANO)
    for ang in range(0, 360, 60):
        x = 20 + math.cos(math.radians(ang)) * 11.5
        y = 14 + math.sin(math.radians(ang)) * 11.5
        t.ponto(round(x), round(y), P.BRANCO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_barreira.png")

    # bola de fogo
    t = Tela(40, 28)
    t.poligono([(22, 6), (3, 25), (26, 20)], P.VERMELHO)
    t.poligono([(22, 9), (8, 23), (24, 18)], P.LARANJA)
    t.elipse(26, 12, 9, 9, P.VERMELHO)
    t.elipse(26, 12, 7, 7, P.LARANJA)
    t.elipse(27, 11, 4.5, 4.5, P.AMARELO)
    t.elipse(28, 10, 2, 2, P.BRANCO)
    for x, y in ((12, 11), (6, 16), (36, 23), (15, 3)):
        t.ponto(x, y, P.AMARELO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_bola_de_fogo.png")

    # concentração (grimório aberto)
    t = Tela(40, 28)
    t.poligono([(6, 17), (20, 21), (34, 17), (34, 26), (20, 27), (6, 26)], P.MARROM)
    t.poligono([(7, 14), (20, 18), (20, 25), (7, 22)], P.BEGE)
    t.poligono([(20, 18), (33, 14), (33, 22), (20, 25)], P.BRANCO)
    for i in range(3):
        t.linha(9, 16 + i * 2, 17, 19 + i * 2, P.MARROM)
        t.linha(23, 19 + i * 2, 31, 16 + i * 2, P.CINZA_CLARO)
    t.linha(20, 18, 20, 25, P.MARROM_ESCURO)
    t.elipse(20, 7, 3, 3, P.CIANO)
    t.ponto(19, 6, P.BRANCO)
    for x, y in ((13, 6), (27, 4), (24, 11), (15, 11)):
        t.ponto(x, y, P.AZUL_CLARO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_grimorio.png")


def gerar_ilustracoes_ladino():
    # adagas cruzadas (Punhalada)
    t = Tela(40, 28)
    _adaga(t, (9, 25), (27, 5))
    _adaga(t, (31, 25), (13, 5))
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_adagas.png")

    # esquiva (capa em movimento)
    t = Tela(40, 28)
    t.poligono([(26, 3), (34, 10), (30, 25), (19, 22), (9, 26), (15, 12)], P.VERDE_ESCURO)
    t.poligono([(26, 3), (29, 6), (18, 22), (15, 12)], P.VERDE)
    for y, xa, xb in ((8, 3, 12), (14, 1, 9), (20, 2, 7)):
        t.linha(xa, y, xb, y, P.CINZA_CLARO)
        t.ponto(xb + 1, y, P.BRANCO)
    t.linha(34, 13, 38, 13, P.CINZA_CLARO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_esquiva.png")

    # adaga veloz (arremessada)
    t = Tela(40, 28)
    t.ret(19, 13, 16, 2, P.BRANCO)
    t.ret(19, 14, 16, 1, P.CINZA_CLARO)
    t.ponto(35, 13, P.BRANCO)
    t.ret(17, 10, 2, 8, P.AMARELO)
    t.ret(11, 13, 6, 2, P.MARROM)
    t.ret(9, 13, 2, 2, P.AMARELO)
    for y, xa, xb in ((7, 2, 12), (21, 4, 14), (11, 1, 6), (17, 0, 7)):
        t.linha(xa, y, xb, y, P.CINZA)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_adaga_veloz.png")

    # golpe furtivo (vulto encapuzado)
    t = Tela(40, 28)
    t.elipse(20, 12, 10, 10, P.VERDE_ESCURO)
    t.poligono([(10, 14), (30, 14), (35, 28), (5, 28)], P.VERDE_ESCURO)
    t.elipse(21, 13, 6, 5, P.PRETO)
    t.ponto(18, 12, P.AMARELO)
    t.ponto(23, 12, P.AMARELO)
    t.elipse(17, 7, 3, 2, P.VERDE)
    _adaga(t, (27, 26), (38, 15))
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_golpe_furtivo.png")


def gerar_rato():
    t = Tela(48, 48)
    # cauda
    t.linha(38, 40, 44, 34, P.BEGE)
    t.linha(44, 34, 46, 26, P.BEGE)
    t.linha(39, 41, 45, 35, P.MARROM)
    # corpo
    t.elipse(27, 37, 14, 8, P.CINZA)
    t.elipse(27, 40, 11, 4, P.CINZA_CLARO)
    t.elipse(31, 33, 8, 3, P.CINZA_ESCURO)
    for x in range(18, 38, 4):
        t.poligono([(x, 31), (x + 3, 31), (x + 2, 27)], P.CINZA_ESCURO)
    # cabeça (voltada para a esquerda)
    t.poligono([(17, 30), (4, 37), (17, 43)], P.CINZA)
    t.poligono([(17, 38), (4, 37), (17, 43)], P.CINZA_CLARO)
    t.elipse(16, 29, 3.5, 3.5, P.CINZA)
    t.elipse(16, 29, 2, 2, P.VERMELHO)
    t.ponto(11, 35, P.PRETO)
    t.ponto(10, 35, P.VERMELHO)
    t.ret(3, 36, 2, 2, P.VERMELHO)
    t.ponto(6, 39, P.BRANCO)
    t.ponto(8, 39, P.BRANCO)
    for y in (34, 37):
        t.linha(1, y - 1, 5, y, P.CINZA_CLARO)
    # patas
    for x in (16, 24, 32, 37):
        t.ret(x, 44, 3, 2, P.CINZA_ESCURO)
    _salvar_personagem(t, "inimigos/rato", corte=43)


def gerar_cultista():
    t = Tela(48, 48)
    # cajado com chama
    t.ret(8, 10, 2, 37, P.MARROM)
    t.ret(9, 10, 1, 37, P.MARROM_ESCURO)
    t.elipse(9, 6, 3.5, 4.5, P.VERMELHO)
    t.elipse(9, 7, 2.2, 3, P.LARANJA)
    t.ponto(9, 8, P.AMARELO)
    t.ponto(12, 1, P.LARANJA)
    t.ponto(5, 3, P.LARANJA)
    # manto
    t.poligono([(17, 16), (31, 16), (38, 46), (11, 46)], P.VERMELHO)
    t.poligono([(26, 16), (31, 16), (38, 46), (31, 46)], P.ROXO)
    t.poligono([(17, 16), (19, 16), (14, 46), (11, 46)], P.LARANJA)
    t.ret(15, 29, 18, 2, P.AMARELO)
    t.ret(23, 31, 2, 6, P.AMARELO)
    # símbolo no peito
    t.elipse(24, 23, 2.5, 2.5, P.PRETO)
    t.ponto(24, 23, P.AMARELO)
    # braço segurando o cajado
    t.linha(18, 19, 11, 24, P.VERMELHO)
    t.linha(18, 20, 11, 25, P.ROXO)
    t.ret(9, 23, 3, 3, P.CINZA_CLARO)
    # capuz
    t.elipse(24, 11, 7, 7, P.VERMELHO)
    t.poligono([(20, 5), (28, 5), (24, -1)], P.VERMELHO)
    t.elipse(22, 12, 4, 3.5, P.PRETO)
    t.ponto(20, 12, P.AMARELO)
    t.ponto(23, 12, P.AMARELO)
    t.elipse(27, 9, 2, 3, P.ROXO)
    _salvar_personagem(t, "inimigos/cultista", corte=30, extra=_extra_cultista)


def gerar_orc():
    t = Tela(48, 48)
    # clava (braço da frente, voltado para a esquerda)
    t.linha(13, 31, 6, 14, P.MARROM)
    t.linha(14, 31, 7, 14, P.MARROM_ESCURO)
    t.elipse(6, 10, 4.5, 5.5, P.MARROM_ESCURO)
    t.elipse(5, 9, 2.5, 3, P.MARROM)
    for x, y in ((1, 8), (4, 4), (9, 6), (10, 11)):
        t.ponto(x, y, P.CINZA_CLARO)
    # pernas
    t.ret(16, 34, 7, 10, P.VERDE_ESCURO)
    t.ret(28, 34, 7, 10, P.VERDE_ESCURO)
    t.ret(14, 43, 9, 3, P.MARROM_ESCURO)
    t.ret(28, 43, 9, 3, P.MARROM_ESCURO)
    # tronco largo
    t.poligono([(9, 17), (41, 17), (37, 35), (13, 35)], P.VERDE)
    t.poligono([(33, 17), (41, 17), (37, 35), (32, 35)], P.VERDE_ESCURO)
    t.ret(9, 17, 5, 3, P.VERDE_CLARO)
    t.linha(12, 18, 36, 33, P.MARROM)
    t.linha(13, 18, 37, 33, P.MARROM_ESCURO)
    t.ret(14, 32, 22, 3, P.MARROM)
    t.ret(22, 32, 4, 3, P.CINZA_CLARO)
    t.poligono([(15, 35), (35, 35), (32, 42), (18, 42)], P.MARROM)
    # ombreira de metal
    t.elipse(35, 18, 5, 3.5, P.CINZA)
    t.elipse(34, 17, 2.5, 1.5, P.CINZA_CLARO)
    # braço da frente
    t.elipse(13, 25, 4, 7, P.VERDE)
    t.ret(10, 29, 6, 4, P.VERDE_ESCURO)
    # cabeça
    t.elipse(24, 11, 8, 7, P.VERDE)
    t.elipse(28, 11, 4, 6, P.VERDE_ESCURO)
    t.ret(17, 8, 12, 2, P.VERDE_ESCURO)
    t.ponto(20, 10, P.VERMELHO)
    t.ponto(25, 10, P.VERMELHO)
    t.ret(19, 15, 9, 2, P.PRETO)
    t.ret(19, 13, 1, 3, P.BRANCO)
    t.ret(27, 13, 1, 3, P.BRANCO)
    t.ret(21, 3, 6, 2, P.PRETO)
    _salvar_personagem(t, "inimigos/orc", corte=34)


def gerar_icones_intencao_extras():
    # fortalecimento: seta para cima
    t = Tela(16, 16)
    t.poligono([(8, 1), (15, 8), (11, 8), (11, 15), (5, 15), (5, 8), (1, 8)], P.LARANJA)
    t.poligono([(8, 3), (11, 7), (8, 7)], P.AMARELO)
    t.ret(6, 8, 2, 6, P.AMARELO)
    t.contornar(P.PRETO)
    t.salvar("icones/intencao_buff.png")

    # ataque em área: explosão
    t = Tela(16, 16)
    pontos = []
    for k in range(16):
        ang = math.radians(k * 22.5 - 90)
        raio = 7.5 if k % 2 == 0 else 3.5
        pontos.append((8 + math.cos(ang) * raio, 8 + math.sin(ang) * raio))
    t.poligono(pontos, P.VERMELHO)
    t.elipse(8, 8, 3.5, 3.5, P.LARANJA)
    t.elipse(8, 8, 1.8, 1.8, P.AMARELO)
    t.contornar(P.PRETO)
    t.salvar("icones/intencao_area.png")

    # força acumulada (ao lado da intenção)
    t = Tela(11, 11)
    t.poligono([(5.5, 1), (10, 6), (7, 6), (7, 10), (4, 10), (4, 6), (1, 6)], P.VERMELHO)
    t.ret(4, 6, 1, 4, P.LARANJA)
    t.contornar(P.PRETO)
    t.salvar("icones/forca.png")


# ---------------------------------------------------------------- inimigos novos

def _desenhar_morcego(asas_baixas):
    t = Tela(48, 48)
    dy = 2 if asas_baixas else 0  # o corpo desce um pouco quando as asas batem para baixo
    if asas_baixas:
        asa = [(19, 21), (12, 22), (4, 30), (8, 30), (8, 36), (12, 32), (16, 36), (18, 29)]
        ossos = [((19, 21), (4, 30)), ((15, 22), (8, 35))]
        luz = ((18, 22), (10, 24))
    else:
        asa = [(19, 22), (12, 12), (2, 7), (5, 15), (3, 23), (8, 21), (11, 27), (17, 26)]
        ossos = [((19, 22), (2, 7)), ((14, 18), (4, 22))]
        luz = ((18, 22), (12, 15))
    espelhada = [(47 - x, y) for x, y in asa]
    for pontos in (asa, espelhada):
        t.poligono([(x, y + dy) for x, y in pontos], P.CINZA_ESCURO)
    for (ax, ay), (bx, by) in ossos:
        t.linha(ax, ay + dy, bx, by + dy, P.ROXO)
        t.linha(47 - ax, ay + dy, 47 - bx, by + dy, P.ROXO)
    (ax, ay), (bx, by) = luz  # luz vem da esquerda
    t.linha(ax, ay + dy, bx, by + dy, P.CINZA)
    # corpo
    t.elipse(24, 26 + dy, 6, 8, P.ROXO)
    t.elipse(22, 24 + dy, 2.5, 4, P.VERMELHO)
    t.elipse(26, 29 + dy, 3, 4, P.CINZA_ESCURO)
    # cabeça, orelhas, olhos e presas (voltado para a esquerda)
    t.elipse(23, 16 + dy, 5, 4.5, P.ROXO)
    t.poligono([(19, 15 + dy), (17, 7 + dy), (22, 13 + dy)], P.ROXO)
    t.poligono([(25, 13 + dy), (29, 7 + dy), (28, 15 + dy)], P.CINZA_ESCURO)
    t.ponto(18, 10 + dy, P.VERMELHO)
    t.ponto(20, 16 + dy, P.AMARELO)
    t.ponto(24, 16 + dy, P.AMARELO)
    t.ponto(21, 19 + dy, P.BRANCO)
    t.ponto(23, 19 + dy, P.BRANCO)
    t.ponto(21, 20 + dy, P.VERMELHO)
    # garras
    t.linha(21, 34 + dy, 20, 37 + dy, P.CINZA_CLARO)
    t.linha(27, 34 + dy, 28, 37 + dy, P.CINZA_CLARO)
    return t


def gerar_morcego():
    _salvar_personagem(_desenhar_morcego(False), "inimigos/morcego", quadro2=_desenhar_morcego(True))


def _desenhar_aranha(passo):
    t = Tela(48, 48)
    dy = passo  # o corpo balança 1 pixel
    # patas: 4 pares (joelho, pé); a cada quadro, pares alternados erguem
    patas = [(8, 22, 3, 44), (14, 19, 10, 45), (30, 18, 34, 45), (37, 20, 44, 44)]
    for k, (jx, jy, px, py) in enumerate(patas):
        ergue = 3 if (k % 2) == passo else 0
        for lado, cor in ((0, P.CINZA_ESCURO), (2, P.CINZA)):
            base_x = 20 + k * 3 + lado
            t.linha(base_x, 31 + dy, jx + lado, jy + dy - ergue, cor)
            t.linha(jx + lado, jy + dy - ergue, px + lado, py - ergue, cor)
    # abdômen com marcas venenosas
    t.elipse(31, 27 + dy, 11, 9, P.CINZA_ESCURO)
    t.elipse(28, 23 + dy, 6, 4, P.CINZA)
    t.elipse(34, 31 + dy, 6, 4, P.PRETO)
    for x, y in ((31, 24), (35, 27), (29, 29), (33, 32)):
        t.elipse(x, y + dy, 1.5, 1.5, P.VERDE_CLARO if (x + y) % 2 else P.VERDE)
    # cefalotórax e cabeça (voltada para a esquerda)
    t.elipse(17, 31 + dy, 7, 6, P.CINZA_ESCURO)
    t.elipse(15, 29 + dy, 3, 2, P.CINZA)
    for x, y in ((12, 29), (14, 28), (12, 31), (14, 31)):
        t.ponto(x, y + dy, P.VERMELHO)
    t.ponto(12, 29 + dy, P.LARANJA)
    # quelíceras pingando veneno
    t.linha(11, 34 + dy, 9, 37 + dy, P.CINZA_CLARO)
    t.linha(14, 35 + dy, 13, 38 + dy, P.CINZA_CLARO)
    t.ponto(9, 39 + passo * 2, P.VERDE_CLARO)
    t.ponto(13, 40 + (1 - passo) * 2, P.VERDE_CLARO)
    return t


def gerar_aranha():
    _salvar_personagem(_desenhar_aranha(0), "inimigos/aranha", quadro2=_desenhar_aranha(1))


def _desenhar_espectro(q):
    t = Tela(48, 48)
    dy = q  # flutua 1 pixel
    # cauda em fiapos que ondulam
    if q == 0:
        pontas = [(14, 41), (19, 45), (24, 41), (29, 46), (34, 41)]
    else:
        pontas = [(13, 43), (18, 40), (24, 45), (30, 41), (35, 44)]
    corpo = [(15, 14), (33, 14), (37, 36)] + list(reversed(pontas)) + [(11, 36)]
    t.poligono([(x, y + dy) for x, y in corpo], P.AZUL_CLARO)
    # névoa translúcida por dithering na parte de baixo
    for y in range(30, 48):
        for x in range(8, 40):
            if t.get(x, y) is not None and dither(x, y, (y - 30) / 16):
                t.ponto(x, y, P.AZUL)
    t.poligono([(x, y + dy) for x, y in ((15, 14), (18, 14), (14, 36), (11, 36))], P.CIANO)
    t.poligono([(x, y + dy) for x, y in ((30, 14), (33, 14), (37, 36), (33, 36))], P.AZUL)
    # braço espectral estendido com garras
    t.poligono([(x, y + dy) for x, y in ((16, 20), (6, 25 - q), (5, 28 - q), (16, 26))], P.AZUL_CLARO)
    for k in range(3):
        t.linha(6, 25 + k - q + dy, 2, 23 + k * 2 - q * 2 + dy, P.CIANO)
    # cabeça encapuzada
    t.elipse(24, 13 + dy, 9, 9, P.AZUL_CLARO)
    t.elipse(21, 9 + dy, 4, 3, P.CIANO)
    t.elipse(28, 16 + dy, 4, 5, P.AZUL)
    t.elipse(23, 15 + dy, 6, 5.5, P.PRETO)
    # olhos (piscam) e boca
    olho = P.BRANCO if q else P.CIANO
    t.ponto(20, 13 + dy, olho)
    t.ponto(25, 13 + dy, olho)
    t.elipse(22.5, 18 + dy, 1.5, 1.5 + q * 0.6, P.AZUL_ESCURO)
    # centelhas ao redor
    for x, y in ((40, 10), (7, 12), (42, 30)) if q == 0 else ((39, 13), (8, 9), (41, 27)):
        t.ponto(x, y, P.CIANO)
    return t


def gerar_espectro():
    _salvar_personagem(_desenhar_espectro(0), "inimigos/espectro", quadro2=_desenhar_espectro(1))


def _brilho_da_runa(t):
    # a runa e os olhos do golem pulsam (coordenadas já descidas 1 pixel pela respiração)
    t.poligono([(25, 22), (29, 27), (25, 32), (21, 27)], P.AMARELO)
    t.poligono([(25, 24), (27, 27), (25, 30), (23, 27)], P.BRANCO)
    for x, cor in ((21, P.BRANCO), (22, P.AMARELO), (25, P.BRANCO), (26, P.AMARELO)):
        t.ponto(x, 11, cor)


def gerar_golem():
    t = Tela(48, 48)
    # pernas de pedra
    t.ret(14, 36, 8, 9, P.CINZA)
    t.ret(27, 36, 8, 9, P.CINZA_ESCURO)
    t.ret(14, 36, 2, 9, P.CINZA_CLARO)
    t.ret(12, 44, 11, 3, P.CINZA_ESCURO)
    t.ret(26, 44, 11, 3, P.CINZA_ESCURO)
    # braço de trás (direita)
    t.elipse(40, 24, 5, 8, P.CINZA_ESCURO)
    t.elipse(41, 36, 5, 4.5, P.CINZA_ESCURO)
    t.ponto(39, 34, P.CINZA)
    # tronco maciço
    t.poligono([(12, 14), (37, 14), (39, 37), (10, 37)], P.CINZA)
    t.poligono([(30, 14), (37, 14), (39, 37), (32, 37)], P.CINZA_ESCURO)
    t.poligono([(12, 14), (16, 14), (14, 37), (10, 37)], P.CINZA_CLARO)
    # rachaduras e musgo
    t.linha(18, 17, 21, 23, P.CINZA_ESCURO)
    t.linha(21, 23, 19, 28, P.CINZA_ESCURO)
    t.linha(31, 28, 28, 34, P.PRETO)
    for x, y in ((13, 15), (14, 15), (15, 16), (35, 15), (36, 16), (11, 35), (12, 36), (36, 36)):
        t.ponto(x, y, P.VERDE)
    t.ponto(13, 16, P.VERDE_ESCURO)
    # runa no peito
    t.poligono([(25, 21), (29, 26), (25, 31), (21, 26)], P.LARANJA)
    t.poligono([(25, 23), (27, 26), (25, 29), (23, 26)], P.AMARELO)
    # cabeça pequena afundada nos ombros
    t.ret(19, 6, 12, 10, P.CINZA)
    t.ret(19, 6, 12, 2, P.CINZA_CLARO)
    t.ret(28, 8, 3, 8, P.CINZA_ESCURO)
    t.ret(20, 10, 8, 2, P.PRETO)
    t.ponto(21, 10, P.AMARELO)
    t.ponto(25, 10, P.AMARELO)
    t.ponto(24, 6, P.VERDE)
    t.ponto(25, 6, P.VERDE)
    # braço da frente (esquerda) com punho enorme
    t.elipse(10, 23, 5.5, 8, P.CINZA)
    t.elipse(8, 20, 2.5, 3, P.CINZA_CLARO)
    t.elipse(9, 36, 7, 6, P.CINZA)
    t.elipse(7, 34, 3, 2.5, P.CINZA_CLARO)
    t.linha(5, 38, 12, 38, P.CINZA_ESCURO)
    t.ret(12, 22, 2, 3, P.CINZA_ESCURO)
    _salvar_personagem(t, "inimigos/golem", corte=36, extra=_brilho_da_runa)


def gerar_icones_intencao_novas():
    # dreno: gota de sangue com presas
    t = Tela(16, 16)
    t.poligono([(8, 1), (13, 9), (8, 15), (3, 9)], P.VERMELHO)
    t.elipse(8, 10, 4.5, 4.5, P.VERMELHO)
    t.elipse(7, 9, 2, 2.5, P.LARANJA)
    t.ponto(6, 7, P.BRANCO)
    t.poligono([(4, 1), (6, 1), (5, 5)], P.BRANCO)
    t.poligono([(10, 1), (12, 1), (11, 5)], P.BRANCO)
    t.contornar(P.PRETO)
    t.salvar("icones/intencao_dreno.png")

    # veneno: gota verde borbulhando
    t = Tela(16, 16)
    t.poligono([(8, 1), (13, 9), (8, 15), (3, 9)], P.VERDE)
    t.elipse(8, 10, 4.5, 4.5, P.VERDE)
    t.elipse(7, 9, 2, 2.5, P.VERDE_CLARO)
    t.ponto(6, 7, P.BRANCO)
    t.elipse(10, 12, 1.2, 1.2, P.VERDE_ESCURO)
    t.contornar(P.PRETO)
    t.salvar("icones/intencao_veneno.png")

    # espectral: garras fantasmas atravessando um escudo
    t = Tela(16, 16)
    t.poligono([(2, 4), (8, 4), (8, 9), (5, 12), (2, 9)], P.CINZA_ESCURO)
    for k in range(3):
        t.linha(5 + k * 3, 14, 13 + k, 2 + k * 2, P.CIANO)
        t.ponto(13 + k, 2 + k * 2, P.BRANCO)
    t.contornar(P.PRETO)
    t.salvar("icones/intencao_espectral.png")


# ---------------------------------------------------------------- carta especial (combinação)

def _faisca(t, x, y, centro=P.BRANCO, braco=P.AMARELO, tamanho=1):
    """Estrelinha em cruz: centro e quatro braços de `tamanho` pixels."""
    for k in range(1, tamanho + 1):
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            t.ponto(x + dx, y + dy, braco)
    t.ponto(x, y, centro)


def _joia(t, cx, cy, base, luz, sombra):
    """Joia lapidada em losango (5x5) com borda preta própria."""
    for y in range(cy - 3, cy + 4):
        for x in range(cx - 3, cx + 4):
            d = abs(x - cx) + abs(y - cy)
            if d == 3:
                t.ponto(x, y, P.PRETO)
            elif d <= 2:
                t.ponto(x, y, luz if (x - cx) + (y - cy) < 0 else base)
    t.ponto(cx + 1, cy + 1, sombra)
    t.ponto(cx, cy + 2, sombra)
    t.ponto(cx + 2, cy, sombra)
    t.ponto(cx - 1, cy - 1, P.BRANCO)


# estrelas do céu da janela: (x, y, cor); as fixas aparecem nos dois quadros
_ESTRELAS_FIXAS = [(8, 9, P.BRANCO), (15, 6, P.CIANO), (27, 7, P.BRANCO), (35, 12, P.CIANO),
                   (11, 17, P.CIANO), (38, 20, P.BRANCO), (23, 14, P.BRANCO), (7, 27, P.BRANCO),
                   (31, 26, P.CIANO), (19, 24, P.CIANO), (40, 28, P.BRANCO), (14, 29, P.BRANCO)]
_ESTRELAS_QUADRO = [
    [(20, 8, P.CIANO), (32, 17, P.BRANCO), (9, 22, P.CIANO), (26, 29, P.BRANCO)],
    [(22, 9, P.BRANCO), (29, 19, P.CIANO), (6, 14, P.BRANCO), (36, 28, P.CIANO)],
]
# estrelas maiores, em cruz, que piscam de um quadro para o outro
_CINTILANTES_QUADRO = [[(38, 7), (12, 12)], [(31, 10), (8, 20)]]
# faíscas sobre a moldura dourada (invadem o contorno, como um reflexo)
_FAISCAS_MOLDURA = [[(1, 21), (46, 45), (30, 62)], [(46, 16), (1, 50), (17, 1)]]
# trechos da borda que brilham mais no quadro 1: (x, y, largura, altura)
_REFLEXOS_BORDA = [(12, 1, 6, 1), (1, 26, 1, 6), (34, 1, 4, 1), (1, 44, 1, 3)]


def _quadro_moldura_especial(classe, quadro):
    base, luz, sombra = CORES_CLASSE[classe]
    t = Tela(48, 64)
    # moldura dourada com chanfro (luz no canto superior esquerdo)
    t.ret(1, 1, 46, 62, P.LARANJA)
    t.ret(1, 1, 45, 1, P.AMARELO)
    t.ret(1, 1, 1, 61, P.AMARELO)
    t.ret(2, 62, 45, 1, P.MARROM)
    t.ret(46, 2, 1, 61, P.MARROM)
    # gravação: pontinhos alternados ao longo da faixa dourada
    for y in range(4, 61, 3):
        t.ponto(2, y, P.AMARELO)
        t.ponto(45, y, P.MARROM)
    for x in range(4, 45, 3):
        t.ponto(x, 2, P.AMARELO)

    # janela da ilustração: céu noturno em degradê com estrelas
    for y in range(4, 32):
        for x in range(4, 44):
            p = (y - 4) / 27
            if p < 0.5:
                cor = P.AZUL_ESCURO if dither(x, y, p * 2) else P.PRETO
            else:
                cor = P.ROXO if dither(x, y, (p - 0.5) * 2) else P.AZUL_ESCURO
            t.ponto(x, y, cor)
    for x, y, cor in _ESTRELAS_FIXAS + _ESTRELAS_QUADRO[quadro]:
        t.ponto(x + 2, y + 2, cor)
    for x, y in _CINTILANTES_QUADRO[quadro]:
        _faisca(t, x + 2, y + 2, P.BRANCO, P.CIANO)
    t.ret_contorno(3, 3, 42, 30, P.PRETO)
    # filete interno na cor da classe, com reflexo junto ao canto superior esquerdo
    t.ret_contorno(4, 4, 40, 28, base)
    t.ret(4, 4, 14, 1, luz)
    t.ret(4, 4, 1, 10, luz)

    # faixa do nome: veludo escuro com filetes dourados (o nome vai em fonte dourada)
    for y in range(34, 42):
        for x in range(3, 45):
            t.ponto(x, y, P.PRETO if dither(x, y, (y - 36) / 7) else P.ROXO)
    t.ret(3, 33, 42, 1, P.AMARELO)
    t.ret(3, 42, 42, 1, P.LARANJA)
    t.ret_contorno(2, 32, 44, 12, P.PRETO)

    # área de descrição (pergaminho liso, como na carta normal)
    t.ret(4, 45, 40, 16, P.BEGE)
    for x in range(4, 44):
        if dither(x, 60, 0.5):
            t.ponto(x, 60, P.MARROM)
    t.ret_contorno(3, 44, 42, 18, P.PRETO)

    # gema de custo especial: anel roxo e vermelho, miolo claro para o número escuro
    t.elipse(7, 7, 6.5, 6.5, P.PRETO)
    t.elipse(7, 7, 5.5, 5.5, P.ROXO)
    t.elipse(6.6, 6.6, 4.9, 4.9, P.VERMELHO)
    t.elipse(7.2, 7.2, 4.1, 4.1, P.LARANJA)
    t.elipse(7, 7, 3.1, 3.1, P.AMARELO)
    t.ponto(3, 5, P.LARANJA)
    t.ponto(4, 4, P.BRANCO)
    t.ponto(5, 3, P.LARANJA)

    # joias da classe nos outros cantos
    for cx, cy in ((44, 3), (3, 60), (44, 60)):
        _joia(t, cx, cy, base, luz, sombra)

    t.contornar(P.PRETO)

    # brilho: reflexos mais fortes na borda e faíscas (diferentes em cada quadro)
    if quadro == 1:
        for x, y, w, h in _REFLEXOS_BORDA:
            t.ret(x, y, w, h, P.BRANCO)
        t.ponto(3, 4, P.BRANCO)
        t.ponto(4, 3, P.BRANCO)
    for x, y in _FAISCAS_MOLDURA[quadro]:
        _faisca(t, x, y, P.BRANCO, P.AMARELO)
    return t


def gerar_moldura_especial(classe):
    """Folha de 2 quadros (96x64) da moldura da carta especial; o jogo alterna os quadros (cintilar)."""
    folha = Tela(96, 64)
    for quadro in range(2):
        folha.colar(_quadro_moldura_especial(classe, quadro), quadro * 48, 0)
    folha.salvar(f"cartas/moldura_especial_{classe}.png")


def _meteoro(t, cx, cy, raio, direcao, comprimento):
    """Meteoro de fogo com a cabeça em (cx, cy), caindo na `direcao` (a cauda fica para trás)."""
    n = math.hypot(*direcao)
    ux, uy = direcao[0] / n, direcao[1] / n
    px, py = -uy, ux
    for escala, cor in ((1.0, P.VERMELHO), (0.62, P.LARANJA), (0.3, P.AMARELO)):
        r = raio * escala
        fim = (cx - ux * comprimento * escala, cy - uy * comprimento * escala)
        t.poligono([(cx + px * r, cy + py * r), fim, (cx - px * r, cy - py * r)], cor)
    t.elipse(cx, cy, raio, raio, P.VERMELHO)
    t.elipse(cx + ux * 0.4, cy + uy * 0.4, raio * 0.72, raio * 0.72, P.LARANJA)
    t.elipse(cx + ux * 0.8, cy + uy * 0.8, raio * 0.42, raio * 0.42, P.AMARELO)
    t.ponto(round(cx + ux * raio * 0.3 - 0.5), round(cy + uy * raio * 0.3 - 0.5), P.BRANCO)


def _corte(t, inicio, fim, curva, espessura):
    """Risco de lâmina levemente curvo, fino nas pontas e mais grosso no meio."""
    (x0, y0), (x1, y1) = inicio, fim
    dx, dy = x1 - x0, y1 - y0
    comprimento = math.hypot(dx, dy)
    px, py = -dy / comprimento, dx / comprimento
    passos = int(comprimento * 4)
    centro = []
    for i in range(passos + 1):
        s = i / passos
        bojo = math.sin(math.pi * s)
        cx = x0 + dx * s + px * curva * bojo
        cy = y0 + dy * s + py * curva * bojo
        centro.append((cx, cy))
        meia = espessura * bojo
        o = 0.0
        while o <= meia:
            t.ponto(round(cx + px * o), round(cy + py * o), P.CINZA_CLARO)
            o += 0.25
    for cx, cy in centro:
        t.ponto(round(cx), round(cy), P.BRANCO)


_GOTAS = {
    "grande": ["..G..", "..G..", ".GGG.", "GBGGG", "GLGGE", ".GEE."],
    "pequena": [".G.", "GGG", "LGE", ".E."],
}


def _gota(t, x, y, tamanho):
    """Gota de veneno com a ponta para cima; (x, y) é o canto superior esquerdo."""
    t.ascii(_GOTAS[tamanho], {"G": P.VERDE, "L": P.VERDE_CLARO, "E": P.VERDE_ESCURO, "B": P.BRANCO}, x, y)


def gerar_ilustracoes_especiais():
    # Bastião (guerreiro): espada cruzada à frente do escudo, com aura de luz
    t = Tela(40, 28)
    cx, cy = 21, 13
    for k in range(12):
        ang = math.radians(k * 30 + 15)
        raio = 14.5 if k % 2 == 0 else 12
        meia = math.radians(8 if k % 2 == 0 else 6)
        ponta_a = (cx + math.cos(ang - meia) * raio, cy + math.sin(ang - meia) * raio)
        ponta_b = (cx + math.cos(ang + meia) * raio, cy + math.sin(ang + meia) * raio)
        t.poligono([(cx, cy), ponta_a, ponta_b], P.AMARELO if k % 2 == 0 else P.LARANJA)
    t.elipse(cx, cy, 8, 8, P.AMARELO)
    t.poligono([(14, 4), (28, 4), (28, 14), (21, 23), (14, 14)], P.CINZA_CLARO)
    t.poligono([(16, 6), (26, 6), (26, 14), (21, 20), (16, 14)], P.VERMELHO)
    t.ret(22, 6, 4, 10, P.ROXO)
    t.ret(20, 6, 2, 14, P.AMARELO)
    t.ret(16, 10, 10, 2, P.AMARELO)
    t.ret(15, 5, 2, 1, P.BRANCO)
    # espada (diagonal, na frente)
    t.linha(12, 19, 30, 1, P.BRANCO)
    t.linha(13, 19, 31, 1, P.CINZA_CLARO)
    t.linha(12, 20, 30, 2, P.CINZA_CLARO)
    t.linha(13, 20, 31, 2, P.CINZA)
    t.ponto(31, 0, P.BRANCO)
    t.linha(8, 17, 14, 23, P.AMARELO)
    t.linha(8, 18, 13, 23, P.LARANJA)
    t.linha(7, 24, 10, 21, P.MARROM)
    t.linha(7, 25, 10, 22, P.MARROM_ESCURO)
    t.elipse(6, 25.5, 1.2, 1.2, P.AMARELO)
    for x, y in ((35, 5), (5, 8), (36, 21), (30, 25), (4, 16)):
        _faisca(t, x, y, P.BRANCO, P.AMARELO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_bastiao.png")

    # Tempestade (mago): chuva de meteoros e um raio
    # (o canto superior esquerdo fica livre: é onde está a gema de custo)
    t = Tela(40, 28)
    _meteoro(t, 27, 9, 1.6, (1, 1.3), 7)
    _meteoro(t, 15, 5, 1.4, (1, 1.3), 6)
    _meteoro(t, 9, 22, 2.4, (1, 1.3), 10)
    _meteoro(t, 21, 21, 4.3, (1, 1.3), 13)
    t.poligono([(31, 0), (37, 0), (33, 10), (37, 10), (28, 27), (31, 14), (27, 14)], P.AZUL_CLARO)
    t.poligono([(32, 1), (35, 1), (32, 11), (35, 11), (29, 23), (31, 13), (28, 13)], P.CIANO)
    t.linha(33, 1, 30, 12, P.BRANCO)
    t.linha(34, 11, 30, 20, P.BRANCO)
    for x, y in ((4, 15), (38, 20), (21, 3), (15, 26), (35, 26)):
        t.ponto(x, y, P.AMARELO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_tempestade.png")

    # Mil Cortes (ladino): rajada de cortes em leque com gotas de veneno
    t = Tela(40, 28)
    origem = (4, 25)
    for ang, dist, comprimento in ((-6, 12, 23), (-19, 7, 27), (-32, 11, 21), (-45, 6, 22),
                                   (-58, 10, 15), (-71, 7, 13)):
        a = math.radians(ang)
        inicio = (origem[0] + math.cos(a) * dist, origem[1] + math.sin(a) * dist)
        fim = (origem[0] + math.cos(a) * (dist + comprimento), origem[1] + math.sin(a) * (dist + comprimento))
        _corte(t, inicio, fim, 1.0, 0.8)
        t.ponto(round(fim[0]), round(fim[1]), P.BRANCO)
    _adaga(t, (3, 26), (10, 19))
    _gota(t, 34, 16, "grande")
    _gota(t, 25, 2, "grande")
    _gota(t, 13, 7, "pequena")
    _gota(t, 36, 6, "pequena")
    _gota(t, 29, 22, "pequena")
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_mil_cortes.png")


def gerar_icones_combinacao():
    # combinar: dois elos de corrente dourados entrelaçados
    # (o elo de baixo passa por cima no cruzamento da esquerda e por baixo no da direita)
    t = Tela(12, 12)
    t.ascii([
        "............",
        ".......BAAA.",
        "......AA..L.",
        ".....AA...L.",
        ".....A...LL.",
        "...BAAL.LL..",
        "..AA.MLLL...",
        ".AA...M.....",
        ".A...LL.....",
        ".A..LL......",
        ".ALLL.......",
        "............",
    ], {"A": P.AMARELO, "L": P.LARANJA, "M": P.MARROM, "B": P.BRANCO})
    t.contornar(P.PRETO)
    t.salvar("icones/combo.png")

    # cartas guardadas: duas cartinhas empilhadas (verso como o verso_mini)
    t = Tela(11, 14)
    for ox, oy in ((3, 0), (0, 3)):
        t.ret(ox, oy, 8, 11, P.PRETO)
        t.ret(ox + 1, oy + 1, 6, 9, P.MARROM)
        t.ret(ox + 1, oy + 1, 6, 1, P.BEGE)
        t.ret(ox + 1, oy + 1, 1, 9, P.BEGE)
        t.ret(ox + 2, oy + 2, 4, 7, P.ROXO)
        t.ret(ox + 3, oy + 4, 2, 3, P.AMARELO)
        t.ponto(ox + 3, oy + 4, P.BRANCO)
    t.salvar("icones/guardadas.png")


def gerar_botao_combo():
    """Botão dourado 'COMBINAR': frame 0 = normal, frame 1 = hover (mesmo formato de ui/botao.png)."""
    t = Tela(140, 16)
    estilos = (
        # (borda clara, borda escura, miolo em cima, miolo embaixo, sombra, enfeite)
        (P.AMARELO, P.MARROM, P.LARANJA, P.VERMELHO, P.ROXO, P.AMARELO),
        (P.BRANCO, P.LARANJA, P.VERMELHO, P.VERMELHO, P.ROXO, P.BRANCO),
    )
    for i, (clara, escura, topo, fundo, sombra, enfeite) in enumerate(estilos):
        ox = i * 70
        t.ret(ox + 1, 0, 68, 16, P.PRETO)
        t.ret(ox, 1, 70, 14, P.PRETO)
        # aro dourado
        t.ret(ox + 1, 1, 68, 14, P.AMARELO if i == 1 else P.LARANJA)
        t.ret(ox + 1, 1, 68, 1, clara)
        t.ret(ox + 1, 1, 1, 14, clara)
        t.ret(ox + 1, 14, 68, 1, escura)
        t.ret(ox + 68, 2, 1, 13, escura)
        # miolo: faixa clara em cima, corpo vermelho e sombra embaixo
        t.ret(ox + 3, 3, 64, 9, fundo)
        t.ret(ox + 3, 3, 64, 2, topo)
        for x in range(ox + 3, ox + 67):
            if dither(x, 5, 0.5):
                t.ponto(x, 5, topo)
        t.ret(ox + 3, 12, 64, 1, sombra)
        t.ret_contorno(ox + 2, 2, 66, 12, P.MARROM_ESCURO if i == 0 else P.MARROM)
        # losangos dourados nas pontas (fora da área do texto)
        for cx in (ox + 7, ox + 62):
            t.poligono([(cx + 0.5, 4), (cx + 3.5, 7.5), (cx + 0.5, 11), (cx - 2.5, 7.5)], P.PRETO)
            t.poligono([(cx + 0.5, 5), (cx + 2.5, 7.5), (cx + 0.5, 10), (cx - 1.5, 7.5)], P.AMARELO)
            t.ponto(cx, 6, enfeite)
            t.ponto(cx, 7, enfeite)
            t.ponto(cx + 1, 8, P.LARANJA)
    t.salvar("ui/botao_combo.png")


def gerar():
    gerar_guerreiro()
    gerar_esqueleto()
    gerar_rei_esqueleto()
    gerar_rato()
    gerar_cultista()
    gerar_orc()
    gerar_morcego()
    gerar_aranha()
    gerar_espectro()
    gerar_golem()
    gerar_icones_intencao_novas()
    gerar_icones()
    gerar_icones_intencao_extras()
    gerar_mago()
    gerar_ladino()
    for classe in CORES_CLASSE:
        gerar_moldura_carta(classe)
    gerar_ilustracoes()
    gerar_ilustracoes_mago()
    gerar_ilustracoes_ladino()
    gerar_ui()
    gerar_pilhas()
    gerar_titulo()
    for classe in CORES_CLASSE:
        gerar_moldura_especial(classe)
    gerar_ilustracoes_especiais()
    gerar_icones_combinacao()
    gerar_botao_combo()


if __name__ == "__main__":
    gerar()
