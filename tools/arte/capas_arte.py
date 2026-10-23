"""Fase 1, segunda rodada: posteres com cara de capa de disco, a camisa do
Criciuma de 1991 e os cavalos montados que o jogador conduz.

    cd tools/arte
    python capas_arte.py <pasta de saida>

POSTERES. Na parede eles ficam do tamanho de verdade (10x10 px, uns 65 cm),
pequenos demais para ler. Quando o neto examina, entra o poster de perto
(56x56 px, mostrado em 6x), com o titulo legivel numa fonte de 3x5.
Sao homenagens desenhadas, nao copias das capas.

MONTARIA. O cavalo ganha quatro quadros de passo e o cavaleiro vai sentado no
pelego: o neto no Alexandre, o vo no Apollo. Os quadros saem em folha
horizontal, como as do Tiago.
"""
import os
import sys

from px import Tela, rng
from estilo import OL, poligono, traco, escurecer, gradiente

OUT = sys.argv[1] if len(sys.argv) > 1 else "."

# ================================================================== FONTE
# 3x5, so as letras que os posteres usam.
_GLIFOS = {
    "A": ["###", "#.#", "###", "#.#", "#.#"], "B": ["##.", "#.#", "##.", "#.#", "##."],
    "C": ["###", "#..", "#..", "#..", "###"], "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "E": ["###", "#..", "##.", "#..", "###"], "F": ["###", "#..", "##.", "#..", "#.."],
    "G": ["###", "#..", "#.#", "#.#", "###"], "I": ["###", ".#.", ".#.", ".#.", "###"],
    "J": ["..#", "..#", "..#", "#.#", "###"], "L": ["#..", "#..", "#..", "#..", "###"],
    "M": ["#.#", "###", "###", "#.#", "#.#"], "N": ["##.", "#.#", "#.#", "#.#", "#.#"],
    "O": ["###", "#.#", "#.#", "#.#", "###"], "P": ["###", "#.#", "###", "#..", "#.."],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"], "S": ["###", "#..", "###", "..#", "###"],
    "T": ["###", ".#.", ".#.", ".#.", ".#."], "U": ["#.#", "#.#", "#.#", "#.#", "###"],
    "V": ["#.#", "#.#", "#.#", "#.#", ".#."], "Z": ["###", "..#", ".#.", "#..", "###"],
    "&": [".#.", "#.#", ".#.", "#.#", ".##"], "'": [".#.", ".#.", "...", "...", "..."],
    "9": ["###", "#.#", "###", "..#", "###"], "1": [".#.", "##.", ".#.", ".#.", "###"],
    "H": ["#.#", "#.#", "###", "#.#", "#.#"], "K": ["#.#", "#.#", "##.", "#.#", "#.#"],
    "0": ["###", "#.#", "#.#", "#.#", "###"], "2": ["###", "..#", "###", "#..", "###"],
    "3": ["###", "..#", ".##", "..#", "###"], "7": ["###", "..#", ".#.", ".#.", ".#."],
    " ": ["...", "...", "...", "...", "..."],
}


def escrever(t, x, y, texto, cor, sombra=None):
    for ch in texto.upper():
        g = _GLIFOS.get(ch, _GLIFOS[" "])
        for dy, linha in enumerate(g):
            for dx, c in enumerate(linha):
                if c == "#":
                    if sombra:
                        t.put(x + dx + 1, y + dy + 1, sombra)
                    t.put(x + dx, y + dy, cor)
        x += 4
    return x


def largura(texto):
    return len(texto) * 4 - 1


