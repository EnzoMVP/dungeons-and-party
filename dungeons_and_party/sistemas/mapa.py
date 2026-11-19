import random

from entidades.no_mapa import NoMapa

COMBATES = 4  # batalhas antes do chefe; entre duas delas há sempre uma escolha entre 2 encontros
X_PRIMEIRA_CAMADA = 160
X_ULTIMA_CAMADA = 860
Y_CENTRO = 300
AFASTAMENTO_ESCOLHA = 75  # distância vertical de cada opção da escolha até o centro
TIPOS_ESCOLHA = ["descanso", "tesouro", "evento"]


def gerar_mapa(rng=None):
    """Gera as camadas de nós, da entrada ao chefe:
    combate → escolha entre 2 encontros sem batalha → combate → … → último combate → fogueira → chefe.
    Cada escolha tem 2 tipos diferentes entre fogueira (descanso), tesouro e evento. Os pares saem
    de um "saco" embaralhado: cada par aparece uma vez antes de qualquer um se repetir."""
    rng = rng or random.Random()
    tipos = []
    saco = []
    for i in range(COMBATES):
        tipos.append(["combate"])
        if i < COMBATES - 1:
            if not saco:
                saco = [[a, b] for k, a in enumerate(TIPOS_ESCOLHA) for b in TIPOS_ESCOLHA[k + 1:]]
                rng.shuffle(saco)
            par = saco.pop()
            rng.shuffle(par)  # qual opção fica em cima
            tipos.append(par)
    tipos += [["descanso"], ["chefe"]]

    total = len(tipos)
    camadas = []
    for c, tipos_camada in enumerate(tipos):
        x = X_PRIMEIRA_CAMADA + c * (X_ULTIMA_CAMADA - X_PRIMEIRA_CAMADA) / (total - 1)
        if len(tipos_camada) == 1:
            posicoes = [Y_CENTRO]
        else:
            posicoes = [Y_CENTRO - AFASTAMENTO_ESCOLHA, Y_CENTRO + AFASTAMENTO_ESCOLHA]
        camadas.append([NoMapa(tipo, c, round(x), y) for tipo, y in zip(tipos_camada, posicoes)])
    for atual, seguinte in zip(camadas, camadas[1:]):
        for no in atual:
            no.conectados.extend(seguinte)
    return camadas
