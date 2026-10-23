"""Ferramentas de desenho no estilo do tutorial: mais natural, puxado para o
Stardew Valley, sem perder o traco de pixel do resto do jogo.

O que muda em relacao ao px.py puro:
  - gradiente com dither ordenado (Bayer 4x4) em vez de faixas chapadas;
  - sombra que esfria e luz que esquenta (a cor muda de matiz, nao so de brilho);
  - copas de arvore em cachos, nuvens com volume, grama com fiapos e flores;
  - tabuas com veio, no e prego.

Tudo desenha numa Tela do px.py, em resolucao nativa.
"""
import math

from px import Tela, rng, hx

OL = "#2b1a14"

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


# ------------------------------------------------------------------ basico

def poligono(t, pontos, cor):
    ys = [p[1] for p in pontos]
    for y in range(int(min(ys)), int(max(ys)) + 1):
        cortes = []
        n = len(pontos)
        for i in range(n):
            (x1, y1), (x2, y2) = pontos[i], pontos[(i + 1) % n]
            if (y1 <= y + .5 < y2) or (y2 <= y + .5 < y1):
                cortes.append(x1 + (y + .5 - y1) * (x2 - x1) / (y2 - y1))
        cortes.sort()
        for a, b in zip(cortes[0::2], cortes[1::2]):
            for x in range(int(round(a)), int(round(b))):
                t.put(x, y, cor)


def traco(t, x0, y0, x1, y1, cor, grossura=1):
    passos = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(passos + 1):
        f = i / max(passos, 1)
        x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        if grossura <= 1:
            t.put(x, y, cor)
        else:
            t.disco(x, y, grossura / 2.0, cor)


def escurecer(t, x0, y0, x1, y1, forca, cor="#1a1020"):
    """Sombra por mistura (cor com alfa no put() troca o pixel, nao mistura)."""
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            t.mix(x, y, cor, forca)


def clarear(t, x0, y0, x1, y1, forca, cor="#fff4d8"):
    escurecer(t, x0, y0, x1, y1, forca, cor)


def sombra_no_chao(t, cx, y, meia, forca=0.35):
    """Sombra de contato debaixo de objeto e personagem: elipse achatada."""
    for x in range(int(cx - meia), int(cx + meia) + 1):
        f = 1 - abs(x - cx) / max(meia, 1)
        t.mix(x, y, "#1a1020", forca * f)
        t.mix(x, y + 1, "#1a1020", forca * f * 0.5)


def _mistura(a, b, f):
    a, b = hx(a), hx(b)
    return "#%02x%02x%02x" % tuple(round(a[i] + (b[i] - a[i]) * f) for i in range(3))


def gradiente(t, x0, y0, x1, y1, cores, passos=4):
    """Gradiente vertical por varias cores, com dither ordenado nas passagens.
    Entre cada par de cores entram tons intermediarios: o dither fica entre
    cores quase iguais e o ceu sai liso, como no Stardew, sem o xadrez."""
    if passos > 1 and len(cores) > 1:
        finas = []
        for a, b in zip(cores, cores[1:]):
            finas += [_mistura(a, b, k / float(passos)) for k in range(passos)]
        cores = finas + [cores[-1]]
    n = len(cores) - 1
    for y in range(int(y0), int(y1)):
        f = (y - y0) / max(y1 - y0 - 1, 1) * n
        i = min(int(f), n - 1)
        r = f - i
        for x in range(int(x0), int(x1)):
            limiar = (BAYER[y % 4][x % 4] + .5) / 16.0
            t.put(x, y, cores[i + 1] if r > limiar else cores[i])


# ------------------------------------------------------------------ ceu

