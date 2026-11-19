from PPlay.gameimage import GameImage
from PPlay.window import Window


class _Camada:
    def __init__(self, caminho, y, velocidade, transparencia):
        self.imagem = GameImage(caminho)
        self.y = y
        self.velocidade = velocidade
        self.transparencia = transparencia
        self.deslocamento = 0.0


class Nevoa:
    """Camadas de névoa que deslizam em velocidades diferentes (paralaxe) e se repetem sem emenda.

    O ParallaxSystem do PPlay depende de uma Camera global, que deslocaria também sprites e textos;
    por isso as camadas são GameImages movidas com o delta_time da janela.
    """

    def __init__(self, camadas):
        """camadas: lista de (caminho, y, velocidade em px/s, transparência 0–255)."""
        self.camadas = [_Camada(*c) for c in camadas]

    def atualizar(self):
        dt = Window.get_instance().delta_time()
        for camada in self.camadas:
            camada.deslocamento = (camada.deslocamento + camada.velocidade * dt) % camada.imagem.width

    def draw(self, indices=None, dx=0, dy=0):
        for i, camada in enumerate(self.camadas):
            if indices is not None and i not in indices:
                continue
            imagem = camada.imagem
            imagem.set_transparency(camada.transparencia)
            x0 = -camada.deslocamento + dx
            for x in (x0, x0 + imagem.width):
                imagem.set_position(round(x), camada.y + dy)
                imagem.draw()


def nevoa_da_masmorra():
    """Névoa padrão dos cenários: uma camada lenta atrás dos personagens e outra rápida na frente."""
    return Nevoa([
        ("images/fundos/nevoa_longe.png", 190, 12, 150),
        ("images/fundos/nevoa_perto.png", 250, 30, 90),
    ])
