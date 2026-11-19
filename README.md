# Dungeons & Party

Deckbuilder roguelike por turnos em fantasia medieval e pixel art, feito em Python com a biblioteca **PPlay (Power PPlay 2.0)**.

Projeto da disciplina Laboratório de Programação de Jogos (IC/UFF, Prof. Esteban Clua).

- **Enzo Menezes**: sistemas e código
- **Matheus da Costa**: arte, VFX e UI

## Como rodar

Requer Python 3.10+ e pygame (dependência do PPlay):

```
pip install pygame
cd dungeons_and_party
python main.py
```

No Windows também há uma versão executável na página do jogo no itch.io.

## Controles

| Ação | Comando |
| --- | --- |
| Escolher heróis, nós do mapa, cartas e botões | Botão esquerdo do mouse |
| Cancelar escolha de alvo ou descarte | Botão direito ou ESC |
| Pausar (no combate) | ESC |
| Tela cheia | F11 |

## O jogo

- 4 classes (Guerreiro, Mago, Ladino e Berserker) com atributos sorteados: HP, força, poder, defesa, velocidade e roubo de vida.
- Grupo de até 3 heróis com um **baralho único compartilhado**: recrutar adiciona as cartas do herói, e herói que cai leva as cartas embora.
- Turnos por velocidade: heróis e inimigos agem uma vez por rodada; na vez de um herói ele compra 3 cartas suas e tem 3 de energia.
- Inimigos com intenções visíveis, mapa gerado a cada run (combates, eventos, tesouros e fogueira) e chefe final.
- Combos de classe que fundem duas cartas numa carta especial, buffs e debuffs, cartas passivas, relíquias e eventos.

## Estrutura

```
dungeons_and_party/   o jogo (rode o main.py daqui)
  PPlay/              biblioteca Power PPlay 2.0
  cenas/              menu, seleção, mapa, combate, recompensa, recrutamento...
  entidades/          Carta, Heroi, Inimigo, NoMapa
  sistemas/           baralho, turnos, grupo, run, mapa, relíquias...
  ui/                 botões, mão de cartas, barras, efeitos, texto
  data/               cartas, classes, inimigos, encontros, eventos (JSON)
  images/  sounds/    assets gerados
arte/                 geradores dos sprites e cenários (Pillow, fora do jogo)
audio/                gerador das músicas e efeitos chiptune (fora do jogo)
ARQUITETURA_Dungeons_and_Party.md
GDD_Dungeons_and_Party.docx
```

A arte e o áudio são gerados por código: `cd arte && python gerar_tudo.py` (requer Pillow) e `cd audio && python gerar_audio.py`.
