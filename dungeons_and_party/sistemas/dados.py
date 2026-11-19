import json

_cache = {}


def carregar(nome):
    """Carrega data/<nome>.json uma única vez e devolve o conteúdo (não modifique o retorno)."""
    if nome not in _cache:
        with open(f"data/{nome}.json", encoding="utf-8") as arquivo:
            _cache[nome] = json.load(arquivo)
    return _cache[nome]
