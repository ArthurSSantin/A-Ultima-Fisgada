"""As cinco especies da Fase 1, desenhadas em resolucao nativa e exportadas em 2x.

Todo peixe sai virado para a direita (cabeca na direita, rabo na esquerda), que
e como o cais mostra a captura. Para cada especie saem dois arquivos: o peixe e
a sombra, o vulto escuro que aparece na agua.

    cd tools/arte
    python peixes_arte.py ../../assets/sprites/peixes

A silhueta de cada especie vem de dois perfis de pontos de controle, um para as
costas e outro para a barriga: pares (u, meia_altura), com u de 0 na ponta do
rabo a 1 no focinho. E so mexer nesses numeros para engordar ou afinar um peixe.
"""
import math
import sys

from px import Tela, rng

OUT = sys.argv[1] if len(sys.argv) > 1 else "."

OL = "#171d1a"  # contorno, o mesmo para todas as especies


# --------------------------------------------------------------- base do corpo

def _interpolar(pontos, u):
    """Altura no ponto u, interpolando suave entre os pontos de controle."""
    for i in range(len(pontos) - 1):
        u0, h0 = pontos[i]
        u1, h1 = pontos[i + 1]
        if u0 <= u <= u1:
            f = (u - u0) / max(u1 - u0, 1e-6)
            f = f * f * (3.0 - 2.0 * f)  # smoothstep, para nao ficar facetado
            return h0 + (h1 - h0) * f
    return pontos[-1][1]


def perfil(L, costas, barriga):
    """Meia-altura das costas e da barriga para cada uma das L colunas."""
    return [
        (_interpolar(costas, (x + 0.5) / L), _interpolar(barriga, (x + 0.5) / L))
        for x in range(L)
    ]


def pintar_corpo(t, x0, cy, colunas, dorso, meio, ventre):
    """Preenche o corpo em tres faixas: dorso escuro, meio e barriga clara."""
    for i, (cima, baixo) in enumerate(colunas):
        x = x0 + i
        topo, base = cy - cima, cy + baixo
        altura = base - topo
        if altura < 1.0:
            continue
        for y in range(int(round(topo)), int(round(base)) + 1):
            f = (y - topo) / altura
            if f < 0.26:
                cor = dorso
            elif f < 0.38:
                cor = dorso if (x + y) % 2 == 0 else meio
            elif f < 0.64:
                cor = meio
            elif f < 0.76:
                cor = meio if (x + y) % 2 == 0 else ventre
            else:
                cor = ventre
            t.put(x, y, cor)


def listras(t, x0, cy, colunas, cor, passo, de=0.0, ate=1.0):
    """Barras verticais no lombo, como as da tilapia."""
    n = len(colunas)
    for i, (cima, baixo) in enumerate(colunas):
        if i % passo or not (de * n <= i <= ate * n):
            continue
        for y in range(int(cy - cima) + 1, int(cy + baixo * 0.3)):
            if (x0 + i + y) % 2 == 0:
                t.put(x0 + i, y, cor)


def escamas(t, x0, cy, colunas, cor, passo=3):
    """Meia-lua alternada no meio do corpo, a assinatura da carpa."""
    for i in range(1, len(colunas) - 1):
        cima, baixo = colunas[i]
        for k in range(-3, 4):
            y = cy + k * 2
            x = x0 + i + (k % 2)
            if i % passo != (k % 2) or not (cy - cima + 1 < y < cy + baixo - 1):
                continue
            if t.get(x, y)[3] and t.get(x + 1, y + 1)[3]:
                t.put(x, y, cor)
                t.put(x + 1, y + 1, cor)


def nadadeira(t, pontos, cor, raios=None):
    """Triangulo preenchido, com raios internos de uma cor mais escura."""
    (ax, ay), (bx, by), (cx, cy) = pontos
    minx, maxx = int(min(ax, bx, cx)), int(max(ax, bx, cx))
    miny, maxy = int(min(ay, by, cy)), int(max(ay, by, cy))

    def lado(px, py, qx, qy, rx, ry):
        return (qx - px) * (ry - py) - (qy - py) * (rx - px)

    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            d1 = lado(ax, ay, bx, by, x + .5, y + .5)
            d2 = lado(bx, by, cx, cy, x + .5, y + .5)
            d3 = lado(cx, cy, ax, ay, x + .5, y + .5)
            if not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0)):
                t.put(x, y, cor)
    if raios:
        for k in range(6):
            fx = bx + (cx - bx) * k / 5.0
            fy = by + (cy - by) * k / 5.0
            n = int(max(abs(fx - ax), abs(fy - ay)))
            for s in range(n):
                if s % 2 == 0:
                    t.put(ax + (fx - ax) * s / max(n, 1), ay + (fy - ay) * s / max(n, 1), raios)


