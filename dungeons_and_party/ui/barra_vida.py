from PPlay.gameimage import GameImage

from ui.texto import fonte


class BarraVida:
    """Barra de HP com contador e indicador de bloqueio. (x, y) é o canto superior esquerdo."""

    def __init__(self):
        self.moldura = GameImage("images/ui/barra_moldura.png")
        self.preenchimento = GameImage("images/ui/barra_preenchimento.png")
        self.icone_bloqueio = GameImage("images/icones/bloqueio.png")
        self.width = self.moldura.width
        self.height = self.moldura.height

    def set_position(self, x, y):
        self.moldura.set_position(x, y)
        self.preenchimento.set_position(x + 3, y + 3)
        self.icone_bloqueio.set_position(x - self.icone_bloqueio.width - 6,
                                         y + (self.height - self.icone_bloqueio.height) / 2)

    def draw(self, atual, maximo, bloqueio=0):
        self.moldura.draw()
        razao = max(0.0, min(1.0, atual / maximo))
        if razao > 0:
            self.preenchimento.set_scale(razao, 1)
            self.preenchimento.draw()
        centro_x = self.moldura.x + self.width / 2
        centro_y = self.moldura.y + self.height / 2
        fonte(2, "claro").desenhar(f"{atual}/{maximo}", centro_x, centro_y, "centro", True)
        if bloqueio > 0:
            self.icone_bloqueio.draw()
            fonte(2, "claro").desenhar(
                bloqueio,
                self.icone_bloqueio.x + self.icone_bloqueio.width / 2,
                self.icone_bloqueio.y + self.icone_bloqueio.height / 2 - 3,
                "centro", True,
            )
