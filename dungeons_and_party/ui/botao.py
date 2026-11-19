from PPlay.sprite import Sprite
from PPlay.window import Window

from ui import audio
from ui.texto import fonte


class Botao:
    """Botão com imagem de 2 frames (normal/hover) e rótulo em fonte pixel."""

    def __init__(self, texto, x, y, imagem="images/ui/botao.png"):
        self.sprite = Sprite(imagem, 2)
        self.sprite.set_position(x, y)
        self.texto = texto
        self.habilitado = True
        self.mouse = Window.get_instance().mouse

    def sob_mouse(self):
        return self.habilitado and self.mouse.is_over_object(self.sprite)

    def foi_clicado(self):
        clicado = self.sob_mouse() and self.mouse.button_down(1)
        if clicado:
            audio.tocar_efeito("clique")
        return clicado

    def draw(self):
        self.sprite.set_curr_frame(1 if self.sob_mouse() else 0)
        alfa = 255 if self.habilitado else 110
        self.sprite.set_transparency(alfa)
        self.sprite.draw()
        centro_x = self.sprite.x + self.sprite.width / 2
        centro_y = self.sprite.y + self.sprite.height / 2 - 3
        fonte(2, "claro").desenhar(self.texto, centro_x, centro_y, "centro", True, alfa)
