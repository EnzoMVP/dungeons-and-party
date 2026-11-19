"""Regenera todos os assets do jogo: python gerar_tudo.py (a partir de arte/)."""
import gerar_expansao
import gerar_fonte
import gerar_fundos
import gerar_itens
import gerar_mapa
import gerar_sprites

if __name__ == "__main__":
    gerar_fonte.gerar()
    gerar_sprites.gerar()
    gerar_fundos.gerar()
    gerar_mapa.gerar()
    gerar_itens.gerar()
    gerar_expansao.gerar()
    print("Assets gerados em dungeons_and_party/images/")