def crista(t, x0, cy, colunas, de, ate, altura, cor, raios, para_cima=True):
    """Nadadeira comprida acompanhando as costas (ou a barriga)."""
    n = len(colunas)
    i0, i1 = int(de * n), int(ate * n)
    for i in range(i0, i1):
        f = (i - i0) / max(i1 - i0 - 1, 1)
        h = altura * max(math.sin(math.pi * f), 0.0) ** 0.55
        alt = colunas[i][0] if para_cima else colunas[i][1]
        passo = range(int(cy - alt - h), int(cy - alt) + 1) if para_cima \
            else range(int(cy + alt), int(cy + alt + h) + 1)
        if h < 0.6:
            continue
        borda = int(cy - alt - h) if para_cima else int(cy + alt + h)
        for y in passo:
            # Nadadeira fina fica chapada: a 1 px de altura, raio vira serrilha.
            raio = h >= 2.2 and i % 4 == 0 and abs(y - borda) < h * 0.7
            t.put(x0 + i, y, raios if (y == borda or raio) else cor)


def rabo(t, x0, cy, largura, abertura, cor, raios, fenda=0.45, barras=None):
    """Leque da cauda, a esquerda do corpo. fenda=0 deixa a ponta arredondada.

    Com "barras" a cauda sai listrada na vertical, que e o que faz uma tilapia
    parecer uma tilapia mesmo nesse tamanho.
    """
    for i in range(largura):
        f = i / max(largura - 1, 1)
        alt = 1.2 + (abertura - 1.2) * (f ** 1.3)
        corte = alt * fenda * (f ** 1.9)
        for y in range(int(cy - alt), int(cy + alt) + 1):
            if abs(y + .5 - cy) < corte:
                continue
            if barras and i % 2 == 1:
                t.put(x0 - i, y, barras)
            else:
                raio = i > 1 and (y - int(cy)) % 3 == 0
                t.put(x0 - i, y, raios if raio else cor)


def olho(t, x, y, escuro=OL):
    """Dois por dois de pupila com um brilho no canto: o que cabe nessa escala."""
    t.rect(x, y, 2, 2, escuro)
    t.put(x, y, "#ffffff")


def boca(t, x, y, cor, largura=2):
    t.hline(x, x + largura - 1, y, cor)


def barbilhao(t, x, y, comprimento, queda, cor):
    """Bigode do bagre: sai do canto da boca e cai desenhando uma curva."""
    for i in range(comprimento):
        f = i / max(comprimento - 1, 1)
        t.put(x + i, y + queda * (f ** 1.7), cor)


def sombra_de(t):
    """Mesma silhueta em tom chapado, que e o vulto visto de cima na agua."""
    s = Tela(t.w, t.h)
    for y in range(t.h):
        for x in range(t.w):
            r, g, b, a = t.get(x, y)
            if a:
                luz = (r + g + b) / 765.0
                s.put(x, y, "#2c3f46d9" if luz > 0.45 else "#1d2b31d9")
    return s


# ------------------------------------------------------------------- especies

def tilapia():
    """Tilapia: corpo alto e comprimido, dorsal espinhosa correndo as costas
    inteiras, barras escuras no flanco e a cauda listrada."""
    t = Tela(34, 20)
    x0, cy, L = 7, 11, 25
    cols = perfil(L, costas=[(0, 1.6), (.14, 3.8), (.36, 5.4), (.60, 5.6), (.80, 4.8), (.92, 3.4), (1, 1.8)],
                     barriga=[(0, 1.4), (.18, 3.4), (.44, 4.8), (.68, 4.4), (.86, 2.9), (1, 1.5)])
    DORSO, MEIO, VENTRE = "#43594c", "#8ba291", "#dde2d2"
    FINA, FINA_OL, ROSA = "#90ab98", "#3d5146", "#c97f72"

    rabo(t, x0 - 1, cy, 7, 6.0, "#a8bfae", FINA_OL, fenda=0.20, barras="#4f6659")
    # dorsal unica correndo as costas inteiras, da nuca ate o pedunculo
    crista(t, x0, cy, cols, .04, .84, 4.2, FINA, FINA_OL)
    crista(t, x0, cy, cols, .12, .60, 2.6, FINA, FINA_OL, para_cima=False)
    pintar_corpo(t, x0, cy, cols, DORSO, MEIO, VENTRE)
    listras(t, x0, cy, cols, "#4b6256", 3, de=.08, ate=.82)
    nadadeira(t, [(x0 + 18, cy + 1), (x0 + 13, cy + 6), (x0 + 19, cy + 5)], "#9db5a4", FINA_OL)
    t.vline(x0 + 19, cy - 4, cy + 3, "#7d9a86")        # opérculo
    t.put(x0 + 19, cy + 2, ROSA)                       # a mancha rosada da guelra
    t.put(x0 + 20, cy + 3, ROSA)
    olho(t, x0 + 21, cy - 2)
    boca(t, x0 + 23, cy + 1, "#3d5146")
    t.contorno(OL)
    return t


