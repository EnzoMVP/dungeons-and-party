import random

from PPlay.gameimage import GameImage
from PPlay.sprite import Sprite

from ui.barra_vida import BarraVida
from ui.texto import fonte

QUADROS_ANIMACAO = 2  # os sprites de personagem são folhas de 2 quadros que se alternam
DURACAO_ANIMACAO_MS = 1100  # uma volta completa pelos quadros

# Estados (contadores; 0 = inativo), na ordem em que aparecem sobre a barra de vida:
# (atributo, cor do número, prefixo, sufixo). O ícone é images/icones/<atributo>.png.
# - forca (inimigos): soma em todos os ataques seguintes.
# - veneno: perde essa vida no início da própria vez, e diminui 1.
# - vigor (buff): recupera essa vida no início da própria vez, e diminui 1.
# - furia (buff): cartas de dano do herói causam +50%; conta vezes (cai no fim da vez dele).
# - esquiva (buff): a próxima ação inimiga contra o herói falha; conta ações evitadas.
# - sede (buff): as cartas do herói roubam mais dano como vida (ROUBO_SEDE); conta vezes.
# - acelerado (buff): velocidade x2; conta vezes.
# - vulneravel (debuff): recebe +50% de dano das cartas; conta vezes (cai no fim da vez dele).
# - fraqueza (debuff): os ataques do inimigo causam -50%; conta vezes (cai no fim da vez dele).
# - congelado (debuff): o inimigo perde a próxima ação; conta ações perdidas.
# - marcado (debuff): quem o ataca com cartas rouba mais dano como vida (ROUBO_MARCADO); conta vezes.
# Passivas (cartas que ficam em jogo até o fim do combate):
# - bonus_energia / bonus_compra: +energia total e +cartas compradas em cada vez do herói.
# - peconha: os ataques do herói aplicam esse veneno; selvageria: +% de roubo de vida.
# - imortal: cargas; ao cair, o herói volta com 1 de vida e entra em frenesi.
# - frenesi: multiplicador do dano das cartas do herói até o fim do combate.
ESTADOS = [("forca", "vermelho", "+", ""), ("veneno", "verde", "", ""), ("vigor", "verde", "", ""),
           ("furia", "vermelho", "", ""), ("esquiva", "claro", "", ""), ("sede", "vermelho", "", ""),
           ("acelerado", "verde", "", ""), ("vulneravel", "vermelho", "", ""), ("fraqueza", "azul", "", ""),
           ("congelado", "azul", "", ""), ("marcado", "vermelho", "", ""),
           ("bonus_energia", "dourado", "+", ""), ("bonus_compra", "azul", "+", ""),
           ("peconha", "verde", "", ""), ("selvageria", "vermelho", "", "%"), ("imortal", "claro", "", ""),
           ("frenesi", "vermelho", "X", "")]
ESTADOS_COM_DURACAO = ("furia", "vulneravel", "fraqueza", "sede", "acelerado", "marcado")
MULTIPLICADOR_FRENESI = 3
LARGURA_LINHA_ESTADOS = 104  # a fileira quebra antes do ícone da direita (força/provocação)


