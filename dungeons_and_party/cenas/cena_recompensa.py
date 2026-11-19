from PPlay.gameimage import GameImage
from PPlay.scenemanager import Scene

from cenas.navegacao import seguir
from entidades.carta import Carta
from sistemas import dados
from ui import audio
from ui.botao import Botao
from ui.texto import fonte

ESPACO = 60
TOPO_CARTAS = 150
ELEVACAO = 16


class RecompensaScene(Scene):
    """Após um combate: escolher uma de três cartas novas; ela entra no conjunto do herói indicado."""

    def __init__(self, run):
        super().__init__()
        self.run = run
        largura, altura = self.janela.largura, self.janela.altura
        self.fundo = GameImage("images/fundos/masmorra.png")
        self.escurecer = GameImage("images/ui/pixel_preto.png")
        self.escurecer.set_scale(largura, altura)
        self.escurecer.set_transparency(170)

        todas = dados.carregar("cartas")
        self.opcoes = []
        pares = run.sortear_recompensas()
        x0 = (largura - (len(pares) * Carta.LARGURA + (len(pares) - 1) * ESPACO)) / 2
        for i, (heroi, id_carta) in enumerate(pares):
            carta = Carta(id_carta, todas[id_carta])
            carta.dono = heroi  # mostra os valores já multiplicados pelos atributos desse herói
            carta.reliquias = run.reliquias
            carta.set_position(x0 + i * (Carta.LARGURA + ESPACO), TOPO_CARTAS)
            self.opcoes.append(carta)
        self.botao_pular = Botao("PULAR", (largura - 210) / 2, altura - 48 - 24)
        audio.tocar_musica("musica_exploracao")

    def _carta_sob_mouse(self):
        return next((c for c in self.opcoes if self.mouse.is_over_object(c)), None)

    def loop(self):
        carta = self._carta_sob_mouse()
        if carta is not None and self.mouse.button_down(1):
            audio.tocar_efeito("recrutar")
            carta.dono.cartas.append(carta.id)
            seguir(self.run)
        elif self.botao_pular.foi_clicado():
            seguir(self.run)

    def draw(self):
        self.fundo.draw()
        self.escurecer.draw()
        centro_x = self.janela.largura / 2
        fonte(5, "dourado").desenhar("RECOMPENSA", centro_x, 48, "centro", True)
        fonte(2, "claro").desenhar("ESCOLHA UMA CARTA NOVA PARA UM DOS HERÓIS", centro_x, 96, "centro", True)
        sob_mouse = self._carta_sob_mouse()
        for carta in self.opcoes:
            elevacao = ELEVACAO if carta is sob_mouse else 0
            carta.draw(True, carta.x, carta.y - elevacao)
            fonte(2, "dourado" if carta is sob_mouse else "claro").desenhar(
                f"PARA {carta.dono.nome}", carta.x + Carta.LARGURA / 2, carta.y + Carta.ALTURA + 24, "centro", True)
        self.botao_pular.draw()
