from PPlay.gameimage import GameImage
from PPlay.window import Window

from sistemas import dados
from ui.texto import fonte

PASSO = 54


class BarraReliquias:
    """Fileira de ícones das relíquias da run, com nome e descrição ao passar o mouse."""

    def __init__(self, reliquias, x, y):
        self.reliquias = reliquias
        self.x = x
        self.y = y
        self.mouse = Window.get_instance().mouse
        self._icones = {}
        self.fundo_dica = GameImage("images/ui/pixel_preto.png")
        self.fundo_dica.set_transparency(220)

    def _icone(self, id_reliquia):
        if id_reliquia not in self._icones:
            self._icones[id_reliquia] = GameImage(f"images/reliquias/{id_reliquia}.png")
        return self._icones[id_reliquia]

    def draw(self):
        sob_mouse = None
        for i, id_reliquia in enumerate(self.reliquias.ids):
            icone = self._icone(id_reliquia)
            icone.set_position(self.x + i * PASSO, self.y)
            icone.draw()
            if self.mouse.is_over_object(icone):
                sob_mouse = (id_reliquia, icone)
        if sob_mouse:
            self._desenhar_dica(*sob_mouse)

    def _desenhar_dica(self, id_reliquia, icone):
        info = dados.carregar("reliquias")[id_reliquia]
        titulo, descricao = fonte(2, "dourado"), fonte(2, "claro")
        largura = max(titulo.largura(info["nome"]), descricao.largura(info["descricao"])) + 24
        largura_tela = Window.get_instance().largura
        x = max(8, min(icone.x, largura_tela - largura - 8))
        y = icone.y + icone.height + 6
        self.fundo_dica.set_scale(largura, 58)
        self.fundo_dica.set_position(x, y)
        self.fundo_dica.draw()
        titulo.desenhar(info["nome"], x + 12, y + 16, "esquerda", True)
        descricao.desenhar(info["descricao"], x + 12, y + 40, "esquerda", True)
