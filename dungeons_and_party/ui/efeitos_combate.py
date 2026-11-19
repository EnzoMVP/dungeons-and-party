import random

from PPlay.effects import ScreenEffects
from PPlay.particles import ParticleEmitter
from PPlay.tween import Tween
from PPlay.window import Window

from ui import audio

DURACAO_REACAO = 0.25  # mesma duração em todo Tween de brilho/recuo (o Tween do PPlay não cancela animações antigas)
RECUO = 14
DANO_FORTE = 10

COR_DANO_HEROI = (177, 62, 83)
COR_DANO_INIMIGO = (244, 244, 244)
COR_BLOQUEIO = (115, 239, 247)
COR_CURA = (167, 240, 112)
COR_FORCA = (239, 125, 87)
COR_MORTE = (148, 176, 194)
COR_ESPECIAL = (255, 205, 117)
# Partículas quando um estado (buff/debuff) é aplicado; a força tem reação própria (som de buff).
COR_POR_ESTADO = {"veneno": (56, 183, 100), "vigor": (167, 240, 112), "furia": (239, 125, 87),
                  "esquiva": (148, 176, 194), "vulneravel": (93, 39, 93), "fraqueza": (65, 166, 246),
                  "congelado": (115, 239, 247), "sede": (177, 62, 83), "acelerado": (167, 240, 112),
                  "marcado": (177, 62, 83), "bonus_energia": (255, 205, 117), "bonus_compra": (65, 166, 246),
                  "peconha": (56, 183, 100), "selvageria": (177, 62, 83), "imortal": (244, 244, 244),
                  "frenesi": (239, 125, 87)}
COR_POR_CLASSE = {"guerreiro": (255, 205, 117), "mago": (65, 166, 246), "ladino": (167, 240, 112),
                  "berserker": (239, 125, 87)}
EFEITO_POR_TIPO_DE_CARTA = {"ataque": "carta_ataque", "defesa": "carta_defesa", "magia": "carta_magia"}


class _Tremor:
    def __init__(self):
        self.intensidade = 0
        self.restante = 0
        self.duracao = 1

    def iniciar(self, intensidade, duracao):
        if intensidade >= self.intensidade * (self.restante / self.duracao):
            self.intensidade, self.restante, self.duracao = intensidade, duracao, duracao

    def atualizar(self, dt):
        self.restante = max(0.0, self.restante - dt)

    def deslocamento(self):
        if self.restante <= 0:
            return 0, 0
        forca = self.intensidade * self.restante / self.duracao
        return round(random.uniform(-forca, forca)), round(random.uniform(-forca, forca))


