"""Cenario do acude (1/4 da resolucao, exportado em 4x).

A Fase 1 se passa num acude de interior, nao mais no cais de mar: morros de
pasto no fundo, um sitio na beira, agua parada esverdeada com aguape e um
trapiche de madeira saindo do barranco.

    cd tools/arte
    python acude_arte.py ../../assets/sprites/acude

A estrutura de pesca tem tres partes, da terra para a agua: a ponte estreita,
o quiosque redondo e coberto no meio, e a sacada aberta na ponta, que e de
onde se pesca. O sprite dela e alto o bastante para o telhado passar por
cima do Tiago sem encostar nele.
"""
import math
import sys

from px import Tela, faixas, rng, hx

OUT = sys.argv[1] if len(sys.argv) > 1 else "."


def passaro(t, x, y, cor="#3d4658"):
    """Passarinho de 5 px visto de longe (garca ou quero-quero, a essa distancia)."""
    for dx, dy in ((0, 0), (1, -1), (2, 0), (3, -1), (4, 0)):
        t.put(x + dx, y + dy, cor)


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
                tmp.px[xx, yy] = (0, 0, 0, 0)
    # sombreado: brilho em cima a esquerda, sombra azulada embaixo
    for yy in range(t.h):
        for xx in range(t.w):
            if not tmp.get(xx, yy)[3]:
                continue
            if yy >= base:
                tmp.put(xx, yy, "#bcd9ee")
            elif yy >= base - 1:
                tmp.put(xx, yy, "#d6e9f6")
            elif tmp.get(xx, yy - 1)[3] == 0 or tmp.get(xx - 1, yy)[3] == 0:
                tmp.put(xx, yy, "#ffffff")
    t.colar(tmp, 0, 0)


def morro(xs, picos, base):
    """Altura (linha do topo) para cada x a partir de picos gaussianos."""
    alt = {}
    for x in xs:
        h = 0
        for px_, py, larg in picos:
            h = max(h, (base - py) * math.exp(-((x - px_) / larg) ** 2))
        alt[x] = base - h
    return alt


def arvore(t, x, base, altura, copa, tronco="#4e3a22", folha="#2f6b3c", luz="#4f9450"):
    """Arvore de beira de acude: tronco fino e copa redonda em dois tons."""
    t.vline(x, base - altura, base, tronco)
    t.disco(x, base - altura - copa * 0.4, copa, folha, sy=1.05)
    t.disco(x - copa * 0.35, base - altura - copa * 0.75, copa * 0.55, luz, sy=1.0)


