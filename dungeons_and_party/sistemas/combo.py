"""Combinação de ataque: cada classe tem duas cartas (`combo` em data/classes.json) que, juntas
na mão do mesmo herói, podem ser fundidas numa carta especial de custo 3.

A especial guarda as duas cartas em `componentes`; o baralho as devolve ao descarte quando a
especial é descartada, então o conjunto de cartas do herói nunca muda.
"""
from entidades.carta import Carta
from sistemas import dados


def definicao(classe):
    """{"cartas": [id_a, id_b], "especial": id} da classe, ou None."""
    return dados.carregar("classes")[classe].get("combo")


def custo_da_especial(classe):
    return dados.carregar("cartas")[definicao(classe)["especial"]]["custo"]


def par_na_mao(heroi, mao):
    """As duas cartas do herói na mão que formam o combo dele, ou None."""
    combo = definicao(heroi.classe)
    if combo is None:
        return None
    id_a, id_b = combo["cartas"]
    carta_a = next((c for c in mao if c.dono is heroi and c.id == id_a and not c.especial), None)
    carta_b = next((c for c in mao if c.dono is heroi and c.id == id_b and not c.especial and c is not carta_a),
                   None)
    if carta_a is None or carta_b is None:
        return None
    return carta_a, carta_b


def criar_especial(heroi, carta_a, carta_b, reliquias):
    combo = definicao(heroi.classe)
    id_especial = combo["especial"]
    especial = Carta(id_especial, dados.carregar("cartas")[id_especial])
    especial.dono = heroi
    especial.reliquias = reliquias
    especial.componentes = [carta_a, carta_b]
    return especial
