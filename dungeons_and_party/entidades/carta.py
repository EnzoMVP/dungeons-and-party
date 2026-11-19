from PPlay.gameimage import GameImage
from PPlay.sprite import Sprite

from entidades.heroi import ROUBO_SEDE
from entidades.inimigo import TIPOS_ALVO_UNICO
from sistemas import dados
from ui.texto import fonte

# Posições internas (pixels virtuais) derivadas da moldura 48x64 em escala 3.
_OFFSET_ILUSTRACAO = (12, 12)
_CENTRO_CUSTO = (22, 22)
_CENTRO_NOME_Y = 114
_CENTRO_DESCRICAO_Y = (150, 171)
_CENTRO_DESCRICAO_3_LINHAS_Y = (141, 156, 170)  # descrições de 3 linhas (especiais, buffs, debuffs)
_OFFSET_ICONE_COMBO = (108, 12)  # canto superior direito, sobre a janela da ilustração
DURACAO_BRILHO_ESPECIAL_MS = 700
MULTIPLICADOR_FURIA = 1.5  # dano das cartas de um herói com fúria
MULTIPLICADOR_VULNERAVEL = 1.5  # dano das cartas num inimigo vulnerável
ROUBO_MARCADO = 0.2  # fração do dano que vira vida ao atacar um inimigo marcado
# Efeitos de estado (ver ESTADOS em entidades/personagem.py): buffs miram um herói, debuffs um inimigo.
EFEITOS_BUFF = ("furia", "vigor", "esquiva", "sede", "acelerar")
EFEITOS_DEBUFF = ("quebrar", "vulneravel", "congelar", "fraqueza", "marcar")
# Efeitos de cartas passivas: somam ao estado de mesmo nome do dono até o fim do combate.
EFEITOS_PASSIVOS = ("bonus_energia", "bonus_compra", "peconha", "selvageria", "imortal")


