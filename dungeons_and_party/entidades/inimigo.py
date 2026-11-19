import random

from PPlay.gameimage import GameImage

from entidades.personagem import Personagem
from ui.texto import fonte

# Estados que afetam o inimigo (ver entidades/personagem.py): fraqueza corta o valor dos ataques
# pela metade, congelado pula a próxima ação, e a esquiva do herói alvo faz a ação falhar.
# Tipos de intenção (opcionalmente com "vezes"):
# - ataque: um herói; ataque_area: todo o grupo;
# - dreno: ataca um herói e cura o inimigo pelo dano causado;
# - espectral: ataca um herói ignorando o bloqueio;
# - veneno: aplica veneno a um herói (perde vida no início de cada vez dele);
# - defesa: bloqueio para si; buff: força, que soma em todos os ataques seguintes.
TIPOS_ALVO_UNICO = ("ataque", "dreno", "espectral", "veneno")
TIPOS_DE_ATAQUE = ("ataque", "ataque_area", "dreno", "espectral")  # recebem o bônus de força
COR_INTENCAO = {"ataque": "vermelho", "ataque_area": "vermelho", "dreno": "vermelho", "espectral": "azul",
                "veneno": "verde", "defesa": "azul", "buff": "dourado"}
ICONE_INTENCAO = {"ataque": "ataque", "ataque_area": "area", "dreno": "dreno", "espectral": "espectral",
                  "veneno": "veneno", "defesa": "defesa", "buff": "buff"}
# Pesos do sorteio de alvo (1 = chance normal), para o dano não se concentrar num herói só.
PESO_ALVO_REPETIDO = 0.5
PESO_ALVO_JA_MIRADO = 0.5


