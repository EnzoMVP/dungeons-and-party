"""Gera ícones de atributos, status e relíquias, objetos das cenas (fogueira, baú) e painéis."""
import math

import paleta as P
from pixelart import Tela, dither


# ---------------------------------------------------------------- atributos e status (9x9 / 11x11)

def gerar_icones_atributos():
    # vida: coração
    t = Tela(9, 9)
    t.elipse(2.5, 2.8, 2.2, 2.2, P.VERMELHO)
    t.elipse(6.5, 2.8, 2.2, 2.2, P.VERMELHO)
    t.poligono([(0.3, 3), (8.7, 3), (4.5, 8.5)], P.VERMELHO)
    t.ponto(2, 2, P.LARANJA)
    t.contornar(P.PRETO)
    t.salvar("icones/atr_hp.png")

    # força: espada
    t = Tela(9, 9)
    t.linha(2, 6, 7, 1, P.BRANCO)
    t.linha(1, 4, 4, 7, P.AMARELO)
    t.ponto(1, 7, P.MARROM)
    t.contornar(P.PRETO)
    t.salvar("icones/atr_forca.png")

    # poder: estrela arcana
    t = Tela(9, 9)
    pontos = []
    for k in range(10):
        ang = math.radians(k * 36 - 90)
        raio = 4.3 if k % 2 == 0 else 1.8
        pontos.append((4.5 + math.cos(ang) * raio, 4.6 + math.sin(ang) * raio))
    t.poligono(pontos, P.AZUL_CLARO)
    t.ponto(4, 4, P.CIANO)
    t.contornar(P.PRETO)
    t.salvar("icones/atr_poder.png")

    # defesa: escudo
    t = Tela(9, 9)
    t.poligono([(1, 1), (8, 1), (8, 5), (4.5, 8.5), (1, 5)], P.CIANO)
    t.poligono([(3, 3), (6, 3), (6, 5), (4.5, 6.5), (3, 5)], P.AZUL)
    t.contornar(P.PRETO)
    t.salvar("icones/atr_defesa.png")

    # velocidade: raio
    t = Tela(9, 9)
    t.poligono([(5, 0), (1, 5), (4, 5), (3, 9), (8, 3), (5, 3), (6, 0)], P.VERDE_CLARO)
    t.contornar(P.PRETO)
    t.salvar("icones/atr_velocidade.png")

    # veneno: gota verde
    t = Tela(11, 11)
    t.poligono([(5.5, 0.5), (9, 6), (2, 6)], P.VERDE)
    t.elipse(5.5, 6.8, 3.5, 3.2, P.VERDE)
    t.elipse(4.5, 6, 1, 1.2, P.VERDE_CLARO)
    t.contornar(P.PRETO)
    t.salvar("icones/veneno.png")

    # provocando: exclamação num escudo vermelho
    t = Tela(11, 11)
    t.poligono([(1, 1), (10, 1), (10, 6), (5.5, 10.5), (1, 6)], P.VERMELHO)
    t.ret(5, 2, 1, 4, P.AMARELO)
    t.ret(5, 7, 1, 1, P.AMARELO)
    t.contornar(P.PRETO)
    t.salvar("icones/provocando.png")


# ---------------------------------------------------------------- relíquias (16x16)

def _reliquia(nome, desenhar):
    t = Tela(16, 16)
    desenhar(t)
    t.contornar(P.PRETO)
    t.salvar(f"reliquias/{nome}.png")