def ceu():
    t = Tela(320, 120)
    # Ceu de interior: um pouco mais quente e empoeirado que o do litoral.
    faixas(t, 0, 0, 320, [("#3f82c6", 14), ("#498dce", 12), ("#5599d7", 11), ("#62a6de", 10),
                          ("#71b3e5", 9), ("#81bfea", 8), ("#92caee", 8), ("#a4d4f1", 7),
                          ("#b6ddf3", 6), ("#c8e5f3", 6), ("#d9ecf0", 6), ("#e9f2ea", 23)],
           dither=False)
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
    for cx, cy, w, r in ((60, 30, 34, 6), (150, 16, 26, 5), (200, 48, 30, 5.5),
                         (110, 62, 20, 4), (300, 58, 22, 4.5), (20, 72, 18, 3.5)):
        nuvem(t, cx, cy, w, r)
    for x, y in ((90, 44), (97, 41), (230, 70), (176, 34)):
        passaro(t, x, y)

    xs = range(320)
    # serra distante, azulada pela distancia
    far = morro(xs, [(40, 96, 44), (120, 100, 32), (235, 84, 48), (300, 92, 32)], 117)
    for x in xs:
        topo = int(far[x])
        for y in range(topo, 117):
            t.put(x, y, "#8fb3ae" if y < topo + 1 else ("#7fa69f" if (y - topo) < 6 else "#729a93"))
    # morro de pasto mais perto, com capoeira no alto
    near = morro(xs, [(200, 94, 36), (270, 90, 32), (320, 98, 22)], 117)
    R = rng(3)
    copas = []
    for x in range(150, 320, 3):
        if near[x] < 115:
            copas.append((x + R.uniform(-1, 1), near[x] + 1, R.uniform(1.6, 2.8)))
    tmp = Tela(320, 120)
    for x in xs:
        topo = int(near[x])
        for y in range(topo, 117):
            tmp.put(x, y, "#4f8a45")
    for x, y, r in copas:
        tmp.disco(x, y, r, "#4f8a45")
    for y in range(120):
        for x in range(320):
            if tmp.get(x, y)[3]:
                acima = tmp.get(x, y - 1)[3] == 0
                acima2 = tmp.get(x, y - 2)[3] == 0
                cor = "#7cbd63" if acima else ("#63a453" if acima2 else ("#4f8a45" if y < 110 else "#41713a"))
                t.put(x, y, cor)

    # beira do acude: pasto, um sitio e a mata ciliar
    t.rect(150, 113, 170, 4, "#6fa64c")
    t.hline(150, 319, 112, "#5d9040")
    for x in range(152, 320, 7):  # cerca de madeira
        t.vline(x, 109, 112, "#8a6a3a")
    t.hline(152, 319, 110, "#9c7a44")

    casa = 186  # casa de sitio com telhado de barro
    t.rect(casa, 104, 12, 8, "#f1ead6")
    t.vline(casa, 104, 111, "#ddd3bb")
    t.hline(casa - 1, casa + 12, 103, "#a8452f")
    t.hline(casa, casa + 11, 102, "#a8452f")
    t.hline(casa + 1, casa + 10, 101, "#c2583f")
    t.rect(casa + 2, 107, 2, 3, "#3a4a5a")   # janela
    t.rect(casa + 7, 106, 2, 6, "#6b4a2e")   # porta
    t.vline(casa + 9, 98, 101, "#8a8a8a")    # chamine
    t.put(casa + 9, 97, "#cfd6dc"); t.put(casa + 10, 96, "#dfe6ea")

    curral = 214  # curral e galpao baixo
    t.rect(curral, 107, 10, 5, "#b88a56")
    t.hline(curral - 1, curral + 10, 106, "#7a5a30")
    for x in range(curral, curral + 10, 3):
        t.vline(x, 107, 111, "#9c7444")
    for x, y in ((236, 110), (241, 111), (246, 110)):  # gado longe, so o vulto
        t.hline(x, x + 2, y, "#6b4a2e"); t.put(x, y + 1, "#5a3a22"); t.put(x + 2, y + 1, "#5a3a22")

    for x, alt, copa in ((160, 7, 4.5), (172, 5, 3.4), (254, 8, 5.0), (268, 6, 3.8),
                         (284, 9, 5.4), (302, 6, 4.0), (314, 7, 4.6)):
        arvore(t, x, 112, alt, copa)
    t.salvar(f"{OUT}/ceu.png")
    return t


# ----------------------------------------------------------- AGUA DO ACUDE 320x63