def cascudo():
    """Cascudo: barriga reta de peixe de fundo, lombo arqueado, couraca de
    placas pintadas, dorsal em vela e peitorais abertas. A boca e uma ventosa
    virada para baixo, e os olhos ficam no alto da cabeca achatada."""
    t = Tela(34, 19)
    x0, cy, L = 7, 11, 24
    cols = perfil(L, costas=[(0, 1.4), (.14, 3.2), (.40, 4.4), (.64, 4.6), (.84, 3.8), (1, 2.0)],
                     barriga=[(0, 1.1), (.18, 2.0), (.50, 2.2), (.82, 2.2), (1, 1.4)])
    DORSO, MEIO, VENTRE = "#473524", "#8a6c43", "#c6ab7c"
    FINA, FINA_OL = "#6d5330", "#3c2d1c"

    # cauda de lobos desiguais, o de baixo um pouco mais comprido
    rabo(t, x0 - 1, cy, 7, 5.2, "#9c7a49", FINA_OL, fenda=0.34)
    for i in range(4):
        t.vline(x0 - 3 - i, cy + 2 + i, cy + 3 + i, "#9c7a49")
    # vela dorsal: o traco do cascudo, alta e inclinada para tras
    nadadeira(t, [(x0 + 7, cy - 4), (x0 + 17, cy - 4), (x0 + 9, cy - 11)], "#a8884f", FINA_OL)
    for k in range(5):  # raios da vela
        t.put(x0 + 9 + k, cy - 9 + k, FINA_OL)
    crista(t, x0, cy, cols, .14, .50, 1.6, FINA, FINA_OL, para_cima=False)
    pintar_corpo(t, x0, cy, cols, DORSO, MEIO, VENTRE)

    R = rng(21)
    for _ in range(34):  # pintas escuras espalhadas pela couraca
        x, y = R.randrange(x0 + 1, x0 + L - 1), R.randrange(cy - 4, cy + 2)
        if t.get(x, y)[3]:
            t.put(x, y, "#3f3020")
            if R.random() < .4:
                t.put(x + 1, y, "#3f3020")
    for x in range(x0 + 2, x0 + L - 3, 3):  # fiadas de placas osseas
        t.put(x, cy - 2, "#a8884f")
        t.put(x + 1, cy, "#a8884f")

    # peitoral larga e espalhada, apoiada no fundo
    nadadeira(t, [(x0 + 18, cy), (x0 + 11, cy + 5), (x0 + 19, cy + 4)], "#a8884f", FINA_OL)
    t.hline(x0 + 12, x0 + 18, cy + 4, FINA_OL)
    # cabeca achatada: olho no alto e ventosa por baixo
    t.vline(x0 + 19, cy - 3, cy + 2, "#9c7a49")
    olho(t, x0 + 20, cy - 3)
    for x in range(x0 + 21, x0 + 24):
        t.put(x, cy + 2, "#3f3020")
    t.put(x0 + 22, cy + 3, "#3f3020")
    t.put(x0 + 21, cy + 3, "#5c4529")
    t.put(x0 + 23, cy + 3, "#5c4529")
    t.contorno(OL)
    return t


def carpa():
    """Carpa: corpo alto e grosso, escamas grandes em fiadas, dorsal comprida
    de borda recortada e dois pares de barbilhoes nos beicos."""
    t = Tela(36, 23)
    x0, cy, L = 8, 12, 25
    cols = perfil(L, costas=[(0, 2.0), (.14, 4.4), (.34, 6.4), (.56, 6.8), (.78, 5.8), (.92, 4.2), (1, 2.4)],
                     barriga=[(0, 1.7), (.18, 4.0), (.44, 5.8), (.70, 5.4), (.88, 3.8), (1, 2.2)])
    DORSO, MEIO, VENTRE = "#6a4a1e", "#cf9a3f", "#f3dc9e"
    FINA, FINA_OL = "#d2a349", "#67481d"

    rabo(t, x0 - 1, cy, 7, 6.8, FINA, FINA_OL, fenda=0.50)
    crista(t, x0, cy, cols, .06, .78, 4.0, FINA, FINA_OL)
    crista(t, x0, cy, cols, .12, .54, 2.6, FINA, FINA_OL, para_cima=False)
    pintar_corpo(t, x0, cy, cols, DORSO, MEIO, VENTRE)
    escamas(t, x0, cy, cols, "#a8792f", passo=3)
    escamas(t, x0 + 1, cy + 1, cols, "#e8bc63", passo=3)
    nadadeira(t, [(x0 + 19, cy + 1), (x0 + 14, cy + 6), (x0 + 20, cy + 5)], "#e0b14e", FINA_OL)
    t.vline(x0 + 19, cy - 4, cy + 3, "#e0b14e")
    olho(t, x0 + 21, cy - 3)
    # beicos grossos e os quatro barbilhoes
    t.hline(x0 + 22, x0 + 24, cy + 1, "#5c3f19")
    t.put(x0 + 24, cy, "#8a6327")
    t.put(x0 + 24, cy + 2, "#8a6327")
    barbilhao(t, x0 + 24, cy + 1, 3, 2, "#8a6327")
    barbilhao(t, x0 + 23, cy + 3, 3, 2, "#8a6327")
    t.contorno(OL)
    return t


