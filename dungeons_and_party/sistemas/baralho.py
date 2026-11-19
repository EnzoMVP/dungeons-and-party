import random


class Baralho:
    """Baralho único do grupo: pilha de compra, mão, pilha de descarte e as cartas que cada herói
    guardou (escolheu manter) ao fim da própria vez.

    Cartas especiais (combo) existem só na mão ou guardadas; ao ir para o descarte, entram no lugar
    delas as duas cartas que as formaram (`componentes`). Cartas passivas jogadas ficam `em_jogo`
    (fora das pilhas) até o fim do combate.
    """

    LIMITE_MAO = 10

    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.compra = []
        self.mao = []
        self.descarte = []
        self.guardadas = {}  # herói -> cartas mantidas para a próxima vez dele
        self.em_jogo = []  # cartas passivas já jogadas neste combate
        self.reembaralhamentos = 0  # contador para a UI reagir a cada reembaralho

    def todas(self):
        """Todas as cartas do baralho, em qualquer pilha."""
        guardadas = [c for cartas in self.guardadas.values() for c in cartas]
        return self.compra + self.mao + self.descarte + guardadas + self.em_jogo

    def adicionar_cartas(self, cartas):
        self.compra.extend(cartas)
        self.rng.shuffle(self.compra)

    def comprar(self, quantidade):
        """Compra até `quantidade` cartas, reembaralhando o descarte quando a compra acaba.

        Para se a mão atingir o limite ou não houver mais cartas. Devolve as cartas compradas.
        """
        compradas = []
        for _ in range(quantidade):
            if len(self.mao) >= self.LIMITE_MAO:
                break
            if not self.compra:
                if not self.descarte:
                    break
                self._reembaralhar_descarte()
            carta = self.compra.pop()
            self.mao.append(carta)
            compradas.append(carta)
        return compradas

    def comprar_de(self, heroi, quantidade):
        """Compra até `quantidade` cartas do herói (as de outros heróis ficam na pilha).

        Se a pilha de compra não tiver mais cartas dele, o descarte é reembaralhado nela.
        """
        compradas = []
        for _ in range(quantidade):
            if len(self.mao) >= self.LIMITE_MAO:
                break
            indice = self._indice_da_ultima_carta_de(heroi)
            if indice is None:
                if not any(c.dono is heroi for c in self.descarte):
                    break
                self._reembaralhar_descarte()
                indice = self._indice_da_ultima_carta_de(heroi)
            carta = self.compra.pop(indice)
            self.mao.append(carta)
            compradas.append(carta)
        return compradas

    def _indice_da_ultima_carta_de(self, heroi):
        for i in range(len(self.compra) - 1, -1, -1):
            if self.compra[i].dono is heroi:
                return i
        return None

    def retirar_da_mao(self, carta):
        """Tira a carta da mão enquanto seus efeitos resolvem (ela não pode ser reembaralhada)."""
        self.mao.remove(carta)

    def enviar_ao_descarte(self, carta):
        self.descarte.extend(self._cartas_reais(carta))

    def colocar_em_jogo(self, carta):
        """Carta passiva jogada: sai das pilhas até o fim do combate."""
        self.em_jogo.append(carta)

    def esta_em_jogo(self, carta):
        return carta in self.em_jogo

    def descartar_mao(self):
        for carta in self.mao:
            self.descarte.extend(self._cartas_reais(carta))
        self.mao.clear()

    def foi_descartada(self, carta):
        """Se a carta (ou, para uma especial, suas componentes) está no descarte."""
        return any(c in self.descarte for c in self._cartas_reais(carta))

    @staticmethod
    def _cartas_reais(carta):
        return carta.componentes if carta.componentes else [carta]

    # ---------- manter cartas entre vezes ----------
    def guardar_mao(self, heroi):
        """Fim da vez com "manter": as cartas da mão ficam guardadas até a próxima vez do herói."""
        self.guardadas.setdefault(heroi, []).extend(self.mao)
        self.mao.clear()

    def devolver_guardadas(self, heroi):
        """Início da vez do herói: as cartas que ele guardou voltam para a mão. Devolve quantas."""
        cartas = self.guardadas.pop(heroi, [])
        self.mao.extend(cartas)
        return len(cartas)

    def quantidade_guardada(self, heroi):
        return len(self.guardadas.get(heroi, []))

    def esta_guardada(self, carta):
        return any(carta in cartas for cartas in self.guardadas.values())

    # ---------- combo ----------
    def combinar(self, carta_a, carta_b, especial):
        """Troca as duas cartas da mão pela especial (na posição da primeira)."""
        indice = self.mao.index(carta_a)
        self.mao[indice] = especial
        self.mao.remove(carta_b)

    # ---------- heróis caídos ----------
    def remover_cartas_de(self, heroi):
        """Remove de todas as pilhas as cartas trazidas por um herói (ex.: herói derrotado)."""
        removidas = [c for c in self.compra + self.mao + self.descarte + self.em_jogo if c.dono is heroi]
        removidas += self.guardadas.pop(heroi, [])
        self.compra = [c for c in self.compra if c.dono is not heroi]
        self.mao[:] = [c for c in self.mao if c.dono is not heroi]
        self.descarte = [c for c in self.descarte if c.dono is not heroi]
        self.em_jogo = [c for c in self.em_jogo if c.dono is not heroi]
        return removidas

    def total_de_cartas(self):
        return len(self.todas())

    def _reembaralhar_descarte(self):
        self.compra.extend(self.descarte)
        self.descarte = []
        self.rng.shuffle(self.compra)
        self.reembaralhamentos += 1
