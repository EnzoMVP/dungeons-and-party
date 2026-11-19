from PPlay.gameimage import GameImage
from PPlay.scenemanager import Scene, SceneManager

from ui import audio
from ui.botao import Botao
from ui.texto import fonte

PASSO_VOLUME = 10
LINHAS = [("musica", "MÚSICA", 200), ("efeitos", "EFEITOS", 280)]


class OpcoesScene(Scene):
    """Volume de música e efeitos (salvos em config.json) e dica de tela cheia."""

    def __init__(self):
        super().__init__()
        largura, altura = self.janela.largura, self.janela.altura
        self.fundo = GameImage("images/fundos/menu.png")
        self.escurecer = GameImage("images/ui/pixel_preto.png")
        self.escurecer.set_scale(largura, altura)
        self.escurecer.set_transparency(160)
        self.controles = []
        for tipo, _rotulo, y in LINHAS:
            menos = Botao("-", largura / 2 + 20, y - 24, "images/ui/botao_pequeno.png")
            mais = Botao("+", largura / 2 + 170, y - 24, "images/ui/botao_pequeno.png")
            self.controles.append((tipo, menos, mais))
        self.botao_voltar = Botao("VOLTAR", (largura - 210) / 2, 420)
        audio.tocar_musica("musica_exploracao")

    def loop(self):
        for tipo, menos, mais in self.controles:
            if menos.foi_clicado():
                audio.definir_volume(tipo, audio.volume(tipo) - PASSO_VOLUME)
            elif mais.foi_clicado():
                audio.definir_volume(tipo, audio.volume(tipo) + PASSO_VOLUME)
        if self.botao_voltar.foi_clicado():
            from cenas.cena_menu import MenuScene
            SceneManager.change_scene(MenuScene())

    def draw(self):
        self.fundo.draw()
        self.escurecer.draw()
        centro_x = self.janela.largura / 2
        fonte(5, "dourado").desenhar("OPÇÕES", centro_x, 90, "centro", True)
        for (tipo, rotulo, y), (_, menos, mais) in zip(LINHAS, self.controles):
            fonte(3, "claro").desenhar(rotulo, centro_x - 20, y, "direita", True)
            menos.draw()
            mais.draw()
            fonte(3, "dourado").desenhar(f"{audio.volume(tipo)}%", centro_x + 118, y, "centro", True)
        fonte(2, "claro").desenhar("F11 ALTERNA A TELA CHEIA", centro_x, 360, "centro", True)
        self.botao_voltar.draw()
