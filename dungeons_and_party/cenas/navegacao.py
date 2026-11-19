"""Transições da run entre mapa, encontros e etapas pós-encontro (imports locais evitam ciclos)."""
from PPlay.scenemanager import SceneManager


def ir_para_mapa(run):
    from cenas.cena_mapa import MapaScene
    SceneManager.change_scene(MapaScene(run))


def iniciar_encontro(run):
    """Abre a cena do nó escolhido no mapa."""
    tipo = run.encontro_atual
    if tipo in ("combate", "chefe"):
        from cenas.cena_combate import CombateScene
        SceneManager.change_scene(CombateScene(run))
    elif tipo == "evento":
        from cenas.cena_evento import EventoScene
        SceneManager.change_scene(EventoScene(run))
    elif tipo == "descanso":
        from cenas.cena_descanso import DescansoScene
        SceneManager.change_scene(DescansoScene(run))
    elif tipo == "tesouro":
        from cenas.cena_tesouro import TesouroScene
        SceneManager.change_scene(TesouroScene(run))


def concluir_encontro(run, recompensa_extra=False):
    """Fecha o encontro atual; vai à vitória final se o chefe caiu, senão segue para as etapas pendentes."""
    run.concluir_encontro(recompensa_extra)
    if run.terminou():
        from cenas.cena_gameover import GameOverScene
        SceneManager.change_scene(GameOverScene(True, run))
    else:
        seguir(run)


def seguir(run):
    """Abre a próxima etapa pós-encontro (recompensa, recrutamento) ou volta ao mapa."""
    etapa = run.proxima_etapa()
    if etapa == "recompensa":
        from cenas.cena_recompensa import RecompensaScene
        SceneManager.change_scene(RecompensaScene(run))
    elif etapa == "recrutamento":
        from cenas.cena_recrutamento import RecrutamentoScene
        SceneManager.change_scene(RecrutamentoScene(run))
    else:
        ir_para_mapa(run)
