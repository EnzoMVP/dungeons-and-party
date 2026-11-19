from PPlay.gameimage import GameImage
from PPlay.scenemanager import Scene

from cenas.navegacao import seguir
from sistemas import dados
from ui import audio
from ui.botao import Botao
from ui.painel_classe import PainelClasse, posicoes_centralizadas
from ui.texto import fonte

TOPO_PAINEIS = 96


class RecrutamentoScene(Scene):
    """Oferecido automaticamente ao completar um andar com vaga no grupo: um candidato por classe ausente."""

    def __init__(self, run):
        super().__init__()
        self.run = run
        largura, altura = self.janela.largura, self.janela.altura
        self.fundo = GameImage("images/fundos/menu.png")
        self.escurecer = GameImage("images/ui/pixel_preto.png")
        self.escurecer.set_scale(largura, altura)
        self.escurecer.set_transparency(150)

        classes = dados.carregar("classes")
        candidatos = run.sortear_candidatos()
        self.paineis = [
            PainelClasse(heroi, classes[heroi.classe], x, TOPO_PAINEIS,
                         rodape=f"+{len(heroi.cartas)} CARTAS")
            for heroi, x in zip(candidatos, posicoes_centralizadas(len(candidatos), largura))
        ]
        self.botao_recusar = Botao("RECUSAR", (largura - 210) / 2, altura - 48 - 4)
        audio.tocar_musica("musica_exploracao")

    def loop(self):
        for painel in self.paineis:
            if painel.foi_clicado():
                audio.tocar_efeito("recrutar")
                self.run.recrutar(painel.heroi)
                seguir(self.run)
                return
        if self.botao_recusar.foi_clicado():
            seguir(self.run)

    def draw(self):
        self.fundo.draw()
        self.escurecer.draw()
        centro_x = self.janela.largura / 2
        fonte(5, "dourado").desenhar("NOVO ALIADO", centro_x, 28, "centro", True)
        fonte(2, "claro").desenhar("ANDAR CONCLUÍDO! UM AVENTUREIRO QUER SE JUNTAR AO GRUPO.", centro_x, 62,
                                   "centro", True)
        resumo = "   ".join(f"{h.nome} {h.hp}/{h.hp_max}" for h in self.run.grupo.herois)
        fonte(2, "vermelho").desenhar(f"GRUPO: {resumo}", centro_x, 82, "centro", True)
        for painel in self.paineis:
            painel.draw()
        self.botao_recusar.draw()