def gerar_reliquias():
    def pedra(t):
        t.poligono([(2, 10), (11, 3), (14, 6), (5, 13)], P.CINZA)
        t.linha(3, 10, 11, 4, P.CINZA_CLARO)
        t.linha(5, 12, 13, 6, P.CINZA_ESCURO)
        t.ponto(12, 2, P.BRANCO)

    def tomo(t):
        t.ret(3, 2, 10, 12, P.ROXO)
        t.ret(3, 2, 2, 12, P.VERMELHO)
        t.ret(12, 3, 1, 10, P.BEGE)
        t.elipse(8.5, 8, 2.5, 2.5, P.CIANO)
        t.ponto(8, 7, P.BRANCO)

    def escudo(t):
        t.poligono([(2, 2), (14, 2), (14, 9), (8, 15), (2, 9)], P.AMARELO)
        t.poligono([(4, 4), (12, 4), (12, 9), (8, 13), (4, 9)], P.MARROM)
        t.ret(7, 4, 2, 9, P.AMARELO)

    def botas(t):
        t.ret(3, 2, 4, 9, P.MARROM)
        t.ret(3, 10, 8, 3, P.MARROM)
        t.ret(3, 2, 4, 1, P.BEGE)
        for y in (4, 7):
            t.linha(9, y, 14, y, P.VERDE_CLARO)
        t.linha(12, 11, 15, 11, P.VERDE_CLARO)

    def presa(t):
        t.poligono([(4, 2), (12, 2), (9, 14)], P.BRANCO)
        t.poligono([(9, 2), (12, 2), (9, 14)], P.CINZA_CLARO)
        t.elipse(10, 13, 1.5, 1.5, P.VERDE)
        t.ponto(12, 15, P.VERDE_CLARO)

    def pocao(t):
        t.ret(6, 1, 4, 3, P.MARROM)
        t.elipse(8, 10, 5.5, 5, P.CINZA_CLARO)
        t.elipse(8, 11, 4.5, 3.5, P.VERMELHO)
        t.ponto(6, 8, P.BRANCO)

    def coracao(t):
        t.elipse(5, 6, 3.6, 3.6, P.CINZA)
        t.elipse(11, 6, 3.6, 3.6, P.CINZA)
        t.poligono([(1.5, 7), (14.5, 7), (8, 14.5)], P.CINZA)
        t.elipse(5, 6, 1.5, 1.5, P.CINZA_CLARO)
        t.ret(7, 7, 2, 4, P.VERMELHO)

    def ampulheta(t):
        t.ret(3, 1, 10, 2, P.MARROM)
        t.ret(3, 13, 10, 2, P.MARROM)
        t.poligono([(4, 3), (12, 3), (8, 8)], P.CIANO)
        t.poligono([(4, 13), (12, 13), (8, 8)], P.CIANO)
        t.poligono([(6, 13), (10, 13), (8, 10)], P.AMARELO)
        t.ponto(8, 6, P.AMARELO)

    for nome, funcao in (("pedra_de_amolar", pedra), ("tomo_proibido", tomo), ("escudo_ancestral", escudo),
                         ("botas_velozes", botas), ("presa_venenosa", presa), ("pocao_vital", pocao),
                         ("coracao_de_ferro", coracao), ("ampulheta", ampulheta)):
        _reliquia(nome, funcao)


# ---------------------------------------------------------------- ilustrações de cartas novas (40x28)

