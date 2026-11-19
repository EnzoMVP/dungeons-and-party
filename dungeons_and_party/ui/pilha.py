from PPlay.sprite import Sprite
from PPlay.window import Window

from ui import audio
from ui.texto import fonte


class IconePilha:
    """Ícone clicável de uma pilha de cartas, com contador (frame 0 = normal, 1 = hover)."""

    def __init__(self, imagem, x, y, rotulo, lado_rotulo="direita"):
        self.sprite = Sprite(imagem, 2)
        self.sprite.set_position(x, y)
        self.rotulo = rotulo
        self.lado_rotulo = lado_rotulo
        self._hover = False
        self.mouse = Window.get_instance().mouse

    def centro(self):
        return self.sprite.x + self.sprite.width / 2, self.sprite.y + self.sprite.height / 2

    def sob_mouse(self):
        return self.mouse.is_over_object(self.sprite)

    def foi_clicado(self):
        clicado = self.sob_mouse() and self.mouse.button_down(1)
        if clicado:
            audio.tocar_efeito("clique")
        return clicado

    def draw(self, quantidade, destacar=True):
        self._hover = destacar and self.sob_mouse()
        self.sprite.set_curr_frame(1 if self._hover else 0)
        self.sprite.draw()
        fonte(3, "dourado").desenhar(quantidade, self.sprite.x + self.sprite.width - 6,
                                     self.sprite.y + self.sprite.height - 12, "direita", True)

    def draw_rotulo(self):
        """Rótulo de hover ao lado do ícone; desenhar por cima da mão de cartas."""
        if not self._hover:
            return
        cy = self.sprite.y + self.sprite.height / 2
        if self.lado_rotulo == "acima":
            fonte(2, "claro").desenhar(self.rotulo, self.sprite.x, self.sprite.y - 14, "esquerda", True)
        elif self.lado_rotulo == "direita":
            fonte(2, "claro").desenhar(self.rotulo, self.sprite.x + self.sprite.width + 10, cy, "esquerda", True)
        else:
            fonte(2, "claro").desenhar(self.rotulo, self.sprite.x - 10, cy, "direita", True)