def nuvem(t, cx, cy, larg, luz, meio, sombra, seed=1, alto=1.0):
    """Nuvem fofa de fundo reto: cachos de bolas, borda de cima iluminada e a
    barriga mais fria. "alto" estica para cima (cumulus)."""
    R = rng(seed)
    tmp = Tela(t.w, t.h)
    bolas = []
    n = max(3, int(larg / 4))
    for i in range(n):
        f = i / max(n - 1, 1)
        r = (3 + 4 * math.sin(math.pi * f) ** 0.8) * alto * R.uniform(.8, 1.15)
        bolas.append((cx - larg / 2 + f * larg + R.uniform(-1, 1), cy - r * .45, max(2, r)))
    for x, y, r in bolas:
        tmp.disco(x, y, r, meio, sy=0.85)
    base = int(cy + 2)
    for y in range(t.h):
        for x in range(t.w):
            if not tmp.get(x, y)[3]:
                continue
            if y > base:
                continue
            acima = tmp.get(x, y - 1)[3] == 0
            esq = tmp.get(x - 1, y)[3] == 0
            if y >= base - 1:
                cor = sombra
            elif acima or (esq and y < cy - 1):
                cor = luz
            elif y >= base - 3 and (x + y) % 2:
                cor = sombra
            else:
                cor = meio
            t.put(x, y, cor)


def estrelas(t, x0, y0, x1, y1, n, seed=3, cor="#f4f0ff"):
    R = rng(seed)
    for _ in range(n):
        x, y = R.randrange(x0, x1), R.randrange(y0, y1)
        t.put(x, y, cor)
        if R.random() < .15:  # uma ou outra cintila em cruz
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                t.mix(x + dx, y + dy, cor, 0.45)


def passaros(t, pontos, cor="#3a3048"):
    for x, y in pontos:
        for dx, dy in ((0, 0), (1, -1), (2, 0), (3, -1), (4, 0)):
            t.put(x + dx, y + dy, cor)


# ------------------------------------------------------------- paisagem

def serra(t, base, picos, cor, cor_topo, x0=0, x1=None):
    """Silhueta de morro a partir de picos gaussianos (x, altura, largura)."""
    x1 = t.w if x1 is None else x1
    for x in range(x0, x1):
        h = 0
        for px_, py, larg in picos:
            h = max(h, py * math.exp(-((x - px_) / larg) ** 2))
        h += 1.2 * math.sin(x / 3.7) + 0.8 * math.sin(x / 1.9)
        topo = int(base - h)
        for y in range(topo, base):
            t.put(x, y, cor_topo if y < topo + 2 else cor)


def neblina(t, y0, y1, cor="#f2eef2", forca=0.4, seed=1):
    """Faixa de neblina que some para cima e para baixo, com fiapos."""
    R = rng(seed)
    meio = (y0 + y1) / 2.0
    for y in range(int(y0), int(y1)):
        f = 1 - abs(y - meio) / ((y1 - y0) / 2.0)
        for x in range(t.w):
            fiapo = 0.7 + 0.3 * math.sin(x / 9.0 + y * .7 + seed)
            t.mix(x, y, cor, max(0, forca * f * fiapo))


def copa(t, cx, cy, r, cores, seed=1, achatada=0.85):
    """Copa de arvore em cachos: bolas de folha sobrepostas, cada uma com
    sombra embaixo a direita, luz em cima a esquerda e uns brilhos.
    cores = (escura, media, clara, brilho)."""
    escura, media, clara, brilho = cores
    R = rng(seed)
    bolas = [(cx, cy, r * .7)]
    for _ in range(int(5 + r * .9)):
        a = R.uniform(0, 2 * math.pi)
        d = R.uniform(r * .2, r * .75)
        bolas.append((cx + math.cos(a) * d, cy + math.sin(a) * d * achatada, R.uniform(r * .32, r * .52)))
    bolas.sort(key=lambda b: b[1])  # de tras (em cima) para a frente (embaixo)
    for x, y, rr in bolas:
        t.disco(x, y, rr, escura, sy=achatada)
        t.disco(x - rr * .18, y - rr * .2, rr * .82, media, sy=achatada)
        t.disco(x - rr * .34, y - rr * .38, rr * .5, clara, sy=achatada)
        for _ in range(2):
            t.put(x - rr * R.uniform(.2, .6), y - rr * R.uniform(.3, .7), brilho)
    for _ in range(int(r * 1.4)):  # folhinhas soltas na borda
        a = R.uniform(0, 2 * math.pi)
        t.put(cx + math.cos(a) * r * 1.02, cy + math.sin(a) * r * achatada * 1.02, media)


