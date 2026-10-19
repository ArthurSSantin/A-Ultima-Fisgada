# A Última Fisgada

Jogo de pesca 2D feito em Godot 4.7, portado de um projeto original em Construct 3.
O protótipo original no Construct se chamava PescaAlfa.

## Rodando

Abra a pasta do projeto no Godot 4.7 e aperte F5. O jogo começa no hub da
Loja de Pesca (`scenes/Hub.tscn`); o cais é `scenes/CaisTeste.tscn`.

## Controles

As setas esquerda e direita andam. O espaço faz o resto: segure para carregar o
arremesso e solte para lançar, aperte de novo quando a boia chacoalhar para
fisgar, e no minijogo segure para a zona verde subir e solte para ela descer.

No hub, espaço fala com quem estiver perto. Nas listas, as setas para cima e
para baixo escolhem e o ESC sai.

## A Fase 1

Tiago tem uma barra de energia (canto inferior esquerdo). Lançar gasta energia,
mais quanto mais longe, e brigar com o peixe também. Quando ela acaba, ele cansa
e volta para a Loja de Pesca, vende o balde para o Zeca, compra com o Seu Aldo e
dorme, o que enche a energia de novo. A fase fecha quando o telhado
(R$ 800) está pago e um robalo foi entregue à Dona Marlene. O dia 1 é o
tutorial, só com parati; a partir do dia 2 entram as beliscadas falsas e o
resto da loja.

## Como funciona a pesca

Ande até a ponta do cais e segure espaço. A barra de força sobe e desce sozinha,
até o limite da vara (a marca vermelha). O valor no momento em que você solta
define a distância do arremesso, e a distância define a espécie e o peso do
peixe que morde.

Depois do arremesso, espere. Quando a boia começar a chacoalhar forte, aperte
espaço para fisgar. A janela é curta, 0,6 s. Se ela só tremer de leve, é uma
beliscada: puxar ali perde o peixe.

Aí começa o minijogo: mantenha o peixe dentro da zona verde para encher a barra
de captura. Com o peixe fora dela, a barra esvazia. Encheu, o peixe é seu;
esvaziou, ele escapa. Peixe mais pesado nada mais rápido, então lançar com
força máxima rende mais quilos mas torna a captura mais difícil.

Os números do minijogo (ganho, perda, gravidade, velocidade do peixe) estão no
topo de `scripts/minijogo.gd`. Os da economia (varas, loja, telhado, janela da
fisgada, bônus) estão no topo de `scripts/partida.gd`, e as espécies em
`dados/especies/`.

## Estrutura

    scenes/Hub.tscn           Loja de Pesca: compras, venda, reforma e cama
    scenes/CaisTeste.tscn     cais, onde se pesca
    scripts/hub.gd            lógica e diálogos do hub
    scripts/cais_teste.gd     lógica de pesca e interface
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
