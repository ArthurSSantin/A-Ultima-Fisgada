"""Cenario do cais (1/4 da resolucao, exportado em 4x).

O cais e o ponto de partida da Fase 1: dali o Tiago pega o barco e escolhe
para onde ir. Nao se pesca aqui, entao o deck e de passagem e de atracar.

    cd tools/arte
    python cais_arte.py ../../assets/sprites/cais
"""
import math, sys
from px import Tela, faixas, rng, hx, gaivota

OUT = sys.argv[1]

# ------------------------------------------------------------------ CEU 320x120
def nuvem(t, cx, cy, w, r):
    R = rng(int(cx * 7 + cy))
    pts = []
    x = cx - w / 2
    while x < cx + w / 2:
        rr = r * (0.6 + 0.5 * math.sin((x - cx) / w * math.pi + 1.6) ** 2) + R.uniform(-.6, .6)
        pts.append((x, cy - rr * 0.35, max(2.2, rr)))
        x += max(2.5, rr * 0.9)
    base = cy + 2
    tmp = Tela(t.w, t.h)
    for x, y, rr in pts:
        tmp.disco(x, y, rr, "#eef7ff", sy=0.8)
    tmp.rect(cx - w / 2, cy - 1, w, 4, "#eef7ff")
    for yy in range(t.h):
        for xx in range(t.w):
            if tmp.get(xx, yy)[3] and yy > base + 1:
                tmp.put(xx, yy, None); tmp.px[xx, yy] = (0, 0, 0, 0)
    # sombreado: brilho em cima a esquerda, sombra azulada embaixo
    for yy in range(t.h):
        for xx in range(t.w):
            if not tmp.get(xx, yy)[3]:
                continue
            if yy >= base:
                tmp.put(xx, yy, "#b9d8f3")
            elif yy >= base - 1:
                tmp.put(xx, yy, "#d3e8fa")
            elif tmp.get(xx, yy - 1)[3] == 0 or tmp.get(xx - 1, yy)[3] == 0:
                tmp.put(xx, yy, "#ffffff")
    t.colar(tmp, 0, 0)


def morro(xs, picos, base):
    """altura (linha do topo) para cada x a partir de picos gaussianos"""
    alt = {}
    for x in xs:
        h = 0
        for px_, py, larg in picos:
            h = max(h, (base - py) * math.exp(-((x - px_) / larg) ** 2))
        alt[x] = base - h
    return alt


