from PPlay.gameimage import GameImage
from PPlay.scenemanager import Scene

from cenas.navegacao import concluir_encontro
from ui import audio
from ui.botao import Botao
from ui.texto import fonte

TOPO_PAINEL = 70


class EventoScene(Scene):
    """Evento narrativo do nó '?': um texto e duas escolhas com consequências."""

    def __init__(self, run):
        super().__init__()
        self.run = run
        largura, altura = self.janela.largura, self.janela.altura
        self.evento = run.sortear_evento()
        self.fundo = GameImage("images/fundos/menu.png")
        self.escurecer = GameImage("images/ui/pixel_preto.png")
        self.escurecer.set_scale(largura, altura)
        self.escurecer.set_transparency(150)
        self.painel = GameImage("images/ui/painel_largo.png")
        self.painel.set_position((largura - self.painel.width) / 2, TOPO_PAINEL)
        x_botao = (largura - 210) / 2
        self.botoes = [Botao(opcao["rotulo"], x_botao, 394 + i * 56) for i, opcao in enumerate(self.evento["opcoes"])]
        self.botao_continuar = Botao("CONTINUAR", x_botao, 394)
        self.resultado = None  # (texto, texto extra, ganhou recompensa)
        audio.tocar_musica("musica_exploracao")

    def loop(self):
        if self.resultado is None:
            for botao, opcao in zip(self.botoes, self.evento["opcoes"]):
                if botao.foi_clicado():
                    extra, recompensa = self.run.aplicar_efeitos_de_evento(opcao["efeitos"])
                    self.resultado = (opcao["resultado"], extra, recompensa)
                    return
        elif self.botao_continuar.foi_clicado():
            concluir_encontro(self.run, recompensa_extra=self.resultado[2])

    def draw(self):
        self.fundo.draw()
        self.escurecer.draw()
        self.painel.draw()
        centro_x = self.janela.largura / 2
        fonte(5, "dourado").desenhar(self.evento["titulo"], centro_x, TOPO_PAINEL + 48, "centro", True)
        if self.resultado is None:
            for i, linha in enumerate(self.evento["texto"]):
                fonte(2, "claro").desenhar(linha, centro_x, TOPO_PAINEL + 110 + i * 28, "centro", True)
            for botao in self.botoes:
                botao.draw()
        else:
            texto, extra, _ = self.resultado
            fonte(2, "claro").desenhar(texto, centro_x, TOPO_PAINEL + 124, "centro", True)
            if extra:
                fonte(2, "dourado").desenhar(extra, centro_x, TOPO_PAINEL + 156, "centro", True)
            self.botao_continuar.draw()
        resumo = "   ".join(f"{h.nome} {h.hp}/{h.hp_max}" for h in self.run.grupo.herois)
        fonte(2, "vermelho").desenhar(f"GRUPO: {resumo}", centro_x, 30, "centro", True)
