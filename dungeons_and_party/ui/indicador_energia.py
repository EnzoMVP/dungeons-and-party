from PPlay.sprite import Sprite

from ui.texto import fonte


class IndicadorEnergia:
    """Orbe de energia no formato atual/máximo (frame 0 = com energia, 1 = vazio)."""

    def __init__(self, x, y):
        self.orbe = Sprite("images/ui/orbe_energia.png", 2)
        self.orbe.set_position(x, y)

    def draw(self, atual, maximo):
        self.orbe.set_curr_frame(0 if atual > 0 else 1)
        self.orbe.draw()
        fonte(3, "escuro" if atual > 0 else "claro").desenhar(
            f"{atual}/{maximo}",
            self.orbe.x + self.orbe.width / 2,
            self.orbe.y + self.orbe.height / 2,
            "centro", True,
        )
