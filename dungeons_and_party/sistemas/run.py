import random

from entidades.heroi import Heroi
from sistemas import dados
from sistemas.atributos import ATRIBUTOS_INTEIROS, sortear_atributos
from sistemas.dificuldade import escalar_inimigo
from sistemas.grupo import Grupo
from sistemas.mapa import gerar_mapa
from sistemas.reliquias import Reliquias

FRACAO_CURA_DESCANSO = 0.3


class Run:
    """Estado de uma partida completa: grupo (HP e atributos persistentes), relíquias, mapa,
    nó atual e as etapas pendentes após um encontro (recompensa de carta, recrutamento)."""

    def __init__(self, heroi_lider, semente=None):
        self.classe_lider = heroi_lider.classe
        self.grupo = Grupo()
        self.grupo.adicionar_heroi(heroi_lider)
        self.reliquias = Reliquias()
        self.mapa = gerar_mapa(random.Random(semente))
        self.rng = random.Random(None if semente is None else semente + 1)
        self.no_atual = None
        self.caminho = []  # nós escolhidos, em ordem
        self.combates_vencidos = 0
        self.etapas_pendentes = []
        # Histórico para o sorteio não repetir o que o jogador acabou de ver.
        self.encontros_vistos = []  # grupos de inimigos já enfrentados (tuplas de tipos)
        self.eventos_vistos = []
        self._ultima_oferta = []  # pares (herói, carta) da última recompensa

    @classmethod
    def nova(cls, classe_lider, semente=None):
        return cls(cls.criar_heroi(classe_lider, lider=True), semente)

    @staticmethod
    def criar_heroi(classe, lider=False, rng=None):
        dados_classe = dados.carregar("classes")[classe]
        return Heroi(classe, dados_classe, sortear_atributos(dados_classe, rng), lider=lider)

    # ---------- mapa ----------
    def proximos_nos(self):
        if self.no_atual is None:
            return list(self.mapa[0])
        return list(self.no_atual.conectados)

    def escolher_no(self, no):
        if no not in self.proximos_nos():
            raise ValueError("nó não alcançável a partir da posição atual")
        self.no_atual = no
        self.caminho.append(no)

    @property
    def encontro_atual(self):
        """Tipo do encontro em andamento (combate, evento, descanso, tesouro ou chefe), ou None."""
        if self.no_atual is None or self.no_atual.visitado:
            return None
        return self.no_atual.tipo

    def concluir_encontro(self, recompensa_extra=False):
        """Marca o nó como visitado e define as etapas seguintes.

        Combates dão recompensa de carta e, se houver vaga no grupo, oferecem o recrutamento
        automaticamente. Eventos, descanso, tesouro e o chefe não oferecem recrutamento.
        """
        no = self.no_atual
        no.visitado = True
        self.etapas_pendentes = []
        if no.tipo in ("combate", "chefe"):
            self.grupo.remover_derrotados()
            self.combates_vencidos += 1
            for heroi in self.grupo.herois:
                heroi.curar(self.reliquias.cura_pos_combate())
        if no.tipo == "combate" or recompensa_extra:
            self.etapas_pendentes.append("recompensa")
        if no.tipo == "combate" and self.classes_recrutaveis():
            self.etapas_pendentes.append("recrutamento")

    def proxima_etapa(self):
        return self.etapas_pendentes.pop(0) if self.etapas_pendentes else None

    def terminou(self):
        return self.mapa[-1][0].visitado

    def andar_atual(self):
        return 0 if self.no_atual is None else self.no_atual.camada + 1

    def total_andares(self):
        return len(self.mapa)

    # ---------- combate ----------
    def inimigos_do_encontro(self):
        """Dados (já escalados pelo andar e pelo tamanho do grupo) dos inimigos do nó atual."""
        inimigos = dados.carregar("inimigos")
        encontros = dados.carregar("encontros")
        tamanho_grupo = len(self.grupo.herois_vivos())
        if self.no_atual.tipo == "chefe":
            return [escalar_inimigo(inimigos[tipo], 0, tamanho_grupo) for tipo in encontros["chefe"]]
        andares = encontros["andares"]
        andar = self._andar_de_combate()
        grupo_inimigos = self._sortear_encontro(andares[min(andar, len(andares) - 1)])
        return [escalar_inimigo(inimigos[tipo], andar, tamanho_grupo) for tipo in grupo_inimigos]

    def _sortear_encontro(self, opcoes):
        """Sorteia um grupo de inimigos do andar sem repetir um grupo já enfrentado na run e, se
        possível, sem repetir nenhum tipo de inimigo do combate anterior."""
        ineditos = [g for g in opcoes if tuple(g) not in self.encontros_vistos] or opcoes
        anterior = set(self.encontros_vistos[-1]) if self.encontros_vistos else set()
        variados = [g for g in ineditos if not set(g) & anterior] or ineditos
        escolhido = self.rng.choice(variados)
        self.encontros_vistos.append(tuple(escolhido))
        return escolhido

    def _andar_de_combate(self):
        """Quantas camadas de combate vêm antes do nó atual (0 = primeiro combate)."""
        return sum(1 for camada in self.mapa[:self.no_atual.camada] if camada[0].tipo == "combate")

    def sortear_recompensas(self, quantidade=3):
        """Pares (herói, id da carta) com cartas da classe de heróis vivos, sem repetir.

        Cartas que o herói ainda não tem e que não estavam na última oferta têm prioridade.
        """
        classes = dados.carregar("classes")
        opcoes = [(h, c) for h in self.grupo.herois_vivos() for c in classes[h.classe]["recompensas"]]
        self.rng.shuffle(opcoes)
        opcoes.sort(key=lambda par: (par[1] in par[0].cartas) + (par in self._ultima_oferta))  # estável
        escolhidas = []
        for heroi, carta in opcoes:  # primeiro, uma carta para cada herói diferente
            if heroi not in [h for h, _ in escolhidas]:
                escolhidas.append((heroi, carta))
        for par in opcoes:  # depois, completa com as restantes
            if par not in escolhidas:
                escolhidas.append(par)
        self._ultima_oferta = escolhidas[:quantidade]
        return self._ultima_oferta

    # ---------- recrutamento ----------
    def classes_recrutaveis(self):
        if self.grupo.cheio():
            return []
        presentes = self.grupo.classes()
        return [classe for classe in dados.carregar("classes") if classe not in presentes]

    def sortear_candidatos(self):
        return [self.criar_heroi(classe, rng=self.rng) for classe in self.classes_recrutaveis()]

    def recrutar(self, heroi):
        if self.reliquias.tem("coracao_de_ferro"):
            heroi.hp_max += 8
            heroi.hp += 8
        self.grupo.adicionar_heroi(heroi)

    # ---------- eventos, descanso e tesouro ----------
    def sortear_evento(self):
        """Evento ainda não visto nesta run (quando todos já saíram, qualquer um)."""
        eventos = dados.carregar("eventos")
        ineditos = [e for e in sorted(eventos) if e not in self.eventos_vistos] or sorted(eventos)
        escolhido = self.rng.choice(ineditos)
        self.eventos_vistos.append(escolhido)
        return eventos[escolhido]

    def aplicar_efeitos_de_evento(self, efeitos):
        """Aplica os efeitos de uma opção de evento. Devolve (texto extra, ganhou recompensa de carta)."""
        extras, recompensa = [], False
        vivos = self.grupo.herois_vivos()
        for efeito in efeitos:
            tipo = efeito["tipo"]
            if tipo == "dano_grupo":
                for heroi in vivos:
                    heroi.hp = max(1, heroi.hp - efeito["valor"])  # eventos não matam
            elif tipo == "cura_grupo":
                for heroi in vivos:
                    heroi.curar(efeito["valor"])
            elif tipo == "reliquia":
                id_reliquia = self.reliquias.sortear_nova(self.rng)
                self.reliquias.adicionar(id_reliquia, self.grupo)
                if id_reliquia:
                    extras.append(f"RELÍQUIA: {dados.carregar('reliquias')[id_reliquia]['nome']}")
            elif tipo == "atributo":
                heroi = self.rng.choice(vivos)
                atributo = efeito["atributo"]
                heroi.atributos[atributo] = round(heroi.atributos[atributo] + efeito["valor"], 1)
                if atributo in ATRIBUTOS_INTEIROS:
                    heroi.atributos[atributo] = int(heroi.atributos[atributo])
                extras.append(f"{heroi.nome} MELHOROU.")
            elif tipo == "carta":
                recompensa = True
        return " ".join(extras), recompensa

    def descansar(self):
        for heroi in self.grupo.herois_vivos():
            heroi.curar(round(heroi.hp_max * FRACAO_CURA_DESCANSO))

    def abrir_tesouro(self):
        id_reliquia = self.reliquias.sortear_nova(self.rng)
        self.reliquias.adicionar(id_reliquia, self.grupo)
        return id_reliquia
