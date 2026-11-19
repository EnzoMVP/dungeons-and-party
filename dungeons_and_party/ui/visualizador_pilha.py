import math

from PPlay.gameimage import GameImage
from PPlay.window import Window

from entidades.carta import Carta
from ui.texto import fonte

COLUNAS = 5
ESPACO = 16
TOPO_GRADE = 80
BASE_GRADE = 500


class VisualizadorPilha:
    """Sobreposição que lista as cartas de uma pilha. Fecha com clique ou ESC."""

    def __init__(self):
        janela = Window.get_instance()
        self.largura = janela.largura
        self.altura = janela.altura
        self.mouse = janela.mouse
        self.teclado = janela.keyboard
        self.escurecer = GameImage("images/ui/pixel_preto.png")
        self.escurecer.set_scale(self.largura, self.altura)
        self.escurecer.set_transparency(215)
        self.aberto = False
        self.titulo = ""
        self.cartas = []

    def abrir(self, titulo, cartas):
        self.aberto = True
        self.titulo = titulo
        self.cartas = list(cartas)

    def atualizar(self):
        if self.mouse.button_down(1) or self.teclado.key_down("ESC"):
            self.aberto = False

    def draw(self):
        self.escurecer.draw()
        centro_x = self.largura / 2
        fonte(3, "dourado").desenhar(f"{self.titulo} ({len(self.cartas)})", centro_x, 40, "centro", True)
        if not self.cartas:
            fonte(2, "claro").desenhar("NENHUMA CARTA", centro_x, self.altura / 2, "centro", True)
        else:
            linhas = math.ceil(len(self.cartas) / COLUNAS)
            passo_x = Carta.LARGURA + ESPACO
            passo_y = Carta.ALTURA + ESPACO
            if linhas > 1:
                passo_y = min(passo_y, (BASE_GRADE - TOPO_GRADE - Carta.ALTURA) / (linhas - 1))
            x0 = (self.largura - (COLUNAS * Carta.LARGURA + (COLUNAS - 1) * ESPACO)) / 2
            for i, carta in enumerate(self.cartas):
                linha, coluna = divmod(i, COLUNAS)
                carta.draw(True, x0 + coluna * passo_x, TOPO_GRADE + linha * passo_y)
        fonte(2, "claro").desenhar("CLIQUE PARA FECHAR", centro_x, self.altura - 20, "centro", True)
