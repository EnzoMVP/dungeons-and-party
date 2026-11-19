from PPlay.gameimage import GameImage
from PPlay.scenemanager import Scene, SceneManager
from PPlay.timer import Timer

from entidades.carta import Carta
from entidades.inimigo import Inimigo
from sistemas import dados
from sistemas.baralho import Baralho
from sistemas.turno import FIM_DA_VEZ, GerenciadorDeTurno, INICIO_RODADA, VEZ_HEROI, VEZ_INIMIGO, VITORIA
from ui import audio
from ui.barra_reliquias import BarraReliquias
from ui.botao import Botao
from ui.efeitos_combate import EfeitosDeCombate
from ui.indicador_energia import IndicadorEnergia
from ui.mao import MaoDeCartas
from ui.nevoa import nevoa_da_masmorra
from ui.numeros_flutuantes import NumerosFlutuantes
from ui.painel_classe import desenhar_atributo, icones_de_atributos
from ui.pilha import IconePilha
from ui.texto import fonte
from ui.visualizador_pilha import VisualizadorPilha

# Layout (pixels virtuais do canvas 960x540)
TOPO_PERSONAGENS = 138
LARGURA_AREA_HEROIS = 600
PASSO_HEROIS = 185
X_INIMIGO_UNICO = 696
X_INIMIGOS_EM_GRUPO = [606, 796]  # até 2 inimigos por encontro
MAO_ESQUERDA = 210
MAO_DIREITA = 630
MAO_Y = 340
# Coluna de ações à direita da mão: COMBINAR em cima, MANTER no meio, PASSAR VEZ/DESCARTAR embaixo.
X_ACOES = 634
Y_COMBINAR = 352
Y_MANTER = 408

TEXTO_SELECAO = {
    "heroi": "ESCOLHA UM HERÓI COMO ALVO (BOTÃO DIREITO CANCELA)",
    "inimigo": "ESCOLHA UM INIMIGO COMO ALVO (BOTÃO DIREITO CANCELA)",
    "descarte": "ESCOLHA {n} CARTA{s} PARA DESCARTAR (BOTÃO DIREITO CANCELA)",
}


