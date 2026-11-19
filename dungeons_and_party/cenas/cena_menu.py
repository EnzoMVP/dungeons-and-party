from PPlay.gameimage import GameImage
from PPlay.scenemanager import Scene, SceneManager

from ui import audio
from ui.botao import Botao
from ui.nevoa import nevoa_da_masmorra


class MenuScene(Scene):
    def __init__(self):
        super().__init__()
        largura, altura = self.janela.largura, self.janela.altura
        self.fundo = GameImage("images/fundos/menu.png")
        self.titulo = GameImage("images/ui/titulo.png")
        self.titulo.set_position((largura - self.titulo.width) / 2, 60)
        x_botoes = (largura - 210) / 2
        self.botao_jogar = Botao("JOGAR", x_botoes, 300)
        self.botao_opcoes = Botao("OPÇÕES", x_botoes, 362)
        self.botao_sair = Botao("SAIR", x_botoes, 424)
        self.nevoa = nevoa_da_masmorra()
        audio.tocar_musica("musica_exploracao")

    def loop(self):
        self.nevoa.atualizar()
        if self.botao_jogar.foi_clicado():
            from cenas.cena_selecao import SelecaoScene
            SceneManager.change_scene(SelecaoScene())
        elif self.botao_opcoes.foi_clicado():
            from cenas.cena_opcoes import OpcoesScene
            SceneManager.change_scene(OpcoesScene())
        elif self.botao_sair.foi_clicado():
            self.janela.close()

    def draw(self):
        self.fundo.draw()
        self.nevoa.draw()
        self.titulo.draw()
        self.botao_jogar.draw()
        self.botao_opcoes.draw()
        self.botao_sair.draw()
