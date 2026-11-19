import os

# Os assets são carregados por caminho relativo: roda sempre a partir da pasta do jogo.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PPlay.effects import ScreenEffects
from PPlay.scenemanager import SceneManager
from PPlay.timer import Timer
from PPlay.tween import Tween
from PPlay.window import Window

from cenas.cena_menu import MenuScene

LARGURA = 960
ALTURA = 540


def main():
    janela = Window(LARGURA, ALTURA, "Dungeons & Party")
    janela.set_background_color((26, 28, 44))
    SceneManager.change_scene(MenuScene())

    while True:
        Timer.update()
        Tween.update()
        ScreenEffects.update()
        SceneManager.run()
        ScreenEffects.draw_flash()
        janela.update()


if __name__ == "__main__":
    main()
