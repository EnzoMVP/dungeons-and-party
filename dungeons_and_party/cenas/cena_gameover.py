from PPlay.gameimage import GameImage
from PPlay.scenemanager import Scene, SceneManager

from cenas.navegacao import ir_para_mapa
from sistemas.run import Run
from ui import audio
from ui.botao import Botao
from ui.texto import fonte


class GameOverScene(Scene):
    def __init__(self, vitoria, run):
        super().__init__()
        largura, altura = self.janela.largura, self.janela.altura
        self.vitoria = vitoria
        self.run = run
        self.fundo = GameImage("images/fundos/masmorra.png")
        self.escurecer = GameImage("images/ui/pixel_preto.png")
        self.escurecer.set_scale(largura, altura)
        self.escurecer.set_transparency(170)
        x_botoes = (largura - 210) / 2
        self.botao_novamente = Botao("JOGAR NOVAMENTE", x_botoes, 300)
        self.botao_trocar = Botao("TROCAR LÍDER", x_botoes, 364)
        self.botao_menu = Botao("MENU", x_botoes, 428)
        audio.parar_musica()
        audio.tocar_efeito("vitoria" if vitoria else "derrota")

    def loop(self):
        if self.botao_novamente.foi_clicado():
            audio.tocar_musica("musica_exploracao")
            ir_para_mapa(Run.nova(self.run.classe_lider))
        elif self.botao_trocar.foi_clicado():
            from cenas.cena_selecao import SelecaoScene
            SceneManager.change_scene(SelecaoScene())
        elif self.botao_menu.foi_clicado():
            from cenas.cena_menu import MenuScene
            SceneManager.change_scene(MenuScene())

    def draw(self):
        self.fundo.draw()
        self.escurecer.draw()
        centro_x = self.janela.largura / 2
        if self.vitoria:
            fonte(5, "dourado").desenhar("VITÓRIA!", centro_x, 140, "centro", True)
            fonte(2, "claro").desenhar("O REI ESQUELETO FOI DERROTADO!", centro_x, 205, "centro", True)
        else:
            fonte(5, "vermelho").desenhar("DERROTA", centro_x, 140, "centro", True)
            fonte(2, "claro").desenhar("A MASMORRA FAZ MAIS UMA VÍTIMA.", centro_x, 205, "centro", True)
        fonte(2, "dourado").desenhar(
            f"ANDAR {self.run.andar_atual()}/{self.run.total_andares()}   "
            f"COMBATES VENCIDOS: {self.run.combates_vencidos}",
            centro_x, 240, "centro", True)
        self.botao_novamente.draw()
        self.botao_trocar.draw()
        self.botao_menu.draw()