def _bagre(t, x0, cy, L, altura, cores, escala=1.0, musgo=False, seed=7):
    """Corpo de jundia: bagre de couro, sem escama, cabeca larga e achatada,
    dorsal curta com espinho, adiposa bem atras e seis barbilhoes."""
    DORSO, MEIO, VENTRE, FINA = cores
    FINA_OL = DORSO
    a = altura
    cols = perfil(L,
        costas=[(0, .38 * a), (.14, .78 * a), (.40, .98 * a), (.62, 1.0 * a), (.84, .94 * a), (1, .58 * a)],
        barriga=[(0, .32 * a), (.16, .70 * a), (.46, .88 * a), (.72, .88 * a), (.92, .70 * a), (1, .44 * a)])

    rabo(t, x0 - 1, cy, int(6 * escala), a * 1.4, MEIO, FINA, fenda=0.42)
    crista(t, x0, cy, cols, .16, .40, 1.7 * escala, FINA, FINA_OL)   # adiposa
    crista(t, x0, cy, cols, .06, .44, 1.5 * escala, FINA, FINA_OL, para_cima=False)
    pintar_corpo(t, x0, cy, cols, DORSO, MEIO, VENTRE)

    # dorsal curta e alta, com o primeiro raio virando espinho
    dx = x0 + int(L * 0.58)
    topo = cy - cols[int(L * 0.58)][0]
    nadadeira(t, [(dx, topo - 3.4 * escala), (dx - 3 * escala, topo + 1), (dx + 2 * escala, topo + 1)],
              FINA, FINA_OL)
    t.vline(dx + int(2 * escala), int(topo - 2.6 * escala), int(topo), DORSO)
    px_ = x0 + int(L * 0.76)
    base = cy + cols[int(L * 0.76)][1]
    nadadeira(t, [(px_, base - 1), (px_ - 4 * escala, base + 2.2 * escala), (px_ + 2, base + escala)],
              FINA, FINA_OL)

    R = rng(seed)
    for _ in range(int(20 * escala)):  # pele marmorizada do lombo
        x, y = R.randrange(x0 + 2, x0 + L - 3), R.randrange(int(cy - a) + 1, int(cy))
        if t.get(x, y)[3]:
            t.put(x, y, DORSO)
            if R.random() < .4:
                t.put(x + 1, y + 1, DORSO)
    if musgo:
        for _ in range(14):  # limo e cicatrizes de peixe velho
            x, y = R.randrange(x0 + 2, x0 + L - 6), R.randrange(int(cy - a) + 1, int(cy + a * .4))
            if t.get(x, y)[3]:
                t.put(x, y, "#4c6b4a")
                if R.random() < .5:
                    t.put(x + 1, y, "#3d5a3d")

    # cabeca: larga, baixa e de boca rasgada
    cab = x0 + L - 1
    t.vline(cab - 4, int(cy - a * .66), int(cy + a * .60), MEIO)
    olho(t, cab - 3, int(cy - a * .50))
    t.hline(cab - 2, cab, cy + 1, DORSO)
    t.put(cab, cy, DORSO)
    # seis barbilhoes: um par longo em cima, dois pares curtos no queixo
    barbilhao(t, cab + 1, cy - 1, int(8 * escala), 4 * escala, MEIO)
    barbilhao(t, cab + 1, cy, int(6 * escala), 5 * escala, FINA)
    barbilhao(t, cab, cy + 2, int(4 * escala), 3 * escala, MEIO)
    barbilhao(t, cab - 2, cy + int(a * .72), int(3 * escala), 2 * escala, MEIO)
    return t


def jundia():
    t = Tela(38, 17)
    _bagre(t, 7, 8, L=27, altura=4.0,
           cores=("#45413c", "#8d8176", "#dbd0be", "#6a6158"), escala=1.0, seed=7)
    t.contorno(OL)
    return t


def jundia_gigante():
    """O mesmo bagre, mas de outro porte: quase o dobro do comprimento do
    jundia comum, escuro de limo e com o lombo marcado. E o peixe que fecha a
    fase, entao tem de dar para ver de longe que nao e um jundia qualquer."""
    t = Tela(56, 26)
    _bagre(t, 8, 13, L=42, altura=6.6,
           cores=("#272e27", "#55614e", "#a9b08e", "#3c4439"), escala=1.5, musgo=True, seed=13)
    t.contorno(OL)
    return t


# ------------------------------------------------- Foz e Vila e Arvoredo
# Peixes de estuario e de mar, para os dois pesqueiros rio abaixo. Usam as
# mesmas pecas dos peixes do acude.

def faixa_lateral(t, x0, cy, colunas, cor, frac, de=0.0, ate=1.0, pontilhada=False):
    """Linha ao longo do corpo, a uma fracao da altura (0 nas costas, 1 na
    barriga): a linha lateral do robalo, as listras da tainha."""
    n = len(colunas)
    for i, (cima, baixo) in enumerate(colunas):
        if not (de * n <= i <= ate * n):
            continue
        if pontilhada and i % 2:
            continue
        y = cy - cima + (cima + baixo) * frac
        if t.get(x0 + i, int(y))[3]:
            t.put(x0 + i, y, cor)


