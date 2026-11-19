from PPlay.gameimage import GameImage
from PPlay.sprite import Sprite
from PPlay.window import Window

from ui.texto import fonte

NOMES = {"combate": "COMBATE", "evento": "EVENTO", "descanso": "DESCANSO", "tesouro": "TESOURO",
         "chefe": "CHEFE"}


class NoMapa:
    """Ponto de parada do mapa. (x, y) é o centro do ícone."""

    def __init__(self, tipo, camada, x, y):
        self.tipo = tipo
        self.camada = camada
        self.x = x
        self.y = y
        self.conectados = []  # nós da camada seguinte alcançáveis a partir deste
        self.visitado = False
        self.mouse = Window.get_instance().mouse
        self.icone = GameImage(f"images/mapa/no_{tipo}.png")
        self.icone.set_position(x - self.icone.width / 2, y - self.icone.height / 2)
        self.anel = Sprite("images/mapa/anel_chefe.png" if tipo == "chefe" else "images/mapa/anel.png", 2)
        self.anel.set_position(x - self.anel.width / 2, y - self.anel.height / 2)

    def sob_mouse(self):
        return self.mouse.is_over_object(self.icone)

    def draw(self, selecionavel):
        destacado = selecionavel and self.sob_mouse()
        if selecionavel:
            self.anel.set_curr_frame(1 if destacado else 0)
            self.anel.draw()
        if selecionavel or self.visitado:
            self.icone.set_transparency(255)
        else:
            self.icone.set_transparency(130)
        self.icone.draw()
        if destacado:
            fonte(2, "escuro").desenhar(NOMES[self.tipo], self.x, self.icone.y - 16, "centro", True)
