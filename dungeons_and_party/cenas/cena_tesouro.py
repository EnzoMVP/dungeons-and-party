from PPlay.gameimage import GameImage
from PPlay.scenemanager import Scene
from PPlay.sprite import Sprite

from cenas.navegacao import concluir_encontro
from sistemas import dados
from ui import audio
from ui.botao import Botao
from ui.texto import fonte


class TesouroScene(Scene):
    """Baú com uma relíquia passiva aleatória que o grupo ainda não tem."""

    def __init__(self, run):
        super().__init__()
        self.run = run
        largura, altura = self.janela.largura, self.janela.altura
        self.fundo = GameImage("images/fundos/masmorra.png")
        self.escurecer = GameImage("images/ui/pixel_preto.png")
        self.escurecer.set_scale(largura, altura)
        self.escurecer.set_transparency(140)
        self.bau = Sprite("images/cenas/bau.png", 2)
        self.bau.set_position((largura - self.bau.width) / 2, 150)
        x_botao = (largura - 210) / 2
        self.botao_abrir = Botao("ABRIR", x_botao, 420)
        self.botao_continuar = Botao("CONTINUAR", x_botao, 420)
        self.aberto = False
        self.reliquia = None
        self.icone = None
        audio.tocar_musica("musica_exploracao")

    def loop(self):
        if not self.aberto and self.botao_abrir.foi_clicado():
            audio.tocar_efeito("recrutar")
            self.aberto = True
            self.bau.set_curr_frame(1)
            self.reliquia = self.run.abrir_tesouro()
            if self.reliquia:
                self.icone = GameImage(f"images/reliquias/{self.reliquia}.png")
                self.icone.set_position((self.janela.largura - self.icone.width) / 2, 70)
        elif self.aberto and self.botao_continuar.foi_clicado():
            concluir_encontro(self.run)

    def draw(self):
        self.fundo.draw()
        self.escurecer.draw()
        self.bau.draw()
        centro_x = self.janela.largura / 2
        fonte(5, "dourado").desenhar("TESOURO", centro_x, 40, "centro", True)
        if not self.aberto:
            fonte(2, "claro").desenhar("UM BAÚ ANTIGO REPOUSA ENTRE AS PEDRAS.", centro_x, 330, "centro", True)
            self.botao_abrir.draw()
            return
        if self.reliquia:
            info = dados.carregar("reliquias")[self.reliquia]
            self.icone.draw()
            fonte(3, "dourado").desenhar(info["nome"], centro_x, 330, "centro", True)
            fonte(2, "claro").desenhar(info["descricao"], centro_x, 366, "centro", True)
        else:
            fonte(2, "claro").desenhar("O BAÚ ESTÁ VAZIO.", centro_x, 340, "centro", True)
        self.botao_continuar.draw()