def ceu():
    t = Tela(320, 120)
    faixas(t, 0, 0, 320, [("#3a84d6", 14), ("#4490de", 12), ("#4f9de6", 11), ("#5baaed", 10),
                          ("#68b7f2", 9), ("#77c3f5", 8), ("#87cef7", 8), ("#98d8f9", 7),
                          ("#abe1fa", 6), ("#bfe9fb", 6), ("#d1f0fc", 6), ("#e0f5fd", 23)], dither=False)
    # sol com halo pontilhado
    sx, sy = 262, 22
    for y in range(sy - 14, sy + 15):
        for x in range(sx - 14, sx + 15):
            d = math.hypot(x + .5 - sx, y + .5 - sy)
            if d < 5.5: t.put(x, y, "#fffbe8")
            elif d < 7.5: t.put(x, y, "#fff0b0")
            elif d < 9: t.put(x, y, "#ffe07a")
            elif d < 11.5: t.mix(x, y, "#fff6d8", 0.45)
            elif d < 14: t.mix(x, y, "#fff6d8", 0.18)
    t.put(sx - 2, sy - 3, "#ffffff"); t.put(sx - 3, sy - 2, "#ffffff"); t.put(sx - 2, sy - 2, "#ffffff")
    for cx, cy, w, r in ((60, 30, 34, 6), (150, 16, 26, 5), (200, 48, 30, 5.5), (110, 62, 20, 4), (300, 58, 22, 4.5), (20, 72, 18, 3.5)):
        nuvem(t, cx, cy, w, r)
    for x, y in ((90, 44), (97, 41), (230, 70), (176, 34)):
        gaivota(t, x, y)
    # morros distantes (azulados)
    xs = range(320)
    far = morro(xs, [(40, 98, 40), (120, 102, 30), (235, 82, 45), (300, 90, 30)], 117)
    for x in xs:
        top = int(far[x])
        for y in range(top, 117):
            c = "#88b9bb" if y < top + 1 else ("#78abaf" if (y - top) < 6 else "#6c9fa5")
            t.put(x, y, c)
    # morro verde mais perto, com copas de mata atlantica
    near = morro(xs, [(200, 96, 34), (270, 92, 30), (320, 100, 20)], 117)
    R = rng(3)
    copas = []
    for x in range(150, 320, 3):
        if near[x] < 115:
            copas.append((x + R.uniform(-1, 1), near[x] + 1, R.uniform(1.6, 2.8)))
    tmp = Tela(320, 120)
    for x in xs:
        top = int(near[x])
        for y in range(top, 117):
            tmp.put(x, y, "#3f8550")
    for x, y, r in copas:
        tmp.disco(x, y, r, "#3f8550")
    for y in range(120):
        for x in range(320):
            if tmp.get(x, y)[3]:
                up = tmp.get(x, y - 1)[3] == 0
                up2 = tmp.get(x, y - 2)[3] == 0
                c = "#6bb56c" if up else ("#54a05e" if up2 else ("#3f8550" if y < 110 else "#356f45"))
                t.put(x, y, c)
    # vilarejo acoriano na beira (casinhas coloridas + igreja branca)
    t.rect(150, 114, 170, 3, "#e9d7a6")
    t.hline(150, 319, 113, "#d9c48f")
    casas = [(176, "#f4efe0"), (183, "#f2c94c"), (190, "#6fb3e0"), (205, "#e89a6a"), (212, "#f4efe0"), (226, "#9bd18a"), (233, "#f2c94c"), (248, "#f4efe0")]
    for x, cor in casas:
        t.rect(x, 109, 5, 4, cor)
        t.hline(x - 1, x + 5, 108, "#b9452f"); t.hline(x, x + 4, 107, "#b9452f"); t.hline(x + 1, x + 3, 106, "#d9604a")
        t.put(x + 1, 110, "#3a4a5a"); t.put(x + 3, 110, "#3a4a5a"); t.put(x + 2, 112, "#6b4a2e")
    ig = 196  # igreja
    t.rect(ig, 105, 7, 8, "#ffffff"); t.vline(ig, 105, 112, "#dfe6ea")
    t.rect(ig + 2, 99, 3, 6, "#ffffff"); t.put(ig + 3, 97, "#c0a060"); t.put(ig + 3, 98, "#c0a060"); t.put(ig + 2, 97, "#c0a060"); t.put(ig + 4, 97, "#c0a060")
    t.put(ig + 3, 101, "#3a4a5a"); t.put(ig + 3, 110, "#6b4a2e"); t.put(ig + 3, 111, "#6b4a2e")
    t.hline(ig - 1, ig + 7, 104, "#b9452f")
    t.salvar(f"{OUT}/ceu.png")
    return t