def pintas(t, x0, cy, L, alt, cores, n, seed, tam=1):
    """Manchas espalhadas pelo corpo (garoupa, linguado, mero)."""
    R = rng(seed)
    for _ in range(n):
        x, y = R.randrange(x0 + 1, x0 + L - 2), R.randrange(int(cy - alt) + 1, int(cy + alt))
        cor = R.choice(cores)
        for dx in range(tam):
            for dy in range(tam):
                if t.get(x + dx, y + dy)[3]:
                    t.put(x + dx, y + dy, cor)


def tainha():
    """Tainha: fusiforme, dorso azul-esverdeado, flanco prateado com listras
    escuras ao comprido, duas dorsais pequenas e cauda bifurcada."""
    t = Tela(36, 16)
    x0, cy, L = 8, 8, 25
    cols = perfil(L, costas=[(0, 1.3), (.16, 2.8), (.44, 3.9), (.70, 3.8), (.90, 2.8), (1, 1.6)],
                     barriga=[(0, 1.2), (.18, 2.6), (.48, 3.5), (.76, 3.2), (.92, 2.2), (1, 1.3)])
    DORSO, MEIO, VENTRE = "#3c5a63", "#a9bcc2", "#eef2f0"
    FINA, FINA_OL = "#8ea3aa", "#3a4f57"
    rabo(t, x0 - 1, cy, 7, 5.0, FINA, FINA_OL, fenda=0.62)
    nadadeira(t, [(x0 + 13, cy - 4), (x0 + 16, cy - 4), (x0 + 15, cy - 7)], FINA, FINA_OL)
    nadadeira(t, [(x0 + 6, cy - 3), (x0 + 9, cy - 3), (x0 + 7, cy - 5)], FINA, FINA_OL)
    crista(t, x0, cy, cols, .14, .30, 1.6, FINA, FINA_OL, para_cima=False)
    pintar_corpo(t, x0, cy, cols, DORSO, MEIO, VENTRE)
    for f in (.30, .45, .60):
        faixa_lateral(t, x0, cy, cols, "#6f8790", f, .06, .80)
    nadadeira(t, [(x0 + 18, cy), (x0 + 14, cy + 3), (x0 + 19, cy + 2)], "#c7d3d6", FINA_OL)
    t.vline(x0 + 20, cy - 3, cy + 2, "#7d939a")
    olho(t, x0 + 21, cy - 2)
    boca(t, x0 + 23, cy, "#3a4f57")
    t.contorno(OL)
    return t


def robalo():
    """Robalo: alongado e prateado, a linha lateral preta correndo do opérculo
    ao rabo, boca grande de queixo saliente e dorsal espinhosa."""
    t = Tela(42, 18)
    x0, cy, L = 8, 9, 31
    cols = perfil(L, costas=[(0, 1.5), (.14, 3.0), (.40, 4.4), (.66, 4.6), (.86, 3.8), (1, 2.0)],
                     barriga=[(0, 1.3), (.18, 2.8), (.46, 3.9), (.74, 3.8), (.92, 2.6), (1, 1.5)])
    DORSO, MEIO, VENTRE = "#4b5a4f", "#b8c4bd", "#f1f3ef"
    FINA, FINA_OL = "#9aa69e", "#3b463f"
    rabo(t, x0 - 1, cy, 8, 5.6, FINA, FINA_OL, fenda=0.38)
    crista(t, x0, cy, cols, .50, .70, 3.6, FINA, FINA_OL)  # dorsal espinhosa
    crista(t, x0, cy, cols, .22, .44, 2.4, FINA, FINA_OL)  # dorsal mole
    crista(t, x0, cy, cols, .16, .34, 2.0, FINA, FINA_OL, para_cima=False)
    pintar_corpo(t, x0, cy, cols, DORSO, MEIO, VENTRE)
    faixa_lateral(t, x0, cy, cols, "#1f2622", .40, .02, .84)
    nadadeira(t, [(x0 + 23, cy + 1), (x0 + 19, cy + 4), (x0 + 24, cy + 3)], "#cbd3cd", FINA_OL)
    t.vline(x0 + 24, cy - 4, cy + 3, "#7f8c84")
    olho(t, x0 + 26, cy - 2)
    # boca rasgada e o queixo passando da maxila
    t.hline(x0 + 27, x0 + 30, cy + 1, "#3b463f")
    t.put(x0 + 31, cy + 1, "#3b463f")
    t.put(x0 + 31, cy + 2, "#7f8c84")
    t.contorno(OL)
    return t


def bagre_do_mar():
    """Bagre de estuario: o mesmo corpo do jundia, mas cinza-azulado, de
    barriga branca e com o rabo bem bifurcado."""
    t = Tela(38, 17)
    _bagre(t, 7, 8, L=27, altura=3.8,
           cores=("#47545e", "#8c9aa5", "#e7ebee", "#6a7884"), escala=1.0, seed=31)
    # o rabo bifurcado por cima do leque redondo do jundia
    for i in range(3):
        t.put(6 - i, 8, (0, 0, 0, 0))
        t.put(6 - i, 9, (0, 0, 0, 0))
    t.contorno(OL)
    return t


