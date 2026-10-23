"""Fase 1, o tutorial: uma manha com o vo.

    cd tools/arte
    python tutorial_arte.py <pasta de saida>

ESCALA. Tudo e medido pelo vo: 28 linhas da sola ao topo do chapeu, uns 1,85 m,
ou seja ~15 px por metro. Dai sai o resto: o neto de 8 anos com 18 linhas,
a Vo Marlene com 22, porta de 2,1 m (31 px), janela de 1 m, poster de 60 cm.

CAMERA. Os exteriores seguem o resto do jogo: 320x180, exportados em 4x, chao
na linha 130. Os interiores (quarto e cozinha) usam a camera duas vezes mais
perto: 160x90, exportados em 8x, chao na linha 65. Com tamanhos reais, um
comodo na camera de fora ocuparia um canto da tela; de perto, ele enche a tela.
Nos interiores os personagens entram com escala 2 no Godot, para o pixel
continuar do mesmo tamanho que o do cenario.
"""
import math
import os
import sys

from px import Tela, rng, hx
from estilo import (OL, poligono, traco, escurecer, sombra_no_chao, gradiente,
                    nuvem, estrelas, passaros, serra, neblina, copa, arvore, gramado,
                    terra, tabuas, telhado_por_dentro, piso_tabuado, tapete_retalho,
                    VERDES_MATA, VERDES_DIA, VERDES_MADRUGADA)
from capas_arte import CAPAS, miniatura, camisa_1991, folha_montado

OUT = sys.argv[1] if len(sys.argv) > 1 else "."

W, H, CHAO = 320, 180, 130                   # exteriores
WI, HI, CHAO_I, PAREDE_I = 160, 90, 65, 60   # interiores: chao dos pes e base da parede


# ============================================================ PERSONAGENS

def personagem(w, h, mapa, paleta, braco=None):
    t = Tela(w, h)
    base = h - len(mapa)
    t.mapa(0, base, mapa, paleta)
    for (x, y), c in (braco or []):
        t.put(x, y + base, paleta[c])
    return t


PELE = {"s": "#f7cba2", "S": "#e3a87d", "z": "#c4825c", "m": "#ee9a82"}


def neto():
    """O neto aos 8 anos: 18 linhas, no quadro 16x24 do Tiago adulto (os pes
    caem no mesmo lugar). A cabeca chega na barba do vo."""
    pal = {"O": OL, "c": "#5a3420", "C": "#7d4c2b",
           "e": "#7cc45e", "E": "#5aa046", "f": "#3f7d33",
           "b": "#4f86c6", "B": "#3a6aa8", "n": "#2b4f80",
           "g": "#f2c94c", "G": "#c9a030", **PELE}
    mapa = [
        ".....OOOOO......",
        "....OCCCCCO.....",
        "...OCcCCCCCO....",
        "...OccSSSSSO....",
        "...OcCsssOsO....",
        "...OcSsssOssO...",
        "....OzssmsO.....",
        ".....OEzzEO.....",
        "....OeeeeeEO....",
        "....OeeeeEEO....",
        "....OeeeEEfO....",
        "....ObbbbbnO....",
        "....ObBOObnO....",
        "....OsSO.OsSO...",
        "....OsSO.OsSO...",
        "....OsSO.OsSO...",
        "....OsSO.OsSO...",
        "...OGgO..OGgO...",
    ]
    braco = [((6, 8), "E"), ((7, 8), "E"), ((6, 9), "S"), ((7, 9), "s"),
             ((6, 10), "S"), ((7, 10), "s"), ((6, 11), "z"), ((7, 11), "S")]
    return personagem(16, 24, mapa, pal, braco)


# Pernas do neto por quadro de caminhada (as 5 ultimas linhas do mapa),
# do mesmo jeito que o Tiago adulto: parado, passo, pernas cruzando, passo.
PERNAS_NETO = {
    "parado": ["....OsSO.OsSO...", "....OsSO.OsSO...", "....OsSO.OsSO...", "....OsSO.OsSO...",
               "...OGgO..OGgO..."],
    "passo1": ["....OsSO.OsSO...", "...OsSO...OsSO..", "...OsSO...OsSO..", "..OsSO.....OsSO.",
               "..OGgO.....OGgO."],
    "passo2": [".....OsSSO......", ".....OsSSO......", ".....OsSSO......", ".....OGgGO......"],
    "passo3": ["....OSsO.OSsO...", "...OSsO...OSsO..", "...OSsO...OSsO..", "..OSsO.....OSsO.",
               "..OGgO.....OGgO."],
}
QUADROS_NETO = ["parado", "passo1", "passo2", "passo3"]
BAMBU = ("#e6c266", "#9a742f", "#c99a62")


def neto_quadro(pernas="parado", pose="sem"):
    """Um quadro 16x24 do neto. pose: "sem" vara, "costas" (vara de bambu
    presa nas costas) ou "mao" (vara na mao, ponta no pixel (15, 0), que e de
    onde a linha sai na cena de pesca)."""
    pal = {"O": OL, "c": "#5a3420", "C": "#7d4c2b", "e": "#7cc45e", "E": "#5aa046", "f": "#3f7d33",
           "b": "#4f86c6", "B": "#3a6aa8", "n": "#2b4f80", "g": "#f2c94c", "G": "#c9a030", **PELE}
    corpo = [
        ".....OOOOO......", "....OCCCCCO.....", "...OCcCCCCCO....", "...OccSSSSSO....",
        "...OcCsssOsO....", "...OcSsssOssO...", "....OzssmsO.....", ".....OEzzEO.....",
        "....OeeeeeEO....", "....OeeeeEEO....", "....OeeeEEfO....", "....ObbbbbnO....",
        "....ObBOObnO....",
    ]
    bob = 1 if pernas == "passo2" else 0
    mapa = corpo + PERNAS_NETO[pernas]
    t = Tela(16, 24)
    base = 24 - (len(corpo) + 5)          # pes sempre na ultima linha
    cor, no, cabo = BAMBU
    if pose == "costas":                   # atras do corpo
        for i, y in enumerate(range(0, 22)):
            t.put(round(1 + y * 0.14), y, no if i % 4 == 1 else cor)
        t.put(4, 21, cabo)
    t.mapa(0, base + bob, mapa, pal)
    if pose == "mao":
        for i, y in enumerate(range(0, 15)):
            t.put(round(10 + (15 - y) * 5 / 15.0), y, no if i % 4 == 2 else cor)
        braco = [((6, 8), "E"), ((7, 8), "E"), ((8, 9), "s"), ((9, 9), "s"), ((9, 10), "S"), ((10, 9), "z")]
        t.put(10, 17, cabo)
    else:
        braco = [((6, 8), "E"), ((7, 8), "E"), ((6, 9), "S"), ((7, 9), "s"),
                 ((6, 10), "S"), ((7, 10), "s"), ((6, 11), "z"), ((7, 11), "S")]
    for (x, y), c in braco:
        t.put(x, y + base + bob, pal[c])
    return t


def neto_folha(pose):
    from PIL import Image
    folha = Image.new("RGBA", (64 * 4, 96), (0, 0, 0, 0))
    for i, q in enumerate(QUADROS_NETO):
        folha.alpha_composite(neto_quadro(q, pose).im.resize((64, 96), Image.NEAREST), (64 * i, 0))
    return folha


def vo():
    """O vo: 28 linhas, corpo de adulto (o Tiago adulto tem 24). Mesmo chapeu
    de palha de fita vermelha que o neto vai usar crescido, barba grisalha,
    camisa xadrez, calca escura e botina."""
    pal = {"O": OL, "h": "#f6d77c", "H": "#e2b655", "k": "#b8893a", "r": "#c0452f", "R": "#8a2c22",
           "s": "#e8b48a", "S": "#cf9268", "z": "#a8704c", "m": "#c9806a",
           "y": "#e4e2dc", "Y": "#b8b5ae", "x": "#b8433a", "X": "#7a2a26", "n": "#5a1e1c",
           "j": "#41557a", "J": "#2f3f5c", "L": "#5a3a22", "g": "#d9c27a"}
    mapa = [
        "................",
        ".....OOOO.......",
        "....OhhhhO......",
        "...OhhhhHHO.....",
        "...ORrrrrRO.....",
        ".OHhhhhhhhhhhO..",
        "..OOkkkkkkkOO...",
        "...OYYSSSSSO....",
        "...OYysssOsO....",
        "...OYSsssOssO...",
        "...OyyyyyysO....",
        "....OYyyyYO.....",
        ".....OxyyxO.....",
        "....OxXxXxXO....",
        "...OxXxXxXxXO...",
        "...OXxXxXxXxO...",
        "...OxXxXxXxXO...",
        "...OXxXxXxXnO...",
        "....OLLLgLLO....",
        "....OjjJOjjO....",
        "....OjjJOjjO....",
        "....OjjJOjjO....",
        "....OjjJOjjO....",
        "....OjjJOjjO....",
        "....OjjJOjjO....",
        "....OjjJOjjO....",
        "....OLLLOLLLO...",
        "....OOOOOOOOO...",
    ]
    braco = [((6, 13), "X"), ((7, 13), "x"), ((6, 14), "X"), ((7, 14), "x"),
             ((6, 15), "X"), ((7, 15), "x"), ((6, 16), "S"), ((7, 16), "s"),
             ((6, 17), "S"), ((7, 17), "s"), ((6, 18), "z"), ((7, 18), "S")]
    return personagem(16, 28, mapa, pal, braco)


def espelha(metades):
    return [m + m[::-1] for m in metades]


def marlene_jovem():
    """A Dona Marlene uns doze anos antes: 22 linhas, mais baixa que o vo.
    Mesmo vestido roxo e avental, cabelo ainda grisalho."""
    pal = {"O": OL, "h": "#9a9088", "H": "#6e655e", "s": "#f2c39a", "S": "#dda07a", "z": "#b97d5c",
           "g": "#6a5070", "m": "#ee9a82", "d": "#b06aa8", "D": "#8e4f8a", "a": "#f4efe6", "A": "#d9d0c4",
           "k": "#5a3a2a", "f": "#f7d36b"}
    metade = [
        "......OO", ".....Ohh", "...OOhhh", "..OhhhhH", "..OhHsss", "..OhSsss",
        "..Osgggs", "..OsgOgs", "..Osmssz", "...OsssO", "....OOzs", "...OODdd",
        "..ODddaa", ".ODODfaa", ".ODODaAa", ".OsODaaa", "..OODaaa", "..ODdfaa",
        "..ODdddd", "...OOdOO", "....OsO.", "....OkO.",
    ]
    t = Tela(16, 22)
    t.mapa(0, 0, espelha(metade), pal)
    return t


# =================================================================== BICHOS

def maumau(pose="sentado"):
    """MauMau, o gato frajola da casa: preto com peito, focinho e patas
    brancas. Do tamanho de gato de verdade (uns 35 cm sentado, 6 linhas).
    Poses: "sentado", "carinho" (olho fechado, rabo em pe enrolado,
    ronronando) e "deitado" (dormindo enrolado na cama)."""
    P, B, R, V = "#2a2630", "#f4f0ea", "#e89aa8", "#8ac04a"
    if pose == "deitado":
        t = Tela(11, 6)
        t.disco(4.5, 3.6, 3.6, P, sy=0.55)
        t.disco(8, 3, 1.8, P)
        t.put(7, 1, P); t.put(9, 1, P)
        t.put(8, 4, B); t.put(9, 3, B)
        t.put(7, 2, "#1a1820"); t.put(9, 2, "#1a1820")
        traco(t, 1, 4, 3, 5, P)
        t.hline(4, 6, 5, B)
    else:
        t = Tela(10, 8)
        t.disco(4, 5.2, 2.4, P)
        t.disco(4.6, 5.8, 1.2, B)
        t.disco(6.6, 2.6, 1.9, P)
        poligono(t, [(5, 1.4), (5.4, -0.4), (6.2, 1.2)], P)
        poligono(t, [(7, 1.2), (7.8, -0.4), (8.4, 1.6)], P)
        t.put(8, 3, B); t.put(7, 3, B); t.put(8, 2, R)
        if pose == "carinho":
            t.hline(6, 7, 2, "#1a1820")
            pontos = [(2, 6), (0, 5), (0, 3), (1, 1)]
        else:
            t.put(6, 2, V); t.put(7, 2, "#1a1820")
            pontos = [(2, 6), (0, 7)]
        for (a, b), (c, d) in zip(pontos, pontos[1:]):
            traco(t, a, b, c, d, P)
        t.put(3, 7, B); t.put(5, 7, B)
    t.contorno(OL)
    return t