# ------------------------------------------------------------------ MAR 320x63
def mar():
    t = Tela(320, 63)
    bands = [("#e8fbff", 1), ("#a6e4f5", 2), ("#6dcbec", 5), ("#4fb5e3", 7), ("#3c9fd6", 9),
             ("#2f88c4", 11), ("#2672b0", 12), ("#1e5e9a", 16)]
    faixas(t, 0, 0, 320, bands, dither=False)
    R = rng(11)
    y = 0
    lights = {}
    for i, (c, h) in enumerate(bands):
        lights[i] = bands[max(0, i - 1)][0]
    y = 0
    for i, (c, h) in enumerate(bands):
        if i >= 1:
            n = int(320 * h / (12 + i * 5))
            for _ in range(n):
                x = R.randrange(320); yy = y + R.randrange(h)
                L = R.randint(3, 8)
                t.hline(x, x + L, yy, lights[i])
                if i <= 3 and R.random() < 0.2:
                    t.put(x + L, yy, "#ffffff" if i <= 2 else "#bfeffa")
        y += h
    # reflexo do sol
    for yy in range(1, 34):
        for _ in range(2):
            if R.random() < 0.8 - yy / 40:
                x = int(262 + R.gauss(0, 4 + yy * 0.25))
                L = R.randint(1, 4)
                t.hline(x, x + L, yy, "#fff3c6" if yy < 14 else "#d9f4ff")
    # canoa de garapuvu ao longe com um pescador
    cx, cy = 222, 3
    t.hline(cx, cx + 11, cy + 1, "#5a3a22"); t.hline(cx + 1, cx + 10, cy + 2, "#3d2616")
    t.put(cx - 1, cy, "#5a3a22"); t.put(cx + 12, cy, "#5a3a22")
    t.rect(cx + 5, cy - 3, 2, 3, "#3f7cc8"); t.hline(cx + 4, cx + 7, cy - 4, "#f2cf63")
    t.vline(cx + 8, cy - 6, cy, "#8a6a3a")
    t.hline(cx - 2, cx + 14, cy + 3, "#a6e4f5")
    # espuma batendo no costao (borda da terra em x=80)
    for yy in range(0, 7):
        for x in range(80, 86 - yy // 2):
            if R.random() < 0.55 - yy * 0.06:
                t.put(x, yy, "#ffffff" if R.random() < .5 else "#c9f0fa")
    t.salvar(f"{OUT}/mar.png")
    return t


# ------------------------------------------------------------------ TERRA 80x92 (grama + costao)
def terra():
    t = Tela(80, 92)
    R = rng(5)
    # placa em forma de seta "< Loja de Pesca" (o texto e um Label por cima)
    OL, W1, W2, W3 = "#3b2414", "#c48d52", "#a8743f", "#8c5c30"
    for x in (9, 38):
        t.rect(x, 15, 2, 5, W3); t.vline(x - 1, 15, 19, OL); t.vline(x + 2, 15, 19, OL)
    for y in range(9, 16):
        dx = abs(y - 12)
        t.hline(1 + dx, 45, y, W2 if y < 12 else W3)
    t.hline(4, 45, 9, W1)
    t.hline(2, 45, 12, W2)
    for y in range(8, 17):
        dx = abs(y - 12.0)
        t.put(int(dx), y, OL)
    t.hline(4, 46, 8, OL); t.hline(4, 46, 16, OL); t.vline(46, 8, 16, OL)
    for x in (6, 43):
        t.put(x, 10, "#5a3a22"); t.put(x, 14, "#5a3a22")
    # grama
    G1, G2, G3, G4, G5 = "#8fd44f", "#6fbf45", "#58a63a", "#468f2f", "#347526"
    for x in range(80):
        t.put(x, 18, G1 if x % 5 else G2)
        t.vline(x, 19, 20, G2); t.vline(x, 21, 22, G3); t.put(x, 23, G4)
        if x % 3 == 0: t.put(x, 24, G5)
        if x % 7 == 3: t.put(x, 25, G5)
    for x in range(0, 80, 2):
        h = R.choice((0, 1, 1, 2))
        for k in range(h):
            t.put(x + R.choice((0, 1)), 17 - k, G2 if k == 0 else G1)
    for x, c in ((14, "#ffffff"), (27, "#ffe066"), (52, "#ff9fb8"), (63, "#ffffff"), (33, "#ffe066")):
        t.put(x, 16, c); t.put(x, 17, G4)
    # terra em camadas com divisas onduladas e torroes
    camadas = [("#9b6b3f", "#b07d4c", "#7f5532"), ("#88592f", "#9b6b3f", "#6d4827"), ("#714826", "#86592f", "#5a3a1f")]
    for x in range(80):
        b1 = 40 + 2 * math.sin(x / 7.0) + math.sin(x / 2.3)
        b2 = 62 + 2 * math.sin(x / 9.0 + 1) + math.sin(x / 3.1)
        for y in range(24, 92):
            if t.get(x, y)[3]:
                continue
            k = 0 if y < b1 else (1 if y < b2 else 2)
            t.put(x, y, camadas[k][0])
    for x in range(80):  # sombra logo abaixo da grama
        t.put(x, 24, "#6e4626"); t.put(x, 25, "#7f5532") if x % 2 else None
    for _ in range(70):  # torroes
        x, yy = R.randrange(80), R.randrange(27, 91)
        base = t.get(x, yy)
        k = 0 if base == hx(camadas[0][0]) else (1 if base == hx(camadas[1][0]) else 2)
        L = R.randint(2, 4)
        t.hline(x, x + L - 1, yy, camadas[k][2])
        t.hline(x, x + L - 2, yy - 1, camadas[k][1])
    for _ in range(18):  # pedrinhas
        x, yy = R.randrange(64), R.randrange(30, 90)
        t.hline(x, x + 1, yy, "#c2b8a8"); t.put(x + 2, yy, "#968b7c"); t.hline(x, x + 2, yy + 1, "#6e655a")
    for _ in range(8):  # raizes
        x, yy = R.randrange(64), R.randrange(26, 38)
        for k in range(R.randint(3, 7)):
            t.put(x + k, yy + k // 2, "#5b3a1f")
    # costao rochoso de granito: blocos irregulares com facetas
    def pedra(cx, cy, r, seed):
        Rr = rng(seed)
        n = 7
        raios = [r * Rr.uniform(0.75, 1.1) for _ in range(n)]
        for yy in range(int(cy - r * 1.2), int(cy + r * 1.2) + 1):
            for xx in range(int(cx - r * 1.3), int(cx + r * 1.3) + 1):
                ang = math.atan2(yy + .5 - cy, xx + .5 - cx)
                k = (ang + math.pi) / (2 * math.pi) * n
                i0 = int(k) % n; f = k - int(k)
                lim = raios[i0] * (1 - f) + raios[(i0 + 1) % n] * f
                d = math.hypot(xx + .5 - cx, (yy + .5 - cy) * 1.15)
                if d <= lim:
                    face = int(k) % n
                    if d > lim - 1: col = "#474b53"
                    elif ang < -1.6: col = "#c7ccd1"
                    elif ang < -0.6: col = "#a7adb4"
                    elif ang < 1.2 and ang > -0.6 and face % 2: col = "#8b919a"
                    elif ang >= 1.2: col = "#6c727b"
                    else: col = "#979da5"
                    t.put(xx, yy, col)
        for k in range(Rr.randint(2, 4)):
            t.put(cx - 2 + k, cy - int(raios[1]) + 1, "#64a24c")
    for cx, cy, r, sd in ((72, 30, 9, 1), (63, 42, 7, 2), (76, 46, 6, 3), (69, 56, 5, 4), (77, 60, 4, 5)):
        pedra(cx, cy, r, sd)
    for yy in range(25, 29):  # espuma na linha da agua
        for x in range(70, 80):
            if R.random() < 0.4:
                t.put(x, yy, "#ffffff" if R.random() < .6 else "#c9f0fa")
    t.salvar(f"{OUT}/costao.png")
    return t


# ------------------------------------------------------------------ CAIS 80x48
def cais():
    t = Tela(80, 48)
    R = rng(9)
    OL = "#3a2215"
    # estacas (embaixo d'agua ficam azuladas e tremidas)
    for px_ in (3, 37, 72):
        for y in range(21, 48):
            sh = 0 if y < 24 else (1 if (y // 3) % 2 else 0)
            if y < 24:
                cols = ["#5a3820", "#9a6438", "#7a4c2b", "#7a4c2b", "#5a3820", OL]
            else:
                k = min(1.0, (y - 23) / 14)
                cols = [None, "#5f87a0", "#4d7690", "#4d7690", "#3c627c", "#2f5068"]
            t.put(px_ - 1 + sh, y, OL if y < 24 else "#2f5068")
            for i in range(4):
                t.put(px_ + i + sh, y, cols[1 + i] if y >= 24 else cols[1 + i])
            t.put(px_ + 4 + sh, y, OL if y < 24 else "#2f5068")
        # corda enrolada
        for i in range(4):
            t.put(px_ + i, 22, "#d9c27a" if i % 2 == 0 else "#b39a55")
        t.put(px_ - 1, 22, "#8a7340"); t.put(px_ + 4, 22, "#8a7340")
        # espuma em volta da estaca
        for x in range(px_ - 3, px_ + 7):
            if x < px_ - 1 or x > px_ + 4:
                t.put(x, 24, "#ffffff" if (x + px_) % 2 else "#c9f0fa")
        t.put(px_ - 2, 25, "#c9f0fa"); t.put(px_ + 6, 25, "#c9f0fa")
    # viga embaixo do deck
    t.hline(0, 79, 21, "#5a3820"); t.hline(0, 79, 22, OL) if False else None
    # deck de tabuas
    tons = ["#b97f48", "#ad7442", "#c2884f", "#b37a45"]
    x = 0; i = 0
    while x < 80:
        L = R.randint(7, 10)
        c = tons[i % 4]
        for xx in range(x, min(80, x + L)):
            t.put(xx, 16, "#e0aa6c")
            t.vline(xx, 17, 19, c)
            t.put(xx, 20, "#8a5a33")
        if x > 0:
            t.vline(x, 17, 19, "#6b4325")
        t.put(x + 1, 18, "#4a2c18"); t.put(min(79, x + L - 2), 18, "#4a2c18")
        if R.random() < 0.5:
            gx = x + R.randint(2, max(2, L - 3))
            t.hline(gx, gx + 2, 17 + R.randint(0, 2), "#9e683a")
        x += L; i += 1
    t.hline(0, 79, 15, OL)
    t.hline(0, 79, 21, OL)
    # rede de pesca pendurada na frente do deck (boias de cortica laranja)
    for yy in range(17, 26):
        for xx in range(46, 60):
            w = int(2 + (yy - 17) * 0.4)
            if xx < 46 + (yy - 17) // 2 or xx > 59 - (yy - 17) // 2:
                continue
            if (xx + yy) % 3 == 0 or (xx - yy) % 3 == 0:
                t.put(xx, yy, "#e8e0c8")
    for xx in (47, 51, 55, 59):
        t.put(xx, 16, "#e0703a"); t.put(xx, 17, "#b9502a")
    # lampiao na ponta do cais
    t.rect(74, 4, 2, 12, "#7a4c2b"); t.vline(73, 4, 15, OL); t.vline(76, 4, 15, OL)
    t.rect(72, 0, 6, 1, OL)
    t.caixa(72, 1, 6, 4, "#ffe08a", OL); t.put(74, 2, "#fff6d0"); t.put(75, 3, "#ffc94a")
    t.hline(71, 78, 5, OL)
    # balde com rabo de peixe e rolo de corda no deck
    t.caixa(20, 11, 6, 5, "#aab3bb", "#4a5058"); t.hline(21, 24, 12, "#cfd6dc"); t.vline(21, 13, 14, "#8d969e")
    t.put(19, 10, "#4a5058"); t.put(26, 10, "#4a5058"); t.hline(20, 25, 9, "#4a5058")
    t.put(23, 9, "#4fb5e3"); t.put(22, 8, "#4fb5e3"); t.put(24, 8, "#4fb5e3"); t.put(21, 7, "#2f88c4"); t.put(25, 7, "#2f88c4")
    for xx, yy in ((30, 15), (31, 14), (32, 14), (33, 14), (34, 14), (35, 15), (31, 15), (34, 15), (32, 13), (33, 13)):
        t.put(xx, yy, "#d9c27a")
    t.put(32, 15, "#a88a48"); t.put(33, 15, "#a88a48"); t.put(32, 14, "#a88a48")

    # guarda-corpo correndo ao fundo do deck: fica atras do Tiago e da
    # profundidade ao cais, que antes era so uma tabua reta
    for x in range(2, 72, 9):
        t.vline(x, 9, 15, "#8a5a33")
        t.vline(x + 1, 9, 15, "#6b4325")
        t.put(x, 9, "#c2884f")
    t.hline(2, 71, 10, "#a8743f"); t.hline(2, 71, 11, "#7a4c2b")
    t.hline(2, 71, 13, "#a8743f"); t.hline(2, 71, 14, "#7a4c2b")

    # caixaria e tambor de oleo encostados no guarda-corpo
    t.caixa(52, 10, 8, 6, "#b07c45", "#5a3a22")
    t.hline(53, 58, 12, "#8a5a33"); t.vline(56, 11, 14, "#8a5a33")
    t.caixa(60, 12, 6, 4, "#9c6c3c", "#5a3a22"); t.hline(61, 64, 13, "#7a4c2b")
    t.caixa(44, 11, 5, 5, "#4a6a7a", "#24343d")
    t.hline(45, 47, 12, "#6b8f9e"); t.hline(45, 47, 14, "#36505c")

    # bolardo de amarracao na beira, com a corda caindo para a agua
    t.rect(66, 12, 3, 4, "#5f6a72"); t.hline(66, 68, 11, "#848f97")
    t.put(69, 12, "#848f97"); t.put(65, 12, "#848f97")
    for i, (dx, dy) in enumerate(((3, 1), (4, 2), (5, 4), (6, 6), (7, 9), (7, 12))):
        t.put(66 + dx, 15 + dy, "#d9c27a" if i % 2 else "#b39a55")

    # gaivota pousada no poste do lampiao
    t.put(74, -1, "#f2f4f6") if False else None
    for dx, dy in ((0, 0), (1, 0), (2, 0), (1, -1), (2, -1), (3, 0)):
        t.put(70 + dx, 7 + dy, "#f2f4f6")
    t.put(73, 7, "#9aa6ae"); t.put(70, 8, "#e0a24a"); t.put(71, 8, "#e0a24a")
    t.put(69, 6, "#f2f4f6"); t.put(73, 6, "#3a4a5a")

    t.salvar(f"{OUT}/cais.png")
    return t


# -------------------------------------------------------------- BARCO 40x20

def _linha(pontos, u):
    """Altura em u (0 a 1), interpolando suave entre os pontos de controle."""
    for i in range(len(pontos) - 1):
        u0, h0 = pontos[i]
        u1, h1 = pontos[i + 1]
        if u0 <= u <= u1:
            f = (u - u0) / max(u1 - u0, 1e-6)
            return h0 + (h1 - h0) * (f * f * (3.0 - 2.0 * f))
    return pontos[-1][1]


def barco():
    """Bote de madeira atracado na ponta do cais: proa levantada, bancos e remo.

    E o unico objeto com que se interage no cais, entao leva contorno escuro
    fechado para se destacar do mar. A popa fica a esquerda, virada para o cais.
    """
    t = Tela(40, 20)
    OL = "#2e1b0f"
    BORDA, TABUA, TABUA_SOMBRA = "#d9a263", "#8a5a33", "#5f3d20"
    DENTRO, DENTRO_FUNDO = "#6b4325", "#43291440"

    X0, X1 = 3, 37
    # borda de cima (do costado) e fundo do casco, da popa a proa
    SHEER = [(0, 6.6), (.14, 8.0), (.46, 8.6), (.74, 7.6), (.90, 5.4), (1, 3.2)]
    FUNDO = [(0, 11.4), (.12, 13.2), (.42, 14.6), (.70, 14.2), (.90, 12.0), (1, 8.0)]
    # O bote flutua: tudo abaixo desta linha fica escondido pela agua.
    AGUA = 13

    for x in range(X0, X1 + 1):
        u = (x - X0) / (X1 - X0)
        cima, baixo = _linha(SHEER, u), _linha(FUNDO, u)
        for y in range(int(round(cima)), int(round(baixo)) + 1):
            f = (y - cima) / max(baixo - cima, 0.001)
            if f < 0.16:
                cor = BORDA
            elif f < 0.62:
                cor = TABUA
            else:
                cor = TABUA_SOMBRA
            t.put(x, y, cor)
        if x % 3 == 0:  # friso das tabuas do costado
            t.put(x, int(cima) + 3, TABUA_SOMBRA)

    # boca do bote: duas linhas escuras logo abaixo da borda, so no meio
    for x in range(X0 + 3, X1 - 3):
        u = (x - X0) / (X1 - X0)
        cima = int(round(_linha(SHEER, u)))
        t.put(x, cima, DENTRO)
        if 0.10 < u < 0.86:
            t.put(x, cima + 1, DENTRO)

    # bancos atravessados
    for bx in (12, 23):
        u = (bx - X0) / (X1 - X0)
        y = int(round(_linha(SHEER, u)))
        t.hline(bx, bx + 4, y, "#e8c38a")
        t.hline(bx, bx + 4, y + 1, "#a8743f")

    # remo apoiado na borda, saindo para cima e para a esquerda
    for i in range(15):
        t.put(18 - i, 9 - i * 0.42, "#c9a06a" if i % 4 else "#a8743f")
    for dx, dy, w in ((0, 0, 3), (-1, 1, 3), (-1, 2, 2)):  # pa do remo
        t.hline(4 + dx, 4 + dx + w, 2 + dy, "#b38c56")
    t.put(4, 3, "#d9b47c"); t.put(5, 3, "#d9b47c")

    # faixa clara pintada na popa, como os botes de madeira da regiao
    for x in range(X0 + 1, X0 + 7):
        u = (x - X0) / (X1 - X0)
        t.put(x, int(round(_linha(SHEER, u))) + 3, "#e8dcc0")

    # corta o casco na linha d'agua: o resto fica submerso
    for y in range(AGUA + 1, t.h):
        for x in range(t.w):
            t.px[x, y] = (0, 0, 0, 0)

    t.contorno(OL)

    # marca d'agua: um friso claro no casco e duas marolinhas nas pontas,
    # em vez de uma fileira de pontos que vira cerca branca
    for x in range(X0 - 1, X1 + 2):
        if t.get(x, AGUA)[3]:
            t.put(x, AGUA, "#8fb6cf" if (x * 5) % 3 else "#bfe7f7")
    for x, y in ((X0 - 3, AGUA), (X0 - 4, AGUA), (X0 - 5, AGUA + 1),
                 (X1 + 2, AGUA), (X1 + 3, AGUA), (X1 + 4, AGUA + 1), (X1 + 5, AGUA + 1)):
        t.put(x, y, "#dff2fb")

    # corda de amarracao saindo da popa em direcao ao cais
    for i, dy in enumerate((0, -1, -1, -2, -2, -3, -3)):
        t.put(X0 - i, 9 + dy, "#d9c27a" if i % 2 else "#b39a55")

    t.salvar(f"{OUT}/barco.png")
    return t


if __name__ == "__main__":
    ceu(); mar(); terra(); cais(); barco()
    print("ok")