def corvina():
    """Corvina: costas arqueadas e barriga quase reta, prateada com reflexo
    dourado, linhas obliquas escuras no lombo e cauda reta."""
    t = Tela(36, 18)
    x0, cy, L = 7, 9, 26
    cols = perfil(L, costas=[(0, 1.6), (.16, 3.4), (.46, 5.4), (.70, 5.0), (.88, 3.6), (1, 1.8)],
                     barriga=[(0, 1.3), (.18, 2.6), (.50, 3.4), (.78, 3.2), (.92, 2.4), (1, 1.4)])
    DORSO, MEIO, VENTRE = "#6b6747", "#c9bf91", "#f2ecd5"
    FINA, FINA_OL = "#c2ac6a", "#5a5131"
    rabo(t, x0 - 1, cy, 6, 4.6, FINA, FINA_OL, fenda=0.0)
    crista(t, x0, cy, cols, .14, .76, 3.0, FINA, FINA_OL)
    crista(t, x0, cy, cols, .16, .36, 2.0, FINA, FINA_OL, para_cima=False)
    pintar_corpo(t, x0, cy, cols, DORSO, MEIO, VENTRE)
    for i in range(2, L - 6, 3):  # as riscas obliquas da corvina
        for k in range(4):
            x, y = x0 + i + k, cy - cols[i][0] + 1 + k
            if t.get(x, y)[3]:
                t.put(x, y, "#7a6f44")
    nadadeira(t, [(x0 + 18, cy + 1), (x0 + 14, cy + 4), (x0 + 19, cy + 3)], "#e0cd8a", FINA_OL)
    t.vline(x0 + 19, cy - 4, cy + 2, "#a39668")
    olho(t, x0 + 21, cy - 2)
    boca(t, x0 + 22, cy + 2, "#5a5131")
    barbilhao(t, x0 + 21, cy + 3, 2, 1, "#a39668")
    t.contorno(OL)
    return t


def linguado():
    """Linguado: peixe chato, de corpo oval e baixo, com a franja das
    nadadeiras contornando o corpo todo, pele parda de pintas e os dois olhos
    no lado de cima da cabeca."""
    t = Tela(38, 18)
    x0, cy, L = 7, 9, 28
    cols = perfil(L, costas=[(0, 1.0), (.12, 2.6), (.40, 4.2), (.70, 4.2), (.90, 3.0), (1, 1.4)],
                     barriga=[(0, 1.0), (.12, 2.4), (.40, 3.8), (.70, 3.8), (.90, 2.6), (1, 1.2)])
    DORSO, MEIO, VENTRE = "#6b5638", "#9c8158", "#b89a6a"
    FINA, FINA_OL = "#8a7048", "#4a3b25"
    rabo(t, x0 - 1, cy, 5, 3.6, FINA, FINA_OL, fenda=0.0)
    crista(t, x0, cy, cols, .04, .94, 2.2, FINA, FINA_OL)
    crista(t, x0, cy, cols, .04, .88, 2.0, FINA, FINA_OL, para_cima=False)
    pintar_corpo(t, x0, cy, cols, DORSO, MEIO, VENTRE)
    pintas(t, x0, cy, L, 3, ["#4a3b25", "#c9ae7c", "#5b4a2e"], 34, seed=44)
    olho(t, x0 + L - 5, cy - 3)
    olho(t, x0 + L - 3, cy - 1)
    boca(t, x0 + L - 1, cy + 1, "#4a3b25", largura=1)
    t.contorno(OL)
    return t


def pampo():
    """Pampo: alto, quase um losango, prateado com o ventre amarelado,
    dorsal e anal compridas em foice e a cauda funda em V."""
    t = Tela(34, 22)
    x0, cy, L = 9, 11, 20
    cols = perfil(L, costas=[(0, 1.5), (.18, 3.8), (.46, 6.6), (.68, 6.4), (.88, 4.4), (1, 2.0)],
                     barriga=[(0, 1.4), (.18, 3.6), (.46, 6.0), (.68, 5.8), (.88, 3.8), (1, 1.6)])
    DORSO, MEIO, VENTRE = "#5b6c76", "#c6d0d4", "#f0e3a4"
    FINA, FINA_OL = "#c9b765", "#5a5230"
    rabo(t, x0 - 1, cy, 8, 7.0, FINA, FINA_OL, fenda=0.72)
    nadadeira(t, [(x0 + 4, cy - 5), (x0 + 11, cy - 6), (x0 + 6, cy - 10)], FINA, FINA_OL)
    nadadeira(t, [(x0 + 4, cy + 5), (x0 + 11, cy + 6), (x0 + 6, cy + 10)], FINA, FINA_OL)
    pintar_corpo(t, x0, cy, cols, DORSO, MEIO, VENTRE)
    nadadeira(t, [(x0 + 14, cy + 1), (x0 + 10, cy + 4), (x0 + 15, cy + 3)], "#e8dc9a", FINA_OL)
    t.vline(x0 + 15, cy - 4, cy + 3, "#9aa6ab")
    olho(t, x0 + 16, cy - 2)
    boca(t, x0 + 18, cy + 1, "#5a5230")
    t.contorno(OL)
    return t


