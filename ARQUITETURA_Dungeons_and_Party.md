# Documento de Arquitetura Técnica — Dungeons & Party

**Laboratório de Programação de Jogos — Prof. Esteban Walter Gonzalez Clua**
**Enzo Menezes e Matheus da Costa**

Este documento define a estrutura técnica, a organização de módulos e a ordem de desenvolvimento do projeto Dungeons & Party. Serve como guia de implementação para o desenvolvimento.

---

## 0. Regra fundamental de tecnologia

**Todo o jogo deve ser desenvolvido usando exclusivamente a biblioteca PPlay (Power PPlay 2.0) sobre Python.**

- Não usar outras engines ou frameworks de jogo (nada de pygame puro por fora do PPlay, arcade, godot, unity, etc.).
- Toda janela, sprite, entrada de teclado/mouse, colisão, texto, cena, áudio e efeito visual deve vir dos módulos do PPlay (Window, Sprite, GameImage, Animation, Keyboard, Mouse, Collision, SceneManager, ObjectGroup, Tween, Timer, Sound, ScreenEffects, etc.).
- Bibliotecas-padrão do Python que não sejam de jogo (por exemplo `random` para sorteios, `json` para salvar dados, `os` para caminhos de arquivo) são permitidas, pois são utilitárias e não substituem a engine.
- O objetivo é que o jogo inteiro seja demonstravelmente feito em PPlay, como exige a disciplina.

---

## 1. Estratégia de desenvolvimento

O desenvolvimento segue a abordagem **MVP vertical primeiro, expansão por partes depois**.

- Primeiro constrói-se uma fatia fina e jogável que atravessa o jogo inteiro (um combate mínimo funcional).
- Em seguida, cada nova funcionalidade é adicionada como uma fatia que se conecta ao que já roda.
- **Regra de ouro:** ao fim de cada etapa, o jogo deve estar rodável, sem estados quebrados esperando a "próxima parte".

---

## 2. Estrutura de pastas e módulos

```
dungeons_and_party/
├── main.py                  # ponto de entrada: cria a Window e inicia o SceneManager
├── images/                  # todos os sprites (heróis, inimigos, cartas, UI, fundos)
├── sounds/                  # trilhas e efeitos sonoros
├── data/                    # dados em texto/json (cartas, decks das classes, ranking)
│
├── cenas/                   # cada tela do jogo é uma cena separada
│   ├── cena_menu.py         # MenuScene
│   ├── cena_mapa.py         # MapaScene (navegação por nós)
│   ├── cena_combate.py      # CombateScene (o coração do jogo)
│   ├── cena_recrutamento.py # RecrutamentoScene
│   └── cena_gameover.py     # GameOverScene
│
├── entidades/               # os game objects do jogo
│   ├── carta.py             # Carta
│   ├── heroi.py             # Heroi (líder e companheiros)
│   ├── inimigo.py           # Inimigo (com rotina de intenção)
│   └── no_mapa.py           # NoMapa
│
├── sistemas/                # lógica de regras que não é um objeto visual único
│   ├── baralho.py           # Baralho (compra, descarte, reembaralho, cartas dinâmicas)
│   ├── turno.py             # GerenciadorDeTurno (FSM: StartTurn/PlayerTurn/EnemyTurn)
│   ├── grupo.py             # Grupo (composição de heróis, energia global)
│   └── dificuldade.py       # ajustes de dificuldade (vida/dano dos inimigos)
│
└── ui/                      # elementos de interface reutilizáveis
    ├── botao.py             # Botao (imagem + detecção de clique via Mouse)
    ├── barra_vida.py        # BarraVida
    └── indicador_energia.py # IndicadorEnergia
```

**Princípio de modularização:** cada arquivo tem uma responsabilidade única. Uma cena orquestra objetos e sistemas, mas não implementa as regras internas deles. Assim, cada tarefa de desenvolvimento mexe em poucos arquivos por vez.

---

## 3. Papel de cada camada

