"""Cenarios dos dois pesqueiros rio abaixo (1/4 da resolucao, exportados em 4x).

Usam a mesma montagem do acude, em faixas: ceu (320x120), agua (320x63),
barranco (80x92) e estrutura (80x76), com o piso da estrutura na linha 44.

    cd tools/arte
    python pesqueiros_arte.py ../../assets/sprites

- Foz e Vila: onde o rio encontra o mar. Areia e pedra no lugar da terra
  vermelha, a vila de pescadores na outra margem e o mar aberto ao fundo.
  Agua salobra, mais azul que a do acude e sem aguape.
- Arvoredo: mar aberto, as ilhas do caderno do avo com o farol, e uma laje
  de granito no lugar do trapiche.

Os pedacos que ja existem (costao e mar do cais, trapiche do acude) sao
reaproveitados: o costao e o mar saem do cais, o trapiche sai do acude.
"""
import math
import os
import shutil
import sys

from PIL import Image

from px import Tela, faixas, rng, hx, gaivota
import acude_arte as acude

RAIZ = sys.argv[1] if len(sys.argv) > 1 else "."
SPRITES = os.path.dirname(os.path.abspath(__file__)) + "/../../assets/sprites"


def _pasta(nome):
    caminho = os.path.join(RAIZ, nome)
    os.makedirs(caminho, exist_ok=True)
    return caminho


def _recolorir(origem, destino, troca):
    """Troca cores de um PNG pronto pela cor mais proxima de cada par."""
    im = Image.open(origem).convert("RGBA")
    px = im.load()
    pares = [(hx(a)[:3], hx(b)) for a, b in troca]
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            for (cr, cg, cb), nova in pares:
                if abs(r - cr) + abs(g - cg) + abs(b - cb) < 40:
                    px[x, y] = nova[:3] + (a,)
                    break
    im.save(destino)


def _ceu_base(t, sol=(70, 26)):
    faixas(t, 0, 0, 320, [("#3a7cc4", 14), ("#4588cc", 12), ("#5194d5", 11), ("#5ea2dd", 10),
                          ("#6eb0e4", 9), ("#7ebde9", 8), ("#90c8ee", 8), ("#a3d3f1", 7),
                          ("#b6ddf4", 6), ("#c8e6f6", 6), ("#d9eef6", 6), ("#e8f4f4", 23)],
           dither=False)
    sx, sy = sol
    for y in range(sy - 13, sy + 14):
        for x in range(sx - 13, sx + 14):
            d = math.hypot(x + .5 - sx, y + .5 - sy)
            if d < 5.0: t.put(x, y, "#fffbe8")
            elif d < 7.0: t.put(x, y, "#fff0b0")
            elif d < 8.5: t.put(x, y, "#ffe07a")
            elif d < 11: t.mix(x, y, "#fff6d8", 0.45)
            elif d < 13: t.mix(x, y, "#fff6d8", 0.18)


# =============================================================== FOZ E VILA