def anchova():
    """Anchova: torpedo azul-esverdeado de barriga prateada, boca grande com
    dentes, nadadeiras escuras e cauda bifurcada."""
    t = Tela(40, 16)
    x0, cy, L = 8, 8, 29
    cols = perfil(L, costas=[(0, 1.2), (.16, 2.8), (.44, 4.2), (.70, 4.2), (.90, 3.2), (1, 1.8)],
                     barriga=[(0, 1.1), (.18, 2.6), (.48, 3.6), (.76, 3.4), (.92, 2.4), (1, 1.4)])
    DORSO, MEIO, VENTRE = "#2f5f6a", "#8fb2b8", "#eef4f2"
    FINA, FINA_OL = "#4a6e73", "#26434a"
    rabo(t, x0 - 1, cy, 8, 5.4, FINA, FINA_OL, fenda=0.66)
    crista(t, x0, cy, cols, .54, .70, 2.6, FINA, FINA_OL)
    crista(t, x0, cy, cols, .20, .46, 2.0, FINA, FINA_OL)
    crista(t, x0, cy, cols, .18, .40, 1.8, FINA, FINA_OL, para_cima=False)
    pintar_corpo(t, x0, cy, cols, DORSO, MEIO, VENTRE)
    nadadeira(t, [(x0 + 21, cy + 1), (x0 + 17, cy + 4), (x0 + 22, cy + 3)], FINA, FINA_OL)
    t.vline(x0 + 22, cy - 3, cy + 3, "#5f8a90")
    olho(t, x0 + 24, cy - 2)
    t.hline(x0 + 25, x0 + 28, cy + 1, "#26434a")  # boca grande
    t.put(x0 + 26, cy + 2, "#ffffff")            # os dentes
    t.put(x0 + 28, cy + 2, "#ffffff")
    t.contorno(OL)
    return t


def olho_de_boi():
    """Olho-de-boi: robusto e comprido, a faixa amarela do olho ao rabo
    separando o dorso cor de oliva do ventre claro, olho grande e cauda
    amarela."""
    t = Tela(44, 18)
    x0, cy, L = 9, 9, 32
    cols = perfil(L, costas=[(0, 1.4), (.14, 3.2), (.42, 4.8), (.68, 4.9), (.88, 3.8), (1, 2.0)],
                     barriga=[(0, 1.3), (.18, 3.0), (.46, 4.2), (.74, 4.0), (.92, 2.8), (1, 1.4)])
    DORSO, MEIO, VENTRE = "#6b5a2c", "#c7b88c", "#f3eedb"
    FINA, FINA_OL = "#e2b935", "#6b5320"
    rabo(t, x0 - 1, cy, 8, 6.0, FINA, FINA_OL, fenda=0.60)
    crista(t, x0, cy, cols, .44, .64, 3.2, "#b29a52", FINA_OL)
    crista(t, x0, cy, cols, .14, .42, 2.0, "#b29a52", FINA_OL)
    crista(t, x0, cy, cols, .14, .34, 2.0, FINA, FINA_OL, para_cima=False)
    pintar_corpo(t, x0, cy, cols, DORSO, MEIO, VENTRE)
    faixa_lateral(t, x0, cy, cols, "#e8c23a", .44, .02, .96)
    faixa_lateral(t, x0, cy, cols, "#d4ab26", .50, .02, .90)
    nadadeira(t, [(x0 + 24, cy + 1), (x0 + 20, cy + 4), (x0 + 25, cy + 3)], FINA, FINA_OL)
    t.vline(x0 + 25, cy - 4, cy + 3, "#a39266")
    t.rect(x0 + 26, cy - 3, 3, 3, OL)  # o olho grande que da o nome
    t.put(x0 + 26, cy - 3, "#ffffff")
    t.put(x0 + 27, cy - 2, "#e8c23a")
    boca(t, x0 + 29, cy + 1, "#6b5320", largura=3)
    t.contorno(OL)
    return t