def centralizado(t, cx, y, texto, cor, sombra=None):
    escrever(t, cx - largura(texto) // 2, y, texto, cor, sombra)


def letrinhas(t, x, y, w, linhas, cor, seed, passo=2):
    """Texto miudo que le como impresso sem fingir ser legivel."""
    R = rng(seed)
    for i in range(linhas):
        xx = x
        while xx < x + w:
            n = R.randint(1, 4)
            t.hline(xx, min(x + w - 1, xx + n - 1), y + i * passo, cor)
            xx += n + 1


# ============================================================ GENTE DE CAPA

def _busto(t, cx, topo, pele, sombra_pele, cabelo, roupa, roupa2=None, larg=7,
           chapeu=None, bigode=None, cacheado=False, mullet=False):
    """Busto de frente, para capa de disco: rosto de larg px e ombros."""
    meia = larg // 2
    alto = larg + 2
    x0 = cx - meia
    # ombros e roupa
    poligono(t, [(cx - meia - 5, topo + alto + 9), (cx - meia - 3, topo + alto + 2), (cx + meia + 4, topo + alto + 2),
                 (cx + meia + 6, topo + alto + 9)], roupa)
    if roupa2:
        poligono(t, [(cx - 1, topo + alto + 1), (cx + 2, topo + alto + 1), (cx + 1, topo + alto + 7)], roupa2)
    # pescoco
    t.rect(cx - 1, topo + alto - 1, 3, 3, sombra_pele)
    # rosto
    t.rect(x0, topo + 1, larg, alto - 1, pele)
    t.disco(cx + .5, topo + alto - 2, meia + .3, pele, sy=.7)
    t.vline(x0 + larg - 1, topo + 3, topo + alto - 2, sombra_pele)
    t.hline(x0 + 1, x0 + larg - 2, topo + alto, sombra_pele)
    # olhos, sobrancelha, nariz, boca
    t.put(cx - 2, topo + 4, "#2a1a14"); t.put(cx + 2, topo + 4, "#2a1a14")
    t.put(cx - 2, topo + 3, cabelo); t.put(cx + 2, topo + 3, cabelo)
    t.put(cx, topo + 6, sombra_pele)
    t.hline(cx - 1, cx + 1, topo + 8, "#9a5a4a")
    if bigode:
        t.hline(cx - 2, cx + 2, topo + 7, bigode)
    # cabelo
    t.hline(x0, x0 + larg - 1, topo, cabelo)
    t.hline(x0 + 1, x0 + larg - 2, topo - 1, cabelo)
    t.vline(x0, topo, topo + 3, cabelo)
    t.vline(x0 + larg - 1, topo, topo + 2, cabelo)
    if cacheado:
        for dx in range(-1, larg + 1, 2):
            t.put(x0 + dx, topo - 2, cabelo)
        t.vline(x0 - 1, topo - 1, topo + 3, cabelo)
        t.vline(x0 + larg, topo - 1, topo + 3, cabelo)
    if mullet:
        t.rect(x0 - 1, topo, 2, alto + 1, cabelo)
        t.rect(x0 + larg - 1, topo, 2, alto + 1, cabelo)
    if chapeu:
        claro, escuro = chapeu
        t.hline(x0 - 3, x0 + larg + 2, topo, claro)
        t.hline(x0 - 2, x0 + larg + 1, topo + 1, escuro)
        t.rect(x0, topo - 4, larg, 4, claro)
        t.hline(x0, x0 + larg - 1, topo - 1, escuro)
        t.put(x0 + meia, topo - 4, escuro)


def _de_pe(t, x, chao, pele, cabelo, camisa, calca, colete=None):
    """Figura de pe de corpo inteiro (12 px de altura de rosto ate a bota)."""
    alto = 26
    topo = chao - alto
    t.rect(x + 1, topo, 4, 4, pele)
    t.hline(x + 1, x + 4, topo - 1, cabelo)
    t.put(x + 1, topo, cabelo); t.put(x + 4, topo, cabelo)
    t.put(x + 2, topo + 2, "#2a1a14"); t.put(x + 4, topo + 2, "#2a1a14")
    t.rect(x, topo + 5, 6, 8, camisa)
    if colete:
        t.rect(x, topo + 5, 2, 8, colete); t.rect(x + 4, topo + 5, 2, 8, colete)
    t.vline(x - 1, topo + 5, topo + 11, camisa); t.vline(x + 6, topo + 5, topo + 11, camisa)
    t.put(x - 1, topo + 12, pele); t.put(x + 6, topo + 12, pele)
    t.rect(x, topo + 13, 6, 1, "#3a2615")
    t.rect(x, topo + 14, 2, 11, calca); t.rect(x + 4, topo + 14, 2, 11, calca)
    t.rect(x + 2, topo + 14, 2, 3, calca)
    t.rect(x - 1, chao - 1, 3, 1, "#2a1a10"); t.rect(x + 4, chao - 1, 3, 1, "#2a1a10")


# ================================================================== CAPAS
P = 56   # lado do poster de perto


def capa_racionais():
    """Sobrevivendo no Inferno (1997): fundo preto, a cruz dourada no meio,
    o nome em vermelho em cima, o titulo em branco embaixo e o versiculo do
    Salmo 23 miudinho ao lado da cruz. Era do pai."""
    t = Tela(P, P, "#0b0a0a")
    R = rng(23)
    for _ in range(90):                       # grao de papel velho
        t.mix(R.randrange(P), R.randrange(P), "#3a3430", .5)
    centralizado(t, P // 2, 4, "RACIONAIS MC'S", "#c8201e")
    # cruz dourada com brilho e sombra
    cx, topo, base, braco_y = 27, 13, 44, 20
    ouro, ouro_claro, ouro_escuro = "#c9962e", "#f2d06a", "#7a5418"
    t.rect(cx - 2, topo, 5, base - topo, ouro)
    t.rect(cx - 10, braco_y, 21, 5, ouro)
    t.vline(cx - 2, topo, base - 1, ouro_claro)
    t.hline(cx - 10, cx + 10, braco_y, ouro_claro)
    t.vline(cx + 2, braco_y + 5, base - 1, ouro_escuro)
    t.hline(cx - 10, cx - 3, braco_y + 4, ouro_escuro)
    t.hline(cx + 3, cx + 10, braco_y + 4, ouro_escuro)
    for x, y in ((cx - 1, topo + 2), (cx - 8, braco_y + 1), (cx + 1, base - 6)):
        t.put(x, y, "#fff2b0")
    # versiculo em branco miudo
    letrinhas(t, 34, 30, 18, 5, "#d8d4cc", 3)
    centralizado(t, P // 2, 44, "SOBREVIVENDO", "#f0ece4")
    centralizado(t, P // 2, 50, "NO INFERNO", "#f0ece4")
    return t


def capa_djavan():
    """Grandes Sucessos (1982, reeditado em CD em 96): fundo de reboco
    salmao, o Djavan de frente ocupando a metade de baixo, o nome em branco
    em cima com a marca de batom rosa ao lado."""
    t = Tela(P, P)
    gradiente(t, 0, 0, P, P, ["#e89a7a", "#d8806a", "#c86a58", "#b8604e"])
    R = rng(7)
    for _ in range(220):                      # textura de reboco
        x, y = R.randrange(P), R.randrange(P)
        t.mix(x, y, "#f4c0a0" if R.random() < .5 else "#8a4a3a", .35)
    # batom rosa
    t.disco(8, 8, 4, "#e85a9a", sy=.55)
    t.hline(5, 11, 8, "#b83a72")
    escrever(t, 14, 6, "DJAVAN", "#fbf4ee", "#8a4a3a")
    letrinhas(t, 14, 13, 30, 2, "#fbf4ee", 4)
    # o retrato: cabelo curto e crespo, camisa escura, luz de lado
    _busto(t, 33, 24, "#8a5436", "#6a3c26", "#1a1210", "#1c1a1e", larg=13, cacheado=True)
    for y in range(24, 37):
        t.mix(27, y, "#f4c0a0", .25)
    return t


def capa_zeze():
    """Zeze Di Camargo & Luciano, disco de 96: os dois de pe, de jeans,
    num chao de terra vermelha com o ceu de por do sol; o nome em cima a
    direita, branco com o "&" vermelho."""
    t = Tela(P, P)
    gradiente(t, 0, 0, P, 38, ["#f2c48a", "#e8905a", "#c8583a", "#9a3a2a"])
    gradiente(t, 0, 38, P, P, ["#b0482e", "#8a3424", "#6a2a1e"])
    poligono(t, [(0, 38), (12, 33), (24, 36), (40, 31), (56, 35), (56, 39), (0, 39)], "#7a3424")
    escrever(t, 22, 3, "ZEZE DI", "#fbf4ee", "#6a2a1e")
    escrever(t, 22, 9, "CAMARGO", "#fbf4ee", "#6a2a1e")
    escrever(t, 22, 15, "&", "#c8201e")
    escrever(t, 27, 15, "LUCIANO", "#fbf4ee", "#6a2a1e")
    _de_pe(t, 12, 52, "#e3a87d", "#3a2418", "#f4f1ea", "#f4f1ea", colete="#4a4a5a")
    _de_pe(t, 24, 52, "#d99a70", "#1a1210", "#2a2a3a", "#1c2a4a")
    for x in range(10, 32):
        t.mix(x, 52, "#2a0e0a", .4)
    return t


def capa_leonardo():
    """Leandro & Leonardo: os dois rostos lado a lado num fundo dourado de
    estudio, o Leandro de chapeu branco, o nome em cima. (Em 97 o Leonardo
    ainda cantava com o irmao.)"""
    t = Tela(P, P)
    gradiente(t, 0, 0, P, P, ["#f2d8a0", "#d8b070", "#a87840", "#6a4420"])
    centralizado(t, P // 2, 4, "LEANDRO", "#4a2a14")
    centralizado(t, P // 2, 10, "& LEONARDO", "#4a2a14")
    _busto(t, 18, 26, "#e8b48a", "#c88e66", "#3a2418", "#f4f1ea", "#c9a030", larg=11,
           chapeu=("#f8f4ec", "#c8c0b0"))
    _busto(t, 38, 27, "#e3a87d", "#c4825c", "#1a1210", "#2a3a5a", larg=11, mullet=True)
    return t


def poster_criciuma_perto():
    """O Criciuma campeao da Copa do Brasil de 91: elenco em duas fileiras
    com a camisa amarela de listras, o trofeu no gramado na frente."""
    t = Tela(P, P)
    gradiente(t, 0, 0, P, 30, ["#7ab0d8", "#a8cce6", "#d8e6ee"])
    t.rect(0, 22, P, 34, "#4f8a45")
    for y in range(22, P, 3):
        t.hline(0, P - 1, y, "#5a9a50")
    t.rect(0, 0, P, 11, "#111111")
    centralizado(t, P // 2, 3, "CRICIUMA 1991", "#f2c94c")
    for fileira, (y, n, x0) in enumerate(((19, 7, 4), (29, 6, 8))):
        for i in range(n):
            x = x0 + i * 7
            pele = ("#e3a87d", "#c4825c", "#8a5436")[(i + fileira) % 3]
            t.rect(x + 1, y, 3, 3, pele)
            t.hline(x + 1, x + 3, y - 1, "#2a1a14")
            t.rect(x, y + 3, 5, 5, "#f2c94c")
            for xx in (x + 1, x + 3):
                t.vline(xx, y + 3, y + 7, "#111111")
            t.put(x + 2, y + 3, "#f4f1ea")
            t.rect(x, y + 8, 5, 2, "#111111")
    # trofeu
    t.rect(26, 45, 5, 4, "#e2b655"); t.rect(27, 49, 3, 2, "#c9962e"); t.rect(25, 51, 7, 2, "#7a5418")
    t.put(25, 46, "#e2b655"); t.put(31, 46, "#e2b655"); t.put(27, 45, "#fff2b0")
    return t


def camisa_1991(perto=True):
    """A camisa titular de 1991: amarela com listras pretas finas e um
    filete branco entre elas, gola em V preta com debrum branco, o escudo do
    lado do coracao e a faixa do patrocinio no peito. Pendurada no cabide."""
    if not perto:
        return None
    t = Tela(P, P)
    amarelo, preto, branco = "#f2c94c", "#141414", "#f4f1ea"
    cx = 28
    # cabide e prego
    t.put(cx, 3, "#9aa3ab"); t.put(cx, 4, "#5a3a22")
    traco(t, cx - 14, 10, cx, 5, "#6b4325", 2); traco(t, cx, 5, cx + 14, 10, "#6b4325", 2)
    corpo = [(cx - 12, 10), (cx - 24, 22), (cx - 18, 28), (cx - 13, 24), (cx - 13, 52),
             (cx + 13, 52), (cx + 13, 24), (cx + 18, 28), (cx + 24, 22), (cx + 12, 10)]
    poligono(t, corpo, amarelo)
    # listras: preta de 2 px, filete branco no meio do amarelo
    for x in range(cx - 24, cx + 25):
        fase = (x - cx) % 8
        for y in range(8, 53):
            if t.get(x, y)[:3] == (0xf2, 0xc9, 0x4c):
                if fase in (0, 1):
                    t.put(x, y, preto)
                elif fase == 4:
                    t.put(x, y, branco)
    # punhos pretos
    traco(t, cx - 24, 22, cx - 18, 28, preto, 2)
    traco(t, cx + 24, 22, cx + 18, 28, preto, 2)
    # gola em V
    poligono(t, [(cx - 6, 9), (cx + 6, 9), (cx, 18)], preto)
    poligono(t, [(cx - 4, 9), (cx + 4, 9), (cx, 15)], "#3a2a1a")
    traco(t, cx - 6, 9, cx, 18, branco); traco(t, cx + 6, 9, cx, 18, branco)
    # escudo (lado esquerdo do peito de quem veste = direita na tela)
    t.rect(cx + 5, 20, 6, 7, branco)
    t.rect(cx + 6, 21, 4, 4, amarelo)
    t.hline(cx + 6, cx + 9, 21, preto)
    t.put(cx + 7, 25, preto); t.put(cx + 8, 26, branco)
    # marca do fornecedor do outro lado
    t.rect(cx - 10, 21, 3, 2, preto)
    # faixa do patrocinio
    t.rect(cx - 12, 31, 25, 7, branco)
    escrever(t, cx - 11, 32, "ELIANE", preto)
    # sombra do lado de fora e da barra
    for y in range(10, 53):
        for x in range(cx + 9, cx + 14):
            t.mix(x, y, "#1a1020", .12)
    escurecer(t, cx - 13, 51, cx + 13, 52, .3)
    t.contorno(OL)
    return t


# ---------------------------------------------- versoes de parede (10x10)

def miniatura(capa, lado=10):
    """Reduz a capa para a parede pela media de cada bloco: le como a mesma
    capa de longe, que e o que importa ali."""
    from PIL import Image
    pequena = capa.im.convert("RGB").resize((lado, lado), Image.BOX)
    t = Tela(lado, lado)
    t.im.paste(pequena.convert("RGBA"))
    t.px = t.im.load()
    return t


# =============================================================== MONTARIA

PELE = {"s": "#f7cba2", "S": "#e3a87d", "z": "#c4825c", "m": "#ee9a82"}

TRONCO_NETO = [
    ".....OOOOO......", "....OCCCCCO.....", "...OCcCCCCCO....", "...OccSSSSSO....",
    "...OcCsssOsO....", "...OcSsssOssO...", "....OzssmsO.....", ".....OEzzEO.....",
    "....OeeeeeEO....", "....OeeeeEEO....", "....OeeeEEfO....", "....ObbbbbnO....",
]
PAL_NETO = {"O": OL, "c": "#5a3420", "C": "#7d4c2b", "e": "#7cc45e", "E": "#5aa046", "f": "#3f7d33",
            "b": "#4f86c6", "B": "#3a6aa8", "n": "#2b4f80", "g": "#f2c94c", "G": "#c9a030", **PELE}

TRONCO_VO = [
    ".....OOOO.......", "....OhhhhO......", "...OhhhhHHO.....", "...ORrrrrRO.....",
    ".OHhhhhhhhhhhO..", "..OOkkkkkkkOO...", "...OYYSSSSSO....", "...OYysssOsO....",
    "...OYSsssOssO...", "...OyyyyyysO....", "....OYyyyYO.....", ".....OxyyxO.....",
    "....OxXxXxXO....", "...OxXxXxXxXO...", "...OXxXxXxXxO...", "...OxXxXxXxXO...",
    "...OXxXxXxXnO...", "....OLLLgLLO....",
]
PAL_VO = {"O": OL, "h": "#f6d77c", "H": "#e2b655", "k": "#b8893a", "r": "#c0452f", "R": "#8a2c22",
          "s": "#e8b48a", "S": "#cf9268", "z": "#a8704c", "m": "#c9806a",
          "y": "#e4e2dc", "Y": "#b8b5ae", "x": "#b8433a", "X": "#7a2a26", "n": "#5a1e1c",
          "j": "#41557a", "J": "#2f3f5c", "L": "#5a3a22", "g": "#d9c27a"}

# deslocamento do casco por quadro: (traseira perto, dianteira perto,
# traseira longe, dianteira longe). Passo de quatro tempos do cavalo.
PASSADA = [(0, 0, 0, 0), (2, -2, -2, 2), (0, 0, 0, 0), (-2, 2, 2, -2)]


def cavalo_montado(pelagem, sombra, crina, manchas=None, comp=22, perna=10, seed=1,
                   quadro=0, cavaleiro=None):
    """Cavalo de lado andando para a direita, com o cavaleiro no pelego.
    Mesmo desenho do cavalo parado do tutorial, com as pernas em passada e o
    corpo subindo um pixel nos quadros de apoio."""
    t = Tela(comp + 20, perna + 23 + 22)
    g = t.h - 1
    sobe = 1 if quadro in (1, 3) else 0
    barriga = g - perna - sobe
    lombo = barriga - 9
    x0, x1 = 6, 6 + comp
    casco = "#2b1d12"
    tp, dp, tl, dl = PASSADA[quadro]
    for perto in (False, True):
        cor = pelagem if perto else sombra
        xt = x0 + (6 if perto else 3)
        xd = x1 - (3 if perto else 6)
        mt, md = (tp, dp) if perto else (tl, dl)
        alto = g - 1 - (barriga - 3)
        for i, y in enumerate(range(barriga - 3, g - 1)):
            f = i / max(alto - 1, 1)
            jarrete = -1 if y > barriga + perna * 0.45 else 0
            ot = round(mt * f) + jarrete
            od = round(md * f)
            t.put(xt + ot, y, cor); t.put(xt + 1 + ot, y, cor)
            t.put(xd + od, y, cor); t.put(xd + 1 + od, y, cor)
        t.rect(xt - 1 + mt, g - 1, 3, 2, casco)
        t.rect(xd + md, g - 1, 3, 2, casco)
    t.rect(x0 + 3, lombo + 1, comp - 6, 8, pelagem)
    t.disco(x0 + 4, lombo + 4.5, 4.6, pelagem)
    t.disco(x1 - 4, lombo + 4.5, 4.6, pelagem)
    t.disco(x1 - 7, lombo + 0.5, 2.2, pelagem)
    t.disco(x0 + 5, lombo + 1.5, 3.4, pelagem)
    cab = 1 if quadro in (1, 3) else 0          # a cabeca balanca no passo
    poligono(t, [(x1 - 9, lombo + 1), (x1 + 2, lombo - 8 + cab), (x1 + 6, lombo - 5 + cab), (x1 - 1, lombo + 7)], pelagem)
    poligono(t, [(x1 + 1, lombo - 9 + cab), (x1 + 5, lombo - 10 + cab), (x1 + 12, lombo - 5 + cab),
                 (x1 + 12, lombo - 2 + cab), (x1 + 7, lombo - 2 + cab), (x1 + 3, lombo - 4 + cab)], pelagem)
    poligono(t, [(x1 + 2, lombo - 9 + cab), (x1 + 3, lombo - 12 + cab), (x1 + 5, lombo - 9 + cab)], pelagem)
    for x in range(x0 + 3, x1 - 2):
        t.put(x, barriga - 1, sombra)
    if manchas:
        R = rng(seed)
        for _ in range(5):
            mx, my = R.uniform(x0 + 2, x1 - 2), R.uniform(0, 1)
            r = R.uniform(2.2, 3.8)
            my = lombo + 1 + my * (barriga - 3 - lombo)
            for y in range(int(my - r), int(my + r) + 1):
                for x in range(int(mx - r), int(mx + r) + 1):
                    if ((x - mx) / r) ** 2 + ((y - my) / (r * .8)) ** 2 <= 1 and \
                            t.get(x, y)[:3] in (_rgb(pelagem), _rgb(sombra)):
                        t.put(x, y, manchas)
        t.disco(x1 + 8, lombo - 5 + cab, 1.8, manchas)
    for i in range(11):
        f = i / 10.0
        x, y = x1 + 2 - f * 10, lombo - 8 + cab + f * 9
        t.put(x, y, crina); t.put(x - 1, y, crina)
    t.put(x1 + 6, lombo - 7 + cab, "#1d1208")
    t.put(x1 + 11, lombo - 3 + cab, "#1d1208")
    balanco = (0, 1, 0, -1)[quadro]
    pontos = [(x0 + 1, lombo + 1), (x0 - 2, lombo + 4), (x0 - 3 + balanco, lombo + 8), (x0 - 2 + balanco, lombo + 12)]
    for (a, b), (c, d) in zip(pontos, pontos[1:]):
        traco(t, a, b, c, d, crina, grossura=2.4)
    meio = x1 - 11
    t.rect(meio - 5, lombo + 1, 11, 4, "#7a2a26")
    for y in range(lombo - 1, lombo + 3):
        for x in range(meio - 4, meio + 5):
            t.put(x, y, "#f2ede2" if (x + y) % 3 else "#d8d0c0")
    t.contorno(OL)

    if cavaleiro:
        tronco, pal, calca, bota, mao = cavaleiro
        alto = len(tronco)
        cx = meio - 7
        topo = lombo - alto + 1
        # perna de fora: coxa sobre o pelego, canela descendo pelo flanco
        cav = Tela(t.w, t.h)
        cav.mapa(cx, topo, tronco, pal)
        cav.rect(meio - 2, lombo - 1, 5, 2, calca)
        cav.rect(meio + 1, lombo + 1, 2, 5, calca)
        cav.rect(meio + 1, lombo + 6, 3, 2, bota)
        # braco segurando a redea
        cav.rect(cx + 7, topo + alto - 4, 2, 2, pal["S"])
        cav.put(cx + 9, topo + alto - 3, mao)
        cav.contorno(OL)
        t.colar(cav, 0, 0)
        # redea da mao ate a boca
        traco(t, cx + 10, topo + alto - 3, x1 + 9, lombo - 3 + cab, "#3a2615")
    else:
        traco(t, x1 + 9, lombo - 3 + cab, x1 - 9, lombo + 0, "#3a2615")
    return t


def _rgb(c):
    from px import hx
    return hx(c)[:3]


def montado(qual, quadro):
    if qual == "alexandre":
        cav = (TRONCO_NETO, PAL_NETO, "#3a6aa8", "#c9a030", "#e3a87d")
        return cavalo_montado("#f2ede2", "#cfc6b4", "#5a3a22", manchas="#8a5a33", comp=18, perna=10,
                              seed=4, quadro=quadro, cavaleiro=cav)
    cav = (TRONCO_VO, PAL_VO, "#41557a", "#5a3a22", "#cf9268")
    return cavalo_montado("#5a3420", "#3f2416", "#1d1208", comp=24, perna=13, quadro=quadro, cavaleiro=cav)


def folha_montado(qual, escala=4):
    from PIL import Image
    quadros = [montado(qual, q) for q in range(4)]
    w, h = quadros[0].w * escala, quadros[0].h * escala
    folha = Image.new("RGBA", (w * 4, h), (0, 0, 0, 0))
    for i, q in enumerate(quadros):
        folha.alpha_composite(q.im.resize((w, h), Image.NEAREST), (w * i, 0))
    return folha


def salvar(t, nome, escala=4):
    os.makedirs(os.path.dirname(f"{OUT}/{nome}"), exist_ok=True)
    t.salvar(f"{OUT}/{nome}", escala=escala)


def _bracos_pra_cima(t, cx, ombro_y, pele, manga, abertura=9, alto=13):
    """Os dois bracos levantados em V, comemorando: manga curta e antebraco."""
    for lado in (-1, 1):
        x0 = cx + lado * 6
        x1 = cx + lado * (6 + abertura)
        traco(t, x0, ombro_y, x0 + (x1 - x0) * .35, ombro_y - alto * .35, manga, 3)
        traco(t, x0 + (x1 - x0) * .35, ombro_y - alto * .35, x1, ombro_y - alto, pele, 2.4)
        t.disco(x1, ombro_y - alto - 1, 1.6, pele)


def capa_pele():
    """Pele, o Rei, na Copa de 70: camisa amarela de gola verde, os bracos
    pra cima no grito de gol, o gramado embaixo e o ceu do Mexico atras."""
    t = Tela(P, P)
    gradiente(t, 0, 0, P, 40, ["#3a7ac8", "#6aa0d8", "#a8c8e6", "#e6eef2"])
    t.rect(0, 40, P, 16, "#3f8a3a")
    for y in range(40, P, 2):
        t.hline(0, P - 1, y, "#4a9a44")
    # arquibancada borrada la atras
    R = rng(70)
    for x in range(P):
        for y in range(33, 40):
            t.put(x, y, ("#8a8a9a", "#c8b070", "#a86a5a", "#e6e2d8")[R.randrange(4)])
    cx, topo = 28, 16
    _bracos_pra_cima(t, cx, topo + 13, "#5a3622", "#f2c94c")
    _busto(t, cx, topo, "#6a4028", "#4a2a18", "#141010", "#f2c94c", None, larg=11)
    # gola verde em V e o 10 nao aparece de frente: o escudo da CBD no peito
    t.hline(cx - 3, cx + 3, topo + 13, "#2f8a3a")
    t.put(cx - 1, topo + 14, "#2f8a3a"); t.put(cx + 1, topo + 14, "#2f8a3a"); t.put(cx, topo + 15, "#2f8a3a")
    t.rect(cx + 4, topo + 16, 3, 3, "#2a5ab0"); t.put(cx + 5, topo + 17, "#f2c94c")
    # a boca aberta no grito
    t.rect(cx - 1, topo + 7, 3, 2, "#2a0e0a")
    t.hline(cx - 1, cx + 1, topo + 8, "#2a0e0a")
    t.rect(0, 0, P, 9, "#f2c94c")
    centralizado(t, P // 2, 2, "PELE  O REI", "#1f6a2a")
    t.put(20, 1, "#1f6a2a"); t.put(21, 0, "#1f6a2a")   # o acento do E
    escrever(t, 2, 49, "1970", "#f4f1ea", "#1f4a1a")
    return t


def capa_lebron():
    """LeBron James aos 17, na capa de revista de 2002 que chamava ele de
    "The Chosen One": camiseta verde e dourada do colegio, o 23, a faixa na
    cabeca e a bola laranja, num fundo escuro de ginasio com holofote."""
    t = Tela(P, P, "#141822")
    for y in range(P):
        for x in range(P):
            d = ((x - 28) ** 2 + (y - 26) ** 2) ** .5
            if d < 26:
                t.mix(x, y, "#3a4a6a", .55 * (1 - d / 26))
    cx, topo = 26, 15
    _busto(t, cx, topo, "#7a4a2c", "#5a3420", "#120e0c", "#1f6a3a", None, larg=11)
    # regata: cava funda, ombros de fora, debrum dourado
    for lado in (-1, 1):
        poligono(t, [(cx + lado * 6, topo + 13), (cx + lado * 11, topo + 14), (cx + lado * 11, topo + 22),
                     (cx + lado * 7, topo + 22)], "#7a4a2c")
    t.hline(cx - 6, cx + 6, topo + 13, "#e8c04a")
    escrever(t, cx - 3, topo + 16, "23", "#e8c04a", "#0e3a1e")
    # faixa branca na testa e o cavanhaque ralinho
    t.hline(cx - 5, cx + 5, topo + 1, "#f4f1ea")
    t.put(cx, topo + 9, "#2a1a10")
    # a bola na mao, do lado
    t.disco(cx + 15, topo + 20, 5.2, "#e07a2a")
    traco(t, cx + 10, topo + 20, cx + 20, topo + 20, "#6a2a0a")
    traco(t, cx + 15, topo + 15, cx + 15, topo + 25, "#6a2a0a")
    t.rect(cx + 9, topo + 21, 3, 3, "#7a4a2c")
    centralizado(t, P // 2, 3, "LEBRON JAMES", "#f4f1ea", "#000000")
    centralizado(t, P // 2, 46, "CHOSEN ONE", "#e8c04a", "#000000")
    return t


CAPAS = {"racionais": capa_racionais, "djavan": capa_djavan, "zeze": capa_zeze,
         "leonardo": capa_leonardo, "criciuma": poster_criciuma_perto,
         "pele": capa_pele, "lebron": capa_lebron}

if __name__ == "__main__":
    for nome, desenhar in CAPAS.items():
        capa = desenhar()
        salvar(capa, f"cenarios/poster_{nome}_perto.png", escala=6)
    salvar(camisa_1991(), "cenarios/camisa_1991_perto.png", escala=6)
    os.makedirs(f"{OUT}/personagens", exist_ok=True)
    for qual in ("alexandre", "apollo"):
        folha_montado(qual).save(f"{OUT}/personagens/{qual}_montado.png")
    print("ok")