class Carta:
    """Carta com lista de efeitos. Valores de dano, bloqueio e cura são multiplicados pelos
    atributos do herói dono: dano físico × força, dano de magia × poder, bloqueio × defesa, cura × poder.

    Efeitos: dano (vezes?, alvo "todos"?), bloqueio (alvo "proprio" ou "grupo"?), cura (alvo "grupo"?),
    veneno, energia, provocar, comprar, descartar (cartas escolhidas da mão, pagas antes dos outros
    efeitos) e perder_vida (o dono perde vida; a carta não pode ser jogada se isso o derrubasse).
    Buffs num herói (alvo "proprio"?): furia (vezes), vigor (× poder), esquiva (cargas), sede (vezes)
    e acelerar (vezes). Debuffs num inimigo: quebrar (zera o bloqueio), vulneravel (vezes), congelar
    (ações perdidas), fraqueza (vezes) e marcar (vezes).

    Variações de dano: "base" troca valor × força/poder por outra grandeza do dono ("velocidade",
    "bloqueio" ou "vida_perdida"); "por_rodada" soma esse valor a cada rodada do combate; "crescer"
    soma esse valor ao dano da carta, para sempre na run, a cada uso; "roubo" é a fração extra do
    dano causado que vira vida para o dono (somada ao roubo de vida do herói).

    Cartas passivas (`passiva` nos dados) saem do combate ao serem jogadas (ficam em jogo) e o efeito
    vale até o fim dele. Cartas especiais (`especial` nos dados) nascem da combinação de duas cartas do
    mesmo herói (ver sistemas/combo.py) e guardam as duas em `componentes`: quando a especial vai ao
    descarte, são as componentes que entram na pilha.
    """

    LARGURA = 144
    ALTURA = 192

    def __init__(self, id_carta, dados_carta):
        self.id = id_carta
        self.nome = dados_carta["nome"]
        self.classe = dados_carta["classe"]
        self.custo = dados_carta["custo"]
        self.tipo = dados_carta["tipo"]  # ataque, defesa ou magia (magia usa o poder do herói)
        self.efeitos = dados_carta["efeitos"]
        self.especial = dados_carta.get("especial", False)
        self.passiva = dados_carta.get("passiva", False)
        self._linhas_descricao = dados_carta.get("descricao")  # texto fixo com {n} = valor do efeito n
        self.componentes = []  # para especiais: as duas cartas que a formaram
        self.peca_de_combo = id_carta in dados.carregar("classes")[self.classe].get("combo", {}).get("cartas", [])
        self.dono = None  # herói que trouxe a carta para o baralho
        self.reliquias = None  # relíquias da run, para bônus passivos
        self.turno = None  # GerenciadorDeTurno do combate (rodada e velocidade); None fora de combate
        if self.especial:
            self.moldura = Sprite(f"images/cartas/moldura_especial_{self.classe}.png", 2)
            self.moldura.set_total_duration(DURACAO_BRILHO_ESPECIAL_MS)
        else:
            self.moldura = GameImage(f"images/cartas/moldura_{self.classe}.png")
        self.ilustracao = GameImage(f"images/cartas/ilustracao_{dados_carta['ilustracao']}.png")
        self.icone_combo = GameImage("images/icones/combo.png")
        self.x = 0
        self.y = 0
        self.elevacao = 0  # deslocamento vertical do hover, animado pela mão
        self.width = self.LARGURA
        self.height = self.ALTURA

    def set_position(self, x, y):
        self.x = x
        self.y = y

    # ---------- consultas ----------
    def causa_dano(self):
        return any(efeito["tipo"] == "dano" for efeito in self.efeitos)

    def mira_inimigo(self):
        """Se algum efeito atinge um inimigo escolhido (dano, veneno ou debuff)."""
        return any((e["tipo"] == "dano" and e.get("alvo") != "todos") or e["tipo"] == "veneno"
                   or e["tipo"] in EFEITOS_DEBUFF for e in self.efeitos)

    def eh_fisica(self):
        return self.tipo != "magia"

    def descartes_requeridos(self):
        """Quantas outras cartas da mão precisam ser descartadas para jogar esta."""
        return sum(e["valor"] for e in self.efeitos if e["tipo"] == "descartar")

    def vida_requerida(self):
        """Vida que o dono perde ao jogar a carta (ele precisa ter mais que isso)."""
        return sum(e["valor"] for e in self.efeitos if e["tipo"] == "perder_vida")

    def _multiplicador(self, atributo):
        if self.reliquias is not None:
            return self.reliquias.multiplicador(self.dono, atributo)
        return self.dono.atributos[atributo]

    def _velocidade_do_dono(self):
        if self.turno is not None:
            return self.turno.velocidade(self.dono)
        if self.reliquias is not None:
            return self.reliquias.velocidade(self.dono)
        return self.dono.atributos["velocidade"]

    def _rodada(self):
        return self.turno.numero_rodada if self.turno is not None else 1

    def valor_efetivo(self, efeito):
        valor = efeito.get("valor", 0)
        if self.dono is None:
            return valor
        tipo = efeito["tipo"]
        if tipo == "dano":
            return self._dano_efetivo(efeito)
        if tipo == "bloqueio":
            return max(1, round(valor * self._multiplicador("defesa")))
        if tipo in ("cura", "vigor"):
            return max(1, round(valor * self._multiplicador("poder")))
        return valor

    def _dano_efetivo(self, efeito):
        base = efeito.get("base")
        if base == "velocidade":
            dano = self._velocidade_do_dono()
        elif base == "bloqueio":
            dano = self.dono.bloqueio
        elif base == "vida_perdida":
            dano = self.dono.hp_max - self.dono.hp
        else:
            valor = efeito["valor"] + efeito.get("por_rodada", 0) * (self._rodada() - 1)
            dano = max(1, round(valor * self._multiplicador("forca" if self.eh_fisica() else "poder")))
        if self.eh_fisica() and self.reliquias is not None:
            dano += self.reliquias.bonus_dano_fisico()
        if efeito.get("crescer"):
            dano += self.dono.crescimento.get(self.id, 0)
        if self.dono.furia > 0:
            dano = round(dano * MULTIPLICADOR_FURIA)
        if self.dono.frenesi > 0:
            dano *= self.dono.frenesi
        return dano

    def _fracao_de_roubo(self, efeito):
        """Fração do dano causado por este efeito que volta como vida ao dono (sem o bônus do alvo)."""
        return self.dono.roubo_de_vida(self.reliquias) / 100 + efeito.get("roubo", 0)

    def descricao(self):
        """Linhas de texto (até 9 caracteres cada) com os valores já multiplicados."""
        if self._linhas_descricao:
            valores = [self.valor_efetivo(efeito) for efeito in self.efeitos]
            return [linha.format(*valores) for linha in self._linhas_descricao]
        if len(self.efeitos) == 1:
            efeito = self.efeitos[0]
            tipo, valor, vezes = efeito["tipo"], self.valor_efetivo(efeito), efeito.get("vezes", 1)
            if tipo == "dano":
                if efeito.get("alvo") == "todos":
                    return [f"CAUSE {valor}", "EM TODOS"]
                return [f"CAUSE {valor}", "DE DANO" if vezes == 1 else f"DANO X{vezes}"]
            if tipo == "bloqueio":
                return [f"GANHE {valor}", "BLOQUEIO"]
            if tipo == "comprar":
                return [f"COMPRE {valor}", "CARTAS" if valor > 1 else "CARTA"]
            if tipo == "cura":
                return [f"CURE {valor}", "DE VIDA"]
            if tipo == "veneno":
                return [f"APLIQUE {valor}", "VENENO"]
            if tipo == "energia":
                return [f"GANHE {valor}", "ENERGIA"]
            if tipo == "provocar":
                return ["PROVOCA", "INIMIGOS"]
        return [self._descricao_curta(efeito) for efeito in self.efeitos[:2]]

    def _descricao_curta(self, efeito):
        tipo, valor, vezes = efeito["tipo"], self.valor_efetivo(efeito), efeito.get("vezes", 1)
        if tipo == "dano":
            return f"{valor} DANO" if vezes == 1 else f"{valor} DANO X{vezes}"
        return {
            "bloqueio": f"{valor} BLOQ.",
            "comprar": f"COMPRE {valor}",
            "cura": f"CURE {valor}",
            "veneno": f"{valor} VENENO",
            "energia": f"+{valor} ENERG.",
            "provocar": "PROVOCA",
            "descartar": f"DESCAR. {valor}",
            "perder_vida": f"-{valor} VIDA",
            "furia": f"FÚRIA {valor}",
            "vigor": f"{valor} VIGOR",
            "esquiva": "ESQUIVA",
            "sede": f"SEDE {valor}",
            "acelerar": "VELOC. X2",
            "quebrar": "SEM BLOQ.",
            "vulneravel": f"VULNER. {valor}",
            "congelar": "CONGELA",
            "fraqueza": f"FRACO {valor}",
            "marcar": f"MARCA {valor}",
        }.get(tipo, "PASSIVA" if tipo in EFEITOS_PASSIVOS else "")

    # ---------- efeito ----------
    def aplicar(self, alvo_inimigo, alvo_heroi, inimigos, baralho, energia, herois=None, descartes=()):
        """Aplica os efeitos em ordem e devolve uma mensagem descrevendo o resultado.

        `herois` são os heróis vivos (para efeitos com alvo "grupo"); `descartes` são as cartas da mão
        escolhidas para o efeito descartar.
        """
        herois = herois if herois is not None else [alvo_heroi]
        descartes = list(descartes)
        partes = []
        for efeito in self.efeitos:
            tipo, valor = efeito["tipo"], self.valor_efetivo(efeito)
            if tipo == "dano":
                partes.append(self._aplicar_dano(efeito, valor, alvo_inimigo, inimigos))
                if efeito.get("crescer"):
                    self.dono.crescimento[self.id] = self.dono.crescimento.get(self.id, 0) + efeito["crescer"]
                    partes.append(f"+{efeito['crescer']} DE DANO PARA SEMPRE")
            elif tipo == "descartar":
                pagas, descartes = descartes[:valor], descartes[valor:]
                for carta in pagas:
                    baralho.retirar_da_mao(carta)
                    baralho.enviar_ao_descarte(carta)
                partes.append(f"DESCARTA {len(pagas)} CARTA" + ("S" if len(pagas) != 1 else ""))
            elif tipo == "perder_vida":
                partes.append(f"{self.dono.nome} PERDE {self.dono.perder_vida(valor)} DE VIDA")
            elif tipo in EFEITOS_PASSIVOS:
                partes.append(self._aplicar_passiva(tipo, valor))
            elif tipo == "bloqueio":
                if efeito.get("alvo") == "grupo":
                    for heroi in herois:
                        heroi.ganhar_bloqueio(valor)
                    partes.append(f"GRUPO GANHA {valor} DE BLOQUEIO")
                else:
                    destino = self.dono if efeito.get("alvo") == "proprio" else alvo_heroi
                    destino.ganhar_bloqueio(valor)
                    partes.append(f"{destino.nome} GANHA {valor} DE BLOQUEIO")
            elif tipo == "cura":
                if efeito.get("alvo") == "grupo":
                    total = sum(heroi.curar(valor) for heroi in herois)
                    partes.append(f"GRUPO RECUPERA {total} DE VIDA")
                else:
                    curado = alvo_heroi.curar(valor)
                    partes.append(f"{alvo_heroi.nome} RECUPERA {curado} DE VIDA")
            elif tipo == "veneno":
                alvo_inimigo.veneno += valor
                partes.append(f"{valor} DE VENENO NO {alvo_inimigo.nome}")
            elif tipo == "energia":
                energia.ganhar(valor)
                partes.append(f"+{valor} DE ENERGIA")
            elif tipo == "provocar":
                self.dono.provocando = True
                for inimigo in inimigos:
                    if not inimigo.esta_derrotado() and inimigo.intencao_atual["tipo"] in TIPOS_ALVO_UNICO:
                        inimigo.alvo = self.dono
                partes.append(f"{self.dono.nome} PROVOCA OS INIMIGOS")
            elif tipo == "comprar":
                compradas = len(baralho.comprar_de(self.dono, valor))
                partes.append(f"COMPRA {compradas} CARTA" + ("S" if compradas != 1 else ""))
            elif tipo in EFEITOS_BUFF:
                destino = self.dono if efeito.get("alvo") == "proprio" else alvo_heroi
                partes.append(self._aplicar_buff(tipo, valor, destino))
            elif tipo in EFEITOS_DEBUFF:
                partes.append(self._aplicar_debuff(tipo, valor, alvo_inimigo))
        return f"{self.nome}: " + ", ".join(partes)

    @staticmethod
    def _vezes(n):
        return f"{n} VEZ" if n == 1 else f"{n} VEZES"

    @staticmethod
    def _aplicar_buff(tipo, valor, heroi):
        if tipo == "furia":
            heroi.furia += valor
            return f"{heroi.nome} ENTRA EM FÚRIA (+50% DE DANO POR {Carta._vezes(heroi.furia)})"
        if tipo == "vigor":
            heroi.vigor += valor
            return f"{heroi.nome} GANHA {valor} DE VIGOR (CURA NO INÍCIO DE CADA VEZ)"
        if tipo == "sede":
            heroi.sede += valor
            return f"{heroi.nome} TEM SEDE DE SANGUE (ROUBA +{ROUBO_SEDE}% DE VIDA POR {Carta._vezes(heroi.sede)})"
        if tipo == "acelerar":
            heroi.acelerado += valor
            return f"{heroi.nome} ACELERA (VELOCIDADE X2 POR {Carta._vezes(heroi.acelerado)})"
        heroi.esquiva += valor
        return f"{heroi.nome} SOME NA FUMAÇA (ESQUIVA A PRÓXIMA AÇÃO INIMIGA)"

    @staticmethod
    def _aplicar_debuff(tipo, valor, inimigo):
        if tipo == "quebrar":
            perdido, inimigo.bloqueio = inimigo.bloqueio, 0
            return f"{inimigo.nome} PERDE {perdido} DE BLOQUEIO" if perdido else f"{inimigo.nome} SEM DEFESA"
        if tipo == "vulneravel":
            inimigo.vulneravel += valor
            return f"{inimigo.nome} FICA VULNERÁVEL (+50% DE DANO POR {Carta._vezes(inimigo.vulneravel)})"
        if tipo == "congelar":
            inimigo.congelado = max(inimigo.congelado, valor)  # não acumula: evita travar um inimigo
            return f"{inimigo.nome} CONGELA E PERDE A PRÓXIMA AÇÃO"
        if tipo == "marcar":
            inimigo.marcado += valor
            return (f"{inimigo.nome} SANGRA (ATACÁ-LO ROUBA +{round(ROUBO_MARCADO * 100)}% DE VIDA POR "
                    f"{Carta._vezes(inimigo.marcado)})")
        inimigo.fraqueza += valor
        return f"{inimigo.nome} FICA CEGO (-50% DE DANO POR {Carta._vezes(inimigo.fraqueza)})"

    def _aplicar_passiva(self, tipo, valor):
        heroi = self.dono
        setattr(heroi, tipo, getattr(heroi, tipo) + valor)
        return {
            "bonus_energia": f"{heroi.nome} GANHA +{valor} DE ENERGIA EM CADA VEZ",
            "bonus_compra": f"{heroi.nome} COMPRA +{valor} CARTA EM CADA VEZ",
            "peconha": f"OS ATAQUES DO {heroi.nome} APLICAM +{valor} VENENO",
            "selvageria": f"{heroi.nome} ROUBA +{valor}% DE VIDA",
            "imortal": f"{heroi.nome} SE RECUSA A CAIR (VOLTA COM 1 DE VIDA E DANO X3)",
        }[tipo] + " ATÉ O FIM DO COMBATE"

    def _aplicar_dano(self, efeito, valor, alvo_inimigo, inimigos):
        em_todos = efeito.get("alvo") == "todos"
        alvos = [i for i in inimigos if not i.esta_derrotado()] if em_todos else [alvo_inimigo]
        veneno_extra = 0
        if self.eh_fisica():
            veneno_extra = self.dono.peconha + (self.reliquias.veneno_em_ataque_fisico() if self.reliquias else 0)
        roubo = self._fracao_de_roubo(efeito)
        total, vida_roubada = 0, 0.0
        for alvo in alvos:
            golpe = round(valor * MULTIPLICADOR_VULNERAVEL) if alvo.vulneravel > 0 else valor
            hp_antes = alvo.hp
            for _ in range(efeito.get("vezes", 1)):
                total += alvo.receber_dano(golpe)
            fracao = roubo + (ROUBO_MARCADO if alvo.marcado > 0 else 0)
            vida_roubada += (hp_antes - alvo.hp) * min(1.0, fracao)
            alvo.veneno += veneno_extra
        if em_todos:
            texto = f"{total} DE DANO EM TODOS"
        else:
            texto = f"{total} DE DANO NO {alvo_inimigo.nome}" if total else f"BLOQUEADO PELO {alvo_inimigo.nome}"
        curado = self.dono.curar(round(vida_roubada)) if vida_roubada else 0
        return texto + (f" (ROUBA {curado} DE VIDA)" if curado else "")

    # ---------- desenho ----------
    def draw(self, jogavel=True, x=None, y=None, combo_pronto=False):
        """Desenha em (x, y) se informados; senão na posição da carta.

        `combo_pronto`: a carta forma um combo com outra da mão (o ícone de combo pisca).
        """
        x = self.x if x is None else x
        y = self.y if y is None else y
        alfa = 255 if jogavel else 140
        if self.especial:
            self.moldura.update()
        self.moldura.set_position(x, y)
        self.moldura.set_transparency(alfa)
        self.moldura.draw()
        self.ilustracao.set_position(x + _OFFSET_ILUSTRACAO[0], y + _OFFSET_ILUSTRACAO[1])
        self.ilustracao.set_transparency(alfa)
        self.ilustracao.draw()
        if self.peca_de_combo:
            self.icone_combo.set_position(x + _OFFSET_ICONE_COMBO[0], y + _OFFSET_ICONE_COMBO[1])
            self.icone_combo.set_transparency(255 if combo_pronto else min(alfa, 170))
            self.icone_combo.draw()

        centro_x = x + self.LARGURA / 2
        fonte(2, "escuro").desenhar(self.custo, x + _CENTRO_CUSTO[0], y + _CENTRO_CUSTO[1],
                                    "centro", True, alfa)
        cor_nome = "dourado" if self.especial else "azul" if self.passiva else "claro"
        fonte(2, cor_nome).desenhar(self.nome, centro_x, y + _CENTRO_NOME_Y, "centro", True, alfa)
        linhas = self.descricao()
        centros = _CENTRO_DESCRICAO_3_LINHAS_Y if len(linhas) == 3 else _CENTRO_DESCRICAO_Y
        for linha, centro_y in zip(linhas, centros):
            fonte(2, "escuro").desenhar(linha, centro_x, y + centro_y, "centro", True, alfa)