def garoupa():
    """Garoupa: corpo grosso de peixe de toca, marrom-avermelhado salpicado de
    manchas claras, cabeca grande de boca larga, cauda e nadadeiras redondas
    com a borda clara."""
    t = Tela(42, 22)
    x0, cy, L = 8, 11, 30
    cols = perfil(L, costas=[(0, 2.2), (.14, 4.2), (.40, 6.2), (.66, 6.6), (.86, 5.6), (1, 3.2)],
                     barriga=[(0, 2.0), (.18, 4.0), (.46, 5.6), (.74, 5.6), (.92, 4.4), (1, 2.6)])
    DORSO, MEIO, VENTRE = "#5e2f22", "#9c5a3c", "#d29a74"
    FINA, FINA_OL = "#86462e", "#3e1f15"
    rabo(t, x0 - 1, cy, 6, 6.0, FINA, "#e3b48c", fenda=0.0)
    crista(t, x0, cy, cols, .06, .78, 3.4, FINA, "#e3b48c")
    crista(t, x0, cy, cols, .10, .38, 2.6, FINA, "#e3b48c", para_cima=False)
    pintar_corpo(t, x0, cy, cols, DORSO, MEIO, VENTRE)
    pintas(t, x0, cy, L, 5, ["#e0b08a", "#c9946c", "#f0c9a2"], 46, seed=57, tam=1)
    nadadeira(t, [(x0 + 21, cy + 1), (x0 + 16, cy + 6), (x0 + 22, cy + 5)], FINA, "#e3b48c")
    t.vline(x0 + 22, cy - 5, cy + 4, "#7a3d28")
    olho(t, x0 + 24, cy - 3)
    # boca larga, de beico grosso
    t.hline(x0 + 25, x0 + 29, cy + 2, "#3e1f15")
    t.hline(x0 + 26, x0 + 29, cy + 3, "#b06a4a")
    t.contorno(OL)
    return t


def mero():
    """O Velho do Arvoredo: um mero enorme, de cabeca larga e corpo de barril,
    escuro de idade e manchado, com as nadadeiras redondas gastas. No canto
    da boca ainda tem o anzol e a ponta da linha que o avo nao cortou."""
    t = Tela(68, 34)
    x0, cy, L = 11, 17, 50
    cols = perfil(L, costas=[(0, 3.4), (.12, 6.6), (.36, 10.6), (.62, 11.4), (.84, 10.0), (1, 6.0)],
                     barriga=[(0, 3.0), (.16, 6.2), (.44, 9.6), (.72, 9.8), (.90, 8.0), (1, 4.6)])
    DORSO, MEIO, VENTRE = "#2e2f23", "#5d5a3f", "#9d9670"
    FINA, FINA_OL = "#45432f", "#7c7656"
    rabo(t, x0 - 1, cy, 9, 9.0, FINA, FINA_OL, fenda=0.0)
    crista(t, x0, cy, cols, .06, .74, 4.6, FINA, FINA_OL)
    crista(t, x0, cy, cols, .08, .34, 3.6, FINA, FINA_OL, para_cima=False)
    pintar_corpo(t, x0, cy, cols, DORSO, MEIO, VENTRE)
    pintas(t, x0, cy, L, 9, ["#1f2018", "#7d7752", "#3b3a2a"], 120, seed=71, tam=2)
    # cicatrizes de briga, riscos claros no lombo
    for x, y in ((x0 + 18, cy - 7), (x0 + 30, cy - 5)):
        for k in range(5):
            t.put(x + k, y + k // 2, "#b3ac86")
    nadadeira(t, [(x0 + 35, cy + 2), (x0 + 27, cy + 10), (x0 + 37, cy + 8)], FINA, FINA_OL)
    t.vline(x0 + 37, cy - 8, cy + 7, "#4d4a34")
    t.vline(x0 + 38, cy - 7, cy + 6, "#66624a")
    olho(t, x0 + 41, cy - 5)
    t.put(x0 + 40, cy - 6, "#9d9670")
    # boca enorme, de beico pesado
    t.hline(x0 + 42, x0 + 49, cy + 3, "#16170f")
    t.hline(x0 + 43, x0 + 49, cy + 4, "#8a7d5c")
    t.hline(x0 + 44, x0 + 48, cy + 2, "#45432f")
    # o anzol enferrujado e a ponta da linha do avo
    t.put(x0 + 47, cy + 5, "#9a5a2a"); t.put(x0 + 47, cy + 6, "#b86d33")
    t.put(x0 + 48, cy + 6, "#9a5a2a"); t.put(x0 + 49, cy + 5, "#9a5a2a")
    for k in range(7):
        t.put(x0 + 50 + k, cy + 6 + k // 2, "#d9e2e6")
    t.contorno(OL)
    return t


ESPECIES = {
    "tilapia": tilapia,
    "cascudo": cascudo,
    "carpa": carpa,
    "jundia": jundia,
    "jundia_gigante": jundia_gigante,
    "tainha": tainha,
    "robalo": robalo,
    "bagre": bagre_do_mar,
    "corvina": corvina,
    "linguado": linguado,
    "pampo": pampo,
    "anchova": anchova,
    "olho_de_boi": olho_de_boi,
    "garoupa": garoupa,
    "mero": mero,
}


if __name__ == "__main__":
    for nome, desenhar in ESPECIES.items():
        t = desenhar()
        t.salvar(f"{OUT}/{nome}.png", escala=2)
        sombra_de(t).salvar(f"{OUT}/{nome}_sombra.png", escala=2)
        print(f"{nome}: {t.w * 2}x{t.h * 2}")
    print("ok")
