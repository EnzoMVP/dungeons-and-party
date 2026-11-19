"""Texto em fonte bitmap pixel art (uma Animation do PPlay por fonte, um frame por caractere)."""
import json

from PPlay.animation import Animation

_dados_fonte = None
_fontes = {}


def _dados():
    global _dados_fonte
    if _dados_fonte is None:
        with open("data/fonte.json", encoding="utf-8") as arquivo:
            _dados_fonte = json.load(arquivo)
    return _dados_fonte


class Fonte:
    def __init__(self, escala, cor):
        dados = _dados()
        self.escala = escala
        self.indices = {c: i for i, c in enumerate(dados["caracteres"])}
        self.glifos = Animation(f"images/ui/fonte_{cor}_{escala}.png", len(dados["caracteres"]))
        self.avanco = dados["largura_celula"] * escala
        self.topo_corpo = dados["topo_corpo"] * escala
        self.altura_corpo = dados["altura_corpo"] * escala

    def largura(self, texto):
        texto = str(texto)
        return max(0, len(texto) * self.avanco - self.escala)

    def desenhar(self, texto, x, y, alinhar="esquerda", meio_vertical=False, transparencia=255):
        """Desenha o texto. Com meio_vertical, y é o centro das letras (e não o topo da célula)."""
        texto = str(texto).upper()
        if alinhar == "centro":
            x -= self.largura(texto) / 2
        elif alinhar == "direita":
            x -= self.largura(texto)
        if meio_vertical:
            y -= self.topo_corpo + self.altura_corpo / 2
        self.glifos.set_transparency(transparencia)
        interrogacao = self.indices["?"]
        for caractere in texto:
            if caractere != " ":
                self.glifos.set_curr_frame(self.indices.get(caractere, interrogacao))
                self.glifos.set_position(int(x), int(y))
                self.glifos.draw()
            x += self.avanco


def fonte(escala=2, cor="claro"):
    """Fontes disponíveis: escalas 2, 3, 5; cores claro, dourado, vermelho, azul, escuro."""
    chave = (escala, cor)
    if chave not in _fontes:
        _fontes[chave] = Fonte(escala, cor)
    return _fontes[chave]