class EfeitosDeCombate:
    """Juice do combate: flash e recuo no sprite atingido, partículas, tremor de tela e sons.

    Observa hp, bloqueio e força dos personagens a cada frame (como os números flutuantes),
    então as regras do jogo não precisam saber que os efeitos existem.
    """

    def __init__(self, herois, inimigos):
        self.herois = list(herois)
        self.inimigos = list(inimigos)
        self._ultimos = {p: self._estado(p) for p in self.herois + self.inimigos}
        self._emissores = []
        self._emissores_interface = []
        self._tremor = _Tremor()

    @staticmethod
    def _estado(personagem):
        estados = {nome: getattr(personagem, nome) for nome in COR_POR_ESTADO}
        return personagem.hp, personagem.bloqueio, getattr(personagem, "forca", 0), estados

    # ---------- reações ----------
    def atualizar(self):
        self._tremor.atualizar(Window.get_instance().delta_time())
        for personagem in self.herois + self.inimigos:
            hp, bloqueio, forca, estados = self._ultimos[personagem]
            self._ultimos[personagem] = self._estado(personagem)
            dano = hp - personagem.hp
            if dano > 0:
                self._reagir_a_dano(personagem, dano, morreu=personagem.hp <= 0 < hp)
            elif dano < 0:
                self._explosao(personagem, COR_CURA, 24, espalhamento=60, vida=0.7)
                audio.tocar_efeito("cura")
            if personagem.bloqueio > bloqueio:
                self._explosao(personagem, COR_BLOQUEIO, 14, espalhamento=45, vida=0.5)
                audio.tocar_efeito("bloqueio")
            if getattr(personagem, "forca", 0) > forca:
                self._explosao(personagem, COR_FORCA, 22, espalhamento=70, vida=0.7)
                audio.tocar_efeito("buff")
            for nome, cor in COR_POR_ESTADO.items():
                atual = getattr(personagem, nome)
                if nome == "frenesi" and atual > estados[nome]:
                    self._renascer(personagem)
                elif atual > estados[nome]:  # estado aplicado ou reforçado
                    self._explosao(personagem, cor, 26, espalhamento=80, vida=0.7, tamanho=5)
                elif nome == "esquiva" and atual < estados[nome]:  # desviou de uma ação inimiga
                    self._explosao(personagem, cor, 40, espalhamento=130, vida=0.6, tamanho=6)
        for emissor in self._emissores + self._emissores_interface:
            emissor.update()
        self._emissores = [e for e in self._emissores if e.particulas]
        self._emissores_interface = [e for e in self._emissores_interface if e.particulas]

    def _reagir_a_dano(self, personagem, dano, morreu):
        eh_heroi = personagem in self.herois
        personagem.brilho = 255
        Tween.to(personagem, "brilho", 0, DURACAO_REACAO, "ease_out")
        personagem.recuo = -RECUO if eh_heroi else RECUO
        Tween.to(personagem, "recuo", 0, DURACAO_REACAO, "ease_out")
        cor = COR_DANO_HEROI if eh_heroi else COR_DANO_INIMIGO
        self._explosao(personagem, cor, 10 + min(dano, 25), espalhamento=90 + dano * 4, vida=0.45)
        forte = dano >= DANO_FORTE
        if forte:
            self._tremor.iniciar(4 + min(dano, 24) // 3, 0.3)
            if eh_heroi:
                ScreenEffects.flash(COR_DANO_HEROI, 0.12)
        if morreu:
            self._explosao(personagem, COR_MORTE, 45, espalhamento=140, vida=0.9, tamanho=5)
            audio.tocar_efeito("morte")
        else:
            audio.tocar_efeito("dano_forte" if forte else "dano")

    def _renascer(self, personagem):
        """A carga de imortal segurou o herói com 1 de vida: explosão de fúria, tremor e flash."""
        self._explosao(personagem, COR_FORCA, 60, espalhamento=170, vida=0.9, tamanho=6)
        self._explosao(personagem, COR_DANO_HEROI, 40, espalhamento=120, vida=0.8, tamanho=5)
        self._tremor.iniciar(10, 0.5)
        ScreenEffects.flash(COR_DANO_HEROI, 0.2)
        audio.tocar_efeito("renascer")

    def carta_jogada(self, carta, alvo_inimigo=None, alvo_heroi=None):
        """Faísca na cor da classe da carta sobre o alvo e som pelo tipo da carta.

        A carta especial (combo) tem som próprio, faíscas douradas maiores e um tremor curto.
        """
        if carta.especial:
            audio.tocar_efeito("carta_especial")
            self._tremor.iniciar(6, 0.35)
            ScreenEffects.flash(COR_ESPECIAL, 0.1)
            alvos = self.inimigos if any(e.get("alvo") == "todos" for e in carta.efeitos) else [alvo_inimigo]
            for alvo in alvos:
                if alvo is not None and not alvo.esta_derrotado():
                    self._explosao(alvo, COR_ESPECIAL, 40, espalhamento=150, vida=0.8, tamanho=5)
                    self._explosao(alvo, COR_POR_CLASSE.get(carta.classe, COR_ESPECIAL), 24,
                                   espalhamento=120, vida=0.6)
            return
        audio.tocar_efeito(EFEITO_POR_TIPO_DE_CARTA.get(carta.tipo, "carta_ataque"))
        alvo = alvo_inimigo if carta.causa_dano() or carta.mira_inimigo() else alvo_heroi
        if alvo is not None:
            self._explosao(alvo, COR_POR_CLASSE.get(carta.classe, (244, 244, 244)),
                           30 if carta.tipo == "magia" else 16, espalhamento=110, vida=0.55)

    def combinacao(self, x, y):
        """Duas cartas se fundiram numa especial em (x, y): chuva de faíscas douradas e som."""
        audio.tocar_efeito("combinar")
        self._explosao_em(x, y, COR_ESPECIAL, 50, espalhamento=160, vida=0.8, tamanho=5, interface=True)
        self._explosao_em(x, y, (244, 244, 244), 20, espalhamento=90, vida=0.5, interface=True)

    def _explosao(self, personagem, cor, quantidade, espalhamento, vida, tamanho=4):
        sprite = personagem.sprite
        self._explosao_em(personagem.x_base + sprite.width / 2, personagem.y_base + sprite.height / 2,
                          cor, quantidade, espalhamento, vida, tamanho)

    def _explosao_em(self, x, y, cor, quantidade, espalhamento, vida, tamanho=4, interface=False):
        """`interface`: as partículas são desenhadas por cima das cartas (draw_interface)."""
        emissor = ParticleEmitter(x, y)
        emissor.cor = cor
        emissor.spread_x = espalhamento
        emissor.spread_y = espalhamento
        emissor.vida_base = vida
        emissor.tamanho_base = tamanho
        emissor.explodir(quantidade)
        (self._emissores_interface if interface else self._emissores).append(emissor)

    # ---------- desenho ----------
    def deslocamento_tela(self):
        """Deslocamento (dx, dy) do tremor, aplicado ao cenário e aos personagens."""
        return self._tremor.deslocamento()

    def draw(self):
        for emissor in self._emissores:
            emissor.draw()

    def draw_interface(self):
        for emissor in self._emissores_interface:
            emissor.draw()