class Personagem:
    """Base de heróis e inimigos: HP, bloqueio, estados (ESTADOS), sprite animado com flash de dano e recuo.

    `brilho` (0–255) e `recuo` (pixels) são animados de fora (ui/efeitos_combate.py) via Tween;
    o personagem só os aplica ao desenhar.
    """

    def __init__(self, nome, hp_max, caminho_sprite):
        self.nome = nome
        self.hp_max = hp_max
        self.hp = hp_max
        self.bloqueio = 0
        self.zerar_estados()
        self.renasceu = False  # a carga de imortal acabou de segurar o personagem (para a mensagem)
        self.icones_estado = {estado[0]: GameImage(f"images/icones/{estado[0]}.png") for estado in ESTADOS}
        self.sprite = Sprite(f"{caminho_sprite}.png", QUADROS_ANIMACAO)
        self.sprite.set_total_duration(DURACAO_ANIMACAO_MS)
        # Fase inicial aleatória, para os personagens não se mexerem todos juntos.
        self.sprite.set_curr_frame(random.randrange(QUADROS_ANIMACAO))
        self.sprite.tempo_acumulado = random.uniform(0, self.sprite.tempo_por_frame)
        self.sprite_flash = Sprite(f"{caminho_sprite}_flash.png", QUADROS_ANIMACAO)
        self.barra = BarraVida()
        self.brilho = 0
        self.recuo = 0
        self.x_base = 0
        self.y_base = 0

    def set_position(self, x, y):
        self.x_base = x
        self.y_base = y
        self.sprite.set_position(x, y)
        self.barra.set_position(x + (self.sprite.width - self.barra.width) / 2, y + self.sprite.height + 10)

    def receber_dano(self, quantidade):
        absorvido = min(self.bloqueio, quantidade)
        self.bloqueio -= absorvido
        dano = quantidade - absorvido
        self.perder_vida(dano)
        return dano

    def perder_vida(self, quantidade):
        """Tira vida ignorando o bloqueio e devolve quanto foi perdido.

        Com uma carga de `imortal`, o golpe que derrubaria o personagem o deixa com 1 de vida
        e em frenesi (dano das cartas x3 até o fim do combate).
        """
        antes = self.hp
        self.hp = max(0, self.hp - quantidade)
        if self.hp == 0 and antes > 0 and self.imortal > 0:
            self.imortal -= 1
            self.hp = 1
            self.frenesi = MULTIPLICADOR_FRENESI
            self.renasceu = True
        return antes - self.hp

    def ganhar_bloqueio(self, quantidade):
        self.bloqueio += quantidade

    def curar(self, quantidade):
        """Recupera vida até o máximo e devolve quanto foi curado."""
        antes = self.hp
        self.hp = min(self.hp_max, self.hp + quantidade)
        return self.hp - antes

    def esta_derrotado(self):
        return self.hp <= 0

    def sofrer_veneno(self):
        """Aplica o veneno no início da vez (ignora bloqueio). Devolve o dano causado."""
        if self.veneno <= 0:
            return 0
        dano = self.perder_vida(self.veneno)
        self.veneno -= 1
        return dano

    def receber_vigor(self):
        """Aplica o vigor no início da vez. Devolve quanto curou."""
        if self.vigor <= 0:
            return 0
        curado = self.curar(self.vigor)
        self.vigor -= 1
        return curado

    def fim_da_propria_vez(self):
        """Os estados que contam vezes perdem 1 ao fim de cada vez do personagem."""
        for atributo in ESTADOS_COM_DURACAO:
            setattr(self, atributo, max(0, getattr(self, atributo) - 1))

    def zerar_estados(self):
        for estado in ESTADOS:
            setattr(self, estado[0], 0)

    def draw(self, dx=0, dy=0, posicao=None, destaque=False, ja_agiu=False):
        """Desenha sprite (deslocado pelo tremor de tela e pelo recuo), barra de HP e nome.

        `posicao` é a ordem na rodada; `destaque` marca quem está agindo; `ja_agiu` apaga o nome.
        """
        x = self.x_base + self.recuo + dx
        y = self.y_base + dy
        if not self.esta_derrotado():
            self.sprite.update()  # alterna os quadros; quem caiu fica parado
        self.sprite.set_position(x, y)
        self.sprite.set_transparency(90 if self.esta_derrotado() else 255)
        self.sprite.draw()
        if self.brilho >= 1:
            self.sprite_flash.set_curr_frame(self.sprite.get_curr_frame())
            self.sprite_flash.set_position(x, y)
            self.sprite_flash.set_transparency(int(self.brilho))
            self.sprite_flash.draw()
        self.barra.draw(self.hp, self.hp_max, self.bloqueio)
        if not self.esta_derrotado():
            self._draw_estados()
        rotulo = f"{posicao}. {self.nome}" if posicao else self.nome
        fonte(2, "dourado" if destaque else "claro").desenhar(
            rotulo, self.x_base + self.sprite.width / 2, self.barra.moldura.y + 40, "centro", True,
            120 if ja_agiu else 255)

    def _draw_estados(self):
        """Ícone + número de cada estado ativo, em fileiras sobre a barra de vida (da esquerda)."""
        barra = self.barra.moldura
        x, base = barra.x, barra.y - 4
        for atributo, cor, prefixo, sufixo in ESTADOS:
            valor = getattr(self, atributo)
            if valor <= 0:
                continue
            icone = self.icones_estado[atributo]
            texto = f"{prefixo}{valor}{sufixo}"
            largura = icone.width + 4 + len(texto) * 12 + 6
            if x > barra.x and x + largura > barra.x + LARGURA_LINHA_ESTADOS:
                x, base = barra.x, base - icone.height - 4
            icone.set_position(x, base - icone.height)
            icone.draw()
            fonte(2, cor).desenhar(texto, x + icone.width + 4, base - icone.height / 2, "esquerda", True)
            x += largura
