import random

from PPlay.timer import Timer

from entidades.carta import EFEITOS_BUFF
from sistemas import combo
from sistemas.grupo import ENERGIA_BASE

INICIO_RODADA = "INICIO_RODADA"
VEZ_HEROI = "VEZ_HEROI"
FIM_DA_VEZ = "FIM_DA_VEZ"
VEZ_INIMIGO = "VEZ_INIMIGO"
VITORIA = "VITORIA"
DERROTA = "DERROTA"

ALVOS_SEM_ESCOLHA = ("proprio", "grupo", "todos")


class GerenciadorDeTurno:
    """FSM do combate em rodadas: todos os vivos (heróis e inimigos) agem uma vez por rodada,
    na ordem decrescente de velocidade (empate: herói primeiro).

    - Vez de herói (VEZ_HEROI): o herói sofre o veneno (se cair, a vez passa), recebe de volta as
      cartas que guardou, compra `cartas_por_vez(heroi)` menos as guardadas e recebe a energia total
      dele (ENERGIA_BASE + passivas).
    - Fim da vez (FIM_DA_VEZ): quando não resta jogada (ou pelo botão), se ainda há cartas na mão
      o jogador escolhe MANTER (as cartas voltam na próxima vez dele, que compra menos) ou
      DESCARTAR (vão ao descarte, e a próxima vez compra todas novas). Mão vazia passa sozinha.
    - Vez de inimigo (VEZ_INIMIGO): sofre o veneno e executa a intenção, espaçado por Timer.

    Combos: duas cartas do combo da classe na mão do herói da vez podem ser fundidas numa
    carta especial (sistemas/combo.py), em VEZ_HEROI ou FIM_DA_VEZ.

    O Timer do PPlay é global e não cancela agendamentos: cada vez tem um número (`_vez`) e os
    callbacks só agem se ainda for a mesma vez.
    """

    CARTAS_POR_VEZ = 3
    ATRASO_ACAO_INIMIGO = 0.8
    ATRASO_ENTRE_VEZES = 0.35
    ATRASO_FIM_AUTOMATICO = 0.7

    def __init__(self, grupo, baralho, inimigos, reliquias, rng=None):
        self.grupo = grupo
        self.baralho = baralho
        self.inimigos = inimigos
        self.reliquias = reliquias
        self.rng = rng or random.Random()
        self.estado = None
        self.numero_rodada = 0
        self.mensagem = ""
        self.ordem = []
        self.indice = -1
        self.atual = None
        self.passando_vez = False  # fim automático agendado (mão vazia, para a interface avisar)
        self.fim_voluntario = False  # FIM_DA_VEZ aberto pelo botão (pode ser cancelado)
        self._vez = 0
        self._herois_caidos = set()
        self._ja_agiram = set()

    # ---------- consultas ----------
    def eh_heroi(self, participante):
        return participante in self.grupo.herois

    def velocidade(self, participante):
        if self.eh_heroi(participante):
            return self.reliquias.velocidade(participante) * (2 if participante.acelerado > 0 else 1)
        return participante.velocidade

    def cartas_por_vez(self, heroi):
        return self.CARTAS_POR_VEZ + heroi.bonus_compra

    @staticmethod
    def energia_total(heroi):
        return ENERGIA_BASE + heroi.bonus_energia

    def vez_do_jogador(self):
        """Se o herói da vez pode jogar cartas agora."""
        return self.estado == VEZ_HEROI

    def escolhendo_fim(self):
        return self.estado == FIM_DA_VEZ

    def combate_terminou(self):
        return self.estado in (VITORIA, DERROTA)

    def inimigos_vivos(self):
        return [i for i in self.inimigos if not i.esta_derrotado()]

    def pode_jogar(self, carta):
        return self.vez_do_jogador() and carta.dono is self.atual and self._jogavel(carta)

    def _jogavel(self, carta):
        """Energia para o custo, cartas na mão para os descartes e vida para o custo em vida."""
        outras = sum(1 for c in self.baralho.mao if c is not carta)
        return (self.grupo.energia.pode_pagar(carta.custo) and outras >= carta.descartes_requeridos()
                and carta.dono.hp > carta.vida_requerida())

    def tem_jogada(self):
        return any(self.pode_jogar(carta) for carta in self.baralho.mao)

    def combo_disponivel(self):
        """As duas cartas do herói da vez que podem ser combinadas agora, ou None."""
        if self.estado not in (VEZ_HEROI, FIM_DA_VEZ) or not self.eh_heroi(self.atual):
            return None
        return combo.par_na_mao(self.atual, self.baralho.mao)

    def _tem_acao(self):
        """Ainda há algo útil a fazer na vez (em VEZ_HEROI ou FIM_DA_VEZ): jogar uma carta do herói
        da vez ou combinar e poder pagar a especial."""
        heroi, energia = self.atual, self.grupo.energia
        if any(c.dono is heroi and self._jogavel(c) for c in self.baralho.mao):
            return True
        return (self.combo_disponivel() is not None
                and energia.pode_pagar(combo.custo_da_especial(heroi.classe)))

    def ja_agiu_na_rodada(self, participante):
        return participante in self.ordem[:max(0, self.indice)]

    def alvo_requerido(self, carta):
        """'heroi' ou 'inimigo' se o jogador precisa escolher o alvo da carta; None se é automático."""
        precisa_heroi = any(e["tipo"] in ("cura", "bloqueio") + EFEITOS_BUFF
                            and e.get("alvo") not in ALVOS_SEM_ESCOLHA for e in carta.efeitos)
        precisa_inimigo = carta.mira_inimigo()
        if precisa_heroi and len(self.grupo.herois_vivos()) > 1:
            return "heroi"
        if precisa_inimigo and len(self.inimigos_vivos()) > 1:
            return "inimigo"
        return None

    # ---------- rodada e vezes ----------
    def iniciar_combate(self):
        for heroi in self.grupo.herois:
            heroi.zerar_estados()  # veneno, buffs e passivas não passam de um combate para o outro
        for carta in self.baralho.todas():
            carta.turno = self  # rodada e velocidade para cartas que dependem delas
        self._iniciar_rodada()

    def _iniciar_rodada(self):
        self.numero_rodada += 1
        self.estado = INICIO_RODADA
        participantes = self.grupo.herois_vivos() + self.inimigos_vivos()
        self.ordem = sorted(participantes, key=lambda p: (-self.velocidade(p), 0 if self.eh_heroi(p) else 1))
        ja_mirados = []
        for inimigo in self.inimigos_vivos():
            inimigo.escolher_alvo(self.grupo, self.rng, ja_mirados)
            if inimigo.alvo is not None:
                ja_mirados.append(inimigo.alvo)
        self.indice = -1
        self._avancar()

    def _avancar(self):
        self._verificar_fim()
        if self.combate_terminou():
            return
        self._vez += 1
        self.passando_vez = False
        self.fim_voluntario = False
        while True:
            self.indice += 1
            if self.indice >= len(self.ordem):
                self._iniciar_rodada()
                return
            if not self.ordem[self.indice].esta_derrotado():
                break
        self.atual = self.ordem[self.indice]
        if self.eh_heroi(self.atual):
            self._iniciar_vez_heroi(self.atual)
        else:
            self._iniciar_vez_inimigo(self.atual)

    def _avancar_se_ainda_for(self, vez):
        if vez == self._vez and not self.combate_terminou():
            self._avancar()

    def _iniciar_vez_heroi(self, heroi):
        dano_veneno = heroi.sofrer_veneno()
        if dano_veneno:
            self.mensagem = f"{heroi.nome} SOFRE {dano_veneno} DE VENENO. {self._anunciar_renascimentos()}".strip()
        if heroi.esta_derrotado():
            # O veneno derrubou o herói antes de ele agir: a vez passa adiante.
            self._processar_herois_caidos()
            self.mensagem += f" {heroi.nome} CAIU!"
            self.estado = INICIO_RODADA
            self._verificar_fim()
            if not self.combate_terminou():
                Timer.after(self.ATRASO_ENTRE_VEZES, self._avancar_se_ainda_for, self._vez)
            return
        curado = heroi.receber_vigor()
        if curado:
            self.mensagem = f"{heroi.nome} RECUPERA {curado} DE VIDA COM O VIGOR."
        self.estado = VEZ_HEROI
        heroi.bloqueio = self.reliquias.bloqueio_no_inicio_da_vez()
        heroi.provocando = False
        primeira_vez = heroi not in self._ja_agiram
        self._ja_agiram.add(heroi)
        self.grupo.energia.restaurar(self.energia_total(heroi), self.reliquias.energia_extra(primeira_vez))
        guardadas = self.baralho.devolver_guardadas(heroi)
        compra = self.cartas_por_vez(heroi) + self.reliquias.compra_extra(primeira_vez) - guardadas
        self.baralho.comprar_de(heroi, max(0, compra))
        if guardadas:
            self.mensagem = f"{heroi.nome} RECUPERA {guardadas} CARTA{'S' if guardadas > 1 else ''} GUARDADA" \
                            f"{'S' if guardadas > 1 else ''}"
        self._verificar_fim_da_vez()

    def _iniciar_vez_inimigo(self, inimigo):
        self.estado = VEZ_INIMIGO
        inimigo.bloqueio = 0
        Timer.after(self.ATRASO_ACAO_INIMIGO, self._acao_inimigo, inimigo, self._vez)

    def _acao_inimigo(self, inimigo, vez):
        if vez != self._vez or self.estado != VEZ_INIMIGO:
            return
        partes = []
        dano_veneno = inimigo.sofrer_veneno()
        if dano_veneno:
            partes.append(f"{inimigo.nome} SOFRE {dano_veneno} DE VENENO.")
        if not inimigo.esta_derrotado():
            if inimigo.congelado > 0:
                inimigo.congelado -= 1  # a intenção fica para a próxima vez
                partes.append(f"{inimigo.nome} ESTÁ CONGELADO E PERDE A VEZ.")
            else:
                partes.append(inimigo.executar_acao(self.grupo))
            inimigo.fim_da_propria_vez()
        for heroi in self._processar_herois_caidos():
            partes.append(f"{heroi.nome} CAIU!")
        partes.append(self._anunciar_renascimentos())
        self.mensagem = " ".join(p for p in partes if p)
        self._verificar_fim()
        if not self.combate_terminou():
            Timer.after(self.ATRASO_ENTRE_VEZES, self._avancar_se_ainda_for, vez)

    # ---------- ações do jogador ----------
    def jogar_carta(self, carta, alvo_heroi=None, alvo_inimigo=None, descartes=None):
        """Joga a carta do herói da vez. Alvos omitidos (ou inválidos) são escolhidos automaticamente,
        assim como as cartas a descartar que faltarem em `descartes`."""
        if not self.pode_jogar(carta):
            return False
        descartes = self._completar_descartes(carta, descartes or [])
        inimigos = self.inimigos_vivos()
        herois = self.grupo.herois_vivos()
        precisa_inimigo = carta.mira_inimigo() or carta.causa_dano()
        if precisa_inimigo and not inimigos:
            return False
        if alvo_inimigo not in inimigos:
            alvo_inimigo = inimigos[0] if inimigos else None
        if alvo_heroi not in herois:
            alvo_heroi = carta.dono

        self.grupo.energia.gastar(carta.custo)
        self.baralho.retirar_da_mao(carta)
        self.mensagem = carta.aplicar(alvo_inimigo, alvo_heroi, self.inimigos, self.baralho,
                                      self.grupo.energia, herois, descartes)
        if carta.passiva:
            self.baralho.colocar_em_jogo(carta)
        else:
            self.baralho.enviar_ao_descarte(carta)
        self._verificar_fim()
        if not self.combate_terminou():
            self._verificar_fim_da_vez()
        return True

    def _completar_descartes(self, carta, escolhidas):
        """As cartas que a carta vai descartar: as escolhidas válidas (da mão, distintas, sem a própria)
        e, se faltarem, as últimas da mão."""
        validas = []
        for c in escolhidas:
            if c in self.baralho.mao and c is not carta and c not in validas:
                validas.append(c)
        necessarias = carta.descartes_requeridos()
        for c in reversed(self.baralho.mao):
            if len(validas) >= necessarias:
                break
            if c is not carta and c not in validas:
                validas.append(c)
        return validas[:necessarias]

    def combinar(self):
        """Funde as duas cartas do combo do herói da vez na carta especial. Devolve (a, b, especial)."""
        par = self.combo_disponivel()
        if par is None:
            return None
        carta_a, carta_b = par
        especial = combo.criar_especial(self.atual, carta_a, carta_b, self.reliquias)
        especial.turno = self
        self.baralho.combinar(carta_a, carta_b, especial)
        self.mensagem = f"{carta_a.nome} + {carta_b.nome}: {especial.nome}!"
        if self.estado == FIM_DA_VEZ and self._tem_acao():
            self.estado = VEZ_HEROI  # agora dá para pagar a especial: a vez continua
            self.fim_voluntario = False
        self._verificar_fim_da_vez()
        return carta_a, carta_b, especial

    def encerrar_vez(self):
        """Botão PASSAR VEZ: com cartas na mão, abre a escolha entre manter e descartar."""
        if not self.vez_do_jogador():
            return
        if self.baralho.mao:
            self.estado = FIM_DA_VEZ
            self.fim_voluntario = True
        else:
            self._finalizar_vez(manter=False)

    def cancelar_fim_da_vez(self):
        """Volta a jogar (só se a escolha foi aberta pelo botão e ainda há jogada)."""
        if self.escolhendo_fim() and self.fim_voluntario and self._tem_acao():
            self.estado = VEZ_HEROI
            self.fim_voluntario = False

    def manter_cartas(self):
        if self.escolhendo_fim():
            self._finalizar_vez(manter=True)

    def descartar_cartas(self):
        if self.escolhendo_fim():
            self._finalizar_vez(manter=False)

    def _finalizar_vez(self, manter):
        heroi = self.atual
        heroi.fim_da_propria_vez()
        quantidade = len(self.baralho.mao)
        if manter and quantidade:
            self.baralho.guardar_mao(heroi)
            self.mensagem = f"{heroi.nome} GUARDA {quantidade} CARTA{'S' if quantidade > 1 else ''}"
        else:
            self.baralho.descartar_mao()
        self.estado = INICIO_RODADA
        self.passando_vez = False
        self.fim_voluntario = False
        Timer.after(self.ATRASO_ENTRE_VEZES, self._avancar_se_ainda_for, self._vez)

    def _verificar_fim_da_vez(self):
        """Sem nada a fazer: com cartas na mão abre a escolha; mão vazia passa a vez sozinha."""
        if not self.vez_do_jogador() or self._tem_acao():
            return
        if self.baralho.mao:
            self.estado = FIM_DA_VEZ
            self.fim_voluntario = False
        elif not self.passando_vez:
            self.passando_vez = True
            Timer.after(self.ATRASO_FIM_AUTOMATICO, self._fim_automatico, self._vez)

    def _fim_automatico(self, vez):
        if vez == self._vez and self.vez_do_jogador() and not self._tem_acao():
            self._finalizar_vez(manter=False)

    # ---------- fim ----------
    def _anunciar_renascimentos(self):
        """Texto para quem a carga de imortal acabou de segurar com 1 de vida."""
        textos = []
        for heroi in self.grupo.herois:
            if heroi.renasceu:
                heroi.renasceu = False
                textos.append(f"{heroi.nome} SE RECUSA A CAIR: FRENESI (DANO X{heroi.frenesi})!")
        return " ".join(textos)

    def _processar_herois_caidos(self):
        """Heróis que acabaram de cair têm suas cartas removidas do baralho."""
        caidos = [h for h in self.grupo.herois if h.esta_derrotado() and h not in self._herois_caidos]
        for heroi in caidos:
            self._herois_caidos.add(heroi)
            self.baralho.remover_cartas_de(heroi)
        return caidos

    def _verificar_fim(self):
        if self.combate_terminou():
            return
        if not self.inimigos_vivos():
            self.estado = VITORIA
        elif self.grupo.todos_derrotados():
            self.estado = DERROTA
