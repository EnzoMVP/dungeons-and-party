import copy

# Calibrado com simulação lógica (com combos, manter/descartar, buffs e debuffs): um bot heurístico vence ~50%
# das runs com qualquer líder, e as derrotas crescem de combate em combate até o chefe.
AUMENTO_HP_POR_ANDAR = 0.3
AUMENTO_VALOR_POR_ANDAR = 0
# Cada herói tem sua própria vez (e energia), então grupos maiores enfrentam inimigos mais fortes.
AUMENTO_HP_POR_HEROI_EXTRA = 1.35
AUMENTO_VALOR_POR_HEROI_EXTRA = 0.6


def escalar_inimigo(dados, andar, tamanho_grupo=1):
    """Cópia dos dados do inimigo fortalecida pelo andar (0 = primeiro) e pelo tamanho do grupo."""
    escalado = copy.deepcopy(dados)
    extras = max(0, tamanho_grupo - 1)
    escalado["hp_max"] = round(dados["hp_max"] * (1 + AUMENTO_HP_POR_ANDAR * andar)
                               * (1 + AUMENTO_HP_POR_HEROI_EXTRA * extras))
    for intencao in escalado["rotina"]:
        # buff e veneno acumulam ao longo do combate, então não escalam
        if intencao["tipo"] not in ("buff", "veneno"):
            valor = intencao["valor"] + AUMENTO_VALOR_POR_ANDAR * andar
            intencao["valor"] = round(valor * (1 + AUMENTO_VALOR_POR_HEROI_EXTRA * extras))
    return escalado
