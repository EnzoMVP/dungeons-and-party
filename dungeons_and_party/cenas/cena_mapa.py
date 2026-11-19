import math

from PPlay.gameimage import GameImage
from PPlay.scenemanager import Scene

from cenas.navegacao import iniciar_encontro
from ui import audio
from ui.barra_reliquias import BarraReliquias
from ui.texto import fonte

ENTRADA = (70, 300)
ESPACO_PONTOS = 15
FOLGA_NO = 34  # raio sem pontos ao redor de cada nó


class MapaScene(Scene):
    """Mapa de nós entre encontros: só os próximos nós alcançáveis podem ser escolhidos."""

    def __init__(self, run):
        super().__init__()
        self.run = run
        self.fundo = GameImage("images/mapa/fundo.png")
        self.imagem_trilha = GameImage("images/mapa/trilha.png")
        self.imagem_percorrida = GameImage("images/mapa/trilha_percorrida.png")
        self.marcador = GameImage("images/mapa/marcador.png")
        self.pontos = self._calcular_pontos_da_trilha()
        self.barra_reliquias = BarraReliquias(run.reliquias, 40, 38)
        audio.tocar_musica("musica_exploracao")

    def _calcular_pontos_da_trilha(self):
        """Lista de (x, y, percorrido) para os pontinhos entre nós conectados."""
        percorridas = set(zip([None] + self.run.caminho, self.run.caminho))
        pontos = []
        ligacoes = [(None, no) for no in self.run.mapa[0]]
        for camada in self.run.mapa:
            for no in camada:
                ligacoes.extend((no, destino) for destino in no.conectados)
        for origem, destino in ligacoes:
            x0, y0 = ENTRADA if origem is None else (origem.x, origem.y)
            distancia = math.hypot(destino.x - x0, destino.y - y0)
            passos = int(distancia // ESPACO_PONTOS)
            for k in range(1, passos):
                d = k * ESPACO_PONTOS
                if d < FOLGA_NO or distancia - d < FOLGA_NO:
                    continue
                t = d / distancia
                pontos.append((x0 + (destino.x - x0) * t, y0 + (destino.y - y0) * t,
                               (origem, destino) in percorridas))
        return pontos

    def loop(self):
        if not self.mouse.button_down(1):
            return
        for no in self.run.proximos_nos():
            if no.sob_mouse():
                audio.tocar_efeito("passo_mapa")
                self.run.escolher_no(no)
                iniciar_encontro(self.run)
                return

    def draw(self):
        self.fundo.draw()
        centro_x = self.janela.largura / 2
        fonte(5, "escuro").desenhar("MAPA DA MASMORRA", centro_x, 62, "centro", True)
        fonte(2, "escuro").desenhar("ESCOLHA O PRÓXIMO DESTINO", centro_x, 104, "centro", True)

        for x, y, percorrido in self.pontos:
            imagem = self.imagem_percorrida if percorrido else self.imagem_trilha
            imagem.set_position(x - imagem.width / 2, y - imagem.height / 2)
            imagem.draw()

        fonte(2, "escuro").desenhar("ENTRADA", ENTRADA[0], ENTRADA[1] + 26, "centro", True)
        selecionaveis = set(self.run.proximos_nos())
        for camada in self.run.mapa:
            for no in camada:
                no.draw(no in selecionaveis)

        if self.run.no_atual is None:
            mx, my = ENTRADA[0], ENTRADA[1] - 6
        else:
            mx, my = self.run.no_atual.x + 10, self.run.no_atual.y - 30
        self.marcador.set_position(mx - 3, my - self.marcador.height)
        self.marcador.draw()

        resumo = "   ".join(f"{h.nome} {h.hp}/{h.hp_max}" for h in self.run.grupo.herois)
        fonte(2, "escuro").desenhar(f"GRUPO: {resumo}", centro_x, 486, "centro", True)
        self.barra_reliquias.draw()