def _casinha(t, x, base, w, h, parede, telhado, R):
    t.rect(x, base - h, w, h, parede)
    t.vline(x, base - h, base - 1, "#00000022")
    for i in range(3):  # telhado de duas aguas
        t.hline(x - 1 + i, x + w - i, base - h - 1 - i, telhado)
    if R.random() < 0.8:
        t.put(x + 1 + R.randrange(max(1, w - 3)), base - h + 2, "#3a4a5a")
    t.vline(x + w // 2, base - 3, base - 1, "#6b4a2e")


def ceu_foz():
    t = Tela(320, 120)
    _ceu_base(t, sol=(64, 24))
    for cx, cy, w, r in ((140, 22, 30, 5.5), (210, 14, 24, 4.5), (260, 44, 34, 5.5),
                         (30, 56, 22, 4.0), (180, 66, 18, 3.5)):
        acude.nuvem(t, cx, cy, w, r)
    for x, y in ((120, 40), (128, 37), (236, 30), (243, 28)):
        gaivota(t, x, y)

    xs = range(320)
    # morro da costa a esquerda, azulado pela distancia
    far = acude.morro(xs, [(20, 88, 40), (90, 96, 34), (150, 104, 22)], 117)
    for x in xs:
        topo = int(far[x])
        for y in range(topo, 117):
            t.put(x, y, "#8fb3ae" if y == topo else ("#7fa69f" if y - topo < 6 else "#729a93"))
    # o mar aberto, a direita, depois da barra do rio
    for y in range(103, 117):
        cor = "#5d93b8" if y < 106 else ("#6aa1c2" if y < 110 else "#7bb0cb")
        t.hline(196, 319, y, cor)
    t.hline(196, 319, 103, "#4a7fa6")
    R = rng(17)
    for _ in range(18):
        x, y = R.randrange(200, 318), R.randrange(105, 116)
        t.hline(x, x + R.randint(2, 4), y, "#a9d1e2")
    # barco de pesca ao longe
    t.hline(262, 270, 104, "#f1ead6"); t.hline(263, 269, 105, "#c0503a"); t.vline(266, 98, 103, "#6b4a2e")

    # a vila de pescadores na outra margem
    t.rect(0, 112, 230, 5, "#d8c79a")      # praia
    t.hline(0, 229, 111, "#e8dbb2")
    R = rng(23)
    cores = [("#f1ead6", "#b4503a"), ("#e9c46a", "#8a4a2e"), ("#9fc5d6", "#b4503a"),
             ("#f2a7a0", "#7a4a2e"), ("#ffffff", "#4f6f8a"), ("#b9d6a3", "#a8452f")]
    x = 30
    while x < 196:
        parede, telhado = R.choice(cores)
        w = R.randint(6, 9)
        _casinha(t, x, 111, w, R.randint(5, 7), parede, telhado, R)
        x += w + R.randint(2, 5)
    # igrejinha com a torre
    t.rect(120, 100, 6, 11, "#f6f2e4"); t.hline(119, 126, 99, "#b4503a")
    t.vline(122, 94, 98, "#f6f2e4"); t.vline(123, 94, 98, "#e4dece"); t.put(122, 92, "#6b4a2e"); t.put(122, 93, "#6b4a2e")
    # canoas puxadas na areia e as varas de secar rede
    for cx in (52, 96, 160, 188):
        t.hline(cx, cx + 6, 114, "#2f6b8a"); t.hline(cx + 1, cx + 5, 115, "#24546c")
    for cx in (70, 140):
        t.vline(cx, 106, 113, "#6b4a2e"); t.vline(cx + 8, 106, 113, "#6b4a2e")
        for k in range(1, 8):
            t.put(cx + k, 107 + (k % 2), "#8fa3a8")
    # coqueiros e a vegetacao de restinga
    for x0 in (14, 210, 226):
        t.vline(x0, 100, 111, "#7a5a32")
        for dx, dy in ((-3, 0), (-2, -1), (2, -1), (3, 0), (-4, 1), (4, 1), (0, -1)):
            t.put(x0 + dx, 99 + dy, "#3f7d4e")
        t.put(x0, 98, "#56a05f")
    t.salvar(f"{_pasta('foz')}/ceu.png")


def agua_foz():
    """Agua salobra: azul por cima, onde chega o mar, e esverdeada perto."""
    t = Tela(320, 63)
    bands = [("#cfe6e6", 1), ("#9cccd6", 2), ("#76b4c4", 5), ("#5f9fb0", 7), ("#4f8d98", 9),
             ("#437b82", 11), ("#386a6e", 12), ("#2d585a", 16)]
    faixas(t, 0, 0, 320, bands, dither=False)
    R = rng(29)
    y = 0
    for i, (cor, h) in enumerate(bands):
        if i >= 1:
            claro = bands[i - 1][0]
            for _ in range(int(320 * h / (10 + i * 4))):  # mais marola que no acude
                x, yy = R.randrange(320), y + R.randrange(h)
                t.hline(x, x + R.randint(3, 8), yy, claro)
        y += h
    for yy in range(1, 20):  # reflexo do sol
        if R.random() < 0.45 - yy / 40:
            x = int(64 + R.gauss(0, 3 + yy * 0.25))
            t.hline(x, x + R.randint(1, 2), yy, "#eef2d0" if yy < 8 else "#bfe0d8")
    # espuma da correnteza descendo para a barra
    for _ in range(40):
        x, yy = R.randrange(320), R.randrange(6, 60)
        if R.random() < 0.5:
            t.hline(x, x + 1, yy, "#d8ecea")
    t.salvar(f"{_pasta('foz')}/agua.png")


def barranco_foz():
    """O barranco do acude com a terra trocada por areia e o capim por
    vegetacao de restinga: o mesmo desenho, outra cor."""
    tmp = _pasta("foz")
    acude.OUT = tmp
    acude.barranco()
    troca = [
        ("#a06540", "#d9c38e"), ("#b5784e", "#e6d3a2"), ("#855032", "#b9a26f"),
        ("#8c5530", "#c9b07a"), ("#734427", "#a48c5c"), ("#75431f", "#b39a66"),
        ("#8a5529", "#c2a873"), ("#5e3519", "#8f7a50"), ("#6e4626", "#9f8a5e"),
        ("#6b3f1e", "#8c785a"), ("#95602f", "#cbb37c"), ("#5b3a1f", "#7d6a4a"),
        ("#9ad857", "#a7c46a"), ("#7cc248", "#8fb35a"), ("#63a93c", "#789c4a"),
        ("#4f9131", "#65863f"), ("#3c7727", "#526f33"),
        ("#8fc9a6", "#a9d4d6"), ("#74b596", "#86bccb"),
    ]
    _recolorir(f"{tmp}/barranco.png", f"{tmp}/barranco.png", troca)


def estrutura_foz():
    """O trapiche e o mesmo modelo do acude: foi a vila que ensinou o avo a
    fazer o dele."""
    acude.OUT = _pasta("foz")
    acude.estrutura()


# ================================================================ ARVOREDO

def ilha(t, cx, base, larg, alt, R, farol=False):
    """Ilha de granito com mata atlantica por cima."""
    xs = range(int(cx - larg), int(cx + larg) + 1)
    for x in xs:
        f = (x - cx) / larg
        h = alt * (1 - f * f) ** 0.7 * (0.9 + 0.1 * math.sin(x * 0.9))
        topo = int(base - h)
        for y in range(topo, base + 1):
            rocha = y > base - max(2, h * 0.30)
            if rocha:
                cor = "#8b8f8c" if (x + y) % 3 else "#767a78"
            else:
                cor = "#2f5b3c" if y > topo + 1 else "#3f7a4b"
            t.put(x, y, cor)
        if R.random() < 0.3:
            t.put(x, topo, "#558f5c")
    if farol:
        fx = int(cx + larg * 0.35)
        topo = int(base - alt * (1 - 0.35 ** 2) ** 0.7)
        t.rect(fx, topo - 9, 2, 9, "#f4f1e6")
        t.put(fx, topo - 6, "#c0503a"); t.put(fx + 1, topo - 6, "#c0503a")
        t.put(fx, topo - 3, "#c0503a"); t.put(fx + 1, topo - 3, "#c0503a")
        t.rect(fx - 1, topo - 11, 4, 2, "#3a3f44")
        t.put(fx, topo - 10, "#ffe07a"); t.put(fx + 1, topo - 10, "#ffe07a")
    # espuma batendo no costao
    for x in xs:
        if R.random() < 0.5:
            t.put(x, base, "#e6f2f4")


def ceu_arvoredo():
    t = Tela(320, 120)
    _ceu_base(t, sol=(250, 30))
    for cx, cy, w, r in ((60, 26, 36, 6), (130, 14, 22, 4.5), (190, 50, 28, 5),
                         (300, 64, 20, 4), (30, 70, 18, 3.5)):
        acude.nuvem(t, cx, cy, w, r)
    for x, y in ((150, 36), (157, 33), (88, 48), (210, 40), (216, 38)):
        gaivota(t, x, y)
    # horizonte de mar aberto
    for y in range(104, 120):
        cor = "#3f78a6" if y < 108 else ("#4a86b2" if y < 113 else "#5592bd")
        t.hline(0, 319, y, cor)
    t.hline(0, 319, 104, "#2f6a98")
    R = rng(41)
    # o Arvoredo, grande e com o farol, e as ilhas menores
    ilha(t, 205, 108, 62, 26, R, farol=True)
    ilha(t, 92, 107, 26, 12, R)
    ilha(t, 40, 106, 12, 6, R)
    ilha(t, 292, 107, 16, 8, R)
    for _ in range(30):
        x, y = R.randrange(320), R.randrange(110, 119)
        t.hline(x, x + R.randint(2, 5), y, "#8fc0dc")
    t.salvar(f"{_pasta('arvoredo')}/ceu.png")


def agua_arvoredo():
    """Mar aberto: azul fundo, com carneirinhos de espuma."""
    t = Tela(320, 63)
    bands = [("#d6ecf4", 1), ("#8fc3dc", 2), ("#5d9fc6", 5), ("#4688b4", 7), ("#3a77a2", 9),
             ("#306792", 11), ("#285883", 12), ("#204a72", 16)]
    faixas(t, 0, 0, 320, bands, dither=False)
    R = rng(61)
    y = 0
    for i, (cor, h) in enumerate(bands):
        if i >= 1:
            claro = bands[i - 1][0]
            for _ in range(int(320 * h / (8 + i * 3))):
                x, yy = R.randrange(320), y + R.randrange(h)
                t.hline(x, x + R.randint(3, 9), yy, claro)
        y += h
    for yy in range(1, 22):  # reflexo do sol
        if R.random() < 0.5 - yy / 44:
            x = int(250 + R.gauss(0, 3 + yy * 0.3))
            t.hline(x, x + R.randint(1, 3), yy, "#f2f6dc" if yy < 9 else "#bfdcec")
    for _ in range(26):  # carneirinhos
        x, yy = R.randrange(320), R.randrange(4, 58)
        t.hline(x, x + R.randint(1, 3), yy, "#eef6f8")
        t.put(x + 1, yy + 1, "#c6e0ec")
    t.salvar(f"{_pasta('arvoredo')}/agua.png")


def barranco_arvoredo():
    """O barranco do acude virado costao: a terra vira granito e o capim vira
    a vegetacao baixa da ilha."""
    tmp = _pasta("arvoredo")
    acude.OUT = tmp
    acude.barranco()
    troca = [
        ("#a06540", "#9a9e9a"), ("#b5784e", "#b0b4af"), ("#855032", "#7f837f"),
        ("#8c5530", "#8a8e8a"), ("#734427", "#6f736f"), ("#75431f", "#777b77"),
        ("#8a5529", "#868a86"), ("#5e3519", "#5a5e5b"), ("#6e4626", "#666a67"),
        ("#6b3f1e", "#5d615e"), ("#95602f", "#9da19c"), ("#5b3a1f", "#4f6a52"),
        ("#9ad857", "#7fb35c"), ("#7cc248", "#6aa14d"), ("#63a93c", "#578a41"),
        ("#4f9131", "#477436"), ("#3c7727", "#395f2d"),
        ("#8fc9a6", "#d6ecf4"), ("#74b596", "#8fc3dc"), ("#4e7f45", "#4f6a52"),
    ]
    _recolorir(f"{tmp}/barranco.png", f"{tmp}/barranco.png", troca)


def estrutura_arvoredo():
    """Laje de granito saindo do costao, no lugar do trapiche: um amontoado de
    pedras de topo chato. O piso tem de cair na linha 44, como o do acude,
    que e onde o Tiago pisa."""
    t = Tela(80, 76)
    R = rng(53)
    PISO = 44
    # pedras de tras para a frente: (cx, cy, raio)
    pedras = [(8, 58, 13), (24, 60, 14), (40, 58, 13), (55, 59, 12), (68, 61, 10),
              (16, 70, 9), (34, 71, 10), (52, 70, 9), (72, 69, 7)]
    G_LUZ, G1, G2, G3, G4 = "#c4c8c3", "#a3a7a3", "#8b8f8b", "#727672", "#5a5e5b"
    for cx, cy, r in pedras:
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                dx, dy = (x + .5 - cx) / r, (y + .5 - cy) / (r * 0.85)
                d = dx * dx + dy * dy
                if d > 1 or y < PISO:
                    continue
                luz = -dx * 0.5 - dy * 0.7
                cor = G1 if luz > 0.25 else (G2 if luz > -0.2 else (G3 if luz > -0.6 else G4))
                if d > 0.82:
                    cor = G4
                t.put(x, y, cor)
    # topo chato e gasto onde se pisa, com a borda clara
    for x in range(0, 74):
        if t.get(x, PISO + 1)[3]:
            t.put(x, PISO, G_LUZ)
            t.put(x, PISO + 1, G1 if x % 4 else G_LUZ)
    # abaixo da linha d'agua a pedra escurece e pega limo e craca
    for y in range(50, 76):
        for x in range(80):
            if t.get(x, y)[3]:
                r, g, b, a = t.get(x, y)
                t.px[x, y] = (int(r * .72), int(g * .80), int(b * .80), a)
    for x in range(80):
        if t.get(x, 50)[3] and R.random() < 0.7:
            t.put(x, 50, "#e6ece4" if x % 3 else "#3f5f4a")
            if R.random() < 0.4:
                t.put(x, 51, "#4f6a52")
    for _ in range(26):  # liquen amarelado no seco
        x, y = R.randrange(0, 74), R.randrange(PISO + 1, 49)
        if t.get(x, y)[3]:
            t.put(x, y, R.choice(["#c9b86a", "#b7ad72", "#d8d2a6"]))
    # a argola de ferro e o cabo velho do avo
    t.put(60, PISO - 1, "#6b3f22"); t.put(61, PISO - 1, "#6b3f22")
    for k in range(9):
        t.put(62 + k, PISO + 1 + k // 2, "#c2a46a")
    t.contorno("#2e3230")
    t.salvar(f"{_pasta('arvoredo')}/estrutura.png")


if __name__ == "__main__":
    ceu_foz(); agua_foz(); barranco_foz(); estrutura_foz()
    ceu_arvoredo(); agua_arvoredo(); barranco_arvoredo(); estrutura_arvoredo()
    print("ok")
