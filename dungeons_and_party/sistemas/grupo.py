ENERGIA_BASE = 3


class Energia:
    """Energia gasta para jogar cartas; restaurada no início da vez de cada herói.

    `maximo` é a energia total do herói da vez (ENERGIA_BASE + passivas dele).
    """

    def __init__(self, maximo=ENERGIA_BASE):
        self.maximo = maximo
        self.atual = maximo

    def pode_pagar(self, custo):
        return custo <= self.atual

    def gastar(self, custo):
        self.atual -= custo

    def ganhar(self, quantidade):
        self.atual += quantidade

    def restaurar(self, maximo=None, extra=0):
        if maximo is not None:
            self.maximo = maximo
        self.atual = self.maximo + extra


class Grupo:
    """Composição do grupo de heróis (1 líder + até 2 companheiros) e sua energia compartilhada."""

    MAXIMO_HEROIS = 3

    def __init__(self):
        self.herois = []
        self.energia = Energia()

    def adicionar_heroi(self, heroi):
        if not self.cheio():
            self.herois.append(heroi)

    def cheio(self):
        return len(self.herois) >= self.MAXIMO_HEROIS

    def classes(self):
        return {heroi.classe for heroi in self.herois}

    @property
    def lider(self):
        return next((h for h in self.herois if h.lider), None)

    def herois_vivos(self):
        return [h for h in self.herois if not h.esta_derrotado()]

    def todos_derrotados(self):
        return not self.herois_vivos()

    def remover_derrotados(self):
        self.herois = self.herois_vivos()

    def alvo_para_inimigo(self):
        vivos = self.herois_vivos()
        return vivos[0] if vivos else None