def agua():
    """Agua parada de acude: verde-barrenta, sem onda, com reflexo da mata."""
    t = Tela(320, 63)
    bands = [("#cfe6c9", 1), ("#9ccfae", 2), ("#74b596", 5), ("#5a9e85", 7), ("#4a8a74", 9),
             ("#3d7663", 11), ("#336352", 12), ("#2a5244", 16)]
    faixas(t, 0, 0, 320, bands, dither=False)
    R = rng(11)
    claros = {i: bands[max(0, i - 1)][0] for i in range(len(bands))}

    # marolinhas horizontais: em agua parada sao poucas e compridas
    y = 0
    for i, (cor, h) in enumerate(bands):
        if i >= 1:
            n = int(320 * h / (18 + i * 6))
            for _ in range(n):
                x, yy = R.randrange(320), y + R.randrange(h)
                L = R.randint(4, 11)
                t.hline(x, x + L, yy, claros[i])
        y += h

    # reflexo da mata da outra margem, esticado nas primeiras linhas
    for x in range(150, 320):
        if R.random() < 0.5:
            alt = R.randint(1, 4)
            for yy in range(0, alt):
                t.put(x, yy, "#6fae8c" if yy % 2 else "#86bf9c")
    # reflexo do sol, mais discreto que no mar
    for yy in range(1, 22):
        if R.random() < 0.45 - yy / 44:
            x = int(262 + R.gauss(0, 3 + yy * 0.22))
            t.hline(x, x + R.randint(1, 2), yy, "#e8ecc0" if yy < 9 else "#bcdcc4")

    # aguape: as ilhas de folha redonda que ficam paradas na superficie
    def aguape(cx, cy, r):
        t.disco(cx, cy, r, "#3f7d4e", sy=0.42)
        t.disco(cx - r * 0.25, cy - 0.4, r * 0.55, "#56a05f", sy=0.40)
        t.put(cx + r * 0.4, cy, "#2e5f3c")
        if r > 2.4 and (cx + cy) % 3 == 0:
            t.put(cx, cy - 2, "#d9a6d6")  # a florzinha roxa
            t.put(cx, cy - 1, "#7fae63")

    for cx, cy, r in ((24, 12, 3.2), (33, 15, 2.2), (18, 19, 2.6), (58, 9, 2.0),
                      (96, 26, 3.6), (108, 30, 2.4), (87, 33, 2.8),
                      (210, 18, 2.6), (221, 22, 3.0), (276, 40, 3.8), (291, 45, 2.6),
                      (150, 52, 4.2), (168, 57, 3.0), (44, 48, 3.4)):
        aguape(cx, cy, r)

    # taboas saindo da agua rasa perto da margem esquerda
    for x, alt in ((82, 7), (86, 5), (90, 8), (94, 4), (99, 6)):
        t.vline(x, 0, alt, "#4e7f45")
        t.put(x, 0, "#6b4a2e")
    t.salvar(f"{OUT}/agua.png")
    return t


# -------------------------------------------------- BARRANCO 80x92 (grama + terra)

