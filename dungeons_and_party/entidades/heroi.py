from PPlay.gameimage import GameImage

from entidades.personagem import Personagem

ROUBO_SEDE = 25  # % de roubo de vida extra enquanto o herói está com sede


class Heroi(Personagem):
    def __init__(self, classe, dados, atributos, lider=False):
        super().__init__(dados["nome"], atributos["hp"], f"images/herois/{dados['sprite']}")
        self.classe = classe
        # hp, forca, poder, defesa (multiplicadores), velocidade e roubo (% do dano que vira vida)
        self.atributos = dict(atributos)
        self.atributos.setdefault("roubo", 0)
        self.cartas = list(dados["cartas"])  # ids das cartas que o herói adiciona ao baralho
        self.crescimento = {}  # id da carta -> dano extra permanente (cartas que crescem a cada uso)
        self.lider = lider
        self.provocando = False  # atrai todos os ataques a um herói até a próxima vez dele
        self.icone_provocando = GameImage("images/icones/provocando.png")

    def roubo_de_vida(self, reliquias=None):
        """% do dano das cartas do herói que volta como vida: atributo + passiva + relíquia + sede."""
        total = self.atributos["roubo"] + self.selvageria
        if reliquias is not None:
            total += reliquias.roubo_de_vida()
        if self.sede > 0:
            total += ROUBO_SEDE
        return total

    def draw(self, dx=0, dy=0, **rotulo):
        super().draw(dx, dy, **rotulo)
        if self.provocando and not self.esta_derrotado():
            barra = self.barra.moldura
            self.icone_provocando.set_position(barra.x + barra.width - self.icone_provocando.width,
                                               barra.y - self.icone_provocando.height - 4)
            self.icone_provocando.draw()