class Inimigo(Personagem):
    """Inimigo com rotina fixa e cíclica de intenções, sempre visíveis ao jogador."""

    def __init__(self, tipo, dados, indice_inicial=0):
        super().__init__(dados["nome"], dados["hp_max"], f"images/inimigos/{dados['sprite']}")
        self.tipo = tipo
        self.velocidade = dados["velocidade"]
        self.rotina = dados["rotina"]
        self.indice_rotina = indice_inicial % len(self.rotina)
        self.forca = 0
        self.alvo = None  # herói que será atacado (escolhido no início do turno e visível ao jogador)
        self._ultimo_alvo = None
        self.icones_intencao = {tipo: GameImage(f"images/icones/intencao_{arquivo}.png")
                                for tipo, arquivo in ICONE_INTENCAO.items()}

    def set_position(self, x, y):
        super().set_position(x, y)
        for icone in self.icones_intencao.values():
            icone.set_position(x + self.sprite.width / 2 - icone.width, y - icone.height - 4)

    # ---------- intenção ----------
    @property
    def intencao_atual(self):
        return self.rotina[self.indice_rotina]

    def valor_da_intencao(self, intencao=None):
        """Valor efetivo da intenção: ataques somam a força acumulada e a fraqueza corta pela metade."""
        intencao = intencao or self.intencao_atual
        if intencao["tipo"] in TIPOS_DE_ATAQUE:
            valor = intencao["valor"] + self.forca
            return valor // 2 if self.fraqueza > 0 else valor
        return intencao["valor"]

    def texto_da_intencao(self):
        intencao = self.intencao_atual
        valor = self.valor_da_intencao(intencao)
        if intencao["tipo"] == "buff":
            return f"+{valor}"
        vezes = intencao.get("vezes", 1)
        return f"{valor}X{vezes}" if vezes > 1 else str(valor)

    def escolher_alvo(self, grupo, rng=None, ja_mirados=()):
        """Sorteia o herói alvo da próxima ação, se ela atingir um único herói.

        Heróis provocando atraem o ataque. Sem provocação, o sorteio é ponderado para espalhar o
        dano: o alvo da última vez deste inimigo e os heróis já mirados por outros inimigos nesta
        rodada (`ja_mirados`) têm menos chance.
        """
        rng = rng or random
        vivos = grupo.herois_vivos()
        if not vivos or self.intencao_atual["tipo"] not in TIPOS_ALVO_UNICO:
            self.alvo = None
            return
        provocando = [h for h in vivos if h.provocando]
        if provocando:
            self.alvo = rng.choice(provocando)
        else:
            pesos = [(PESO_ALVO_REPETIDO if heroi is self._ultimo_alvo else 1.0)
                     * PESO_ALVO_JA_MIRADO ** list(ja_mirados).count(heroi) for heroi in vivos]
            self.alvo = rng.choices(vivos, weights=pesos)[0]
        self._ultimo_alvo = self.alvo

    def herois_ameacados(self, grupo):
        """Heróis que a próxima ação vai atingir (para os marcadores na tela). Congelado não age."""
        if self.congelado > 0:
            return []
        tipo = self.intencao_atual["tipo"]
        if tipo == "ataque_area":
            return grupo.herois_vivos()
        if tipo in TIPOS_ALVO_UNICO and self.alvo is not None and not self.alvo.esta_derrotado():
            return [self.alvo]
        return []

    def executar_acao(self, grupo):
        """Executa a intenção atual, avança a rotina e devolve uma mensagem descritiva."""
        intencao = self.intencao_atual
        valor = self.valor_da_intencao(intencao)
        self.indice_rotina = (self.indice_rotina + 1) % len(self.rotina)
        alvo_escolhido, self.alvo = self.alvo, None
        tipo = intencao["tipo"]
        vezes = intencao.get("vezes", 1)
        golpes = f" EM {vezes} GOLPES" if vezes > 1 else ""

        if tipo in TIPOS_ALVO_UNICO:
            alvo = alvo_escolhido if alvo_escolhido is not None and not alvo_escolhido.esta_derrotado() \
                else grupo.alvo_para_inimigo()
            if alvo is None:
                return ""
            if alvo.esquiva > 0:
                alvo.esquiva -= 1
                return f"{self.nome} ERRA: {alvo.nome} SE ESQUIVA NA FUMAÇA!"
            if tipo == "veneno":
                alvo.veneno += valor
                return f"{self.nome} ENVENENA {alvo.nome} (+{valor} VENENO)"
            if tipo == "espectral":
                dano = sum(alvo.perder_vida(valor) for _ in range(vezes))
                return f"{self.nome} ATRAVESSA A DEFESA DE {alvo.nome}{golpes}: {dano} DE DANO"
            dano = sum(alvo.receber_dano(valor) for _ in range(vezes))
            if tipo == "dreno":
                curado = self.curar(dano)
                cura = f", +{curado} VIDA" if curado else ""
                return f"{self.nome} DRENA {alvo.nome}{golpes}: {dano} DE DANO{cura}"
            if dano == 0:
                return f"{self.nome} ATACA {alvo.nome}{golpes}: BLOQUEADO!"
            return f"{self.nome} ATACA {alvo.nome}{golpes}: {dano} DE DANO"
        if tipo == "ataque_area":
            total, esquivaram = 0, []
            for heroi in grupo.herois_vivos():
                if heroi.esquiva > 0:
                    heroi.esquiva -= 1
                    esquivaram.append(heroi.nome)
                else:
                    total += heroi.receber_dano(valor)
            verbo = "SE ESQUIVOU" if len(esquivaram) == 1 else "SE ESQUIVARAM"
            extra = f" ({' E '.join(esquivaram)} {verbo})" if esquivaram else ""
            return f"{self.nome} ATINGE TODO O GRUPO: {total} DE DANO NO TOTAL{extra}"
        if tipo == "defesa":
            self.ganhar_bloqueio(valor)
            return f"{self.nome} SE DEFENDE (+{valor} BLOQUEIO)"
        if tipo == "buff":
            self.forca += valor
            return f"{self.nome} FICA MAIS FORTE (+{valor} FORÇA)"
        return ""

    # ---------- desenho ----------
    def draw(self, dx=0, dy=0, **rotulo):
        super().draw(dx, dy, **rotulo)
        if self.esta_derrotado():
            return
        intencao = self.intencao_atual
        icone = self.icones_intencao[intencao["tipo"]]
        if self.congelado > 0:
            # congelado: a próxima ação não acontece
            icone.set_transparency(90)
            icone.draw()
            icone.set_transparency(255)
            fonte(3, "azul").desenhar("CONGELADO", icone.x + icone.width / 2, icone.y + icone.height / 2,
                                      "centro", True)
            return
        icone.draw()
        fonte(3, COR_INTENCAO[intencao["tipo"]]).desenhar(
            self.texto_da_intencao(), icone.x + icone.width + 6, icone.y + icone.height / 2, "esquerda", True)