def barranco():
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
        t.put(int(abs(y - 12.0)), y, OL)
    t.hline(4, 46, 8, OL); t.hline(4, 46, 16, OL); t.vline(46, 8, 16, OL)
    for x in (6, 43):
        t.put(x, 10, "#5a3a22"); t.put(x, 14, "#5a3a22")

    # capim de beira de acude, mais alto e mais seco que grama de jardim
    G1, G2, G3, G4, G5 = "#9ad857", "#7cc248", "#63a93c", "#4f9131", "#3c7727"
    for x in range(80):
        t.put(x, 18, G1 if x % 5 else G2)
        t.vline(x, 19, 20, G2); t.vline(x, 21, 22, G3); t.put(x, 23, G4)
        if x % 3 == 0: t.put(x, 24, G5)
        if x % 7 == 3: t.put(x, 25, G5)
    for x in range(0, 80, 2):
        h = R.choice((0, 1, 1, 2, 2, 3))
        for k in range(h):
            t.put(x + R.choice((0, 1)), 17 - k, G2 if k == 0 else G1)
    for x, c in ((14, "#ffffff"), (27, "#ffe066"), (52, "#ff9fb8"), (63, "#ffffff"), (33, "#ffe066")):
        t.put(x, 16, c); t.put(x, 17, G4)

    # terra vermelha em camadas, com divisas onduladas e torroes
    camadas = [("#a06540", "#b5784e", "#855032"), ("#8c5530", "#a06540", "#734427"),
               ("#75431f", "#8a5529", "#5e3519")]
    for x in range(80):
        b1 = 40 + 2 * math.sin(x / 7.0) + math.sin(x / 2.3)
        b2 = 62 + 2 * math.sin(x / 9.0 + 1) + math.sin(x / 3.1)
        for y in range(24, 92):
            if t.get(x, y)[3]:
                continue
            k = 0 if y < b1 else (1 if y < b2 else 2)
            t.put(x, y, camadas[k][0])
    for x in range(80):  # sombra logo abaixo do capim
        t.put(x, 24, "#6e4626")
        if x % 2:
            t.put(x, 25, "#855032")
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
    for _ in range(10):  # raizes saindo do barranco
        x, yy = R.randrange(64), R.randrange(26, 40)
        for k in range(R.randint(3, 8)):
            t.put(x + k, yy + k // 2, "#5b3a1f")

    # Barranco descendo para a agua, no lugar do costao de granito do cais. A
    # borda e recortada: o sprite fica por cima da agua, entao tudo que e
    # apagado aqui vira acude.
    def limite(yy):
        return 80 - (yy - 24) * 0.30 - 2.2 * math.sin(yy / 5.0) - 1.4 * math.sin(yy / 2.3 + 1)

    for yy in range(25, 92):
        lim = limite(yy)
        for x in range(80):
            if x >= lim:
                t.px[x, yy] = (0, 0, 0, 0)
        for x in range(max(0, int(lim) - 9), int(lim)):
            perto = x >= lim - 2
            t.put(x, yy, "#6b3f1e" if perto else ("#8a5529" if (x + yy) % 3 else "#95602f"))
    for yy in range(26, 92, 5):  # degraus de erosao
        t.hline(max(0, int(limite(yy)) - 9), int(limite(yy)) - 1, yy, "#5e3519")
    for yy in range(28, 90, 7):  # raizes penduradas na barranca
        x = int(limite(yy)) - 1
        for k in range(R.randint(2, 5)):
            t.put(x - k, yy + k, "#5b3a1f")
    for yy in range(25, 92, 3):  # limo na parte molhada
        x = int(limite(yy)) - 1
        if yy > 30:
            t.put(x, yy, "#4e7f52")

    for x in range(58, 80):  # tufos de capim caindo pela beirada
        if R.random() < 0.55:
            for k in range(R.randint(1, 3)):
                t.put(x, 24 + k, G4 if k else G3)

    # taboas e touceira de capim na linha da agua
    for x, alt in ((66, 9), (70, 12), (74, 7), (77, 10)):
        t.vline(x, 25 - alt, 25, "#4e7f45")
        t.put(x, 25 - alt, "#6b4a2e")
        t.put(x - 1, 25 - alt + 2, "#5f9a4d")
    for x in range(64, 80):  # agua rasa batendo na terra
        if R.random() < 0.5:
            t.put(x, 25, "#8fc9a6")
        if R.random() < 0.3:
            t.put(x, 26, "#74b596")
    t.salvar(f"{OUT}/barranco.png")
    return t


# ----------------------------------------------- ESTRUTURA DE PESCA 80x76
#
# A altura do sprite nao e livre: o piso tem de cair na mesma linha em que o
# Tiago pisa (y 440 na tela) e o telhado tem de ficar acima da cabeca dele
# (y 344). Com o sprite ancorado em (460, 416) na cena, isso da PISO = 44 e
# o telhado nas linhas 0 a 19.

PISO = 44           # linha do piso de tabuas
TETO_BASE = 19      # ultima linha do beiral
PONTE = (0, 27)     # faixa em x de cada parte
QUIOSQUE = (25, 55)
SACADA = (53, 80)


def _tabuas(t, x0, x1, y, R, tons=("#b97f48", "#ad7442", "#c2884f", "#b37a45")):
    """Piso de tabuas com veios e junta escura, igual ao do cais."""
    x, i = x0, 0
    while x < x1:
        L = R.randint(5, 8)
        cor = tons[i % len(tons)]
        for xx in range(x, min(x1, x + L)):
            t.put(xx, y, "#e0aa6c")
            t.vline(xx, y + 1, y + 3, cor)
            t.put(xx, y + 4, "#8a5a33")
        if x > x0:
            t.vline(x, y + 1, y + 3, "#6b4325")
        if R.random() < 0.5:
            gx = x + R.randint(1, max(1, L - 2))
            t.hline(gx, gx + 2, y + 1 + R.randint(0, 2), "#9e683a")
        x += L
        i += 1


def _estaca(t, x, de, ate, OL):
    """Estaca de madeira; abaixo da linha d'agua (y 50) fica esverdeada."""
    for y in range(de, ate):
        molhada = y >= 50
        desvio = (1 if (y // 3) % 2 else 0) if molhada else 0
        cores = ("#4e7f6a", "#3f6d5a", "#3f6d5a", "#335848") if molhada \
            else ("#9a6438", "#7a4c2b", "#7a4c2b", "#5a3820")
        borda = "#2a4a3c" if molhada else OL
        t.put(x - 1 + desvio, y, borda)
        for i in range(4):
            t.put(x + i + desvio, y, cores[i])
        t.put(x + 4 + desvio, y, borda)


def _corrimao(t, x0, x1, piso, OL, altura=7):
    """Guarda-corpo baixo: montantes a cada 6 px e dois travessoes."""
    topo = piso - altura
    for x in range(x0, x1, 6):
        t.vline(x, topo, piso - 1, "#8a5a33")
        t.put(x, topo, "#c2884f")
    t.hline(x0, x1 - 1, topo, "#a8743f")
    t.hline(x0, x1 - 1, topo + 1, "#7a4c2b")
    t.hline(x0, x1 - 1, topo + 4, "#a8743f")
    t.hline(x0, x1 - 1, topo + 5, "#7a4c2b")


def estrutura():
    t = Tela(80, 76)
    R = rng(9)
    OL = "#3a2215"

    # --- estacas, de tras para a frente ---
    for x in (4, 14, 30, 44, 58, 70):
        _estaca(t, x, PISO + 2, 76, OL)

    # --- piso: a ponte e estreita, o quiosque e a sacada sao mais fundos ---
    _tabuas(t, PONTE[0], PONTE[1], PISO, R)
    _tabuas(t, QUIOSQUE[0], SACADA[1], PISO - 1, R)

    # saia do piso do quiosque e da sacada, que sao mais largos que a ponte
    t.hline(QUIOSQUE[0], SACADA[1] - 1, PISO + 4, "#7a4c2b")
    t.hline(QUIOSQUE[0], SACADA[1] - 1, PISO + 5, "#5a3820")

    # a sacada termina arredondada, debrucada sobre a agua
    for i in range(5):
        t.vline(SACADA[1] - 1 - i, PISO - 1 + i, PISO + 5 - i, "#8a5a33")
    t.put(SACADA[1] - 1, PISO + 1, "#6b4325")

    t.hline(PONTE[0], PONTE[1] - 1, PISO - 1, OL)
    t.hline(QUIOSQUE[0], SACADA[1] - 1, PISO - 2, OL)
    t.hline(0, 79, PISO + 6, OL)

    # --- guarda-corpo ---
    _corrimao(t, PONTE[0] + 1, PONTE[1], PISO - 1, OL, altura=6)
    _corrimao(t, SACADA[0] + 2, SACADA[1] - 3, PISO - 2, OL, altura=7)

    # --- quiosque: pilares e telhado conico ---
    cx = (QUIOSQUE[0] + QUIOSQUE[1]) // 2
    for x in (QUIOSQUE[0] + 2, cx - 1, QUIOSQUE[1] - 4):
        t.vline(x, TETO_BASE, PISO - 2, "#8a5a33")
        t.vline(x + 1, TETO_BASE, PISO - 2, "#6b4325")
        t.put(x, TETO_BASE, "#c2884f")
        t.hline(x - 1, x + 2, PISO - 3, "#5a3820")  # base do pilar

    # banco corrido entre os pilares do fundo
    t.hline(QUIOSQUE[0] + 4, QUIOSQUE[1] - 6, PISO - 8, "#d9a263")
    t.hline(QUIOSQUE[0] + 4, QUIOSQUE[1] - 6, PISO - 7, "#a8743f")
    for x in range(QUIOSQUE[0] + 5, QUIOSQUE[1] - 6, 7):
        t.vline(x, PISO - 6, PISO - 3, "#8a5a33")

    # telhado: cone de sape visto de lado, beiral passando dos pilares
    BEIRAL = (QUIOSQUE[0] - 5, QUIOSQUE[1] + 5)
    APICE = 2
    for y in range(APICE, TETO_BASE + 1):
        f = (y - APICE) / float(TETO_BASE - APICE)
        meia = (BEIRAL[1] - BEIRAL[0]) / 2.0 * (f ** 0.78)
        e, d = int(cx - meia), int(cx + meia)
        for x in range(e, d + 1):
            if y <= APICE + 1:
                cor = "#b58a4a"
            elif x < cx - meia * 0.45:
                cor = "#c79a53"            # agua-furtada iluminada
            elif x > cx + meia * 0.55:
                cor = "#8c6530"            # lado na sombra
            else:
                cor = "#a87f3e"
            t.put(x, y, cor)
        if y % 3 == 0:                      # ripas do sape
            t.hline(e, d, y, "#7d5a2b")
    # beiral, cumeeira e o pingo de madeira na ponta
    t.hline(BEIRAL[0], BEIRAL[1], TETO_BASE, "#6b4a22")
    t.hline(BEIRAL[0] - 1, BEIRAL[1] + 1, TETO_BASE + 1, "#4e3718")
    t.vline(cx, APICE - 2, APICE, "#6b4a22")
    t.put(cx, APICE - 3, "#c2884f")

    # --- lampiao na ponta da sacada e mato na beira da ponte ---
    poste = SACADA[1] - 7
    t.rect(poste, PISO - 16, 2, 15, "#7a4c2b")
    t.vline(poste - 1, PISO - 16, PISO - 2, OL)
    t.vline(poste + 2, PISO - 16, PISO - 2, OL)
    t.caixa(poste - 2, PISO - 21, 6, 4, "#ffe08a", OL)
    t.put(poste, PISO - 20, "#fff6d0")
    t.put(poste + 1, PISO - 19, "#ffc94a")
    t.hline(poste - 3, poste + 4, PISO - 22, OL)

    for x, alt in ((2, 5), (7, 7), (11, 4)):
        for k in range(alt):
            t.put(x, PISO + 5 + k, "#3f7d4e" if k % 2 else "#4e8f57")
        t.put(x - 1, PISO + 6, "#56a05f")
        t.put(x + 1, PISO + 8, "#56a05f")

    # balde e lata de isca esquecidos na sacada
    t.caixa(SACADA[0] + 5, PISO - 7, 6, 5, "#aab3bb", "#4a5058")
    t.hline(SACADA[0] + 6, SACADA[0] + 9, PISO - 6, "#cfd6dc")
    t.hline(SACADA[0] + 5, SACADA[0] + 10, PISO - 9, "#4a5058")
    t.put(SACADA[0] + 8, PISO - 9, "#5a9e85")
    t.caixa(SACADA[0] + 13, PISO - 6, 5, 4, "#9c7444", "#5a3a22")
    t.hline(SACADA[0] + 14, SACADA[0] + 16, PISO - 7, "#5a3a22")

    t.salvar(f"{OUT}/estrutura.png")
    return t


if __name__ == "__main__":
    ceu(); agua(); barranco(); estrutura()
    print("ok")
