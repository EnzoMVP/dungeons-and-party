from PPlay.gameimage import GameImage
from PPlay.scenemanager import Scene, SceneManager

from cenas.navegacao import ir_para_mapa
from sistemas import dados
from sistemas.run import Run
from ui import audio
from ui.botao import Botao
from ui.painel_classe import PainelClasse, posicoes_centralizadas
from ui.texto import fonte

TOPO_PAINEIS = 72


class SelecaoScene(Scene):
    """Escolha do líder entre três candidatos (um por classe) com atributos sorteados."""

    def __init__(self):
        super().__init__()
        largura, altura = self.janela.largura, self.janela.altura
        self.fundo = GameImage("images/fundos/menu.png")
        self.escurecer = GameImage("images/ui/pixel_preto.png")
        self.escurecer.set_scale(largura, altura)
        self.escurecer.set_transparency(120)
        self.botao_voltar = Botao("VOLTAR", largura / 2 - 210 - 12, altura - 48 - 8)
        self.botao_sortear = Botao("SORTEAR DE NOVO", largura / 2 + 12, altura - 48 - 8)
        self._sortear()
        audio.tocar_musica("musica_exploracao")

    def _sortear(self):
        classes = dados.carregar("classes")
        self.paineis = [
            PainelClasse(Run.criar_heroi(classe, lider=True), classes[classe], x, TOPO_PAINEIS)
            for classe, x in zip(classes, posicoes_centralizadas(len(classes), self.janela.largura))
        ]

    def loop(self):
        if self.botao_voltar.foi_clicado():
            from cenas.cena_menu import MenuScene
            SceneManager.change_scene(MenuScene())
            return
        if self.botao_sortear.foi_clicado():
            self._sortear()
            return
        for painel in self.paineis:
            if painel.foi_clicado():
                ir_para_mapa(Run(painel.heroi))
                return

    def draw(self):
        self.fundo.draw()
        self.escurecer.draw()
        fonte(5, "dourado").desenhar("ESCOLHA SEU LÍDER", self.janela.largura / 2, 34, "centro", True)
        for painel in self.paineis:
            painel.draw()
        self.botao_voltar.draw()
        self.botao_sortear.draw()
