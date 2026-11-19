"""Relíquias passivas da run: cada método é um gancho consultado pelo sistema que a relíquia afeta."""
import random

from sistemas import dados


class Reliquias:
    def __init__(self):
        self.ids = []

    def tem(self, id_reliquia):
        return id_reliquia in self.ids

    def disponiveis(self):
        return [r for r in dados.carregar("reliquias") if r not in self.ids]

    def sortear_nova(self, rng=None):
        opcoes = self.disponiveis()
        return (rng or random).choice(opcoes) if opcoes else None

    def adicionar(self, id_reliquia, grupo):
        """Guarda a relíquia e aplica efeitos imediatos (ex.: vida máxima)."""
        if id_reliquia is None or self.tem(id_reliquia):
            return
        self.ids.append(id_reliquia)
        if id_reliquia == "coracao_de_ferro":
            for heroi in grupo.herois:
                heroi.hp_max += 8
                heroi.hp += 8

    # ---------- ganchos ----------
    def multiplicador(self, heroi, atributo):
        bonus = 0.2 if atributo == "poder" and self.tem("tomo_proibido") else 0.0
        return heroi.atributos[atributo] + bonus

    def velocidade(self, heroi):
        return heroi.atributos["velocidade"] + (3 if self.tem("botas_velozes") else 0)

    def bonus_dano_fisico(self):
        return 2 if self.tem("pedra_de_amolar") else 0

    def veneno_em_ataque_fisico(self):
        return 1 if self.tem("presa_venenosa") else 0

    def bloqueio_no_inicio_da_vez(self):
        return 3 if self.tem("escudo_ancestral") else 0

    def energia_extra(self, primeira_vez_no_combate):
        return 1 if primeira_vez_no_combate and self.tem("ampulheta") else 0

    def compra_extra(self, primeira_vez_no_combate):
        return 1 if primeira_vez_no_combate and self.tem("bolsa_de_truques") else 0

    def roubo_de_vida(self):
        """% extra do dano das cartas que volta como vida para o herói."""
        return 10 if self.tem("calice_de_sangue") else 0

    def cura_pos_combate(self):
        return 6 if self.tem("pocao_vital") else 0
