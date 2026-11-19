from PPlay.gameimage import GameImage
from PPlay.timer import Timer
from PPlay.tween import Tween
from PPlay.window import Window

from entidades.carta import Carta
from ui import audio
from ui.texto import fonte

# Todo movimento de carta usa a MESMA duração: o Tween do PPlay não cancela animações
# antigas do mesmo atributo, e com durações iguais a animação mais nova sempre termina
# por último (e portanto vence).
DURACAO_MOVIMENTO = 0.25
DURACAO_ELEVACAO = 0.1
INTERVALO_COMPRA = 0.09
INTERVALO_DESCARTE = 0.05
ELEVACAO_HOVER = 28
ELEVACAO_COMBO = 14
ELEVACAO_MARCADA = 20
PASSO_MAXIMO = 150
VERSOS_REEMBARALHO = 6


class MaoDeCartas:
    """Exibe a mão do baralho em leque e anima compra, descarte, reembaralho, cartas guardadas
    (voam até o herói e voltam dele na próxima vez) e a fusão de um combo (as duas cartas se
    encontram e a especial surge nesse ponto).

    Cartas passivas jogadas também voam até o herói dono (ficam em jogo) e somem.
    `marcadas` são as cartas escolhidas para descarte: ficam erguidas com o ícone de descarte.

    Não altera o baralho: observa suas listas a cada frame e reage às mudanças.
    `posicao_guardada(carta)` dá o canto superior esquerdo de uma carta centralizada no herói dono.
    """

    def __init__(self, baralho, esquerda, direita, y, pilha_compra, pilha_descarte, posicao_guardada=None):
        self.baralho = baralho
        self.esquerda = esquerda
        self.direita = direita
        self.y = y
        self.pilha_compra = pilha_compra
        self.pilha_descarte = pilha_descarte
        self.posicao_guardada = posicao_guardada
        self.mouse = Window.get_instance().mouse

        self.carta_sob_mouse = None
        self.fixada = None  # carta aguardando escolha de alvo: fica erguida
        self.combo_destacado = set()  # par de combo pronto na mão: fica um pouco erguido
        self.marcadas = set()  # cartas escolhidas para descartar (efeito "descartar" de outra carta)
        self._icone_descarte = GameImage("images/icones/descartar.png")
        self._visiveis = set()
        self._alvos = {}
        self._elevacao_alvo = {}
        self._em_voo = []
        self._mao_anterior = []
        self._foram_guardadas = set()  # cartas que voaram até o herói (voltam de lá)
        self._ponto_de_fusao = {}  # especial -> (x, y) onde as componentes se encontram

        self._reembaralhamentos = baralho.reembaralhamentos
        self._versos = [GameImage("images/cartas/verso_mini.png") for _ in range(VERSOS_REEMBARALHO)]
        self._versos_ativos = []
        self._aviso_ativo = False
        self._contador_aviso = 0

    # ---------- atualização ----------
    def atualizar(self, interativa):
        self._detectar_reembaralho()
        self._detectar_mudancas()
        self.carta_sob_mouse = self._detectar_hover() if interativa else None
        for carta in self.baralho.mao:
            if carta is self.carta_sob_mouse or carta is self.fixada:
                alvo = ELEVACAO_HOVER
            elif carta in self.marcadas:
                alvo = ELEVACAO_MARCADA
            else:
                alvo = ELEVACAO_COMBO if carta in self.combo_destacado else 0
            if self._elevacao_alvo.get(carta) != alvo:
                self._elevacao_alvo[carta] = alvo
                Tween.to(carta, "elevacao", alvo, DURACAO_ELEVACAO, "ease_out")

    def _detectar_mudancas(self):
        mao = self.baralho.mao
        anterior = set(self._mao_anterior)
        atual = set(mao)
        novas = [c for c in mao if c not in anterior]
        saidas = [c for c in self._mao_anterior if c not in atual]
        if not novas and not saidas:
            return
        self._mao_anterior = list(mao)

        for i, carta in enumerate(novas):
            if carta in self._em_voo:
                self._em_voo.remove(carta)
            self._visiveis.discard(carta)
            self._alvos.pop(carta, None)
            self._elevacao_alvo.pop(carta, None)
            carta.elevacao = 0
            if carta in self._foram_guardadas and self.posicao_guardada is not None:
                self._foram_guardadas.discard(carta)
                carta.set_position(*self.posicao_guardada(carta))
                Timer.after(i * INTERVALO_COMPRA, self._revelar, carta)
            elif carta.componentes:
                # especial recém-combinada: surge onde as duas cartas se encontram
                pontos = [(c.x, c.y - c.elevacao) for c in carta.componentes]
                ponto = (sum(x for x, _ in pontos) / len(pontos), sum(y for _, y in pontos) / len(pontos))
                self._ponto_de_fusao[carta] = ponto
                carta.set_position(*ponto)
                Timer.after(DURACAO_MOVIMENTO, self._revelar, carta, False)
            else:
                carta.set_position(*self._origem_na_pilha(self.pilha_compra))
                Timer.after(i * INTERVALO_COMPRA, self._revelar, carta)

        for i, carta in enumerate(saidas):
            self._visiveis.discard(carta)
            self._alvos.pop(carta, None)
            self._elevacao_alvo.pop(carta, None)
            if carta is self.fixada:
                self.fixada = None
            carta.y -= carta.elevacao
            carta.elevacao = 0
            self.marcadas.discard(carta)
            self._ponto_de_fusao.pop(carta, None)
            fusao = next((p for e, p in self._ponto_de_fusao.items() if carta in e.componentes), None)
            if self.baralho.foi_descartada(carta):
                destino, atraso = self._origem_na_pilha(self.pilha_descarte), i * INTERVALO_DESCARTE
            elif fusao is not None:
                destino, atraso = fusao, 0
            elif self.baralho.esta_guardada(carta) and self.posicao_guardada is not None:
                self._foram_guardadas.add(carta)
                destino, atraso = self.posicao_guardada(carta), i * INTERVALO_DESCARTE
            elif self.baralho.esta_em_jogo(carta) and self.posicao_guardada is not None:
                destino, atraso = self.posicao_guardada(carta), 0  # passiva: vai para o herói
            else:
                continue  # removida do baralho (herói caído): some sem animação
            self._em_voo.append(carta)
            Timer.after(atraso, self._voar, carta, destino)

        self._reorganizar()

    def _revelar(self, carta, com_som=True):
        if carta in self.baralho.mao:
            if com_som:
                audio.tocar_efeito("comprar")
            self._visiveis.add(carta)
            self._reorganizar()

    def _voar(self, carta, destino):
        """Leva a carta que saiu da mão até o destino (descarte, herói ou ponto de fusão) e a esconde."""
        if carta not in self._em_voo:
            return
        x, y = destino
        Tween.to(carta, "x", x, DURACAO_MOVIMENTO, "ease_in")
        Tween.to(carta, "y", y, DURACAO_MOVIMENTO, "ease_in")
        Timer.after(DURACAO_MOVIMENTO, self._pousar, carta)

    def _pousar(self, carta):
        if carta in self._em_voo and carta not in self.baralho.mao:
            self._em_voo.remove(carta)

    def _reorganizar(self):
        for carta, (x, y) in zip(self.baralho.mao, self._posicoes_base()):
            if carta in self._visiveis and self._alvos.get(carta) != (x, y):
                self._alvos[carta] = (x, y)
                Tween.to(carta, "x", x, DURACAO_MOVIMENTO, "ease_out")
                Tween.to(carta, "y", y, DURACAO_MOVIMENTO, "ease_out")

    def _posicoes_base(self):
        n = len(self.baralho.mao)
        if n == 0:
            return []
        largura_area = self.direita - self.esquerda
        passo = PASSO_MAXIMO if n == 1 else min(PASSO_MAXIMO, (largura_area - Carta.LARGURA) / (n - 1))
        largura_total = Carta.LARGURA + passo * (n - 1)
        x0 = self.esquerda + (largura_area - largura_total) / 2
        meio = (n - 1) / 2
        return [(x0 + i * passo, self.y + abs(i - meio) ** 2 * 3) for i in range(n)]

    def _detectar_hover(self):
        # Usa as posições base (sem elevação) para o hover não piscar; a carta de cima vence.
        mx, my = self.mouse.get_position()
        pares = list(zip(self.baralho.mao, self._posicoes_base()))
        for carta, (x, y) in reversed(pares):
            if carta in self._visiveis and x <= mx <= x + Carta.LARGURA and y <= my <= y + Carta.ALTURA:
                return carta
        return None

    def _origem_na_pilha(self, pilha):
        """Posição (canto superior esquerdo) de uma carta centralizada sobre o ícone da pilha."""
        cx, cy = pilha.centro()
        return cx - Carta.LARGURA / 2, cy - Carta.ALTURA / 2

    # ---------- reembaralho ----------
    def _detectar_reembaralho(self):
        if self.baralho.reembaralhamentos == self._reembaralhamentos:
            return
        self._reembaralhamentos = self.baralho.reembaralhamentos
        self._contador_aviso += 1
        self._aviso_ativo = True
        Timer.after(1.2, self._esconder_aviso, self._contador_aviso)
        ox, oy = self.pilha_descarte.centro()
        dx, dy = self.pilha_compra.centro()
        for i, verso in enumerate(self._versos):
            Timer.after(i * 0.06, self._lancar_verso, verso, ox, oy, dx, dy)

    def _lancar_verso(self, verso, ox, oy, dx, dy):
        verso.set_position(ox - verso.width / 2, oy - verso.height / 2)
        if verso not in self._versos_ativos:
            self._versos_ativos.append(verso)
        Tween.to(verso, "x", dx - verso.width / 2, DURACAO_MOVIMENTO * 2, "ease_out")
        Tween.to(verso, "y", dy - verso.height / 2, DURACAO_MOVIMENTO * 2, "ease_out")
        Timer.after(DURACAO_MOVIMENTO * 2, self._pousar_verso, verso)

    def _pousar_verso(self, verso):
        if verso in self._versos_ativos:
            self._versos_ativos.remove(verso)

    def _esconder_aviso(self, contador):
        if contador == self._contador_aviso:
            self._aviso_ativo = False

    # ---------- desenho ----------
    def draw(self, pode_jogar):
        destaque = self.fixada or self.carta_sob_mouse
        for carta in self.baralho.mao:
            if carta in self._visiveis and carta is not destaque:
                self._desenhar(carta, pode_jogar)
        if destaque is not None and destaque in self._visiveis:
            self._desenhar(destaque, pode_jogar)
        for carta in self._em_voo:
            carta.draw(True)

    def _desenhar(self, carta, pode_jogar):
        y = carta.y - carta.elevacao
        marcada = carta in self.marcadas
        carta.draw(pode_jogar(carta) and not marcada, carta.x, y, carta in self.combo_destacado)
        if marcada:
            icone = self._icone_descarte
            icone.set_position(carta.x + (Carta.LARGURA - icone.width) / 2, y + 40)
            icone.draw()

    def draw_efeitos_pilhas(self):
        """Versos em voo e aviso de reembaralho (desenhados por cima das pilhas)."""
        for verso in self._versos_ativos:
            verso.draw()
        if self._aviso_ativo:
            centro_x = Window.get_instance().largura / 2
            fonte(3, "dourado").desenhar("DESCARTE EMBARALHADO!", centro_x, 110, "centro", True)
