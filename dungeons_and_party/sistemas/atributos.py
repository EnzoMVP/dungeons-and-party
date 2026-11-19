"""Sorteio dos atributos dos heróis a partir das faixas de cada classe (data/classes.json).

As faixas não se sobrepõem onde a classe precisa se destacar: o guerreiro sempre tem mais HP,
o mago sempre tem mais poder, o ladino sempre é o mais rápido e o berserker sempre bate mais forte.
O roubo de vida (% do dano das cartas que volta como vida) só é sorteado para as classes que têm a faixa.
"""
import random

ATRIBUTOS_MULTIPLICADORES = ("forca", "poder", "defesa")
ATRIBUTOS_INTEIROS = ("hp", "velocidade", "roubo")
ROTULOS = {"hp": "HP", "forca": "FOR", "poder": "POD", "defesa": "DEF", "velocidade": "VEL", "roubo": "ROU"}


def sortear_atributos(dados_classe, rng=None):
    rng = rng or random
    faixas = dados_classe["atributos"]
    atributos = {
        "hp": rng.randint(*faixas["hp"]),
        "velocidade": rng.randint(*faixas["velocidade"]),
    }
    for nome in ATRIBUTOS_MULTIPLICADORES:
        minimo, maximo = faixas[nome]
        passos = round((maximo - minimo) * 10)
        atributos[nome] = round(minimo + rng.randint(0, passos) / 10, 1)
    atributos["roubo"] = rng.randint(*faixas["roubo"]) if "roubo" in faixas else 0
    return atributos


def formatar(nome, valor):
    """Texto curto de um atributo para a interface (ex.: 'X1.3' para multiplicadores)."""
    if nome in ATRIBUTOS_MULTIPLICADORES:
        return f"X{valor:.1f}"
    if nome == "roubo":
        return f"{valor}%"
    return str(valor)
