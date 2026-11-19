from PPlay.gameimage import GameImage
from PPlay.sprite import Sprite
from PPlay.window import Window

from entidades.personagem import DURACAO_ANIMACAO_MS, QUADROS_ANIMACAO
from sistemas.atributos import formatar
from ui import audio
from ui.texto import fonte

LARGURA = 216
ALTURA = 390
COLUNAS_ATRIBUTOS = [("hp", "velocidade"), ("forca", "poder"), ("defesa", "roubo")]
X_COLUNAS = (20, 116)  # início de cada coluna de atributos, relativo ao painel


def desenhar_atributo(icone, nome, valor, x, y_centro):
    """Ícone 27x27 seguido do valor formatado (ex.: 'X1.3')."""
    icone.set_position(x, y_centro - icone.height / 2)
    icone.draw()
    fonte(2, "claro").desenhar(formatar(nome, valor), x + icone.width + 6, y_centro, "esquerda", True)


def icones_de_atributos():
    return {nome: GameImage(f"images/icones/atr_{nome}.png")
            for nome in ("hp", "forca", "poder", "defesa", "velocidade", "roubo")}


class PainelClasse:
    """Painel clicável de um herói candidato: retrato, nome, atributos sorteados e descrição da classe."""

    def __init__(self, heroi, dados_classe, x, y, rodape=""):
        self.heroi = heroi
        self.dados = dados_classe
        self.rodape = rodape
        self.mouse = Window.get_instance().mouse
        self.painel = Sprite("images/ui/painel_selecao.png", 2)
        self.painel.set_position(x, y)
        self.retrato = Sprite(f"images/herois/{dados_classe['sprite']}.png", QUADROS_ANIMACAO)
        self.retrato.set_total_duration(DURACAO_ANIMACAO_MS)
        self.retrato.set_position(x + (self.painel.width - self.retrato.width) / 2, y + 10)
        self.icones = icones_de_atributos()

    def sob_mouse(self):
        return self.mouse.is_over_object(self.painel)

    def foi_clicado(self):
        clicado = self.sob_mouse() and self.mouse.button_down(1)
        if clicado:
            audio.tocar_efeito("clique")
        return clicado

    def draw(self):
        destacado = self.sob_mouse()
        x, y = self.painel.x, self.painel.y
        self.painel.set_curr_frame(1 if destacado else 0)
        self.painel.draw()
        self.retrato.update()
        self.retrato.draw()
        cx = x + self.painel.width / 2
        fonte(3, "dourado" if destacado else "claro").desenhar(self.heroi.nome, cx, y + 176, "centro", True)
        for linha, (esquerda, direita) in enumerate(COLUNAS_ATRIBUTOS):
            y_linha = y + 208 + linha * 28
            for nome, x_coluna in zip((esquerda, direita), (x + X_COLUNAS[0], x + X_COLUNAS[1])):
                if nome:
                    valor = self.heroi.hp_max if nome == "hp" else self.heroi.atributos[nome]
                    desenhar_atributo(self.icones[nome], nome, valor, x_coluna, y_linha)
        for i, linha in enumerate(self.dados["descricao"]):
            fonte(2, "claro").desenhar(linha, cx, y + 298 + i * 24, "centro", True)
        if self.rodape:
            fonte(2, "dourado").desenhar(self.rodape, cx, y + 372, "centro", True)


def posicoes_centralizadas(quantidade, largura_tela, espaco=24):
    """Coordenadas x para `quantidade` painéis centralizados na tela (o espaço encolhe se não couber)."""
    espaco = min(espaco, (largura_tela - quantidade * LARGURA) / (quantidade + 1))
    largura_total = quantidade * LARGURA + (quantidade - 1) * espaco
    x0 = (largura_tela - largura_total) / 2
    return [x0 + i * (LARGURA + espaco) for i in range(quantidade)]
