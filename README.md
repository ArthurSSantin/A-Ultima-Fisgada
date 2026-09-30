# A Última Fisgada

Jogo de pesca 2D feito em Godot 4.7, portado de um projeto original em Construct 3.
O projeto ainda usa o nome interno PescaAlfa, do protótipo no Construct.

## Rodando

Abra a pasta do projeto no Godot 4.7 e aperte F5. A cena principal é `scenes/CaisTeste.tscn`.

## Controles

As setas esquerda e direita andam. O espaço faz o resto: segure para carregar o
arremesso e solte para lançar, aperte de novo quando a boia chacoalhar para
fisgar, e no minijogo segure para a zona verde subir e solte para ela descer.

## Como funciona a pesca

Ande até a ponta do cais e segure espaço. A barra de força sobe e desce sozinha;
o valor no momento em que você solta define a distância do arremesso e o peso do
peixe que morde.

Depois do arremesso, espere. Quando a boia começar a chacoalhar forte, aperte
espaço para fisgar. A janela é curta, menos de um segundo.

Aí começa o minijogo: mantenha o peixe dentro da zona verde para encher a barra
de captura. Com o peixe fora dela, a barra esvazia. Encheu, o peixe é seu;
esvaziou, ele escapa. Peixe mais pesado nada mais rápido, então lançar com
força máxima rende mais quilos mas torna a captura mais difícil.

Os números do minijogo (ganho, perda, tamanho da zona, gravidade) estão como
constantes no topo de `scripts/cais_teste.gd`.

## Estrutura

    scenes/CaisTeste.tscn   cena do jogo
    scripts/cais_teste.gd   lógica de pesca e interface
    scripts/eight_dir.gd    movimento do jogador
    scripts/c3.gd           funções auxiliares herdadas do Construct 3
    assets/sprites/         arte
    _c3-source/             projeto original do Construct 3

## Arte

A arte é desenhada em uma base de 320x180 e exportada em 4x, que é a resolução
do viewport (1280x720). Na prática: personagem de 16x24 vira arquivo de 64x96,
tile de 16x16 vira 64x64. O projeto usa filtro nearest, sem suavização.