def pacoca(pose="em_pe"):
    """Pacoca, a cachorra caramelo do terreiro: vira-lata, orelha meio caida,
    peito claro e coleira vermelha. Poses: "em_pe", "carinho" (sentada, lingua
    de fora, rabo abanando), "correndo1", "correndo2" e "bolinha" (volta com a
    bolinha na boca)."""
    c, C, l, b = "#d9913c", "#b8722a", "#f0b868", "#f4e6cc"
    t = Tela(18, 12)
    if pose == "carinho":
        t.disco(7, 7.5, 3.4, c, sy=1.0)
        t.disco(8.5, 8, 1.8, b)
        t.rect(5, 9, 2, 2, c); t.rect(9, 9, 2, 2, c)
        t.hline(5, 6, 11, b); t.hline(9, 10, 11, b)
        hx_, hy = 10, 3.5
        traco(t, 3, 8, 1, 4, c, 2)
        traco(t, 1, 4, 2, 2, l)
    else:
        corre = pose in ("correndo1", "correndo2")
        t.rect(3, 4, 10, 4, c)
        t.disco(4, 6, 2.2, c)
        t.disco(12, 6, 2.4, c)
        t.hline(4, 12, 4, l)
        t.hline(5, 11, 7, C)
        t.disco(12, 7, 1.4, b)
        if pose == "correndo1":
            traco(t, 4, 8, 1, 10, C, 2); traco(t, 12, 8, 15, 10, c, 2)
            traco(t, 5, 8, 3, 11, c, 2); traco(t, 11, 8, 13, 11, C, 2)
        elif pose == "correndo2":
            traco(t, 5, 8, 7, 10, c, 2); traco(t, 11, 8, 9, 10, c, 2)
        else:
            for x in (4, 6, 10, 12):
                t.rect(x, 8, 2, 3, c if x in (4, 10) else C)
                t.hline(x, x + 1, 10, b)
        hx_, hy = 14, (4.0 if corre else 3.0)
        traco(t, 3, 5, 0, 4 if pose == "correndo2" else 2, c, 2)
    t.disco(hx_, hy, 2.6, c)
    t.rect(hx_ + 1, hy, 3, 2, l)
    t.put(hx_ + 3, hy, "#1a1210")
    t.put(hx_ + 1, hy - 1, "#1a1210")
    poligono(t, [(hx_ - 2, hy - 2), (hx_ - 1, hy - 4), (hx_ + 1, hy - 2)], C)
    t.put(hx_ - 2, hy - 1, C)
    t.hline(hx_ - 2, hx_ - 1, hy + 2, "#c9302a")
    if pose == "carinho":
        t.put(hx_ + 2, hy + 2, "#e86a80"); t.put(hx_ + 2, hy + 3, "#e86a80")
    if pose == "bolinha":
        t.disco(hx_ + 4, hy + 1.5, 1.4, "#d83a2a")
        t.put(hx_ + 4, hy + 1, "#ff8a6a")
    t.contorno(OL)
    return t


def bolinha():
    t = Tela(4, 4)
    t.disco(1.5, 1.5, 1.6, "#d83a2a")
    t.put(1, 1, "#ff8a6a")
    t.contorno(OL)
    return t


