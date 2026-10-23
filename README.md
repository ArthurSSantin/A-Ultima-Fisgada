# A Última Fisgada

Jogo de pesca 2D feito em Godot 4.7, portado de um projeto original em Construct 3.
O protótipo original no Construct se chamava PescaAlfa. A Fase 1 se passa num
açude de interior.

## Rodando

Abra a pasta do projeto no Godot 4.7 e aperte F5. O jogo começa no hub da
tela inicial (`scenes/Inicio.tscn`), onde se escolhe o nome do personagem e o
do avô. Dali a história começa na casa do avô e se abre na rua da vila
(`scenes/Vila.tscn`), que liga os quatro interiores, e no fim da rua está o
cais (`scenes/Cais.tscn`). Pelo barco se chega ao pesqueiro escolhido no mapa —
por enquanto só o açude (`scenes/Acude.tscn`).

## Controles

As setas esquerda e direita andam. O espaço faz o resto: segure para carregar o
arremesso e solte para lançar, aperte de novo quando a boia chacoalhar para
fisgar, e no minijogo segure para a zona verde subir e solte para ela descer.

No hub, espaço fala com quem estiver perto. Nas listas, as setas para cima e
para baixo escolhem e o ESC sai.

## Fase 1: o tutorial

O neto aos 8 anos, numa manhã de 2002: o vô o acorda antes do sol, ele pega a
vara de bambu no quarto, toma café com a Vó Marlene, monta no Alexandre (o
petiço; o Apollo é o cavalo do vô) e desce o rio no bote do vô. A pescaria é
de dentro do barco, no meio do rio, e ensina a mecânica pela voz do vô: a
beliscada do lambari, a mordida, o minijogo. O primeiro peixe é sempre o
Teimoso, um jundiá filhote com um pedaço do rabo arrancado por uma traíra; se
o jogador soltar, o Jundiá Gigante da fase 2 é ele, com a mesma marca.

Cenas em `scenes/tutorial/`, scripts em `scripts/tutorial/`, arte gerada por
`tools/arte/tutorial_arte.py` (com `tools/arte/estilo.py`) e sons por
`tools/sons/gerar_sons.py`. As cenas são geradas por
`tools/gerar_cenas_tutorial.py`. Nos interiores a câmera é duas vezes mais
perto (cenário em 8x, personagens com escala 2).

## Fase 2: a vila

O personagem (o nome sai da tela inicial; o padrão é Tiago) tem uma barra de
energia (canto inferior esquerdo). Lançar gasta energia,
mais quanto mais longe, e brigar com o peixe também. Quando ela acaba, ele cansa
e volta para a Loja de Pesca, vende o balde para o Zeca, compra com o Seu Valdir e
dorme, o que enche a energia de novo. A fase fecha quando a reforma da casa
(R$ 800) está paga e um jundiá foi entregue à Dona Marlene. Reconstruir também
a venda do avô (R$ 1200) é extra: libera depois da casa e conta na tela final. O dia 1 é o
tutorial, só com tilápia; a partir do dia 2 entram as beliscadas falsas e o
resto da loja.

As cinco espécies do açude, da beira para o fundo: **tilápia** (comum),
**cascudo** (comum), **carpa** (incomum), **jundiá** (raro) e o **Jundiá
Gigante**, o especial da fase, que só aparece a partir do dia 3, numa faixa
estreita de força, e pesa de 7 a 10 kg.

## Como funciona a pesca

Ande até a ponta do trapiche e segure espaço. A barra de força sobe e desce
sozinha, até o limite da vara (a marca vermelha). O valor no momento em que você
solta define a distância do arremesso, e a distância define que espécies podem
morder e o peso provável do peixe.

A força é só a tendência, não uma garantia: o peso sai sorteado em volta dela,
com o espalhamento de cada espécie (`desvio_peso`), e por isso o mesmo ponto
rende peixes de tamanhos diferentes. Arremessos no alto da faixa de uma espécie
ainda podem render um **exemplar troféu**, acima do peso máximo dela, que vale
mais e aparece visivelmente maior na tela. A isca de camarão dobra essa chance,
além da de peixe raro.

Depois do arremesso, espere. Quando a boia começar a chacoalhar forte, aperte
espaço para fisgar. A janela é curta, 0,6 s. Se ela só tremer de leve, é uma
beliscada: puxar ali perde o peixe.

Aí começa o minijogo: mantenha o peixe dentro da zona verde para encher a barra
de captura. Com o peixe fora dela, a barra esvazia. Encheu, o peixe é seu;
esvaziou, ele escapa. Peixe mais pesado nada mais rápido, então lançar com
força máxima rende mais quilos mas torna a captura mais difícil.

## Vender o peixe

A vila tem dois compradores, e eles pagam diferente. O **Zeca**, na pescaria,
paga a tabela e leva qualquer peixe. A **Dona Maria Ivone**, no restaurante,
paga 25% acima — menos no cascudo, que ninguém quer no prato (55% da tabela).

Cada um tem três pedidos, um por nível de relacionamento (tantos peixes de uma
espécie, ou um peixe acima de certo peso). Cumprir o pedido da vez paga uma
gorjeta, sobe o nível e aumenta em 10% tudo que aquele comprador paga daí em
diante. Os pedidos estão em `MISSOES`, no `scripts/partida.gd`.

Os números do minijogo (ganho, perda, gravidade, velocidade do peixe) estão no
topo de `scripts/minijogo.gd`. Os da economia (varas, loja, telhado, janela da
fisgada, bônus) estão no topo de `scripts/partida.gd`, e as espécies em
`dados/especies/` — inclusive a variação de peso e a chance de troféu de cada
uma.

## Estrutura

    scenes/Inicio.tscn        título e escolha dos nomes
    scenes/Vila.tscn          a rua da vila, que liga tudo
    scenes/CasaAvo.tscn       casa do avô: cama, Dona Marlene e as obras
    scenes/Venda.tscn         venda do Seu Valdir: varas e consumíveis
    scenes/Pescaria.tscn      pescaria do Zeca: compra peixe
    scenes/Restaurante.tscn   restaurante da Dona Maria Ivone: compra peixe
    scenes/Cais.tscn          o cais: ponto de partida, com o barco
    scenes/Acude.tscn         o açude, onde se pesca
    scripts/lugar.gd          a rua e todos os interiores (um script só)
    scripts/inicio.gd         tela inicial
    scripts/cais.gd           o cais e o embarque
    scripts/acude.gd          lógica de pesca e interface
    scripts/mapa_locais.gd    mapa de escolher o pesqueiro
    scripts/minijogo.gd       minijogo de captura e perfis de briga
    scripts/partida.gd        estado da partida e economia (autoload Partida)
    scripts/caixa_dialogo.gd  caixa de diálogo e de escolha
    scripts/dados/especie.gd  formato dos dados de cada espécie
    dados/especies/           as espécies da Fase 1
    scripts/eight_dir.gd      movimento do jogador
    scripts/c3.gd             funções auxiliares herdadas do Construct 3
    tools/harness/            simulação de balanceamento e testes (ver LEIAME.md)
    assets/sprites/           arte
    _c3-source/               projeto original do Construct 3

## Arte

A arte é desenhada em uma base de 320x180 e exportada em 4x, que é a resolução
do viewport (1280x720). Na prática: personagem de 16x24 vira arquivo de 64x96,
tile de 16x16 vira 64x64. O projeto usa filtro nearest, sem suavização.