- **main.py** — cria a `Window` do PPlay e entrega o controle ao SceneManager, começando pela cena de menu. Não contém lógica de jogo.
- **cenas/** — telas do jogo. Cada cena tem seu ciclo de vida (update/draw) e decide para qual cena transicionar. Usa o SceneManager do PPlay.
- **entidades/** — os objetos visíveis/jogáveis (cartas, heróis, inimigos, nós). Guardam atributos e comportamento próprios.
- **sistemas/** — as regras que coordenam várias entidades (baralho, turnos, grupo, dificuldade). Não desenham nada sozinhos; manipulam estado.
- **ui/** — componentes visuais reutilizáveis entre cenas (botões, barras, indicadores).

---

## 4. Ordem de desenvolvimento (etapas)

Cada etapa termina com o jogo rodável.

### Etapa 1 — Esqueleto navegável
- Estrutura de pastas criada.
- SceneManager funcionando com transições entre MenuScene, CombateScene e GameOverScene (mesmo que as telas estejam quase vazias).
- Menu com botões via Mouse (reaproveitar a lógica de botões já feita no mini-projeto de menu).

### Etapa 2 — MVP de combate (fatia vertical)
- 1 herói (só o líder), 1 inimigo com intenção fixa.
- Baralho pequeno (4–5 cartas de ataque/defesa).
- Loop de turno completo: comprar → jogar carta → gastar energia → turno do inimigo → repetir.
- Vitória e derrota por HP, levando à GameOverScene.
- **Aqui o jogo já é jogável do início ao fim.**

### Etapa 3 — Baralho dinâmico
- Mecânica completa de compra, descarte e reembaralho quando as cartas acabam.

### Etapa 4 — As 3 classes
- Guerreiro, Mago e Ladino, cada uma com seu conjunto de cartas (dados em `data/`).

### Etapa 5 — Sistema de grupo
- Recrutar companheiros; cartas entrando no baralho ao recrutar e saindo ao perder um herói.

### Etapa 6 — Mapa de nós
- MapaScene com navegação Combate → Recrutamento → Chefe.

### Etapa 7 — IA de intenção
- Rotinas de intenção variadas por inimigo, com ícones sinalizando a próxima ação.

### Etapa 8 — Polimento (Juice) e arte
- Partículas (ParticleEmitter), screen shake e flash (ScreenEffects), animações de hover das cartas (Tween).
- Pixel art final, trilha e efeitos sonoros.
- Balanceamento de dano, custo de cartas e vida dos inimigos.

### Expansão (após as 8 etapas)
- Quarta classe, o Berserker (viking), com o atributo de roubo de vida e combo próprio (RAGNAROK).
- Cartas passivas: ficam em jogo até o fim do combate (`Baralho.em_jogo`) e dão estados ao herói (energia total, cartas por vez, peçonha, roubo de vida, imortal).
- Cartas com descarte escolhido pelo jogador (a `CombateScene` pede as cartas antes do alvo), custo em vida e dano por velocidade, bloqueio, vida perdida, rodada ou crescimento permanente.
- Energia total por herói (`GerenciadorDeTurno.energia_total`) e cartas por vez por herói (`cartas_por_vez`).
- Assets em `arte/gerar_expansao.py`; balanceamento conferido pela simulação da lógica.

---

## 5. Recursos do PPlay a aproveitar

Para evitar reimplementar sistemas que a engine já oferece:

- **SceneManager / Scene** — troca de telas com ciclo de vida próprio.
- **ObjectGroup** — gerenciar coleções (cartas na mão, inimigos) e checar colisões em massa.
- **Mouse** (`is_over_object`, `button_down`) — interação com cartas e botões.
- **Tween** — animações suaves de cartas e menus (juice) sem lógica manual de incremento.
- **ScreenEffects** (`shake`, `flash`) — feedback de dano.
- **ParticleEmitter** — partículas de magia e efeitos.
- **Timer** — agendar eventos temporizados por turno.
- **Sound** — trilha e efeitos sonoros.
- **Collision** — checagens pontuais quando necessário.

Todos são parte do PPlay, respeitando a regra da Seção 0.