def arvore(t, x, chao, alt, r, cores, tronco=("#6a4a32", "#4e3424", "#8a6446"), seed=1):
    """Arvore inteira: tronco com raiz e casca, copa em cachos por cima."""
    cor, sombra, luz = tronco
    larg = max(2, int(r * .22))
    for y in range(int(chao - alt), int(chao)):
        abre = 1 if y > chao - 3 else 0
        for x0 in range(-larg // 2 - abre, larg - larg // 2 + abre):
            c = luz if x0 == -larg // 2 - abre else (sombra if x0 >= larg // 2 - 1 else cor)
            t.put(x + x0, y, c)
        if (y * 7) % 5 == 0:
            t.put(x, y, sombra)
    copa(t, x, chao - alt - r * .35, r, cores, seed)


VERDES_MATA = ("#2c5a3a", "#3f7a45", "#5f9a4c", "#8cc06a")
VERDES_DIA = ("#3a6a32", "#56913f", "#7db94e", "#b4dc78")
VERDES_MADRUGADA = ("#2a3e48", "#36565a", "#4c7262", "#6a8e74")


def gramado(t, x0, y0, x1, y1, base, escura, clara, flores=(), seed=1, densidade=0.35):
    """Grama com fiapos de duas alturas e flores esparsas."""
    t.rect(x0, y0, x1 - x0, y1 - y0, base)
    R = rng(seed)
    for y in range(int(y0), int(y1)):
        for x in range(int(x0), int(x1)):
            r = R.random()
            if r < densidade * .5:
                t.put(x, y, escura)
                t.put(x, y - 1, escura)
            elif r < densidade:
                t.put(x, y, clara)
            elif flores and r > 0.994:
                t.put(x, y, R.choice(flores))
                t.put(x, y + 1, escura)


def terra(t, x0, y0, x1, y1, base, escura, clara, seed=1):
    """Chao de terra batida com pedrinhas e marcas."""
    t.rect(x0, y0, x1 - x0, y1 - y0, base)
    R = rng(seed)
    for _ in range(int((x1 - x0) * (y1 - y0) * .05)):
        x, y = R.randrange(int(x0), int(x1)), R.randrange(int(y0), int(y1))
        t.put(x, y, R.choice((escura, clara, escura)))
    for _ in range(int((x1 - x0) * (y1 - y0) * .004)):
        x, y = R.randrange(int(x0), int(x1) - 2), R.randrange(int(y0), int(y1))
        t.hline(x, x + 1, y, "#b8ad9c")
        t.put(x + 2, y, "#8a8070")
        t.hline(x, x + 2, y + 1, "#5a5046")


# ---------------------------------------------------------------- madeira

def tabuas(t, x0, y0, x1, y1, tons, junta, larg=6, seed=1, vertical=True, pregos=True):
    """Parede ou piso de tabuas: cada tabua num tom, veio, no e prego."""
    R = rng(seed)
    if vertical:
        x = x0
        while x < x1:
            w = larg + R.choice((0, 0, 1, -1))
            tom = R.choice(tons)
            t.rect(x, y0, min(w, x1 - x), y1 - y0, tom)
            t.vline(x, y0, y1 - 1, junta)
            t.vline(x + 1, y0, y1 - 1, tons[0] if tom != tons[0] else tons[-1])
            for _ in range(int((y1 - y0) / 14)):
                gx = x + R.randint(2, max(2, w - 2))
                gy = R.randrange(int(y0), int(y1))
                t.vline(gx, gy, gy + R.randint(2, 5), junta)
                if R.random() < .5:
                    t.mix(gx, gy, junta, .5)
            if R.random() < .35 and y1 - y0 > 6:  # no da madeira (so em tabua alta)
                nx, ny = x + w // 2, R.randrange(int(y0) + 2, int(y1) - 2)
                t.put(nx, ny, junta)
                t.put(nx, ny + 1, junta)
                t.put(nx - 1, ny + 1, tom)
            if pregos:
                t.put(x + w // 2, y0 + 2, junta)
            x += w
    else:
        y = y0
        while y < y1:
            h = larg + R.choice((0, 0, 1))
            tom = R.choice(tons)
            t.rect(x0, y, x1 - x0, min(h, y1 - y), tom)
            t.hline(x0, x1 - 1, y, junta)
            t.hline(x0, x1 - 1, y + 1, tons[-1])
            corte = R.randrange(int(x0), int(x1))
            t.vline(corte, y, y + h - 1, junta)
            for _ in range(int((x1 - x0) / 10)):
                gx, gy = R.randrange(int(x0), int(x1)), y + R.randint(2, max(2, h - 1))
                t.hline(gx, gx + R.randint(2, 6), gy, junta)
            y += h


def telhado_por_dentro(t, x0, x1, y0, y1, seed=1):
    """Casa sem forro: o telhado visto de baixo. Fiadas de telha de barro
    (mais escuras la em cima, longe da luz), ripas e caibros, e a linha (a
    viga de travar) atravessando embaixo."""
    R = rng(seed)
    for y in range(y0, y1):
        f = (y - y0) / max(y1 - y0, 1)
        base = "#6e3424" if f < .3 else ("#8a4430" if f < .65 else "#a5553a")
        luz = "#9a4c34" if f < .3 else ("#b5603f" if f < .65 else "#c97448")
        for x in range(x0, x1):
            t.put(x, y, luz if (x // 5 + (y // 3) % 2) % 2 == 0 and y % 3 == 0 else base)
        if y % 3 == 2:
            t.hline(x0, x1 - 1, y, "#4a2218")
    for y in range(y0, y1, 6):  # ripas
        t.hline(x0, x1 - 1, y, "#7a5236")
    for x in range(x0 + 4, x1, 16):  # caibros
        t.rect(x, y0, 3, y1 - y0, "#6a4630")
        t.vline(x, y0, y1 - 1, "#8a6446")
        t.vline(x + 2, y0, y1 - 1, "#4a3020")
    for _ in range(int((x1 - x0) / 25)):  # frestas de luz entre as telhas
        x, y = R.randrange(x0, x1), R.randrange(y0, y1 - 4)
        t.put(x, y, "#ffd890")
    t.rect(x0, y1 - 1, x1 - x0, 4, "#7a5236")  # linha
    t.hline(x0, x1 - 1, y1 - 1, "#9a6c48")
    t.hline(x0, x1 - 1, y1 + 2, "#3a2418")
    escurecer(t, x0, y0, x1 - 1, y0 + int((y1 - y0) * .4), 0.25)


def piso_tabuado(t, x0, x1, y0, y1, tons=("#a87448", "#9a6a40", "#b07c4e"), junta="#5f3e22", seed=1):
    """Piso de tabuas visto de cima e de longe: as tabuas correm na
    horizontal e engrossam para baixo, que da a perspectiva."""
    R = rng(seed)
    y = y0
    h = 2
    while y < y1:
        tom = R.choice(tons)
        t.rect(x0, y, x1 - x0, min(h, y1 - y), tom)
        t.hline(x0, x1 - 1, y, junta)
        x = x0 + R.randint(0, 20)
        while x < x1:
            t.vline(x, y, y + h - 1, junta)
            x += R.randint(18, 30)
        for _ in range(int((x1 - x0) / 14)):
            gx = R.randrange(x0, x1)
            t.hline(gx, gx + R.randint(2, 5), y + h - 1, tons[0])
        y += h
        h = min(h + 1, 5)


def tapete_retalho(t, x0, y0, w, h, cores, seed=1):
    R = rng(seed)
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            t.put(x, y, cores[((x - x0) // 3 + (y - y0) // 2 + R.choice((0, 0, 1))) % len(cores)])
    t.hline(x0, x0 + w - 1, y0, "#f2e6d6")
    t.hline(x0, x0 + w - 1, y0 + h - 1, "#8a6a4a")
    for x in range(x0, x0 + w, 2):  # franja
        t.put(x, y0 + h, "#e8dcc6")