class CombateScene(Scene):
    """Combate em rodadas por velocidade: heróis e inimigos agem um de cada vez (ver GerenciadorDeTurno)."""

    def __init__(self, run):
        super().__init__()
        self.run = run
        self.grupo = run.grupo
        largura, altura = self.janela.largura, self.janela.altura

        self.fundo = GameImage("images/fundos/masmorra.png")
        self.icone_alvo = GameImage("images/icones/alvo.png")
        self.icone_selecao = GameImage("images/icones/selecao.png")
        self.icones_atributos = icones_de_atributos()

        self._posicionar_herois()
        self.baralho = Baralho(run.rng)
        dados_cartas = dados.carregar("cartas")
        for heroi in self.grupo.herois_vivos():
            heroi.bloqueio = 0
            heroi.provocando = False
            cartas = [Carta(id_carta, dados_cartas[id_carta]) for id_carta in heroi.cartas]
            for carta in cartas:
                carta.dono = heroi
                carta.reliquias = run.reliquias
            self.baralho.adicionar_cartas(cartas)

        dados_inimigos = run.inimigos_do_encontro()
        posicoes = [X_INIMIGO_UNICO] if len(dados_inimigos) == 1 else X_INIMIGOS_EM_GRUPO
        self.inimigos = []
        for i, (dados_inimigo, x) in enumerate(zip(dados_inimigos, posicoes)):
            # inimigos iguais começam em pontos diferentes da rotina, para não agirem em uníssono
            iguais_antes = sum(1 for d in dados_inimigos[:i] if d["sprite"] == dados_inimigo["sprite"])
            inimigo = Inimigo(dados_inimigo["sprite"], dados_inimigo, indice_inicial=iguais_antes)
            inimigo.set_position(x, TOPO_PERSONAGENS)
            self.inimigos.append(inimigo)

        self.botao_passar = Botao("PASSAR VEZ", largura - 210 - 24, altura - 48 - 24)
        self.botao_descartar = Botao("DESCARTAR", largura - 210 - 24, altura - 48 - 24)
        self.botao_manter = Botao("MANTER", X_ACOES, Y_MANTER)
        self.botao_combinar = Botao("COMBINAR", X_ACOES, Y_COMBINAR, "images/ui/botao_combo.png")
        self.icone_guardadas = GameImage("images/icones/guardadas.png")
        self.pilha_compra = IconePilha("images/ui/pilha_compra.png", 20, altura - 96 - 6, "VER COMPRA", "acima")
        self.indicador_energia = IndicadorEnergia(104, altura - 96 - 6)
        self.pilha_descarte = IconePilha("images/ui/pilha_descarte.png", largura - 72 - 30, 350,
                                         "VER DESCARTE", "esquerda")
        self.mao = MaoDeCartas(self.baralho, MAO_ESQUERDA, MAO_DIREITA, MAO_Y,
                               self.pilha_compra, self.pilha_descarte, self._posicao_guardada)
        self.visualizador = VisualizadorPilha()
        self.numeros = NumerosFlutuantes(self.grupo.herois + self.inimigos)
        self.efeitos = EfeitosDeCombate(self.grupo.herois, self.inimigos)
        self.nevoa = nevoa_da_masmorra()
        self.barra_reliquias = BarraReliquias(run.reliquias, 12, 36)
        audio.tocar_musica("musica_combate")

        self.turno = GerenciadorDeTurno(self.grupo, self.baralho, self.inimigos, run.reliquias, run.rng)
        self.turno.iniciar_combate()
        self.carta_pendente = None  # carta esperando o jogador escolher cartas a descartar ou um alvo
        self.tipo_alvo = None  # "descarte", "heroi" ou "inimigo"
        self.descartes = []  # cartas já escolhidas para o descarte da carta pendente
        self.saindo = False

    def _posicionar_herois(self):
        """Heróis centralizados na metade esquerda; o líder fica à frente (mais perto dos inimigos)."""
        herois = self.grupo.herois
        n = len(herois)
        largura = 144 + PASSO_HEROIS * (n - 1)
        x0 = (LARGURA_AREA_HEROIS - largura) / 2
        for i, heroi in enumerate(herois):
            heroi.set_position(x0 + (n - 1 - i) * PASSO_HEROIS, TOPO_PERSONAGENS)

    # ---------- lógica ----------
    def loop(self):
        self.numeros.atualizar()
        self.efeitos.atualizar()
        self.nevoa.atualizar()
        if self.visualizador.aberto:
            self.visualizador.atualizar()
            self.mao.atualizar(interativa=False)
            return

        if self.saindo:
            self.mao.atualizar(interativa=False)
            return
        if self.turno.combate_terminou():
            self.saindo = True
            self._cancelar_selecao()
            if self.turno.estado == VITORIA:
                audio.tocar_efeito("vitoria")
            Timer.after(1.2, self._ir_para_resultado)
            return

        if self.carta_pendente is not None:
            self._atualizar_selecao_de_alvo()
            return

        vez_do_jogador = self.turno.vez_do_jogador()
        escolhendo_fim = self.turno.escolhendo_fim()
        par_combo = self.turno.combo_disponivel()
        self.mao.combo_destacado = set(par_combo) if par_combo else set()
        self.mao.atualizar(interativa=vez_do_jogador or escolhendo_fim)
        self.botao_passar.habilitado = vez_do_jogador and not self.turno.passando_vez
        self.botao_combinar.habilitado = par_combo is not None

        if self.pilha_compra.foi_clicado():
            # A ordem da pilha de compra não é revelada: as cartas aparecem ordenadas.
            ordenadas = sorted(self.baralho.compra, key=lambda c: (c.classe, c.custo, c.nome))
            self.visualizador.abrir("PILHA DE COMPRA", ordenadas)
        elif self.pilha_descarte.foi_clicado():
            self.visualizador.abrir("PILHA DE DESCARTE", self.baralho.descarte)
        elif par_combo is not None and self.botao_combinar.foi_clicado():
            self._combinar()
        elif escolhendo_fim:
            if self.botao_manter.foi_clicado():
                self.turno.manter_cartas()
            elif self.botao_descartar.foi_clicado():
                self.turno.descartar_cartas()
            elif self.mouse.button_down(3) or self.teclado.key_down("ESC"):
                self.turno.cancelar_fim_da_vez()
        elif self.botao_passar.foi_clicado():
            self.turno.encerrar_vez()
        elif self.mao.carta_sob_mouse is not None and self.mouse.button_down(1):
            self._clicar_carta(self.mao.carta_sob_mouse)

    def _combinar(self):
        resultado = self.turno.combinar()
        if resultado is None:
            return
        carta_a, carta_b, _especial = resultado
        # centro do ponto onde as duas cartas se encontram (a mão anima a fusão)
        x = (carta_a.x + carta_b.x) / 2 + Carta.LARGURA / 2
        y = (carta_a.y - carta_a.elevacao + carta_b.y - carta_b.elevacao) / 2 + Carta.ALTURA / 2
        self.efeitos.combinacao(x, y)

    def _posicao_guardada(self, carta):
        """Canto superior esquerdo de uma carta centralizada no herói dono (cartas guardadas)."""
        heroi = carta.dono
        sprite = heroi.sprite
        return (heroi.x_base + sprite.width / 2 - Carta.LARGURA / 2,
                heroi.y_base + sprite.height / 2 - Carta.ALTURA / 2)

    def _clicar_carta(self, carta):
        if not self.turno.pode_jogar(carta):
            return
        self.carta_pendente = carta
        self.mao.fixada = carta
        self.descartes = []
        self._proxima_escolha()

    def _proxima_escolha(self):
        """Primeiro as cartas a descartar, depois o alvo; sem nada a escolher, a carta é jogada."""
        carta = self.carta_pendente
        if len(self.descartes) < carta.descartes_requeridos():
            self.tipo_alvo = "descarte"
            return
        self.tipo_alvo = self.turno.alvo_requerido(carta)
        if self.tipo_alvo is None:
            self._jogar(carta, descartes=self.descartes)
            self._cancelar_selecao()

    def _atualizar_selecao_de_alvo(self):
        escolhendo_descarte = self.tipo_alvo == "descarte"
        self.mao.atualizar(interativa=escolhendo_descarte)
        carta = self.carta_pendente
        if carta not in self.baralho.mao or not self.turno.pode_jogar(carta):
            self._cancelar_selecao()
        elif self.mouse.button_down(3) or self.teclado.key_down("ESC"):
            self._cancelar_selecao()
        elif self.mouse.button_down(1):
            if escolhendo_descarte:
                self._alternar_descarte(self.mao.carta_sob_mouse)
                return
            alvo = self._alvo_sob_mouse()
            if alvo is not None:
                if self.tipo_alvo == "heroi":
                    self._jogar(carta, alvo_heroi=alvo, descartes=self.descartes)
                else:
                    self._jogar(carta, alvo_inimigo=alvo, descartes=self.descartes)
            self._cancelar_selecao()

    def _alternar_descarte(self, escolhida):
        """Clique numa carta da mão durante a escolha de descarte: marca ou desmarca."""
        if escolhida is None or escolhida is self.carta_pendente:
            return
        if escolhida in self.descartes:
            self.descartes.remove(escolhida)
        else:
            self.descartes.append(escolhida)
        self.mao.marcadas = set(self.descartes)
        self._proxima_escolha()

    def _jogar(self, carta, alvo_heroi=None, alvo_inimigo=None, descartes=None):
        # alvos padrão iguais aos do GerenciadorDeTurno, só para posicionar os efeitos visuais
        inimigos = self.turno.inimigos_vivos()
        efeito_inimigo = alvo_inimigo or (inimigos[0] if inimigos else None)
        efeito_heroi = alvo_heroi or carta.dono
        if self.turno.jogar_carta(carta, alvo_heroi=alvo_heroi, alvo_inimigo=alvo_inimigo,
                                  descartes=list(descartes or [])):
            self.efeitos.carta_jogada(carta, efeito_inimigo, efeito_heroi)

    def _candidatos_a_alvo(self):
        if self.tipo_alvo == "heroi":
            return self.grupo.herois_vivos()
        if self.tipo_alvo == "inimigo":
            return self.turno.inimigos_vivos()
        return []

    def _alvo_sob_mouse(self):
        for candidato in self._candidatos_a_alvo():
            if self.mouse.is_over_object(candidato.sprite):
                return candidato
        return None

    def _cancelar_selecao(self):
        self.carta_pendente = None
        self.tipo_alvo = None
        self.descartes = []
        self.mao.fixada = None
        self.mao.marcadas = set()

    def _ir_para_resultado(self):
        from cenas.cena_gameover import GameOverScene
        from cenas.navegacao import concluir_encontro
        if self.turno.estado == VITORIA:
            concluir_encontro(self.run)
        else:
            SceneManager.change_scene(GameOverScene(False, self.run))

    # ---------- desenho ----------
    def draw(self):
        dx, dy = self.efeitos.deslocamento_tela()
        self.fundo.set_position(dx, dy)
        self.fundo.draw()
        self.nevoa.draw([0], dx, dy)
        ordem = [p for p in self.turno.ordem if not p.esta_derrotado()]
        for personagem in self.grupo.herois + self.inimigos:
            posicao = ordem.index(personagem) + 1 if personagem in ordem else None
            personagem.draw(dx, dy, posicao=posicao, destaque=personagem is self.turno.atual,
                            ja_agiu=self.turno.ja_agiu_na_rodada(personagem))
        self.nevoa.draw([1], dx, dy)
        self._draw_cartas_guardadas(dx, dy)
        self._draw_marcadores()
        self.efeitos.draw()
        self.numeros.draw()

        self._draw_cabecalho()
        self._draw_atributos()
        energia = self.grupo.energia
        if self.turno.vez_do_jogador() or self.turno.escolhendo_fim():
            self.indicador_energia.draw(energia.atual, energia.maximo)
        else:
            self.indicador_energia.draw(0, energia.maximo)
        interativo = not self.visualizador.aberto and self.carta_pendente is None
        self.pilha_compra.draw(len(self.baralho.compra), interativo)
        self.pilha_descarte.draw(len(self.baralho.descarte), interativo)
        if self.turno.escolhendo_fim():
            self.botao_manter.draw()
            self.botao_descartar.draw()
        else:
            self.botao_passar.draw()
        if self.botao_combinar.habilitado and not self.turno.combate_terminou():
            self.botao_combinar.draw()

        self.mao.draw(self.turno.pode_jogar)
        self.efeitos.draw_interface()
        self.mao.draw_efeitos_pilhas()
        self.pilha_compra.draw_rotulo()
        self.pilha_descarte.draw_rotulo()
        self.barra_reliquias.draw()

        if self.visualizador.aberto:
            self.visualizador.draw()

    def _draw_cabecalho(self):
        centro_x = self.janela.largura / 2
        if self.run.encontro_atual == "chefe":
            rotulo_andar, cor_andar = "CHEFE", "vermelho"
        else:
            rotulo_andar, cor_andar = f"ANDAR {self.run.andar_atual()}/{self.run.total_andares()}", "claro"
        fonte(2, cor_andar).desenhar(f"{rotulo_andar} - RODADA {self.turno.numero_rodada}", 16, 20, "esquerda", True)

        estado = self.turno.estado
        if self.turno.combate_terminou():
            titulo = "VITÓRIA!" if estado == VITORIA else "DERROTA"
            cor = "dourado" if estado == VITORIA else "vermelho"
        elif estado == VEZ_HEROI:
            titulo, cor = f"VEZ DO {self.turno.atual.nome}", "dourado"
        elif estado == FIM_DA_VEZ:
            titulo, cor = f"FIM DA VEZ DO {self.turno.atual.nome}", "dourado"
        elif estado == VEZ_INIMIGO:
            titulo, cor = f"VEZ DO {self.turno.atual.nome}", "vermelho"
        else:
            titulo, cor = f"RODADA {self.turno.numero_rodada}", "claro"
        fonte(3, cor).desenhar(titulo, centro_x, 30, "centro", True)

        if self.carta_pendente is not None and self.tipo_alvo is not None:
            faltam = self.carta_pendente.descartes_requeridos() - len(self.descartes)
            texto = TEXTO_SELECAO[self.tipo_alvo].format(n=faltam, s="S" if faltam > 1 else "")
            fonte(2, "dourado").desenhar(texto, centro_x, 66, "centro", True)
        elif estado == FIM_DA_VEZ:
            por_vez = self.turno.cartas_por_vez(self.turno.atual)
            compra = max(0, por_vez - len(self.baralho.mao))
            fonte(2, "dourado").desenhar(
                f"MANTER: PRÓXIMA VEZ COMPRA {compra}  -  DESCARTAR: COMPRA {por_vez} NOVAS",
                centro_x, 66, "centro", True)
            if self.turno.fim_voluntario:
                fonte(2, "claro").desenhar("ESC: VOLTAR A JOGAR", centro_x, 88, "centro", True)
        elif self.turno.passando_vez:
            fonte(2, "dourado").desenhar("SEM JOGADAS: PASSANDO A VEZ...", centro_x, 66, "centro", True)
        elif self.turno.mensagem:
            fonte(2, "claro").desenhar(self.turno.mensagem, centro_x, 66, "centro", True)

    def _draw_atributos(self):
        """Atributos do herói sob o mouse (ou do herói da vez), no canto inferior esquerdo."""
        heroi = next((h for h in self.grupo.herois_vivos() if self.mouse.is_over_object(h.sprite)), None)
        if heroi is None and (self.turno.vez_do_jogador() or self.turno.escolhendo_fim()):
            heroi = self.turno.atual
        if heroi is None:
            return
        fonte(2, "dourado").desenhar(heroi.nome, 16, 346, "esquerda", True)
        nomes = ["forca", "poder", "defesa", "velocidade"]
        roubo = heroi.roubo_de_vida(self.run.reliquias)
        if roubo:
            nomes.append("roubo")
        for i, nome in enumerate(nomes):
            if nome == "velocidade":
                valor = self.turno.velocidade(heroi)
            elif nome == "roubo":
                valor = roubo
            else:
                valor = round(self.run.reliquias.multiplicador(heroi, nome), 1)
            desenhar_atributo(self.icones_atributos[nome], nome, valor, 16 + (i % 2) * 96, 370 + (i // 2) * 26)

    def _draw_cartas_guardadas(self, dx, dy):
        """Ícone com a quantidade de cartas que cada herói guardou (voltam na próxima vez dele)."""
        for heroi in self.grupo.herois_vivos():
            quantidade = self.baralho.quantidade_guardada(heroi)
            if not quantidade:
                continue
            x, y = heroi.x_base + dx + 4, heroi.y_base + dy + 4
            self.icone_guardadas.set_position(x, y)
            self.icone_guardadas.draw()
            fonte(2, "dourado").desenhar(quantidade, x + self.icone_guardadas.width + 4,
                                         y + self.icone_guardadas.height / 2, "esquerda", True)

    def _draw_marcadores(self):
        estado = self.turno.estado
        # Seta vermelha: heróis que as próximas ações inimigas vão atingir.
        if estado in (VEZ_HEROI, VEZ_INIMIGO, INICIO_RODADA):
            ameacados = {h for inimigo in self.turno.inimigos_vivos() for h in inimigo.herois_ameacados(self.grupo)}
            for heroi in ameacados:
                self._draw_seta(self.icone_alvo, heroi, 0)
        # Seta dourada: alvos válidos enquanto o jogador escolhe (sobe no alvo sob o mouse).
        if self.carta_pendente is not None:
            sob_mouse = self._alvo_sob_mouse()
            for candidato in self._candidatos_a_alvo():
                deslocamento = 36 if candidato is sob_mouse else 28
                if self.tipo_alvo == "inimigo":
                    deslocamento += 52  # acima do ícone de intenção
                self._draw_seta(self.icone_selecao, candidato, deslocamento)

    @staticmethod
    def _draw_seta(icone, personagem, deslocamento):
        sprite = personagem.sprite
        icone.set_position(personagem.x_base + (sprite.width - icone.width) / 2,
                           personagem.y_base - icone.height - 2 - deslocamento)
        icone.draw()