def gerar_ilustracoes_novas():
    # cura: cruz verde brilhante
    t = Tela(40, 28)
    t.ret(17, 4, 6, 20, P.VERDE)
    t.ret(10, 11, 20, 6, P.VERDE)
    t.ret(18, 5, 2, 18, P.VERDE_CLARO)
    t.ret(11, 12, 18, 2, P.VERDE_CLARO)
    for x, y in ((7, 5), (32, 8), (30, 22), (8, 21), (26, 3)):
        t.ponto(x, y, P.BRANCO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_cura.png")

    # veneno: frasco com caveira
    t = Tela(40, 28)
    t.ret(17, 2, 6, 4, P.MARROM)
    t.ret(18, 6, 4, 3, P.CINZA_CLARO)
    t.elipse(20, 17, 9, 9, P.CINZA_CLARO)
    t.elipse(20, 18, 8, 7.5, P.VERDE)
    t.elipse(20, 16, 3, 2.5, P.BRANCO)
    t.ponto(19, 16, P.PRETO)
    t.ponto(21, 16, P.PRETO)
    t.ret(19, 18, 3, 1, P.BRANCO)
    t.ponto(16, 13, P.VERDE_CLARO)
    for x, y in ((31, 6), (9, 10), (33, 20)):
        t.ponto(x, y, P.VERDE_CLARO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_veneno.png")


# ---------------------------------------------------------------- buffs e debuffs

def gerar_icones_status():
    """Ícones 11x11 dos estados de buff (heróis) e debuff (inimigos), ao lado da barra de vida."""
    # fúria: chama vermelha
    t = Tela(11, 11)
    t.poligono([(5.5, 0), (9.5, 6), (8.5, 10), (2.5, 10), (1.5, 6), (3.5, 3), (4.5, 5)], P.VERMELHO)
    t.poligono([(5.5, 3), (7.5, 7), (7, 9.5), (4, 9.5), (3.5, 7)], P.LARANJA)
    t.elipse(5.5, 8, 1.3, 1.5, P.AMARELO)
    t.contornar(P.PRETO)
    t.salvar("icones/furia.png")

    # vigor: cruz verde com brilho
    t = Tela(11, 11)
    t.ret(4, 1, 3, 9, P.VERDE)
    t.ret(1, 4, 9, 3, P.VERDE)
    t.ret(4, 1, 1, 9, P.VERDE_CLARO)
    t.ret(1, 4, 9, 1, P.VERDE_CLARO)
    t.contornar(P.PRETO)
    t.salvar("icones/vigor.png")

    # esquiva: nuvem de fumaça
    t = Tela(11, 11)
    t.elipse(3.5, 6.5, 3, 3, P.CINZA)
    t.elipse(7, 6, 3, 3.2, P.CINZA)
    t.elipse(5.5, 3.8, 2.8, 2.6, P.CINZA_CLARO)
    t.elipse(4.5, 3, 1.2, 1, P.BRANCO)
    t.ret(2, 8, 7, 1, P.CINZA_ESCURO)
    t.contornar(P.PRETO)
    t.salvar("icones/esquiva.png")

    # vulnerável: escudo rachado
    t = Tela(11, 11)
    t.poligono([(1, 1), (10, 1), (10, 6), (5.5, 10.5), (1, 6)], P.CINZA_CLARO)
    t.poligono([(3, 3), (8, 3), (8, 6), (5.5, 8.5), (3, 6)], P.ROXO)
    t.linha(6, 1, 4, 4, P.PRETO)
    t.linha(4, 4, 7, 6, P.PRETO)
    t.linha(7, 6, 5, 9, P.PRETO)
    t.contornar(P.PRETO)
    t.salvar("icones/vulneravel.png")

    # fraqueza: seta azul para baixo
    t = Tela(11, 11)
    t.poligono([(5.5, 10.5), (10.5, 5), (7.5, 5), (7.5, 0.5), (3.5, 0.5), (3.5, 5), (0.5, 5)], P.AZUL)
    t.ret(4, 1, 1, 5, P.AZUL_CLARO)
    t.contornar(P.PRETO)
    t.salvar("icones/fraqueza.png")

    # congelado: cristal de gelo (floco)
    t = Tela(11, 11)
    t.linha(5, 0, 5, 10, P.CIANO)
    t.linha(1, 2, 9, 8, P.CIANO)
    t.linha(1, 8, 9, 2, P.CIANO)
    for x, y in ((3, 1), (7, 1), (3, 9), (7, 9), (0, 5), (10, 5)):
        t.ponto(x, y, P.AZUL_CLARO)
    t.ponto(5, 5, P.BRANCO)
    t.contornar(P.PRETO)
    t.salvar("icones/congelado.png")


def gerar_ilustracoes_buffs():
    """Ilustrações 40x28 das cartas de buff e debuff de cada classe."""
    # BRADO (guerreiro, buff): trompa de guerra soltando ondas de som
    t = Tela(40, 28)
    for raio, cor in ((15, P.LARANJA), (11, P.AMARELO), (7, P.LARANJA)):
        for ang in range(-50, 51, 4):
            x = 22 + math.cos(math.radians(ang)) * raio
            y = 14 + math.sin(math.radians(ang)) * raio
            t.ponto(round(x), round(y), cor)
    t.poligono([(4, 20), (10, 15), (20, 10), (22, 16), (12, 21), (6, 24)], P.BEGE)
    t.poligono([(4, 20), (6, 24), (12, 21), (11, 19)], P.MARROM)
    t.poligono([(19, 8), (23, 7), (24, 18), (20, 19)], P.AMARELO)
    t.ret(21, 8, 1, 10, P.LARANJA)
    t.linha(8, 17, 18, 12, P.BRANCO)
    t.linha(3, 21, 5, 25, P.AMARELO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_brado.png")

    # RACHAR (guerreiro, debuff): escudo inimigo partido por um golpe
    t = Tela(40, 28)
    t.poligono([(8, 3), (19, 3), (19, 25), (16, 24), (8, 15)], P.CINZA)
    t.poligono([(21, 3), (32, 3), (32, 15), (24, 24), (21, 25)], P.CINZA)
    t.poligono([(10, 5), (18, 5), (18, 21), (10, 14)], P.VERMELHO)
    t.poligono([(22, 5), (30, 5), (30, 14), (22, 21)], P.ROXO)
    t.linha(19, 3, 21, 9, P.PRETO)
    t.linha(21, 9, 19, 15, P.PRETO)
    t.linha(19, 15, 21, 25, P.PRETO)
    for x, y in ((5, 6), (35, 8), (4, 18), (36, 20), (13, 1), (27, 26)):
        t.ret(x, y, 2, 2, P.CINZA_CLARO)
    for x, y in ((20, 1), (17, 26), (23, 0)):
        t.ponto(x, y, P.AMARELO)
    t.linha(9, 4, 9, 12, P.CINZA_CLARO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_rachar.png")

    # BÊNÇÃO (mago, buff): broto de vida sob um halo dourado
    t = Tela(40, 28)
    for ang in range(0, 360, 6):
        x = 20 + math.cos(math.radians(ang)) * 9
        y = 6 + math.sin(math.radians(ang)) * 2.5
        t.ponto(round(x), round(y), P.AMARELO)
    t.linha(20, 26, 20, 14, P.VERDE_ESCURO)
    t.linha(21, 26, 21, 14, P.VERDE)
    t.elipse(15, 16, 5, 2.5, P.VERDE)
    t.elipse(26, 13, 5, 2.5, P.VERDE)
    t.elipse(14, 15, 2.5, 1, P.VERDE_CLARO)
    t.elipse(25, 12, 2.5, 1, P.VERDE_CLARO)
    t.elipse(20, 26, 8, 2, P.MARROM)
    for x, y in ((9, 9), (31, 7), (33, 19), (7, 21), (27, 22), (12, 4)):
        t.ponto(x, y, P.VERDE_CLARO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_bencao.png")

    # CONGELAR (mago, debuff): bloco de cristais de gelo
    t = Tela(40, 28)
    for (cx, topo, larg, cor, luz) in ((14, 6, 5, P.AZUL_CLARO, P.CIANO), (22, 2, 6, P.CIANO, P.BRANCO),
                                       (29, 8, 4, P.AZUL_CLARO, P.CIANO), (9, 12, 4, P.AZUL, P.AZUL_CLARO)):
        t.poligono([(cx - larg, 26), (cx - larg, topo + larg), (cx, topo), (cx + larg, topo + larg), (cx + larg, 26)], cor)
        t.poligono([(cx - larg, 26), (cx - larg, topo + larg), (cx, topo), (cx - 1, 26)], luz)
    t.ret(3, 25, 34, 2, P.AZUL_ESCURO)
    for x, y in ((5, 4), (34, 3), (36, 15), (3, 16)):
        t.ponto(x, y, P.BRANCO)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_congelar.png")

    # FUMAÇA (ladino, buff): bomba de fumaça estourando
    t = Tela(40, 28)
    for cx, cy, r, cor in ((12, 13, 7, P.CINZA), (22, 10, 8, P.CINZA_CLARO), (30, 15, 6, P.CINZA),
                           (19, 18, 7, P.CINZA_CLARO), (26, 21, 5, P.CINZA)):
        t.elipse(cx, cy, r, r * 0.8, cor)
    t.elipse(20, 7, 3, 2, P.BRANCO)
    t.elipse(9, 22, 4.5, 4.5, P.PRETO)
    t.elipse(8, 21, 1.5, 1.5, P.CINZA_ESCURO)
    t.linha(12, 18, 15, 15, P.MARROM)
    t.ponto(15, 14, P.AMARELO)
    t.ponto(16, 13, P.LARANJA)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_fumaca.png")

    # CEGAR (ladino, debuff): olho fechado sob uma nuvem de pó brilhante
    t = Tela(40, 28)
    t.poligono([(8, 15), (20, 8), (32, 15), (20, 21)], P.BRANCO)
    t.elipse(20, 15, 4.5, 4.5, P.VERDE)
    t.elipse(20, 15, 2, 2, P.PRETO)
    t.linha(7, 18, 33, 11, P.VERMELHO)
    t.linha(7, 19, 33, 12, P.ROXO)
    for x, y, cor in ((5, 5, P.AMARELO), (11, 3, P.ROXO), (17, 2, P.AMARELO), (25, 3, P.ROXO), (31, 4, P.AMARELO),
                      (35, 8, P.ROXO), (4, 24, P.AMARELO), (13, 25, P.ROXO), (28, 25, P.AMARELO), (36, 22, P.ROXO)):
        t.ponto(x, y, cor)
        t.ponto(x + 1, y, cor)
    t.contornar(P.PRETO)
    t.salvar("cartas/ilustracao_cegar.png")


# ---------------------------------------------------------------- objetos de cena (48x48)

def gerar_objetos_de_cena():
    # fogueira
    t = Tela(48, 48)
    for (x0, y0, x1, y1) in ((8, 42, 38, 36), (10, 36, 40, 42)):
        t.linha(x0, y0, x1, y1, P.MARROM)
        t.linha(x0, y0 + 1, x1, y1 + 1, P.MARROM_ESCURO)
    t.elipse(24, 28, 11, 13, P.VERMELHO)
    t.poligono([(14, 30), (24, 6), (34, 30)], P.VERMELHO)
    t.elipse(24, 31, 8, 9, P.LARANJA)
    t.poligono([(17, 32), (24, 13), (31, 32)], P.LARANJA)
    t.elipse(24, 34, 4.5, 5, P.AMARELO)
    t.ponto(24, 36, P.BRANCO)
    for x, y in ((13, 12), (35, 9), (30, 3), (16, 4)):
        t.ponto(x, y, P.AMARELO)
    for x in range(6, 42, 5):
        t.elipse(x, 44, 2.2, 1.6, P.CINZA)
    t.contornar(P.PRETO)
    t.salvar("cenas/fogueira.png")

    # baú: frame 0 fechado, frame 1 aberto
    folha = Tela(96, 48)
    for i in range(2):
        q = Tela(48, 48)
        q.ret(6, 24, 36, 20, P.MARROM)
        q.ret(6, 24, 36, 2, P.BEGE)
        q.ret(6, 34, 36, 2, P.MARROM_ESCURO)
        for x in (6, 22, 40):
            q.ret(x, 24, 2, 20, P.AMARELO)
        if i == 0:
            q.poligono([(6, 24), (8, 13), (40, 13), (42, 24)], P.MARROM)
            q.ret(8, 14, 32, 2, P.BEGE)
            q.ret(21, 20, 6, 7, P.AMARELO)
            q.ponto(24, 23, P.PRETO)
        else:
            q.poligono([(6, 24), (4, 10), (44, 10), (42, 24)], P.MARROM_ESCURO)
            q.ret(9, 18, 30, 6, P.AMARELO)
            q.elipse(24, 18, 12, 5, P.AMARELO)
            for x, y in ((16, 15), (28, 13), (33, 17), (22, 11)):
                q.ponto(x, y, P.BRANCO)
        q.contornar(P.PRETO)
        folha.colar(q, i * 48, 0)
    folha.salvar("cenas/bau.png")


# ---------------------------------------------------------------- painéis e botões

def _painel(largura, altura, borda, luz):
    q = Tela(largura, altura)
    for y in range(2, altura - 2):
        for x in range(2, largura - 2):
            q.ponto(x, y, P.CINZA_ESCURO if dither(x, y, 0.25 + 0.5 * (y / altura)) else P.AZUL_ESCURO)
    q.ret_contorno(0, 0, largura, altura, borda)
    q.ret_contorno(1, 1, largura - 2, altura - 2, borda)
    q.ret(1, 1, largura - 2, 1, luz)
    q.ret(1, 1, 1, altura - 2, luz)
    q.ret_contorno(2, 2, largura - 4, altura - 4, P.PRETO)
    return q


def gerar_paineis():
    # painel de herói candidato (72 de largura: cabem as 4 classes lado a lado na seleção)
    folha = Tela(144, 130)
    for i, (borda, luz) in enumerate(((P.MARROM, P.BEGE), (P.LARANJA, P.AMARELO))):
        folha.colar(_painel(72, 130, borda, luz), i * 72, 0)
    folha.salvar("ui/painel_selecao.png")

    _painel(220, 100, P.MARROM, P.BEGE).salvar("ui/painel_largo.png")

    # botão pequeno (16x16): frame 0 normal, 1 hover
    folha = Tela(32, 16)
    for i, (corpo, luz, sombra) in enumerate(((P.MARROM, P.BEGE, P.MARROM_ESCURO), (P.VERMELHO, P.AMARELO, P.ROXO))):
        q = Tela(16, 16)
        q.ret(1, 0, 14, 16, P.PRETO)
        q.ret(0, 1, 16, 14, P.PRETO)
        q.ret(1, 1, 14, 14, corpo)
        q.ret(1, 1, 14, 1, luz)
        q.ret(1, 13, 14, 2, sombra)
        folha.colar(q, i * 16, 0)
    folha.salvar("ui/botao_pequeno.png")


def gerar():
    gerar_icones_atributos()
    gerar_reliquias()
    gerar_ilustracoes_novas()
    gerar_icones_status()
    gerar_ilustracoes_buffs()
    gerar_objetos_de_cena()
    gerar_paineis()


if __name__ == "__main__":
    gerar()
