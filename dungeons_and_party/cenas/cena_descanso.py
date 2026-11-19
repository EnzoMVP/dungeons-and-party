from PPlay.gameimage import GameImage
from PPlay.scenemanager import Scene

from cenas.navegacao import concluir_encontro
from sistemas.run import FRACAO_CURA_DESCANSO
from ui import audio
from ui.botao import Botao
from ui.nevoa import nevoa_da_masmorra
from ui.texto import fonte


class DescansoScene(Scene):
    """Acampamento: o grupo recupera parte da vida máxima."""

    def __init__(self, run):
        super().__init__()
        self.run = run
        largura, altura = self.janela.largura, self.janela.altura
        self.fundo = GameImage("images/fundos/masmorra.png")
        self.escurecer = GameImage("images/ui/pixel_preto.png")
        self.escurecer.set_scale(largura, altura)
        self.escurecer.set_transparency(110)
        self.nevoa = nevoa_da_masmorra()
        self.fogueira = GameImage("images/cenas/fogueira.png")
        self.fogueira.set_position((largura - self.fogueira.width) / 2, 170)
        x_botao = (largura - 210) / 2
        self.botao_descansar = Botao("DESCANSAR", x_botao, 400)
        self.botao_continuar = Botao("CONTINUAR", x_botao, 400)
        self.descansou = False
        audio.tocar_musica("musica_exploracao")

    def loop(self):
        self.nevoa.atualizar()
        if not self.descansou and self.botao_descansar.foi_clicado():
            audio.tocar_efeito("cura")
            self.run.descansar()
            self.descansou = True
        elif self.descansou and self.botao_continuar.foi_clicado():
            concluir_encontro(self.run)

    def draw(self):
        self.fundo.draw()
        self.nevoa.draw()
        self.escurecer.draw()
        self.fogueira.draw()
        centro_x = self.janela.largura / 2
        fonte(5, "dourado").desenhar("ACAMPAMENTO", centro_x, 70, "centro", True)
        if self.descansou:
            texto = "O GRUPO DESCANSOU JUNTO AO FOGO."
        else:
            texto = f"DESCANSAR RECUPERA {round(FRACAO_CURA_DESCANSO * 100)}% DA VIDA MÁXIMA DE TODOS."
        fonte(2, "claro").desenhar(texto, centro_x, 130, "centro", True)
        resumo = "   ".join(f"{h.nome} {h.hp}/{h.hp_max}" for h in self.run.grupo.herois)
        fonte(2, "vermelho").desenhar(f"GRUPO: {resumo}", centro_x, 360, "centro", True)
        (self.botao_continuar if self.descansou else self.botao_descansar).draw()