def coracao():
    t = Tela(7, 6)
    for y, linha in enumerate([".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]):
        for x, ch in enumerate(linha):
            if ch == "X":
                t.put(x, y, "#e8506a")
    t.put(1, 1, "#ffb0c0")
    return t


# ================================================================ CAVALOS

def cavalo(pelagem, sombra, crina, manchas=None, comp=22, perna=10, seed=1):
    """Cavalo de lado, virado para a direita, com arreio e pelego.
    Desenhado direto em pixel: encolher pixel art desmancha perna e cabeca,
    entao o petico sai de outras medidas, nao do cavalo grande reduzido."""
    t = Tela(comp + 20, perna + 23)
    g = t.h - 1
    barriga = g - perna
    lombo = barriga - 9
    x0, x1 = 6, 6 + comp
    casco = "#2b1d12"
    for perto in (False, True):
        cor = pelagem if perto else sombra
        xt = x0 + (6 if perto else 3)
        xd = x1 - (3 if perto else 6)
        for y in range(barriga - 3, g - 1):
            jarrete = -1 if y > barriga + perna * 0.45 else 0
            t.put(xt + jarrete, y, cor); t.put(xt + 1 + jarrete, y, cor)
            t.put(xd, y, cor); t.put(xd + 1, y, cor)
        t.rect(xt - 1, g - 1, 3, 2, casco)
        t.rect(xd, g - 1, 3, 2, casco)
    t.rect(x0 + 3, lombo + 1, comp - 6, 8, pelagem)
    t.disco(x0 + 4, lombo + 4.5, 4.6, pelagem)
    t.disco(x1 - 4, lombo + 4.5, 4.6, pelagem)
    t.disco(x1 - 7, lombo + 0.5, 2.2, pelagem)
    t.disco(x0 + 5, lombo + 1.5, 3.4, pelagem)
    poligono(t, [(x1 - 9, lombo + 1), (x1 + 2, lombo - 8), (x1 + 6, lombo - 5), (x1 - 1, lombo + 7)], pelagem)
    poligono(t, [(x1 + 1, lombo - 9), (x1 + 5, lombo - 10), (x1 + 12, lombo - 5),
                 (x1 + 12, lombo - 2), (x1 + 7, lombo - 2), (x1 + 3, lombo - 4)], pelagem)
    poligono(t, [(x1 + 2, lombo - 9), (x1 + 3, lombo - 12), (x1 + 5, lombo - 9)], pelagem)
    for x in range(x0 + 3, x1 - 2):
        t.put(x, barriga - 1, sombra)
    for i in range(6):
        t.put(x1 + 1 - i * 0.4, lombo - 2 + i, sombra)
    if manchas:
        R = rng(seed)
        for _ in range(5):
            cx, cy = R.uniform(x0 + 2, x1 - 2), R.uniform(lombo + 1, barriga - 2)
            r = R.uniform(2.2, 3.8)
            for y in range(int(cy - r), int(cy + r) + 1):
                for x in range(int(cx - r), int(cx + r) + 1):
                    if ((x - cx) / r) ** 2 + ((y - cy) / (r * .8)) ** 2 <= 1 and \
                            t.get(x, y)[:3] in (hx(pelagem)[:3], hx(sombra)[:3]):
                        t.put(x, y, manchas)
        t.disco(x1 + 8, lombo - 5, 1.8, manchas)
    for i in range(11):
        f = i / 10.0
        x, y = x1 + 2 - f * 10, lombo - 8 + f * 9
        t.put(x, y, crina); t.put(x - 1, y, crina)
    t.put(x1 + 4, lombo - 9, crina)
    t.put(x1 + 6, lombo - 7, "#1d1208")
    t.put(x1 + 11, lombo - 3, "#1d1208")
    pontos = [(x0 + 1, lombo + 1), (x0 - 2, lombo + 4), (x0 - 3, lombo + 8), (x0 - 2, lombo + 12)]
    for (a, b), (c, d) in zip(pontos, pontos[1:]):
        traco(t, a, b, c, d, crina, grossura=2.4)
    t.vline(x1 + 6, lombo - 9, lombo - 3, "#3a2615")
    t.vline(x1 + 9, lombo - 5, lombo - 2, "#3a2615")
    traco(t, x1 + 9, lombo - 3, x1 - 9, lombo + 0, "#3a2615")
    meio = x1 - 11
    t.rect(meio - 5, lombo + 1, 11, 4, "#7a2a26")
    for y in range(lombo - 1, lombo + 3):
        for x in range(meio - 4, meio + 5):
            t.put(x, y, "#f2ede2" if (x + y) % 3 else "#d8d0c0")
    t.hline(meio - 4, meio + 4, lombo - 2, "#ffffff")
    t.vline(meio, lombo + 5, lombo + 8, "#3a2615")
    t.rect(meio - 1, lombo + 9, 3, 1, "#9aa3ab")
    for x in range(x0 + 4, x1 - 8):
        if t.get(x, lombo)[3]:
            t.mix(x, lombo, "#ffffff", 0.25)
    t.contorno(OL)
    return t


def alexandre():
    """Alexandre, o petico pampa do neto."""
    return cavalo("#f2ede2", "#cfc6b4", "#5a3a22", manchas="#8a5a33", comp=18, perna=10, seed=4)


def apollo():
    """Apollo, o cavalo zaino do vo."""
    return cavalo("#5a3420", "#3f2416", "#1d1208", comp=24, perna=13)


# ============================================================== POSTERES
# Do tamanho de verdade (60x85 cm = 9x13 px). O nome nao cabe legivel nesse
# tamanho: aparece na etiqueta quando o neto chega perto, como os outros nomes
# do jogo, e na fala ao examinar.

def _texto_de_poster(t, x, y, w, linhas, cor, seed):
    """Linhas de letrinhas miudas: le como impresso sem fingir ser legivel."""
    R = rng(seed)
    for i in range(linhas):
        xx = x
        while xx < x + w:
            n = R.randint(1, 3)
            t.hline(xx, min(x + w - 1, xx + n - 1), y + i * 2, cor)
            xx += n + 1


def _rosto(t, x, y, pele, cabelo, chapeu=None, bigode=False, cabelo_longo=False):
    """Rosto de 3x4 visto de frente, para foto e poster."""
    t.rect(x, y + 1, 3, 3, pele)
    t.hline(x, x + 2, y, cabelo)
    t.put(x, y + 1, cabelo)
    t.put(x + 2, y + 1, cabelo)
    t.put(x, y + 2, "#2a1a14"); t.put(x + 2, y + 2, "#2a1a14")
    if bigode:
        t.put(x + 1, y + 3, cabelo)
    if cabelo_longo:
        t.vline(x - 1, y, y + 5, cabelo)
        t.vline(x + 3, y, y + 5, cabelo)
    if chapeu:
        t.hline(x - 1, x + 3, y, chapeu)
        t.hline(x, x + 2, y - 1, chapeu)


def poster_criciuma(t, x, y):
    """O elenco campeao em duas fileiras no gramado, faixa preta com o escudo."""
    t.rect(x, y, 9, 13, "#f2c94c")
    t.rect(x, y, 9, 3, "#111111")
    t.rect(x + 3, y, 3, 3, "#f2c94c"); t.put(x + 4, y + 1, "#111111")
    t.put(x + 4, y + 2, "#f4f1ea")
    t.rect(x, y + 4, 9, 7, "#4f8a45")
    for i in range(4):
        t.put(x + 1 + i * 2, y + 5, "#e3a87d")
        t.put(x + 1 + i * 2, y + 6, "#f2c94c")
        t.put(x + 1 + i * 2, y + 7, "#111111")
    for i in range(3):
        t.put(x + 2 + i * 2, y + 8, "#e3a87d")
        t.put(x + 2 + i * 2, y + 9, "#f2c94c")
    _texto_de_poster(t, x + 1, y + 11, 7, 1, "#111111", 1)


def poster_zeze(t, x, y):
    """Zeze Di Camargo & Luciano: os dois rostos, palco azul com luz."""
    gradiente(t, x, y, x + 9, y + 13, ["#1f2a5c", "#3a3a7a", "#6a4a8a"])
    for xx in (x + 1, x + 7):
        t.vline(xx, y, y + 3, "#9aa8e0")
    _rosto(t, x + 1, y + 3, "#e3a87d", "#3a2418")
    _rosto(t, x + 5, y + 3, "#d99a70", "#1a1210")
    t.rect(x + 1, y + 7, 3, 2, "#f4f1ea"); t.rect(x + 5, y + 7, 3, 2, "#2a2a3a")
    t.rect(x, y + 10, 9, 3, "#f2c94c")
    _texto_de_poster(t, x + 1, y + 10, 7, 2, "#7a2a26", 2)


def poster_leonardo(t, x, y):
    """Leonardo: rosto de chapeu de vaqueiro e bigode, por do sol atras."""
    gradiente(t, x, y, x + 9, y + 13, ["#e8803a", "#c9503a", "#5a2a2a"])
    t.disco(x + 4.5, y + 5, 2.4, "#f2c94c")
    _rosto(t, x + 3, y + 4, "#e3a87d", "#3a2418", chapeu="#d9b06a", bigode=True)
    t.hline(x + 2, x + 6, y + 3, "#d9b06a")
    t.rect(x + 2, y + 8, 5, 2, "#3a3a4a")
    _texto_de_poster(t, x + 1, y + 11, 7, 1, "#f4f1ea", 3)


def poster_djavan(t, x, y):
    """Djavan: cabelo comprido e violao, verde e amarelo de capa de disco."""
    gradiente(t, x, y, x + 9, y + 13, ["#2f8a5a", "#5fb06a", "#e8c84a"])
    _rosto(t, x + 3, y + 3, "#8a5a3a", "#1a1210", cabelo_longo=True)
    t.rect(x + 2, y + 7, 5, 2, "#f2e6a0")
    poligono(t, [(x + 5, y + 8), (x + 8, y + 7), (x + 8, y + 10), (x + 5, y + 10)], "#a8743f")
    _texto_de_poster(t, x + 1, y + 11, 7, 1, "#1f3a2a", 4)


def moldura_parede(t, x, y, w, h, madeira="#6b4325", luz="#9a6438"):
    t.rect(x, y, w, h, madeira)
    t.hline(x, x + w - 1, y, luz)
    t.vline(x, y, y + h - 1, luz)
    t.hline(x, x + w - 1, y + h - 1, OL)
    t.vline(x + w - 1, y, y + h - 1, OL)


def janela_de_dentro(t, x, y, w, h, ceu, morros, cortina=("#c9503a", "#f2e6d6")):
    """Janela vista de dentro: ceu e morros la fora, caixilho em cruz,
    peitoril e cortina xadrez puxada para o lado."""
    gradiente(t, x, y, x + w, y + h, ceu)
    for xx in range(x, x + w):
        topo = y + int(h * .62 + 2 * math.sin((xx - x) / 3.0))
        for yy in range(topo, y + h):
            t.put(xx, yy, morros[0] if yy < topo + 1 else morros[1])
    for yy in range(y + int(h * .62), y + int(h * .9)):
        for xx in range(x, x + w):
            t.mix(xx, yy, "#f2eef2", .4)
    t.vline(x + w // 2, y, y + h - 1, "#6b4325")
    t.hline(x, x + w - 1, y + h // 2, "#6b4325")
    for xx in range(x - 1, x + w + 1):
        t.put(xx, y - 1, "#7a4c2b")
        t.put(xx, y + h, "#9a6438")
        t.put(xx, y + h + 1, "#5a3a22")
    t.vline(x - 1, y - 1, y + h, "#7a4c2b")
    t.vline(x + w, y - 1, y + h, "#5a3a22")
    a, b = cortina
    for yy in range(y - 2, y + h + 2):
        for xx in range(x - 3, x + 2 - (yy - y) // 6):
            t.put(xx, yy, a if (xx // 2 + yy // 2) % 2 else b)
    t.hline(x - 4, x + w + 3, y - 3, "#5a3a22")


def luz_entrando(t, x0, x1, y_janela, y_chao, forca=.14, cor="#ffc070"):
    """Facho de luz da janela descendo em diagonal ate o chao."""
    for y in range(y_janela, min(t.h, y_chao + 12)):
        desloc = (y - y_janela) * 0.7
        for x in range(int(x0 + desloc), int(x1 + desloc + (y - y_janela) * .15)):
            t.mix(x, y, cor, forca)


def vinheta(t, forca=.28, chao=None):
    """Escurece os cantos (aconchego de comodo iluminado por uma janela) e,
    se "chao" vier, a frente do piso, que senao fica um tablado chapado."""
    cx, cy = t.w / 2, t.h / 2
    for y in range(t.h):
        for x in range(t.w):
            d = math.hypot((x - cx) / cx, (y - cy) / cy)
            if d > .75:
                t.mix(x, y, "#1a1020", min(1, (d - .75) * forca * 2.5))
    if chao is not None:
        for y in range(chao + 8, t.h):
            f = (y - chao - 8) / float(t.h - chao - 8)
            for x in range(t.w):
                t.mix(x, y, "#1a1020", .35 * f)


# ============================================================== INTERIORES

CEU_JANELA_MADRUGADA = ["#3d4a7a", "#7a5e8a", "#d9887a", "#f2b36a"]
MORROS_JANELA = ("#3f5f4a", "#2f4a3a")


# posteres do quarto: (capa, x, y) em pixels nativos
POSTERES_DO_QUARTO = [("racionais", 1, 33), ("criciuma", 47, 31), ("pele", 58, 31), ("zeze", 69, 31),
                      ("leonardo", 80, 31), ("djavan", 91, 31), ("lebron", 102, 31)]


def quarto():
    """Quarto do neto, 5h17. Camera de perto (160x90, 8x).

    Da esquerda para a direita: a janela sobre a cama (onde o MauMau dorme),
    o criado-mudo com a foto dos pais, a foto do vo com o peixe, os quatro
    posteres, a camisa do Criciuma no prego, a prateleira com o toca-fitas e
    o barquinho de madeira, a cadeira com a mochila, a vara de bambu e a porta
    da cozinha. Em cima, o telhado sem forro e a lampada no fio."""
    t = Tela(WI, HI)
    telhado_por_dentro(t, 0, WI, 0, 22, seed=2)
    tabuas(t, 0, 24, WI, PAREDE_I, ("#c49060", "#b8845a", "#cc9a68", "#b07c50"), "#7a4e30", larg=6, seed=5)
    t.rect(0, PAREDE_I - 2, WI, 2, "#7a4e30")
    t.hline(0, WI - 1, PAREDE_I - 2, "#9a6a44")
    piso_tabuado(t, 0, WI, PAREDE_I, HI, seed=7)

    # lampada pendurada no fio, ainda acesa
    t.vline(80, 0, 15, "#2a2420")
    t.rect(79, 15, 3, 2, "#5a4a3a")
    t.disco(80.5, 18, 1.6, "#fff0b0")
    for y in range(14, 30):
        for x in range(70, 92):
            d = math.hypot(x - 80.5, (y - 18) * 1.3)
            if d < 10:
                t.mix(x, y, "#ffe8a0", .18 * (1 - d / 10))

    # janela (1,1 m), peitoril a 1 m do chao
    janela_de_dentro(t, 15, 29, 16, 16, CEU_JANELA_MADRUGADA, MORROS_JANELA)

    # cama: cabeceira, colchao a meio metro, colcha de retalhos amarrotada
    t.rect(5, 47, 3, PAREDE_I + 4 - 47, "#7a4c2b")
    t.hline(5, 7, 47, "#9a6438")
    t.rect(34, 52, 2, PAREDE_I + 4 - 52, "#7a4c2b")
    t.rect(8, 53, 26, 3, "#ece6da")
    t.disco(11, 52, 2.6, "#f6f2ea", sy=.6)
    retalhos = ("#c9503a", "#e8c06a", "#4f86c6", "#7cc45e", "#d98ab8", "#f2e6d6")
    for y in range(52, 60):
        onda = int(math.sin(y / 1.5))
        for x in range(14 + onda, 34):
            t.put(x, y, retalhos[((x - 14) // 3 + (y - 52) // 3) % 6])
    escurecer(t, 14, 58, 33, 59, .25)
    t.rect(8, 60, 26, 4, "#5a3a22")
    sombra_no_chao(t, 21, 64, 15)

    # criado-mudo com a foto dos pais (fita de luto) e um copinho com flor
    t.rect(38, 52, 8, PAREDE_I + 4 - 52, "#8a5a33")
    t.hline(38, 45, 52, "#b07c45")
    t.hline(39, 44, 57, "#6b4325")
    t.put(41, 55, "#d9c27a")
    sombra_no_chao(t, 42, 64, 5)
    moldura_parede(t, 39, 46, 5, 6, "#3a2418", "#6b4325")
    t.rect(40, 47, 3, 4, "#c9d6c8")
    t.put(40, 48, "#e3a87d"); t.put(42, 48, "#e3a87d")
    t.put(40, 49, "#4f6f9c"); t.put(42, 49, "#c9707a")
    t.put(39, 46, "#0a0a0a"); t.put(40, 46, "#0a0a0a"); t.put(39, 47, "#0a0a0a")
    t.vline(45, 48, 51, "#4f8a45")
    t.put(45, 47, "#f2e6d6"); t.put(44, 47, "#f2e6d6"); t.put(45, 46, "#f2c94c")

    # foto do neto pequeno com o vo e o peixe enorme
    moldura_parede(t, 38, 35, 8, 6)
    t.rect(39, 36, 6, 4, "#a8c4a0")
    t.put(40, 38, "#7cc45e"); t.put(40, 37, "#e3a87d")
    t.put(42, 36, "#e2b655"); t.put(42, 37, "#e3a87d"); t.put(42, 38, "#b8433a")
    t.hline(43, 44, 38, "#7f9aa8")

    # os posteres de capa de disco, na altura do olho e menores que a janela;
    # o do Racionais era do pai e fica em cima da cama (capas_arte.py)
    for nome, x, y in POSTERES_DO_QUARTO:
        t.colar(miniatura(CAPAS[nome]()), x, y)
        t.put(x + 4, y - 1, "#9aa3ab")
        escurecer(t, x + 1, y + 10, x + 10, y + 10, .3)

    # camisa titular do Criciuma de 1991 pendurada num prego: amarela com
    # listra preta e filete branco, gola em V e a faixa branca do patrocinio
    cx, cy = 120, 30
    t.put(cx, cy - 2, "#9aa3ab")
    traco(t, cx - 4, cy, cx, cy - 2, "#5a3a22"); traco(t, cx, cy - 2, cx + 4, cy, "#5a3a22")
    poligono(t, [(cx - 4, cy), (cx - 7, cy + 4), (cx - 5, cy + 6), (cx - 4, cy + 5), (cx - 4, cy + 13),
                 (cx + 5, cy + 13), (cx + 5, cy + 5), (cx + 6, cy + 6), (cx + 8, cy + 4), (cx + 5, cy)], "#f2c94c")
    for x in range(cx - 4, cx + 6):
        fase = (x - cx) % 4
        if fase in (0, 2):
            t.vline(x, cy + 1, cy + 12, "#141414" if fase == 0 else "#f4f1ea")
    t.hline(cx - 1, cx + 2, cy, "#141414")
    t.put(cx, cy + 1, "#141414"); t.put(cx + 1, cy + 1, "#141414")
    t.hline(cx - 7, cx - 5, cy + 5, "#141414"); t.hline(cx + 6, cx + 8, cy + 5, "#141414")
    t.rect(cx - 3, cy + 6, 8, 2, "#f4f1ea")
    for x in range(cx - 2, cx + 4, 2):
        t.put(x, cy + 6, "#141414")
    t.rect(cx + 2, cy + 3, 2, 2, "#f4f1ea"); t.put(cx + 2, cy + 3, "#141414")
    escurecer(t, cx - 3, cy + 13, cx + 5, cy + 13, .25)

    # prateleira estreita perto da porta: toca-fitas, fitas e o barquinho do vo
    t.rect(130, 40, 13, 2, "#7a4c2b")
    t.hline(130, 142, 40, "#a8743f")
    t.put(131, 42, "#5a3a22"); t.put(141, 42, "#5a3a22")
    t.rect(130, 35, 7, 5, "#3a3a44")
    t.disco(132, 37.5, 1.1, "#8a8a96"); t.disco(135, 37.5, 1.1, "#8a8a96")
    t.hline(131, 135, 35, "#5a5a66")
    t.put(133, 36, "#e8503a")
    poligono(t, [(137, 37), (143, 37), (142, 40), (138, 40)], "#a8743f")
    t.vline(140, 33, 37, "#6b4325")
    poligono(t, [(141, 33), (143, 35), (141, 35)], "#f4f1ea")

    # cadeira com a mochila da escola
    t.rect(118, 52, 8, 2, "#8a5a33")
    t.vline(118, 54, PAREDE_I + 3, "#6b4325"); t.vline(125, 54, PAREDE_I + 3, "#6b4325")
    t.rect(118, 45, 2, 7, "#8a5a33")
    t.rect(120, 46, 5, 6, "#3a6aa8")
    t.hline(120, 124, 48, "#2b4f80")
    t.put(122, 50, "#f2c94c")
    sombra_no_chao(t, 122, 64, 5)

    # tapete de retalho, o tenis jogado, o chinelo e o carrinho de brinquedo
    tapete_retalho(t, 14, 66, 24, 5, ("#c9503a", "#4f86c6", "#e8c06a", "#7cc45e"), seed=3)
    t.rect(44, 66, 3, 2, "#f4f1ea"); t.put(46, 66, "#c9503a")
    t.rect(48, 67, 3, 2, "#f4f1ea"); t.put(50, 67, "#c9503a")
    t.rect(16, 73, 3, 1, "#3a6aa8"); t.rect(20, 74, 3, 1, "#3a6aa8")          # chinelo
    t.rect(96, 74, 5, 2, "#d83a2a"); t.hline(97, 99, 73, "#ff8a6a")            # carrinho
    t.put(96, 76, "#1a1a1a"); t.put(100, 76, "#1a1a1a")
    for x, y in ((104, 79), (107, 78), (110, 80)):                              # bolinhas de gude
        t.put(x, y, "#9ad0e8"); t.put(x + 1, y, "#ffffff")

    # (a vara de bambu encostada perto da porta e um sprite a parte,
    # vara_parede(), porque some quando o neto pega)

    # porta da cozinha (2,1 m), entreaberta com a luz do lampiao de la
    t.rect(146, 29, 12, 31, "#f2c47a")
    t.rect(146, 29, 4, 31, "#6b4325")
    t.vline(146, 29, 59, "#5a3a22")
    t.rect(144, 27, 16, 2, OL)
    t.vline(144, 27, 59, OL)
    t.vline(159, 27, 59, OL)

    luz_entrando(t, 15, 31, 45, PAREDE_I)
    vinheta(t, chao=PAREDE_I)
    return t


def cozinha():
    """Cozinha da Vo Marlene, camera de perto. Fogao a lenha na altura da
    cintura, chaleira chiando, mesa posta, geladeira de 1997, filtro de barro
    e as panelas penduradas. A porta da direita da pro terreiro."""
    t = Tela(WI, HI)
    telhado_por_dentro(t, 0, WI, 0, 22, seed=4)
    for y in range(24, 45):
        for x in range(WI):
            t.put(x, y, "#efe4cc" if (x * 3 + y * 7) % 23 else "#e2d6bc")
    tabuas(t, 0, 45, WI, PAREDE_I, ("#a87448", "#9c6a40", "#b07c4e"), "#6a4228", larg=5, seed=9, pregos=False)
    t.hline(0, WI - 1, 45, "#c9955a")
    t.hline(0, WI - 1, 46, "#6a4228")
    piso_tabuado(t, 0, WI, PAREDE_I, HI, tons=("#9a6a40", "#8e6038", "#a47246"), seed=11)

    # fogao a lenha (0,8 m de altura, 1,3 m de largura)
    t.rect(4, 48, 20, 13, "#f2ece0")
    t.vline(4, 48, 60, "#d8cfbc"); t.vline(23, 48, 60, "#cfc4ae")
    t.rect(3, 46, 22, 2, "#2b2b30")
    t.hline(3, 24, 46, "#5a5a62")
    t.disco(8, 46.5, 1.4, "#3a3a40"); t.disco(14, 46.5, 1.4, "#3a3a40")
    t.rect(6, 51, 5, 4, "#2b2b30")
    for y in range(52, 55):
        for x in range(7, 10):
            t.put(x, y, "#f28a2a" if (x + y) % 2 else "#ffd04a")
    t.rect(13, 52, 9, 3, "#d8d0bc"); t.hline(13, 21, 52, "#2b2b30")
    sombra_no_chao(t, 14, 61, 11)
    t.rect(20, 0, 3, 46, "#3a3a40")
    t.vline(20, 0, 45, "#5a5a62")
    t.rect(6, 42, 5, 4, "#9aa3ab"); t.hline(6, 10, 42, "#cfd6dc")
    t.disco(15, 43.5, 2.4, "#5a6068", sy=.8)
    traco(t, 17, 43, 19, 41, "#5a6068")
    for i, (x, y) in enumerate(((19, 39), (18, 37), (20, 35), (19, 33))):
        t.mix(x, y, "#ffffff", .7 - i * .15); t.mix(x + 1, y - 1, "#ffffff", .5 - i * .1)
    for i, y in enumerate(range(54, 61, 2)):
        for x in range(25, 32, 3):
            t.disco(x + (1 if i % 2 else 0), y + 1, 1.3, "#8a5a33")
            t.put(x + (1 if i % 2 else 0), y + 1, "#c9955a")

    # janela com cortina e o ceu clareando
    janela_de_dentro(t, 38, 29, 16, 15, CEU_JANELA_MADRUGADA, MORROS_JANELA)
    t.rect(43, 42, 3, 2, "#b5653a"); t.disco(44.5, 40.5, 1.6, "#4f8a45")

    # panelas e canecas penduradas
    t.hline(58, 74, 30, "#5a3a22")
    for x, r, cor in ((60, 2.4, "#c9a070"), (65, 2.0, "#9aa3ab"), (70, 2.6, "#b5653a")):
        t.vline(x, 30, 32, "#3a3030")
        t.disco(x, 34, r, cor)
        t.put(x - 1, 33, "#ffffff")

    # aparador com potes, radio AM e lata de cafe
    t.rect(78, 38, 26, 2, "#7a4c2b"); t.hline(78, 103, 38, "#a8743f")
    for i, x in enumerate(range(79, 92, 4)):
        t.rect(x, 33, 3, 5, ("#c9a86a", "#e8dcc0", "#b5653a", "#9fd0ea")[i % 4])
        t.hline(x, x + 2, 33, "#5a3a22")
    t.rect(94, 33, 8, 5, "#6b4325"); t.rect(95, 34, 3, 3, "#c9a86a")
    t.disco(100, 35.5, 1.0, "#e8c06a")
    traco(t, 101, 33, 104, 28, "#9aa3ab")

    # calendario de 1997
    t.rect(107, 30, 6, 9, "#f4f1ea"); t.rect(107, 30, 6, 4, "#4f86c6")
    t.disco(110, 31.5, 1.2, "#7cc45e")
    for y in range(35, 38):
        for x in range(108, 112, 2):
            t.put(x, y, "#9aa3ab")
    t.put(110, 29, "#9aa3ab")

    # mesa posta (0,75 m) com banco: garrafa termica, bule, xicaras e pao
    t.rect(70, 49, 26, 2, "#a8743f"); t.hline(70, 95, 49, "#c9955a")
    for x in range(70, 96, 2):
        t.put(x, 50, "#c9503a")
    for x in (72, 93):
        t.rect(x, 51, 2, 11, "#7a4c2b")
    sombra_no_chao(t, 83, 62, 13)
    t.rect(74, 43, 3, 6, "#c9503a"); t.hline(74, 76, 43, "#f4f1ea"); t.put(75, 42, "#f4f1ea")
    t.disco(80, 47, 1.8, "#f4f1ea", sy=.8); t.put(82, 46, "#f4f1ea")
    for x in (84, 88):
        t.rect(x, 47, 2, 2, "#f4f1ea"); t.put(x + 2, 47, "#f4f1ea"); t.put(x, 47, "#5a3a22")
    t.disco(92, 47.5, 2.0, "#c98a3a", sy=.6)
    t.rect(78, 56, 18, 2, "#8a5a33"); t.vline(79, 58, 62, "#6b4325"); t.vline(94, 58, 62, "#6b4325")

    # geladeira de 1997, arredondada, com imas
    t.rect(118, 36, 11, 25, "#eef0ea")
    t.vline(118, 36, 60, "#d4d8d0"); t.vline(128, 36, 60, "#c4c8c0")
    t.hline(118, 128, 36, "#ffffff")
    t.hline(118, 128, 44, "#c4c8c0")
    t.vline(126, 39, 42, "#9aa0a0"); t.vline(126, 47, 52, "#9aa0a0")
    t.put(121, 48, "#e8503a"); t.put(123, 50, "#4f86c6"); t.put(120, 52, "#f2c94c")
    sombra_no_chao(t, 123, 61, 7)

    # filtro de barro no suporte
    t.rect(104, 48, 9, 13, "#7a4c2b")
    t.disco(108.5, 41, 3.4, "#b5653a", sy=1.2)
    t.disco(108.5, 46, 3.2, "#a8582f")
    t.put(107, 39, "#d08a5a")
    t.put(108, 48, "#9aa3ab")
    sombra_no_chao(t, 108, 61, 5)

    # a tigela do MauMau perto do fogao, que e onde ele gosta de ficar
    t.rect(30, 63, 4, 2, "#4f86c6"); t.hline(30, 33, 63, "#7aa8e0")
    t.hline(31, 32, 62, "#c98a5a")
    # cesto de pinhao no chao, capacho e vassoura de palha na porta
    t.rect(52, 66, 7, 4, "#b08048"); t.hline(52, 58, 66, "#d0a068")
    for x in range(53, 58, 2):
        t.put(x, 65, "#7a4a2a")
    tapete_retalho(t, 138, 66, 20, 4, ("#8a6a4a", "#a8845a", "#6a4a32"), seed=5)
    traco(t, 134, 60, 137, 36, "#c9a060")
    poligono(t, [(132, 60), (137, 60), (136, 55), (133, 55)], "#e0c070")
    # porta do terreiro, aberta, com o amanhecer entrando
    gradiente(t, 140, 29, 156, 60, ["#d9887a", "#f2b36a", "#f8d08a"])
    t.rect(140, 29, 4, 31, "#6b4325")
    t.rect(138, 27, 20, 2, OL)
    t.vline(138, 27, 59, OL); t.vline(157, 27, 59, OL)
    luz_entrando(t, 141, 156, 30, PAREDE_I, forca=.12, cor="#ffd08a")
    luz_entrando(t, 38, 54, 44, PAREDE_I, forca=.10)
    vinheta(t, chao=PAREDE_I)
    return t


def vara_parede():
    """A vara de bambu encostada na parede do quarto (3 m: passa da parede).
    O pe da vara e o pixel (1, 49): e por ele que a cena posiciona o sprite."""
    t = Tela(14, 50)
    for i in range(46):
        x, y = 1 + i * .22, 49 - i
        t.put(x, y, "#9a742f" if i % 8 == 0 else "#e6c266")
        t.put(x + 1, y, "#c9a24a")
    t.rect(0, 39, 3, 2, "#c99a62")
    return t


# ============================================================== EXTERIORES

CEU_MADRUGADA = ["#28305e", "#3a3e78", "#5a4a8a", "#8a5a90", "#c06e8a", "#e8907a", "#f6b47a", "#fbd690"]
CEU_ALVORADA = ["#4a5a9a", "#6a6aa8", "#9a7aac", "#d08aa0", "#f0a888", "#f8c890", "#fce0a8"]
CEU_MANHA = ["#5a9ad8", "#6eaae0", "#86bce6", "#a0cceb", "#bcdcee", "#d8eaee", "#f2f0e2"]


def ceu_e_serra(t, ceu, horizonte, serras, nuvens, sol=None, estrelado=0, seed=1):
    """Ceu em gradiente, nuvens, estrelas e camadas de serra com neblina entre
    elas (a de tras mais azulada, que e o que da a distancia)."""
    gradiente(t, 0, 0, t.w, horizonte, ceu)
    if estrelado:
        estrelas(t, 0, 0, t.w, int(horizonte * .35), estrelado, seed=seed)
    if sol:
        sx, sy, r, corsol, halo = sol
        for y in range(int(sy - r * 3), int(sy + r * 3)):
            for x in range(int(sx - r * 3), int(sx + r * 3)):
                d = math.hypot(x - sx, y - sy)
                if d < r:
                    t.put(x, y, corsol)
                elif d < r * 3:
                    t.mix(x, y, halo, .35 * (1 - (d - r) / (r * 2)))
    for cx, cy, larg, cores, s in nuvens:
        nuvem(t, cx, cy, larg, *cores, seed=s)
    for i, (base, picos, cor, topo) in enumerate(serras):
        serra(t, base, picos, cor, topo)
        neblina(t, base - 6, base + 2, forca=.30, seed=seed + i)


def casa_de_madeira(t, x0, x1, base, seed=1):
    """Casa colonial de madeira pintada de verde-agua com friso branco,
    telhado de barro, varanda com guarda-corpo, samambaias no xaxim e a
    chamine soltando a fumaca do fogao a lenha."""
    parede, sombra, friso = "#9cc8b8", "#7aab9c", "#f4f0e6"
    topo = base - 39                                          # parede de 2,6 m
    for x in range(x0, x1):
        for y in range(topo, base):
            t.put(x, y, sombra if (x - x0) % 5 == 0 else parede)
    escurecer(t, x0, topo, x1 - 1, topo + 4, .25)
    cume = topo - 20
    cx = (x0 + x1) / 2
    poligono(t, [(x0 - 5, topo + 1), (cx, cume), (x1 + 5, topo + 1)], "#a5553a")
    for y in range(int(cume) + 2, topo + 1, 3):
        meia = (y - cume) * ((x1 - x0) / 2 + 5) / (topo + 1 - cume)
        t.hline(int(cx - meia) + 1, int(cx + meia) - 1, y, "#7a3424")
        for x in range(int(cx - meia) + 2, int(cx + meia) - 1, 4):
            t.put(x, y - 1, "#c97448")
    t.hline(x0 - 5, x1 + 5, topo + 1, OL)
    t.hline(x0 - 4, x1 + 4, topo + 2, friso)
    chx = x1 - 20
    t.rect(chx, cume + 8, 5, 10, "#b5603f")
    t.hline(chx - 1, chx + 5, cume + 8, "#6e2e20")
    for i in range(12):
        x = chx + 2 + 3 * math.sin(i / 1.6) + i * .8
        y = cume + 6 - i * 3.2
        t.disco(x, y, 1.6 + i * .32, "#d8d2e0")
        t.mix(x - 1, y - 1, "#ffffff", .6)
        t.mix(x + 1, y + 1, "#a8a0b8", .4)
    vt = base - 34                                            # varanda a 2,3 m
    t.rect(x0 - 2, vt, x1 - x0 + 4, 3, "#8a4430")
    t.hline(x0 - 2, x1 + 1, vt, "#b5603f")
    t.hline(x0 - 2, x1 + 1, vt + 3, OL)
    for x in range(x0 + 1, x1, 24):
        t.rect(x, vt + 3, 3, base - vt - 3, "#e8e2d4")
        t.vline(x + 2, vt + 3, base - 1, "#c4bcac")
    for x in range(x0, x1):
        if (x - x0) % 3 == 0:
            t.vline(x, base - 13, base - 1, "#e8e2d4")
    t.hline(x0, x1 - 1, base - 14, friso)
    t.hline(x0, x1 - 1, base - 13, "#c4bcac")
    px_ = x0 + 34
    t.rect(px_, base - 31, 12, 31, "#f8d088")
    t.rect(px_, base - 31, 4, 31, "#6a4228")
    t.rect(px_ - 1, base - 32, 14, 1, friso)
    for jx in (x0 + 10, x0 + 60, x0 + 80):
        if jx + 14 > x1:
            continue
        t.rect(jx, base - 29, 14, 15, "#ffd890")
        t.vline(jx + 7, base - 29, base - 15, "#4f7f9c")
        t.hline(jx, jx + 13, base - 22, "#4f7f9c")
        t.rect(jx - 1, base - 30, 16, 1, friso); t.rect(jx - 1, base - 14, 16, 1, friso)
        t.rect(jx - 3, base - 29, 2, 15, "#4f7f9c"); t.rect(jx + 15, base - 29, 2, 15, "#4f7f9c")
    for sx in (x0 + 24, x0 + 54):                             # samambaias no xaxim
        t.vline(sx, vt + 3, vt + 7, "#3a3030")
        t.rect(sx - 2, vt + 7, 5, 3, "#6a4a32")
        for k in range(10):
            a = k / 9.0 * math.pi
            traco(t, sx, vt + 8, sx + math.cos(a) * 6, vt + 9 + math.sin(a) * 6, "#4f9a44" if k % 2 else "#6ab84e")
    t.disco(px_ + 16, vt + 6, 1.4, "#ffe08a")                 # lampiao
    for y in range(vt + 2, vt + 18):
        for x in range(px_ + 6, px_ + 27):
            d = math.hypot(x - px_ - 16, y - vt - 6)
            if d < 10:
                t.mix(x, y, "#ffe08a", .2 * (1 - d / 10))
    t.rect(x0 + 6, base - 7, 14, 2, "#8a5a33")                # banco e botinas
    t.vline(x0 + 7, base - 5, base - 1, "#6b4325"); t.vline(x0 + 18, base - 5, base - 1, "#6b4325")
    t.rect(px_ + 14, base - 3, 2, 3, "#5a3a22"); t.rect(px_ + 17, base - 3, 2, 3, "#5a3a22")


def saida(manha=False):
    """O terreiro, de madrugada (ou de manha, na volta da pescaria): a casa verde-agua com a varanda acesa, o varal
    com roupa, as galinhas ciscando, o palanque onde Alexandre e Apollo
    esperam encilhados, a bergamoteira e os latoes de leite na porteira."""
    t = Tela(W, H)
    t.rect(0, 0, W, H, "#4f6a5a")
    if manha:
        ceu_e_serra(t, CEU_MANHA, 108,
                    serras=[(104, [(60, 30, 50), (180, 24, 40), (290, 34, 46)], "#9ab0c8", "#aac0d4"),
                            (112, [(20, 22, 40), (140, 28, 48), (260, 20, 36)], "#7a98a4", "#88a6b0"),
                            (118, [(90, 14, 40), (220, 18, 44), (320, 12, 30)], "#5a8a68", "#68987a")],
                    nuvens=[(70, 26, 40, ("#ffffff", "#eef4f8", "#c4d4e2"), 1),
                            (230, 16, 32, ("#ffffff", "#eef4f8", "#c4d4e2"), 2)],
                    sol=(250, 30, 7, "#fffbe8", "#fff2c0"), seed=5)
    else:
        ceu_e_serra(t, CEU_MADRUGADA, 108,
                    serras=[(104, [(60, 30, 50), (180, 24, 40), (290, 34, 46)], "#7a7aa4", "#8e8cb4"),
                            (112, [(20, 22, 40), (140, 28, 48), (260, 20, 36)], "#5a6a84", "#6a7a92"),
                            (118, [(90, 14, 40), (220, 18, 44), (320, 12, 30)], "#3e5a5a", "#4c6a66")],
                    nuvens=[(70, 26, 40, ("#ffd2b0", "#e8a0a8", "#9a7a9c"), 1),
                            (230, 16, 32, ("#ffc8a8", "#e096a0", "#8a6a90"), 2),
                            (160, 44, 26, ("#ffd8b8", "#eaa8a8", "#a08098"), 3)],
                    estrelado=40, seed=5)
    passaros(t, [(120, 34), (127, 31), (134, 35)], "#3a3048")
    if manha:
        gramado(t, 0, 116, W, CHAO, "#6a9a52", "#527a40", "#86b868", flores=("#ffffff", "#f2d880"), seed=3)
        terra(t, 0, CHAO, W, H, "#a07a50", "#80603c", "#b8946a", seed=4)
    else:
        gramado(t, 0, 116, W, CHAO, "#5a7a52", "#46663e", "#6e8e5e", flores=("#e8e0f0", "#f2d880"), seed=3)
        terra(t, 0, CHAO, W, H, "#8a6a46", "#6e5034", "#a8865a", seed=4)
    for x in range(0, W, 2):
        if (x * 7) % 5:
            t.put(x, CHAO, "#5a7a52")

    for x in range(118, W, 9):                                 # cerca de tabua (1,1 m)
        t.rect(x, 113, 2, 17, "#9a7a50")
        t.put(x, 113, "#b89668")
    t.hline(116, W - 1, 117, "#8a6a40"); t.hline(116, W - 1, 124, "#8a6a40")

    arvore(t, 268, 118, 18, 15, VERDES_DIA if manha else VERDES_MADRUGADA, seed=7)  # bergamoteira
    R = rng(8)
    for _ in range(14):
        a, d = R.uniform(0, 6.28), R.uniform(2, 13)
        t.put(268 + math.cos(a) * d, 94 + math.sin(a) * d * .8, "#f0902a")

    casa_de_madeira(t, 4, 112, CHAO, seed=2)

    for x in (120, 160):                                       # varal com roupa
        t.vline(x, 103, CHAO - 1, "#7a5a3a")
    traco(t, 120, 104, 160, 105, "#d8d0c0")
    for x, w, h, cor in ((124, 6, 7, "#f4f0e6"), (132, 5, 9, "#4f6a9a"), (139, 8, 6, "#e8c06a"),
                         (149, 6, 8, "#c9503a")):
        t.rect(x, 105, w, h, cor)
        t.hline(x, x + w - 1, 105, "#ffffff")
        escurecer(t, x + w - 1, 106, x + w - 1, 104 + h, .25)

    for gx, cor in ((146, "#f4ece0"), (156, "#b8602a")):        # galinhas ciscando
        t.disco(gx, CHAO + 4, 2.4, cor, sy=.8)
        t.disco(gx + 2, CHAO + 1, 1.3, cor)
        t.put(gx + 2, CHAO, "#e8302a")
        t.put(gx + 4, CHAO + 1, "#e8b03a")
        t.put(gx - 2, CHAO + 2, cor)
        t.vline(gx, CHAO + 6, CHAO + 7, "#e8b03a")

    for x in (182, 252):                                       # palanque dos cavalos
        t.rect(x, 113, 3, 17, "#7a4c2b"); t.hline(x, x + 2, 113, "#9a6438")
    t.rect(180, 116, 76, 2, "#8a5a33"); t.hline(180, 255, 116, "#a8743f")

    t.rect(276, 120, 12, 2, "#8a5a33")                          # latoes de leite
    for x in (277, 283):
        t.vline(x, 122, CHAO - 1, "#6b4325")
        t.rect(x, 113, 4, 7, "#b8c0c4"); t.hline(x, x + 3, 113, "#e0e6e8")
        t.rect(x + 1, 111, 2, 2, "#9aa3ab")
    for i, x in enumerate(range(292, 318, 2)):                  # porteira
        t.vline(x, 113, CHAO - 2, "#a8743f" if i % 2 else "#8a5a33")
    traco(t, 292, CHAO - 3, 317, 114, "#7a4c2b", 2)
    t.hline(290, 318, 113, "#6b4325")

    # o terreiro nao e chao liso: gramado ralo nas beiradas, caminho de
    # pedra da varanda ate o palanque e moitas de capim
    R = rng(21)
    for _ in range(40):
        cx, cy = R.uniform(0, W), R.uniform(CHAO + 8, H)
        if 60 < cx < 200 and cy < CHAO + 22:
            continue  # deixa o caminho principal de terra
        r = R.uniform(4, 11)
        for y in range(int(cy - r * .4), int(cy + r * .4)):
            for x in range(int(cx - r), int(cx + r)):
                if ((x - cx) / r) ** 2 + ((y - cy) / (r * .4)) ** 2 <= 1:
                    t.put(x, y, "#5a7a4e" if (x * 3 + y) % 4 else "#6e8e5a")
        for _ in range(int(r)):
            t.put(cx + R.uniform(-r, r), cy - R.uniform(0, 2), "#46663e")
    for i, x in enumerate(range(42, 186, 9)):                 # caminho de pedra
        y = CHAO + 4 + (i % 2)
        t.disco(x, y, 2.6, "#a8a094", sy=.55)
        t.hline(int(x - 1), int(x + 1), y - 1, "#c8c0b2")
        t.hline(int(x - 2), int(x + 2), y + 1, "#7a7266")
    for x in range(6, 110, 7):                                # canteiro de hortensias
        cor = ("#7a9ae0", "#e09ac0", "#a8a8f0")[x % 3]
        t.disco(x, CHAO + 1, 2.4, "#3e6a3a")
        t.disco(x - .5, CHAO, 1.8, cor)
        t.put(x - 1, CHAO - 1, "#ffffff")
    pcx = 206                                                  # o poco, com telhadinho
    t.rect(pcx - 6, CHAO + 6, 13, 9, "#9a948a")
    for y in range(CHAO + 6, CHAO + 15, 3):
        t.hline(pcx - 6, pcx + 6, y, "#7a746a")
    t.hline(pcx - 6, pcx + 6, CHAO + 6, "#c0b8ac")
    t.vline(pcx - 6, CHAO - 6, CHAO + 6, "#6b4325"); t.vline(pcx + 6, CHAO - 6, CHAO + 6, "#6b4325")
    poligono(t, [(pcx - 9, CHAO - 6), (pcx, CHAO - 12), (pcx + 9, CHAO - 6)], "#a5553a")
    t.hline(pcx - 9, pcx + 9, CHAO - 6, OL)
    t.hline(pcx - 5, pcx + 5, CHAO - 1, "#5a3a22")             # sarilho
    t.rect(pcx - 1, CHAO, 3, 4, "#8a6a4a")                     # balde
    for x, y in ((236, 168), (90, 172), (300, 150)):           # pedras soltas
        t.disco(x, y, 2.4, "#8a8478", sy=.6)
        t.hline(x - 1, x + 1, y - 1, "#aaa49a")
    neblina(t, 108, 124, forca=.25, seed=9)
    return t


def estrada():
    """A estrada de chao ate o rio: pasto com vacas leiteiras, cerca, as
    araucarias e o sol querendo nascer atras da serra."""
    t = Tela(W, H)
    t.rect(0, 0, W, H, "#4f6a5a")
    ceu_e_serra(t, CEU_ALVORADA, 112,
                serras=[(106, [(80, 28, 50), (210, 32, 52)], "#8a86b0", "#9c98bc"),
                        (114, [(30, 20, 40), (160, 24, 44), (300, 26, 40)], "#62788a", "#728898"),
                        (120, [(120, 12, 40), (260, 14, 40)], "#4a6a5a", "#567a66")],
                nuvens=[(60, 30, 36, ("#fff0d8", "#f2c0b0", "#b090a8"), 4),
                        (250, 22, 40, ("#fff0d8", "#f0b8a8", "#a88aa4"), 5)],
                sol=(300, 104, 7, "#fff4c8", "#ffd090"), seed=6)
    gramado(t, 0, 118, W, CHAO, "#6a8a52", "#527240", "#86a868", flores=("#f2e6a0", "#ffffff", "#e8a8c8"), seed=5)
    terra(t, 0, CHAO, W, H, "#a8804e", "#8a6a3e", "#c09a68", seed=6)
    for y in (CHAO + 12, CHAO + 30):                           # sulcos da roda
        for x in range(W):
            if (x * 3) % 7:
                t.put(x, y, "#8a6a3e")
    # beira de capim alto na frente, com flor e pedra: a estrada fica no meio
    gramado(t, 0, CHAO + 34, W, H, "#5f8a4a", "#466e38", "#80aa62",
            flores=("#f2e6a0", "#ffffff", "#e8a8c8", "#a8b8f0"), seed=7, densidade=.5)
    R = rng(31)
    for x in range(0, W, 2):                                   # fiapos altos na borda
        h = R.randint(1, 5)
        t.vline(x, CHAO + 34 - h, CHAO + 34, "#5f8a4a" if x % 4 else "#80aa62")
    for x in range(0, W, 3):                                   # beira de grama la atras
        t.vline(x, CHAO, CHAO + R.randint(1, 3), "#6a8a52")
    for cx, topo in ((40, 66), (150, 78), (276, 60)):           # araucarias
        t.rect(cx, topo + 6, 2, 118 - topo - 6, "#4a3424")
        t.vline(cx + 1, topo + 6, 117, "#3a2818")
        # a copa em taca: andares de galho com as pontas viradas para cima,
        # o de cima mais largo, e o miolo escuro por baixo de cada andar
        for meia, dy in ((15, 0), (12, 4), (9, 8), (5, 11)):
            y = topo + dy
            for x in range(cx - meia, cx + meia + 2):
                curva = int(((x - cx) / float(meia + 1)) ** 2 * 3)
                t.put(x, y - curva, "#3f7048")
                t.put(x, y - curva + 1, "#2f5a3a")
                t.put(x, y - curva + 2, "#22442c")
            traco(t, cx, y + 4, cx - meia + 3, y, "#3a2818")
            traco(t, cx + 1, y + 4, cx + meia - 2, y, "#3a2818")
        for x in range(cx - 15, cx + 17, 3):
            t.put(x, topo - 3 - int(((x - cx) / 16.0) ** 2 * 3) + 3, "#5a9060")
    for vx, vy in ((90, 121), (110, 123), (210, 120)):           # vacas holandesas
        t.rect(vx, vy, 8, 4, "#f4f0ea")
        t.rect(vx + 2, vy, 3, 2, "#2a2630"); t.rect(vx + 6, vy + 2, 2, 2, "#2a2630")
        t.rect(vx + 7, vy - 1, 3, 3, "#f4f0ea"); t.put(vx + 9, vy, "#2a2630")
        for lx in (vx, vx + 2, vx + 5, vx + 7):
            t.vline(lx, vy + 4, vy + 6, "#2a2630")
    for x in range(0, W, 10):                                  # cerca de arame
        t.rect(x, 112, 2, 18, "#8a6a3a")
    for y in (116, 122):
        t.hline(0, W - 1, y, "#9aa0a0")
    neblina(t, 112, 126, forca=.28, seed=10)
    passaros(t, [(150, 40), (157, 37), (164, 41), (171, 38)], "#4a4058")
    return t


LARGURA_ESTRADA = W * 3


def estrada_longa(manha=False):
    """A estrada de chao inteira, tres telas de largura, para o jogador
    conduzir o Alexandre com a camera indo junto. De madrugada na ida, de
    manha na volta. Marcos no caminho, que as falas usam: a porteira (1/3)
    e a bergamoteira do Seu Arlindo (2/3); o rio fica na ponta direita."""
    w = LARGURA_ESTRADA
    t = Tela(w, H)
    t.rect(0, 0, w, H, "#4f6a5a")
    if manha:
        ceu, sol = CEU_MANHA, (w - 140, 34, 8, "#fffbe8", "#fff0c0")
        nuvens = [(x, 20 + (i % 3) * 8, 34 + (i % 2) * 10, ("#ffffff", "#e8eef4", "#b8c8dc"), i + 3)
                  for i, x in enumerate(range(50, w, 130))]
        verdes = VERDES_DIA
    else:
        ceu, sol = CEU_ALVORADA, (w - 30, 104, 7, "#fff4c8", "#ffd090")
        nuvens = [(x, 22 + (i % 3) * 7, 36 + (i % 2) * 8, ("#fff0d8", "#f2c0b0", "#b090a8"), i + 4)
                  for i, x in enumerate(range(60, w, 150))]
        verdes = VERDES_MADRUGADA
    ceu_e_serra(t, ceu, 112,
                serras=[(106, [(x, 28 + (i % 3) * 4, 50) for i, x in enumerate(range(80, w, 140))], "#8a86b0", "#9c98bc"),
                        (114, [(x, 20 + (i % 2) * 6, 42) for i, x in enumerate(range(30, w, 110))], "#62788a", "#728898"),
                        (120, [(x, 12 + (i % 2) * 3, 40) for i, x in enumerate(range(120, w, 140))], "#4a6a5a", "#567a66")],
                nuvens=nuvens, sol=sol, seed=6)
    gramado(t, 0, 118, w, CHAO, "#6a8a52", "#527240", "#86a868", flores=("#f2e6a0", "#ffffff", "#e8a8c8"), seed=5)
    terra(t, 0, CHAO, w, H, "#a8804e", "#8a6a3e", "#c09a68", seed=6)
    for y in (CHAO + 12, CHAO + 30):
        for x in range(w):
            if (x * 3) % 7:
                t.put(x, y, "#8a6a3e")
    gramado(t, 0, CHAO + 34, w, H, "#5f8a4a", "#466e38", "#80aa62",
            flores=("#f2e6a0", "#ffffff", "#e8a8c8", "#a8b8f0"), seed=7, densidade=.5)
    R = rng(31)
    for x in range(0, w, 2):
        h = R.randint(1, 5)
        t.vline(x, CHAO + 34 - h, CHAO + 34, "#5f8a4a" if x % 4 else "#80aa62")
    for x in range(0, w, 3):
        t.vline(x, CHAO, CHAO + R.randint(1, 3), "#6a8a52")
    for cx, topo in ((40, 66), (150, 78), (276, 60), (420, 70), (590, 64), (700, 76), (860, 62), (930, 72)):
        t.rect(cx, topo + 6, 2, 118 - topo - 6, "#4a3424")
        t.vline(cx + 1, topo + 6, 117, "#3a2818")
        for meia, dy in ((15, 0), (12, 4), (9, 8), (5, 11)):
            y = topo + dy
            for x in range(cx - meia, cx + meia + 2):
                curva = int(((x - cx) / float(meia + 1)) ** 2 * 3)
                t.put(x, y - curva, "#3f7048")
                t.put(x, y - curva + 1, "#2f5a3a")
                t.put(x, y - curva + 2, "#22442c")
            traco(t, cx, y + 4, cx - meia + 3, y, "#3a2818")
            traco(t, cx + 1, y + 4, cx + meia - 2, y, "#3a2818")
        for x in range(cx - 15, cx + 17, 3):
            t.put(x, topo - 3 - int(((x - cx) / 16.0) ** 2 * 3) + 3, "#5a9060")
    for vx, vy in ((90, 121), (110, 123), (210, 120), (470, 122), (500, 120), (760, 121)):
        t.rect(vx, vy, 8, 4, "#f4f0ea")
        t.rect(vx + 2, vy, 3, 2, "#2a2630"); t.rect(vx + 6, vy + 2, 2, 2, "#2a2630")
        t.rect(vx + 7, vy - 1, 3, 3, "#f4f0ea"); t.put(vx + 9, vy, "#2a2630")
        for lx in (vx, vx + 2, vx + 5, vx + 7):
            t.vline(lx, vy + 4, vy + 6, "#2a2630")
    porteira = w // 3
    for x in range(0, w, 10):
        if abs(x - porteira) > 10:
            t.rect(x, 112, 2, 18, "#8a6a3a")
    for y in (116, 122):
        for x in range(w):
            if abs(x - porteira) > 9:
                t.put(x, y, "#9aa0a0")
    # a porteira de madeira, aberta pra estrada
    for px in (porteira - 10, porteira + 9):
        t.rect(px, 106, 3, 24, "#6b4a2a")
        t.hline(px, px + 2, 106, "#8a6a3a")
    for y in (110, 116, 122):
        traco(t, porteira - 7, y, porteira - 1, y + 9, "#a8804e")
    t.rect(porteira - 8, 110, 2, 14, "#a8804e")
    # a bergamoteira do Seu Arlindo, carregada, na beira da cerca
    bx = w * 2 // 3
    arvore(t, bx, 124, 12, 13, verdes, seed=11)
    R = rng(12)
    for _ in range(16):
        t.put(bx + R.randint(-10, 10), 124 - 12 - 4 + R.randint(-8, 7), "#f2962a")
    neblina(t, 112, 126, forca=.12 if manha else .28, seed=10)
    passaros(t, [(150, 40), (157, 37), (164, 41), (171, 38), (620, 46), (627, 43)], "#4a4058")
    return t


def rio(t, y0, cores, reflexo_y=None, seed=1):
    """Agua de rio: gradiente, riscos de correnteza e o reflexo escuro da mata
    logo abaixo da margem de la."""
    gradiente(t, 0, y0, t.w, t.h, cores)
    R = rng(seed)
    for _ in range(int(t.w * (t.h - y0) * .02)):
        x, y = R.randrange(t.w), R.randrange(y0 + 1, t.h)
        t.hline(x, x + R.randint(2, 8), y, cores[0] if y < (y0 + t.h) / 2 else cores[1])
    if reflexo_y:
        for y in range(y0, min(t.h, y0 + reflexo_y)):
            for x in range(t.w):
                if (x // 3 + y) % 4 != 0:
                    t.mix(x, y, "#1e3a2e", .35 * (1 - (y - y0) / reflexo_y))
    t.hline(0, t.w - 1, y0, "#d8ece4")


def mata_ciliar(t, y_agua, altura, cores, seed=1):
    """A mata da outra margem: copas de varios tamanhos encostadas, capim e
    taboa na beira d'agua."""
    R = rng(seed)
    x = -6
    while x < t.w + 6:
        r = R.uniform(7, 13)
        copa(t, x, y_agua - altura + R.uniform(-3, 4), r, cores, seed=int(x) + seed)
        x += r * R.uniform(1.0, 1.5)
    for x in range(t.w):
        for y in range(y_agua - 6, y_agua):
            if t.get(x, y)[:3] != hx(cores[2])[:3]:
                t.put(x, y, cores[0])
    for x in range(0, t.w, 2):
        h = R.randint(1, 4)
        t.vline(x, y_agua - h, y_agua - 1, cores[1])
        if R.random() < .08:
            t.vline(x, y_agua - 7, y_agua - 1, "#5a7a3a"); t.put(x, y_agua - 8, "#6a4a2a")


def cais_rio():
    """O cais do vo no rio, com o sol nascendo: a figueira onde se amarram
    Alexandre e Apollo, o trapiche e o bote esperando na agua."""
    t = Tela(W, H)
    t.rect(0, 0, W, H, "#2f5538")
    ceu_e_serra(t, CEU_ALVORADA, 100,
                serras=[(92, [(100, 26, 50), (250, 30, 50)], "#8a86b0", "#9c98bc"),
                        (100, [(40, 20, 40), (190, 22, 44), (310, 18, 36)], "#62788a", "#728898")],
                nuvens=[(80, 24, 40, ("#fff0d8", "#f2c0b0", "#b090a8"), 6),
                        (230, 36, 30, ("#fff0d8", "#f0b8a8", "#a88aa4"), 7)],
                sol=(270, 92, 8, "#fff4c8", "#ffd090"), seed=7)
    mata_ciliar(t, 112, 10, VERDES_MATA, seed=3)
    rio(t, 112, ["#c8b8c8", "#8aa8b0", "#5a8a90", "#3e6e74", "#2e5a60"], reflexo_y=10, seed=4)
    for y in range(113, 128):                                  # o sol refletido
        if (y * 7) % 3:
            w = 3 + (y - 113) // 3
            t.hline(268 - w + (y % 2), 268 + w, y, "#f8e0b0" if y < 120 else "#c8d4c8")
    neblina(t, 108, 130, forca=.45, seed=11)

    # barranco de ca: terra em camadas descendo ate a agua, raiz e pedra
    R = rng(41)
    for x in range(0, 106):
        borda = 94 + 3 * math.sin(x / 5.0)
        for y in range(CHAO - 1, H):
            limite = 94 + (y - CHAO) * .45 + 2 * math.sin(y / 4.0)
            if x > limite:
                continue
            camada = (y - CHAO) // 9
            cor = ("#7a5a3a", "#6a4c30", "#5a4028", "#4a3420")[min(camada, 3)]
            if x > limite - 2:
                cor = "#3a2818"                              # beirada molhada
            t.put(x, y, cor)
    for _ in range(60):
        x, y = R.randrange(0, 90), R.randrange(CHAO + 2, H)
        t.put(x, y, R.choice(("#8a6a48", "#4a3420", "#9a8a70")))
    for x, y, r in ((70, 150, 4), (82, 168, 5), (40, 172, 3)):
        t.disco(x, y, r, "#7a7a74", sy=.6)
        t.hline(int(x - r * .6), int(x + r * .3), int(y - r * .4), "#6a8a4a")
    for i in range(6):                                         # raizes saindo do barranco
        x0, y0 = 20 + i * 12, CHAO + 4 + (i % 3) * 5
        traco(t, x0, y0, x0 + 5, y0 + 6, "#3a2818")
    gramado(t, 0, CHAO - 4, 98, CHAO + 1, "#5a8a4a", "#467038", "#7aa860",
            flores=("#f2e6a0", "#ffffff"), seed=8, densidade=.5)
    for x in range(0, 98, 2):                                  # grama caindo na beirada
        t.vline(x, CHAO + 1, CHAO + 1 + R.randint(0, 3), "#467038")
    arvore(t, 34, CHAO - 2, 30, 24, VERDES_MATA, tronco=("#6a5040", "#4a3628", "#8a6a54"), seed=9)
    for x in range(22, 48, 4):
        traco(t, 34, CHAO - 5, x, CHAO, "#5a3a22")

    for x in (100, 146, 192):                                  # trapiche
        t.rect(x, CHAO + 2, 3, H - CHAO - 2, "#3a5048")
        t.vline(x, CHAO + 2, CHAO + 6, "#5a3a22")
    tabuas(t, 88, CHAO - 4, 212, CHAO, ("#c08a58", "#b07c4e", "#c9955f"), "#6b4325", larg=6, seed=12)
    t.hline(88, 211, CHAO - 5, OL)
    t.hline(88, 211, CHAO, "#4a2c1c")
    for x in range(88, 212, 3):
        t.mix(x, CHAO + 5, "#1e3a2e", .5)
    t.rect(206, CHAO - 12, 3, 8, "#7a4c2b")
    passaros(t, [(150, 50), (158, 47), (166, 51)], "#4a4058")
    return t


def rio_de_passagem():
    """O rio aberto enquanto o vo rema: margens longe, neblina indo embora."""
    t = Tela(W, H)
    t.rect(0, 0, W, H, "#2f5538")
    ceu_e_serra(t, CEU_ALVORADA, 98,
                serras=[(90, [(60, 24, 50), (220, 30, 56)], "#8a86b0", "#9c98bc"),
                        (98, [(130, 18, 44), (290, 20, 40)], "#62788a", "#728898")],
                nuvens=[(110, 22, 44, ("#fff0d8", "#f2c0b0", "#b090a8"), 8),
                        (260, 30, 30, ("#fff0d8", "#f0b8a8", "#a88aa4"), 9)],
                sol=(40, 80, 7, "#fff4c8", "#ffd090"), seed=8)
    mata_ciliar(t, 110, 9, VERDES_MATA, seed=6)
    rio(t, 110, ["#c8b8c8", "#8aa8b0", "#5a8a90", "#3e6e74", "#2e5a60"], reflexo_y=10, seed=7)
    neblina(t, 106, 132, forca=.4, seed=12)
    return t


def meio_do_rio():
    """Onde se pesca: o bote parado no meio do rio, ja de manha. Ceu limpo,
    sol, a mata das duas margens, pedras, a garca e as rodinhas na agua a
    direita, onde o neto lanca."""
    t = Tela(W, H)
    t.rect(0, 0, W, H, "#2f5538")
    ceu_e_serra(t, CEU_MANHA, 96,
                serras=[(88, [(80, 26, 56), (240, 30, 56)], "#9ab0c8", "#aac0d4"),
                        (96, [(20, 18, 40), (170, 22, 50), (310, 16, 36)], "#6e9a8a", "#7eaa98")],
                nuvens=[(70, 22, 46, ("#ffffff", "#eef4f8", "#c4d4e2"), 10),
                        (200, 14, 36, ("#ffffff", "#eef4f8", "#c4d4e2"), 11),
                        (290, 34, 28, ("#ffffff", "#eef4f8", "#c4d4e2"), 12)],
                sol=(262, 26, 7, "#fffbe8", "#fff2c0"), seed=9)
    mata_ciliar(t, 106, 10, VERDES_DIA, seed=9)
    rio(t, 106, ["#a8d4d8", "#6ab0bc", "#4a9aa8", "#3a8090", "#2e6878"], reflexo_y=10, seed=10)
    Rb = rng(77)
    for y in range(108, 142):
        for _ in range(3 if y < 120 else 1):
            if Rb.random() < .85 - (y - 108) / 40.0:
                x = int(262 + Rb.gauss(0, 4 + (y - 108) * .5))
                t.hline(x, x + Rb.randint(1, 3), y, "#fff8d8" if y < 118 else "#d8f0f0")
    for cx, cy, r in ((214, 150, 6), (300, 128, 5), (236, 172, 7)):
        t.disco(cx, cy, r, "#7a7e84", sy=.5)
        t.disco(cx - r * .3, cy - 1, r * .55, "#a0a6ac", sy=.45)
        t.hline(int(cx - r * .6), int(cx + r * .2), int(cy - r * .4), "#6a8a4a")
        t.hline(int(cx - r - 2), int(cx + r + 2), int(cy + r * .5), "#c8e8ec")
    gx, gy = 300, 124
    t.vline(gx, gy, gy + 3, "#2b2b30")
    t.disco(gx, gy - 4, 3.0, "#ffffff", sy=1.3)
    escurecer(t, gx + 1, gy - 5, gx + 2, gy - 2, .15)
    traco(t, gx, gy - 7, gx + 2, gy - 13, "#ffffff", 2)
    t.disco(gx + 3, gy - 13, 1.6, "#ffffff")
    traco(t, gx + 4, gy - 13, gx + 8, gy - 12, "#e8c06a")
    for cx, cy in ((250, 140), (268, 152), (244, 162)):
        for raio, cor in ((6.0, "#9ad0d4"), (3.0, "#c8eef0")):
            for ang in range(0, 360, 4):
                if 200 < ang < 340:
                    continue
                a = math.radians(ang)
                t.put(cx + raio * math.cos(a), cy + raio * .32 * math.sin(a), cor)
    passaros(t, [(120, 44), (127, 41), (134, 45)], "#4a5a6a")
    return t


def bote_grande():
    """O bote do vo, de levar os dois. Popa a esquerda (o vo rema), proa a
    direita (o neto lanca). O casco ja vem cortado na linha d'agua: na cena os
    personagens sao desenhados antes e o bote por cima."""
    t = Tela(68, 20)
    X0, X1 = 3, 64
    SHEER = [(0, 5.0), (.12, 6.2), (.5, 6.8), (.84, 6.0), (.95, 4.2), (1, 2.6)]
    FUNDO = [(0, 11.0), (.1, 13.6), (.48, 15.0), (.86, 13.6), (.96, 11.0), (1, 8.0)]
    AGUA = 13

    def linha(pontos, u):
        for i in range(len(pontos) - 1):
            u0, h0 = pontos[i]
            u1, h1 = pontos[i + 1]
            if u0 <= u <= u1:
                f = (u - u0) / max(u1 - u0, 1e-6)
                return h0 + (h1 - h0) * (f * f * (3 - 2 * f))
        return pontos[-1][1]

    for x in range(X0, X1 + 1):
        u = (x - X0) / float(X1 - X0)
        cima, baixo = linha(SHEER, u), linha(FUNDO, u)
        for y in range(int(round(cima)), int(round(baixo)) + 1):
            f = (y - cima) / max(baixo - cima, 0.001)
            t.put(x, y, "#e0aa6a" if f < .16 else ("#94603a" if f < .62 else "#64422a"))
        if x % 4 == 0:
            t.put(x, int(cima) + 3, "#64422a")
    for x in range(X0 + 1, X0 + 9):
        u = (x - X0) / float(X1 - X0)
        t.put(x, int(round(linha(SHEER, u))) + 3, "#e8dcc0")
    for y in range(AGUA + 1, t.h):
        for x in range(t.w):
            t.px[x, y] = (0, 0, 0, 0)
    t.contorno(OL)
    traco(t, 12, 4, 2, 16, "#c9a06a"); traco(t, 13, 4, 3, 16, "#a8743f")
    t.rect(0, 15, 4, 3, "#b38c56")
    for x in range(X0 - 1, X1 + 2):
        if t.get(x, AGUA)[3]:
            t.put(x, AGUA, "#8fb6cf" if (x * 5) % 3 else "#bfe7f7")
    for x, y in ((X1 + 2, AGUA), (X1 + 3, AGUA), (X1 + 4, AGUA + 1), (X0 - 3, AGUA), (X0 - 4, AGUA + 1)):
        t.put(x, y, "#dff2fb")
    return t


# ================================================================== PEIXES
# Os aprovados na primeira rodada; so a joaninha muda (cores vivas e varias
# coloracoes). Exportados em 2x, como os do acude.

from peixes_arte import (perfil, pintar_corpo, crista, rabo, nadadeira, olho, boca,
                         _bagre, sombra_de, OL as OL_PEIXE)


def lambari():
    t = Tela(24, 12)
    x0, cy, L = 5, 6, 17
    cols = perfil(L, costas=[(0, 1.0), (.2, 2.4), (.5, 3.2), (.78, 3.0), (1, 1.4)],
                     barriga=[(0, 0.9), (.22, 2.2), (.5, 3.0), (.8, 2.4), (1, 1.2)])
    rabo(t, x0 - 1, cy, 5, 3.6, "#f2c94c", "#c9a030", fenda=0.6)
    crista(t, x0, cy, cols, .36, .66, 1.6, "#f2c94c", "#c9a030")
    pintar_corpo(t, x0, cy, cols, "#7f9aa8", "#c8d6dc", "#f0f4f4")
    t.rect(x0 + 11, cy - 1, 2, 2, "#2b3440")
    t.put(x0 + 1, cy, "#2b3440"); t.put(x0 + 2, cy, "#2b3440")
    nadadeira(t, [(x0 + 9, cy + 2), (x0 + 6, cy + 5), (x0 + 10, cy + 4)], "#f2c94c")
    olho(t, x0 + 13, cy - 1)
    t.contorno(OL_PEIXE)
    return t


def cara():
    t = Tela(26, 17)
    x0, cy, L = 6, 9, 17
    cols = perfil(L, costas=[(0, 1.4), (.2, 3.8), (.48, 5.2), (.76, 4.6), (1, 1.8)],
                     barriga=[(0, 1.2), (.22, 3.4), (.5, 4.6), (.8, 3.4), (1, 1.4)])
    rabo(t, x0 - 1, cy, 5, 4.4, "#7a8a5a", "#5a6a3a", fenda=0.05)
    crista(t, x0, cy, cols, .06, .84, 3.4, "#8a9a62", "#5a6a3a")
    crista(t, x0, cy, cols, .16, .52, 2.2, "#8a9a62", "#5a6a3a", para_cima=False)
    pintar_corpo(t, x0, cy, cols, "#5a6a42", "#8a9a62", "#c8c89a")
    R = rng(31)
    for _ in range(18):
        x, y = R.randrange(x0 + 2, x0 + L - 3), R.randrange(cy - 3, cy + 3)
        if t.get(x, y)[3]:
            t.put(x, y, "#a8d0c8")
    t.disco(x0 + 9, cy, 1.6, "#2b3420")
    nadadeira(t, [(x0 + 13, cy + 1), (x0 + 9, cy + 5), (x0 + 14, cy + 4)], "#9aaa72")
    olho(t, x0 + 14, cy - 2)
    boca(t, x0 + 16, cy + 1, "#3a4428", 1)
    t.contorno(OL_PEIXE)
    return t


# Coloracoes da joaninha. Na natureza a mesma especie varia muito de cor
# (macho, femea, agua clara ou barrenta); no jogo cada captura sorteia uma.
JOANINHA = {
    "esmeralda": {"dorso": "#1f5a34", "meio": "#3fbf5a", "ventre": "#ff6a2a", "fina": "#ffb02a",
                  "fina_ol": "#c96a10", "faixa": "#123a20", "pintas": None},
    "dourada": {"dorso": "#8a5a10", "meio": "#ffc82a", "ventre": "#fff2a0", "fina": "#ff7a2a",
                "fina_ol": "#c94a10", "faixa": "#6a3a08", "pintas": "#e8282a"},
    "turquesa": {"dorso": "#14406a", "meio": "#2aa8e0", "ventre": "#b8f4f8", "fina": "#ff8a2a",
                 "fina_ol": "#c95a10", "faixa": "#0a2a48", "pintas": "#ffe84a"},
    "rubi": {"dorso": "#6a0f1a", "meio": "#ff3a3a", "ventre": "#ffc08a", "fina": "#ffe04a",
             "fina_ol": "#c9a010", "faixa": "#4a0810", "pintas": "#ffffff"},
}


def joaninha(variante="esmeralda"):
    """Joaninha: comprida e rolica, faixa escura no flanco, risco atras do olho
    e a pinta do rabo com aro claro, em uma de quatro coloracoes vivas."""
    c = JOANINHA[variante]
    t = Tela(32, 11)
    x0, cy, L = 5, 5, 25
    cols = perfil(L, costas=[(0, 1.2), (.14, 2.4), (.5, 3.0), (.82, 2.8), (1, 1.6)],
                     barriga=[(0, 1.0), (.16, 2.0), (.5, 2.6), (.82, 2.4), (1, 1.2)])
    rabo(t, x0 - 1, cy, 4, 3.0, c["fina"], c["fina_ol"], fenda=0.0)
    crista(t, x0, cy, cols, .14, .80, 1.8, c["fina"], c["fina_ol"])
    crista(t, x0, cy, cols, .14, .40, 1.4, c["fina"], c["fina_ol"], para_cima=False)
    # Pintura lisa, sem o pontilhado de transicao do pintar_corpo: num corpo
    # de 5 px de altura o pontilhado vira um ziper e apaga a cor.
    for i, (cima, baixo) in enumerate(cols):
        topo, base = cy - cima, cy + baixo
        for y in range(int(round(topo)), int(round(base)) + 1):
            f = (y - topo) / max(base - topo, .001)
            t.put(x0 + i, y, c["dorso"] if f < .3 else (c["meio"] if f < .62 else c["ventre"]))
    for x in range(x0 + 5, x0 + L - 6):
        if (x - x0) % 5 != 0:
            t.put(x, cy, c["faixa"])
    if c["pintas"]:
        R = rng(len(variante))
        for _ in range(5):
            x, y = R.randrange(x0 + 3, x0 + L - 4), R.choice((cy - 2, cy - 1, cy + 1))
            if t.get(x, y)[3]:
                t.put(x, y, c["pintas"])
    t.disco(x0 + 2, cy - 1, 1.6, "#fff2a0")
    t.put(x0 + 2, cy - 1, "#0a0806"); t.put(x0 + 2, cy, "#0a0806")
    t.hline(x0 + L - 3, x0 + L - 1, cy, "#1a1008")
    nadadeira(t, [(x0 + 18, cy + 1), (x0 + 15, cy + 4), (x0 + 19, cy + 3)], c["fina"])
    olho(t, x0 + L - 4, cy - 2)
    boca(t, x0 + L - 1, cy + 1, "#3a2010", 2)
    t.contorno(OL_PEIXE)
    return t


CICATRIZ = "#e2c8b8"


def corte_do_teimoso(t, x_corte, y_limite):
    """A mordida de traira que o Teimoso sobreviveu: a ponta do lobo de cima do
    rabo arrancada, borda serrilhada e cicatriz clara. O lobo de baixo fica
    inteiro, e e a assimetria que faz a marca se ler de longe. Roda antes do
    contorno, para a borda acompanhar o recorte."""
    arrancados = set()
    for y in range(0, y_limite):
        for x in range(0, x_corte + 1):
            if not t.get(x, y)[3]:
                continue
            if x == x_corte and y % 2 == 0:
                continue
            t.px[x, y] = (0, 0, 0, 0)
            arrancados.add((x, y))
    for x, y in arrancados:
        for dx, dy in ((1, 0), (1, 1), (0, 1)):
            q = (x + dx, y + dy)
            if q not in arrancados and t.get(*q)[3]:
                t.put(*q, CICATRIZ)


def jundia_filhote():
    t = Tela(30, 13)
    _bagre(t, 6, 6, L=20, altura=3.0,
           cores=("#4a463f", "#958879", "#dfd4c2", "#6e655b"), escala=0.85, seed=21)
    corte_do_teimoso(t, x_corte=3, y_limite=5)
    t.contorno(OL_PEIXE)
    return t


def jundia_gigante_teimoso():
    t = Tela(56, 26)
    _bagre(t, 8, 13, L=42, altura=6.6,
           cores=("#272e27", "#55614e", "#a9b08e", "#3c4439"), escala=1.5, musgo=True, seed=13)
    corte_do_teimoso(t, x_corte=5, y_limite=11)
    t.contorno(OL_PEIXE)
    return t


# ============================================================== EXPORTACAO

def salvar(t, nome, escala=4):
    os.makedirs(os.path.dirname(f"{OUT}/{nome}"), exist_ok=True)
    t.salvar(f"{OUT}/{nome}", escala=escala)


if __name__ == "__main__":
    # personagens e bichos em 4x (no interior o Godot dobra com escala 2)
    salvar(neto(), "personagens/neto.png")
    os.makedirs(f"{OUT}/personagens", exist_ok=True)
    for pose, nome in (("sem", "sem_vara"), ("costas", "costas_bambu"), ("mao", "mao_bambu")):
        neto_folha(pose).save(f"{OUT}/personagens/neto_{nome}.png")
    salvar(vo(), "personagens/vo.png")
    salvar(marlene_jovem(), "personagens/marlene_jovem.png")
    salvar(alexandre(), "personagens/alexandre.png")
    salvar(apollo(), "personagens/apollo.png")
    salvar(bote_grande(), "personagens/bote.png")
    for pose in ("sentado", "carinho", "deitado"):
        salvar(maumau(pose), f"bichos/maumau_{pose}.png")
    for pose in ("em_pe", "carinho", "correndo1", "correndo2", "bolinha"):
        salvar(pacoca(pose), f"bichos/pacoca_{pose}.png")
    salvar(bolinha(), "bichos/bolinha.png")
    salvar(coracao(), "bichos/coracao.png")
    # interiores com a camera de perto (8x) e exteriores (4x)
    salvar(quarto(), "cenarios/quarto.png", escala=8)
    salvar(cozinha(), "cenarios/cozinha.png", escala=8)
    for nome, desenhar in (("saida", saida), ("estrada", estrada), ("cais_rio", cais_rio),
                           ("rio_de_passagem", rio_de_passagem), ("meio_do_rio", meio_do_rio)):
        salvar(desenhar(), f"cenarios/{nome}.png")
    salvar(saida(manha=True), "cenarios/saida_manha.png")
    salvar(estrada_longa(), "cenarios/estrada_longa.png")
    salvar(estrada_longa(manha=True), "cenarios/estrada_longa_manha.png")
    for nome, desenhar in CAPAS.items():
        salvar(desenhar(), f"cenarios/poster_{nome}_perto.png", escala=6)
    salvar(camisa_1991(), "cenarios/camisa_1991_perto.png", escala=6)
    for qual in ("alexandre", "apollo"):
        folha_montado(qual).save(f"{OUT}/personagens/{qual}_montado.png")
    salvar(vara_parede(), "cenarios/vara_parede.png")
    peixes = [("lambari", lambari), ("cara", cara), ("jundia_filhote", jundia_filhote),
              ("jundia_gigante_teimoso", jundia_gigante_teimoso)]
    peixes += [(f"joaninha_{v}", lambda v=v: joaninha(v)) for v in JOANINHA]
    for nome, desenhar in peixes:
        p = desenhar()
        salvar(p, f"peixes/{nome}.png", escala=2)
        salvar(sombra_de(p), f"peixes/{nome}_sombra.png", escala=2)
    print("ok")
