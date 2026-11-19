from PPlay.timer import Timer
from PPlay.tween import Tween

from ui.texto import fonte

DURACAO = 0.9
SUBIDA = 40


class _Numero:
    def __init__(self, texto, cor, x, y):
        self.texto = texto
        self.cor = cor
        self.x = x
        self.y = y
        self.transparencia = 255


class NumerosFlutuantes:
    """Números de dano (vermelho) e bloqueio (azul) que sobem e somem sobre os personagens.

    Observa hp e bloqueio das entidades a cada frame e reage às mudanças, sem que
    entidades ou sistemas precisem conhecer a interface.
    """

    def __init__(self, entidades):
        self.entidades = list(entidades)
        self._ultimos = {e: (e.hp, e.bloqueio) for e in self.entidades}
        self._ativos = []

    def atualizar(self):
        for entidade in self.entidades:
            hp_antes, bloqueio_antes = self._ultimos[entidade]
            self._ultimos[entidade] = (entidade.hp, entidade.bloqueio)
            cx = entidade.sprite.x + entidade.sprite.width / 2 + 36
            topo = entidade.sprite.y + 48
            deslocamento = 0
            if entidade.hp < hp_antes:
                self._criar(f"-{hp_antes - entidade.hp}", "vermelho", cx, topo)
                deslocamento = 34
            elif entidade.hp > hp_antes:
                self._criar(f"+{entidade.hp - hp_antes}", "verde", cx, topo)
                deslocamento = 34
            if entidade.bloqueio > bloqueio_antes:
                self._criar(f"+{entidade.bloqueio - bloqueio_antes}", "azul", cx, topo + deslocamento)

    def _criar(self, texto, cor, x, y):
        numero = _Numero(texto, cor, x, y)
        self._ativos.append(numero)
        Tween.to(numero, "y", y - SUBIDA, DURACAO, "ease_out")
        Tween.to(numero, "transparencia", 0, DURACAO, "ease_in")
        Timer.after(DURACAO, self._remover, numero)

    def _remover(self, numero):
        if numero in self._ativos:
            self._ativos.remove(numero)

    def draw(self):
        contorno = fonte(5, "escuro")
        for numero in self._ativos:
            alfa = int(numero.transparencia)
            for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
                contorno.desenhar(numero.texto, numero.x + dx, numero.y + dy, "centro", True, alfa)
            fonte(5, numero.cor).desenhar(numero.texto, numero.x, numero.y, "centro", True, alfa)
