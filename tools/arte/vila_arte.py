"""A vila: a rua e os tres interiores, mais a Dona Maria Ivone.

    cd tools/arte
    python vila_arte.py ../../assets/sprites

Tudo e desenhado em 320x180 e exportado em 4x (1280x720), como o resto do jogo.
O CHAO fica sempre na mesma linha: y 130 nativo, que da y 520 na tela, que e
onde o Tiago pisa. Mexer nisso desalinha o personagem em todas as cenas.

A rua e uma imagem so, com as fachadas ja no lugar: as estacoes da cena sao
marcadores invisiveis em cima das portas (ver scripts/lugar.gd).
"""
import math
import sys

from px import Tela, faixas, rng

OUT = sys.argv[1] if len(sys.argv) > 1 else "."

W, H = 320, 180
CHAO = 130

OL = "#2b1d12"


# --------------------------------------------------------------- ferramentas

def ceu_da_vila(t):
    faixas(t, 0, 0, W, [("#4f93d8", 10), ("#5c9fdf", 9), ("#6aabe5", 8), ("#79b7ea", 8),
                        ("#89c3ee", 7), ("#9acef1", 7), ("#abd8f4", 6), ("#bde1f5", 6),
                        ("#cfe8f3", 6), ("#dfeeee", 8)], dither=False)
    R = rng(2)
    for cx, cy, w in ((48, 16, 26), (140, 10, 20), (236, 22, 24), (292, 13, 18)):
        for i in range(w):
            f = i / float(w)
            alt = 3.2 * math.sin(math.pi * f) ** 0.7
            for y in range(int(cy - alt), int(cy + 2)):
                t.put(cx - w // 2 + i, y, "#ffffff" if y < cy else "#d8e9f6")
    # morros atras dos telhados
    for x in range(W):
        h = 0
        for px_, py, larg in ((30, 62, 46), (120, 58, 40), (210, 64, 44), (300, 56, 38)):
            h = max(h, (75 - py) * math.exp(-((x - px_) / larg) ** 2))
        topo = int(75 - h)
        for y in range(topo, 76):
            t.put(x, y, "#7cb565" if y < topo + 2 else "#5f9a4c")
    for x in range(0, W, 3):  # mata rala no alto
        if R.random() < 0.5:
            t.put(x, 73, "#4f8a45")

    # Fundo entre os morros e a rua: quintais, cerca viva e arvores soltas.
    # Sem isso sobra um vao branco atras das casas.
    faixas(t, 0, 76, W, [("#5f9a4c", 6), ("#6aa455", 8), ("#74ad5d", 10),
                         ("#7eb566", 12), ("#88bd6f", 18)], dither=False)
    for _ in range(90):  # moitas e capim do fundo
        x, y = R.randrange(W), R.randrange(78, CHAO - 2)
        t.put(x, y, "#4f8a45" if R.random() < 0.6 else "#96c87c")
    for x, alt, copa in ((8, 10, 6.0), (62, 13, 7.5), (104, 9, 5.0), (162, 12, 6.5),
                         (214, 8, 4.5), (278, 14, 8.0), (310, 10, 5.5)):
        base = CHAO - 4
        t.vline(x, base - alt, base, "#4e3a22")
        t.disco(x, base - alt - copa * 0.4, copa, "#3f7d3c", sy=1.05)
        t.disco(x - copa * 0.35, base - alt - copa * 0.75, copa * 0.5, "#58a04e", sy=1.0)
    for x in range(0, W, 4):  # cerca de madeira separando o fundo da rua
        t.vline(x, CHAO - 9, CHAO - 2, "#8a6a3a")
    t.hline(0, W - 1, CHAO - 8, "#9c7a44")
    t.hline(0, W - 1, CHAO - 5, "#9c7a44")


def chao_de_terra(t, R):
    """Rua de terra batida com poca, pedrinhas e a sombra das construcoes."""
    faixas(t, 0, CHAO, W, [("#a9793f", 3), ("#9c6d38", 5), ("#8e6232", 6), ("#80562b", 8),
                           ("#734a24", 10), ("#66401e", 18)], dither=False)
    t.hline(0, W - 1, CHAO, "#c09154")
    t.hline(0, W - 1, CHAO - 1, "#5c3a1c")
    for _ in range(260):  # cascalho
        x, y = R.randrange(W), R.randrange(CHAO + 2, H)
        t.put(x, y, R.choice(("#b89463", "#6e4826", "#8a6235")))
    for _ in range(26):  # pedras maiores
        x, y = R.randrange(W), R.randrange(CHAO + 4, H - 2)
        t.hline(x, x + 1, y, "#c2b8a8")
        t.put(x + 2, y, "#968b7c")
        t.hline(x, x + 2, y + 1, "#6e655a")
    for cx, cy, rx in ((88, 152, 13), (214, 166, 16)):  # pocas de chuva
        for y in range(cy - 4, cy + 5):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) / rx) ** 2 + ((y - cy) / 4.0) ** 2 <= 1:
                    t.put(x, y, "#8aa8a0" if (x + y) % 3 else "#a8c4bc")
    for x in range(W):  # trilha de passagem mais clara no meio da rua
        if (x * 5) % 7 < 3:
            t.put(x, CHAO + 4, "#b08048")


def telhado(t, x0, x1, base, altura, cor, cor_luz, beiral=2):
    """Telhado de duas aguas visto de frente, com beiral para os lados."""
    meio = (x0 + x1) // 2
    for i in range(altura):
        y = base - i
        recuo = int(i * (x1 - x0) / (2.0 * altura))
        e, d = x0 + recuo, x1 - recuo
        for x in range(e, d + 1):
            t.put(x, y, cor_luz if x < meio else cor)
        t.put(e, y, OL)
        t.put(d, y, OL)
    t.hline(x0 - beiral, x1 + beiral, base, cor)
    t.hline(x0 - beiral, x1 + beiral, base + 1, OL)
    t.put(meio, base - altura, "#d8c9a8")


def parede(t, x0, x1, topo, cor, cor_sombra, tabuas=False):
    for x in range(x0, x1 + 1):
        for y in range(topo, CHAO):
            escuro = x > x1 - 6 or (tabuas and x % 5 == 0)
            t.put(x, y, cor_sombra if escuro else cor)
    t.vline(x0, topo, CHAO - 1, OL)
    t.vline(x1, topo, CHAO - 1, OL)
    t.hline(x0, x1, CHAO - 1, "#4a3018")


def porta(t, cx, topo_altura=14, cor="#6b4325", batente=OL):
    e, d = cx - 4, cx + 4
    topo = CHAO - topo_altura
    for x in range(e, d + 1):
        for y in range(topo, CHAO - 1):
            t.put(x, y, cor if x % 3 else "#55351d")
    t.vline(e, topo, CHAO - 2, batente)
    t.vline(d, topo, CHAO - 2, batente)
    t.hline(e, d, topo, batente)
    t.put(d - 2, CHAO - 8, "#e8c06a")  # maçaneta


def janela(t, cx, cy, w=7, h=6, vidro="#9fd0ea"):
    t.rect(cx - w // 2, cy, w, h, vidro)
    t.hline(cx - w // 2, cx + w // 2, cy, "#d6ecf7")
    t.vline(cx, cy, cy + h - 1, "#6b4325")
    t.hline(cx - w // 2, cx + w // 2, cy + h // 2, "#6b4325")
    for x in range(cx - w // 2 - 1, cx + w // 2 + 2):
        t.put(x, cy - 1, OL)
        t.put(x, cy + h, "#5c3a1c")
    t.vline(cx - w // 2 - 1, cy - 1, cy + h, OL)
    t.vline(cx + w // 2 + 1, cy - 1, cy + h, OL)


def placa(t, cx, y, largura, cor="#d9b06a"):
    """Tabuleta pendurada acima da porta; o texto e um Label na cena."""
    e, d = cx - largura // 2, cx + largura // 2
    t.rect(e, y, largura, 7, cor)
    t.hline(e, d, y, "#f0cf96")
    t.hline(e, d, y + 6, "#9c7444")
    t.vline(e, y, y + 6, OL)
    t.vline(d, y, y + 6, OL)
    t.hline(e, d, y - 1, OL)
    t.put(e + 2, y - 2, "#6b4325")
    t.put(d - 2, y - 2, "#6b4325")


def telhas(t, x0, x1, base, altura, cor, luz, sombra, beiral=3):
    """Telhado de duas aguas de telha colonial: fiadas a cada 3 linhas, canais
    desencontrados, a agua da esquerda pega luz e o beiral faz sombra na parede."""
    meio = (x0 + x1) / 2.0
    for i in range(altura):
        y = base - i
        recuo = int(round(i * (x1 - x0) / (2.0 * altura)))
        e, d = x0 + recuo, x1 - recuo
        for x in range(e, d + 1):
            esq = x < meio
            if i % 3 == 0:
                c = sombra
            elif (x + (i // 3) * 2) % 4 == 0:
                c = cor if esq else sombra
            else:
                c = luz if esq else cor
            t.put(x, y, c)
        t.put(e, y, OL)
        t.put(d, y, OL)
    topo = base - altura
    t.hline(int(meio) - 1, int(meio) + 1, topo, OL)
    t.put(int(meio), topo - 1, OL)
    t.hline(x0 - beiral, x1 + beiral, base, luz)
    t.hline(x0 - beiral, x1 + beiral, base + 1, sombra)
    t.hline(x0 - beiral, x1 + beiral, base + 2, OL)
    for x in range(x0 + 1, x1):  # sombra do beiral na parede
        t.mix(x, base + 3, "#000000", 0.28)
        t.mix(x, base + 4, "#000000", 0.14)


def parede_nova(t, R, x0, x1, topo, cor, luz, sombra, tipo="reboco"):
    """Parede com textura: reboco (pintas), tabuas (lambri na horizontal) ou
    tijolo. Quina da esquerda clara, da direita escura, rodape sujo de terra."""
    for x in range(x0, x1 + 1):
        for y in range(topo, CHAO):
            c = cor
            if tipo == "tabuas":
                k = (y - topo) % 4
                c = sombra if k == 3 else (luz if k == 0 else cor)
                if (x * 7 + (y - topo) // 4 * 13) % 23 == 0 and k != 3:
                    c = sombra  # emenda das tabuas
            elif tipo == "tijolo":
                fiada = (y - topo) // 3
                if (y - topo) % 3 == 2 or (x + (fiada % 2) * 3) % 6 == 0:
                    c = sombra
            t.put(x, y, c)
    if tipo == "reboco":
        for _ in range((x1 - x0) * (CHAO - topo) // 14):
            x, y = R.randrange(x0 + 1, x1), R.randrange(topo, CHAO)
            t.put(x, y, R.choice((luz, sombra)))
    for y in range(topo, CHAO):
        t.put(x0 + 1, y, luz)
        t.put(x1 - 1, y, sombra)
        for x in range(x1 - 5, x1 - 1):
            t.mix(x, y, "#000000", 0.10)
    for x in range(x0, x1 + 1):
        for y in range(CHAO - 4, CHAO):
            t.mix(x, y, "#5c3a1c", 0.30)
    t.vline(x0, topo, CHAO - 1, OL)
    t.vline(x1, topo, CHAO - 1, OL)
    t.hline(x0, x1, CHAO - 1, "#4a3018")


def janela_nova(t, cx, cy, w=7, h=6, vidro="#9fd0ea", moldura="#efe6d2",
                veneziana=None, floreira=False, quebrada=False):
    e, d = cx - w // 2, cx + w // 2
    t.rect(e, cy, w, h, vidro)
    for x in range(e, d + 1):  # vidro mais claro em cima
        t.mix(x, cy, "#ffffff", 0.45)
        t.mix(x, cy + 1, "#ffffff", 0.2)
    for k in range(min(w, h) - 1):  # reflexo diagonal
        t.mix(e + 1 + k, cy + h - 2 - k, "#ffffff", 0.35)
    t.vline(cx, cy, cy + h - 1, moldura)
    t.hline(e, d, cy + h // 2, moldura)
    if quebrada:
        for k in range(4):
            t.put(e + 1 + k, cy + 1 + k % 2 + k, "#2b3b44")
            t.put(d - 1 - k // 2, cy + k + 1, "#2b3b44")
    t.hline(e - 1, d + 1, cy - 1, OL)
    t.vline(e - 1, cy - 1, cy + h, OL)
    t.vline(d + 1, cy - 1, cy + h, OL)
    t.hline(e - 2, d + 2, cy + h, moldura)      # peitoril
    t.hline(e - 2, d + 2, cy + h + 1, "#5c3a1c")
    if veneziana:
        for lado in (e - 1 - (w // 2 + 1), d + 2):
            for y in range(cy - 1, cy + h):  # palhetas: linha clara, linha escura
                for x in range(lado, lado + w // 2 + 1):
                    t.put(x, y, veneziana)
                    if (y - cy) % 2 == 0:
                        t.mix(x, y, "#000000", 0.25)
            t.vline(lado, cy - 1, cy + h - 1, OL)
            t.vline(lado + w // 2, cy - 1, cy + h - 1, OL)
    if floreira:
        t.rect(e - 1, cy + h + 2, w + 2, 3, "#8a5a33")
        t.hline(e - 1, d + 1, cy + h + 4, "#5a3a22")
        for x in range(e - 1, d + 2):
            t.put(x, cy + h + 1, "#4f8a45")
            if x % 2 == 0:
                t.put(x, cy + h, "#d9473b" if x % 4 else "#f0d08a")


def porta_nova(t, cx, altura=16, larg=9, cor="#6b4325", luz="#8a5a33", sombra="#4a2c16"):
    e, d = cx - larg // 2, cx + larg // 2
    topo = CHAO - altura
    t.rect(e, topo, larg, altura - 1, cor)
    for px0, px1 in ((e + 1, cx - 1), (cx + 1, d - 1)):  # duas almofadas
        t.caixa(px0, topo + 2, px1 - px0 + 1, altura // 2 - 2, cor, sombra)
        t.caixa(px0, topo + altura // 2 + 1, px1 - px0 + 1, altura // 2 - 4, cor, sombra)
        t.hline(px0 + 1, px1 - 1, topo + 3, luz)
    t.vline(cx, topo, CHAO - 2, sombra)
    t.vline(e - 1, topo - 1, CHAO - 2, OL)
    t.vline(d + 1, topo - 1, CHAO - 2, OL)
    t.hline(e - 1, d + 1, topo - 1, OL)
    t.hline(e - 2, d + 2, topo - 2, "#efe6d2")   # verga
    t.put(d - 2, CHAO - 8, "#e8c06a")             # maçaneta
    t.hline(e - 2, d + 2, CHAO - 1, "#a39a8a")    # degrau de pedra
    t.hline(e - 2, d + 2, CHAO, "#6e655a")


def mato(t, R, x0, x1, n=10):
    """Tufos de capim no pe da parede."""
    for _ in range(n):
        x = R.randrange(x0, x1)
        alt = R.randint(2, 4)
        t.vline(x, CHAO - alt, CHAO - 1, "#4f8a45")
        t.put(x + 1, CHAO - alt + 1, "#6fa84f")


# ------------------------------------------------------------------- A RUA

def rua():
    t = Tela(W, H)
    R = rng(17)
    ceu_da_vila(t)
    chao_de_terra(t, R)

    # --- casa do avo, detonada: reboco manchado, meio telhado, lona e caibros ---
    parede_nova(t, R, 12, 58, 86, "#cdb68e", "#ddc8a2", "#a98f68")
    t.rect(17, 70, 6, 12, "#a5533c")  # chamine sem o topo
    t.vline(17, 70, 81, OL)
    t.vline(22, 70, 81, OL)
    for x in range(17, 23):
        t.put(x, 70 - (x % 2), OL)
    for y in range(72, 82, 3):
        t.hline(18, 21, y, "#8a3f2c")
    for i in range(10):  # telhas so ate a metade, com a borda comida
        y = 86 - i
        recuo = int(i * 46 / 20.0)
        fim = 36 - recuo // 2 - (2 if i % 3 == 1 else 0)
        for x in range(12 + recuo, fim):
            c = "#8a3f2c" if i % 3 == 0 else ("#b05a40" if (x + (i // 3) * 2) % 4 else "#9c4b36")
            t.put(x, y, c)
        t.put(12 + recuo, y, OL)
        t.put(fim, y, OL)
    for x in range(36, 60):  # lona azul no lugar do resto do telhado
        for y in range(78, 88):
            if y > 78 + (x - 36) // 6:
                t.put(x, y, "#3f6f9c" if (x + y) % 3 else "#4d82b4")
                if (x - 36) % 8 == 0:
                    t.put(x, y, "#2d5275")  # dobra da lona
    for x in (38, 46, 54):  # caibros aparecendo por cima da lona
        for k in range(4):
            t.put(x + k, 77 + (x - 36) // 6 - k, "#6b4325")
    for x in (40, 56):  # pedras segurando a lona
        t.hline(x, x + 2, 79 + (x - 36) // 6, "#9a958c")
        t.put(x + 1, 78 + (x - 36) // 6, "#c2b8a8")
    t.hline(9, 61, 87, "#9c4b36")
    t.hline(9, 61, 88, OL)
    for x in range(13, 58):  # sombra do beiral
        t.mix(x, 89, "#000000", 0.25)
    for _ in range(60):  # manchas de enchente
        x, y = R.randrange(13, 58), R.randrange(108, CHAO - 4)
        t.put(x, y, "#9c8460")
    t.hline(13, 57, 108, "#8f7a5a")  # marca d'agua
    for x in range(13, 58):
        if x % 3:
            t.mix(x, 109, "#5c4a30", 0.35)
    for k in range(9):  # rachadura descendo da janela
        t.put(25 + k // 3, 103 + k, "#7a6448")
    porta_nova(t, 35, 16, 9, "#6b4325", "#7d5434", "#4a2c16")
    janela_nova(t, 20, 96, 7, 6, "#5f7f8f", "#d8ccb0", quebrada=True)
    janela_nova(t, 50, 96, 9, 7, "#3a4a52", "#d8ccb0")
    for x in range(45, 56, 3):  # tabuas pregadas na janela da direita
        t.vline(x, 94, 104, "#8a5a33")
        t.vline(x + 1, 94, 104, "#6b4325")
        t.put(x, 96, "#c2b8a8")
        t.put(x, 102, "#c2b8a8")
    placa(t, 35, 90, 26, "#b89a63")
    mato(t, R, 13, 58, 12)

    # --- ruina da venda do avo: tijolo exposto, viga queimada e o balcao na lona ---
    for x in range(68, 102):
        altura = 104 + int(6 * math.sin((x - 68) / 5.0)) + (10 if x > 88 else 0)
        for y in range(altura, CHAO):
            fiada = (y - 100) // 3
            tijolo = (y - 100) % 3 == 2 or (x + (fiada % 2) * 3) % 6 == 0
            c = "#8a5a44" if tijolo else ("#b9a179" if y > altura + 4 or x % 7 else "#a5533c")
            if y > altura + 4 and (x * 3 + y) % 11 == 0:
                c = "#b06a4e"  # reboco caido mostrando tijolo
            t.put(x, y, c)
        t.put(x, altura, OL)
        t.put(x, altura + 1, "#7a4c3a")
    for k in range(26):  # viga queimada atravessada
        x, y = 72 + k, 100 + k // 2
        t.put(x, y, "#3a2a22")
        t.put(x, y + 1, "#2b1d12")
        if k % 5 == 0:
            t.put(x, y - 1, "#5a4034")
    for _ in range(34):  # entulho no chao
        x, y = R.randrange(66, 104), R.randrange(CHAO, CHAO + 8)
        t.hline(x, x + R.randint(1, 3), y, R.choice(("#a89070", "#8a5a33", "#b9a179", "#a5533c")))
    for x in range(70, 92):  # lona cinza cobrindo o balcao
        for y in range(112, 124):
            if y > 112 + abs(x - 81) // 3:
                t.put(x, y, "#8e9299" if (x + y) % 3 else "#a3a7ad")
    t.hline(70, 91, 112, "#5f6368")
    for x in (71, 90):  # corda amarrando a lona
        t.vline(x, 116, 124, "#c9b27a")
    t.rect(94, 118, 8, 12, "#7a4c2b")  # mourao de pe, sozinho
    t.vline(94, 118, 129, OL)
    t.hline(94, 101, 118, "#9c6c3c")
    for k in range(14):  # tabuleta velha caida, encostada no mourao
        t.put(82 + k, 126 - k // 4, "#b89a63")
        t.put(82 + k, 127 - k // 4, "#8a6a3a")
    mato(t, R, 67, 103, 14)

    # --- venda do Seu Valdir: lambri de madeira, alpendre e mercadoria na porta ---
    parede_nova(t, R, 112, 158, 84, "#c08a4e", "#d29c5e", "#a3713c", "tabuas")
    telhas(t, 110, 160, 84, 12, "#9c4b36", "#b8604a", "#7a3526")
    janela_nova(t, 120, 106, 7, 7, "#9fd0ea", "#efe6d2", veneziana="#4f7a4a")
    janela_nova(t, 152, 106, 7, 7, "#9fd0ea", "#efe6d2", veneziana="#4f7a4a")
    porta_nova(t, 136, 17, 9, "#7a4c2b", "#9c6c3c", "#55351d")
    placa(t, 136, 88, 34, "#d9b06a")
    for x in range(107, 166):  # alpendre: telhadinho na frente da venda
        for y in range(98, 101):
            t.put(x, y, "#9c4b36" if y == 98 else ("#b8604a" if (x // 3) % 2 else "#9c4b36"))
        t.put(x, 101, OL)
        t.mix(x, 102, "#000000", 0.25)
    for x in (108, 164):  # esteios
        t.rect(x - 1, 102, 3, CHAO - 102, "#8a5a33")
        t.vline(x - 1, 102, CHAO - 1, OL)
        t.vline(x + 1, 102, CHAO - 1, "#5a3a22")
    t.caixa(113, 120, 9, 10, "#9c6c3c", "#5a3a22")  # barril
    t.hline(113, 121, 122, "#5a3a22")
    t.hline(113, 121, 127, "#5a3a22")
    t.hline(114, 120, 120, "#c9955a")
    for cx in (147, 153):  # sacos de farinha
        t.disco(cx, 125, 3.5, "#e8dcc0", sy=1.2)
        t.put(cx, 121, "#b89a63")
        t.mix(cx + 2, 126, "#000000", 0.2)
    t.vline(158, 112, CHAO - 1, "#c9a86a")  # vassoura encostada
    t.hline(157, 159, 127, "#d9c27a")
    t.hline(156, 160, 128, "#b8a060")

    # --- pescaria do Zeca: alvenaria clara, barra de azulejo, toldo e gelo ---
    parede_nova(t, R, 166, 210, 88, "#dfe5e7", "#f0f3f5", "#bcc5c9")
    for x in range(167, 210):  # barra de azulejo azul e branco
        for y in range(118, CHAO - 1):
            t.put(x, y, "#7aa6cc" if (x // 2 + y // 2) % 2 else "#e8f0f2")
    t.hline(167, 209, 117, "#2f5f8a")
    telhas(t, 164, 212, 88, 10, "#3f6f9c", "#5188b4", "#2d5275")
    for x in range(163, 214):  # toldo listrado com a barra em ondinha
        listra = (x // 4) % 2
        for y in range(100, 103):
            t.put(x, y, "#2f5f8a" if listra else "#f0f3f5")
        if (x % 4) in (1, 2):
            t.put(x, 103, "#2f5f8a" if listra else "#dde4e8")
        t.put(x, 99, "#24455f")
        t.mix(x, 104, "#000000", 0.2)
    porta_nova(t, 189, 16, 9, "#5a7f99", "#7aa0b8", "#3f5f75")
    janela_nova(t, 174, 107, 9, 8, "#8fd0d8", "#f4f7f8")
    janela_nova(t, 204, 107, 9, 8, "#8fd0d8", "#f4f7f8")
    placa(t, 189, 92, 30, "#9fc9dd")
    t.caixa(168, 118, 11, 11, "#9fb6c2", "#4a5058")  # caixa de gelo
    t.hline(169, 177, 120, "#dceef5")
    for x in range(170, 177, 2):
        t.put(x, 122, "#6fb7cf")
    for x in (206, 209):  # dois peixes pendurados
        t.vline(x, 104, 108, "#8a7340")
        t.disco(x, 112, 3.0, "#6f8a9c", sy=0.7)
        t.put(x - 3, 112, "#55707f")
    for y in range(106, 116):  # rede secando na quina
        for x in range(196, 201):
            if (x + y) % 3 == 0 or (x - y) % 3 == 0:
                t.put(x, y, "#8a7a5a")
    t.disco(199, 120, 2.5, "#e8743b")  # boia
    t.put(198, 119, "#f4a070")

    # --- restaurante da Dona Maria Ivone: reboco rosa, cimalha e janelas floridas ---
    parede_nova(t, R, 218, 272, 82, "#e8b9a8", "#f2cbbb", "#cf9a88")
    t.hline(219, 271, 85, "#f4ead8")  # cimalha creme
    t.hline(219, 271, 86, "#d8c4a4")
    for y in range(87, CHAO - 4, 4):  # cunhais nas quinas
        for x0 in (219, 268):
            t.hline(x0, x0 + 3 - (y // 4) % 2, y, "#f4ead8")
            t.hline(x0, x0 + 3 - (y // 4) % 2, y + 1, "#f4ead8")
    telhas(t, 216, 274, 82, 13, "#9c4b36", "#bd6048", "#7a3526")
    janela_nova(t, 230, 99, 9, 10, "#ffe8b8", "#f4ead8", veneziana="#3f7d5c", floreira=True)
    janela_nova(t, 260, 99, 9, 10, "#ffe8b8", "#f4ead8", veneziana="#3f7d5c", floreira=True)
    porta_nova(t, 245, 17, 9, "#7a4c2b", "#9c6c3c", "#55351d")
    placa(t, 245, 86, 40, "#f0d08a")
    t.vline(252, 106, 108, "#2b1d12")  # lampiao ao lado da porta
    t.rect(251, 109, 3, 4, "#f0d08a")
    t.put(252, 110, "#fff4c8")
    for dx in range(-3, 4):
        t.mix(252 + dx, 111, "#fff0b0", 0.18)
    for cx in (223, 267):  # mesinhas com toalha xadrez
        t.vline(cx, 122, CHAO - 1, "#6b4325")
        t.rect(cx - 4, 119, 9, 3, "#f4f0e4")
        for x in range(cx - 4, cx + 5, 2):
            t.put(x, 120, "#c9503a")
        t.put(cx - 5, 121, "#d8d4c6")
        t.put(cx + 5, 121, "#d8d4c6")
        t.put(cx, 118, "#e8c06a")  # vela
    t.rect(238, 118, 3, 4, "#a5533c")  # vaso na porta
    t.disco(239, 116, 3.0, "#4f8a45", sy=0.9)
    t.put(238, 114, "#d9473b")
    mato(t, R, 219, 236, 4)

    # --- fim da rua: placa e o caminho descendo pro cais ---
    # O caminho desce da rua para o cais, com uma nesga de mar ao fundo.
    for x in range(286, W):
        for y in range(92, 104):
            t.put(x, y, "#5f9fd0" if (x + y) % 5 else "#6fb0dd")
        t.hline(286, W - 1, 92, "#bfe0f2")
    for x in range(286, W):
        largura = (x - 286) // 3
        for y in range(CHAO - 2 - largura, H):
            t.put(x, y, "#b08048" if (x * 3 + y) % 7 else "#9c6d38")
    for x in range(286, W, 6):  # mato na beira do caminho
        t.vline(x, CHAO - 6, CHAO - 2, "#4f8a45")
        t.put(x + 2, CHAO - 7, "#6fa84f")
    t.vline(298, 100, CHAO - 1, "#8a5a33")
    t.vline(299, 100, CHAO - 1, "#6b4325")
    placa(t, 299, 96, 30, "#c9a86a")

    # sombra das construcoes caindo na rua
    for x in range(W):
        if t.get(x, CHAO - 2)[3] and t.get(x, CHAO - 2)[:3] != (159, 182, 160):
            t.put(x, CHAO + 1, "#5c3a1c")
            t.put(x, CHAO + 2, "#6e4826")

    t.salvar(f"{OUT}/vila/rua.png")
    return t


# -------------------------------------------------------------- INTERIORES

def interior(nome, parede_cor, parede_sombra, piso_cor, piso_sombra, mobilia):
    """Sala vista de frente: parede atras, rodape e piso. "mobilia" desenha o
    que e proprio de cada lugar, ja com o chao na linha CHAO."""
    t = Tela(W, H)
    R = rng(hash(nome) % 1000)
    for y in range(CHAO):
        for x in range(W):
            escuro = (x % 23) < 2
            t.put(x, y, parede_sombra if escuro else parede_cor)
    for y in range(0, CHAO, 2):  # textura da parede
        for x in range(W):
            if (x * 7 + y * 3) % 29 == 0:
                t.put(x, y, parede_sombra)
    # luz entrando de cima a esquerda
    for y in range(CHAO):
        for x in range(W):
            if x < 120 - y // 2:
                t.mix(x, y, "#ffffff", 0.06)
    for x in range(W):
        t.mix(x, CHAO - 6, "#000000", 0.13)
    t.rect(0, CHAO - 5, W, 5, piso_sombra)       # rodape
    t.hline(0, W - 1, CHAO - 5, "#1d1208")
    for y in range(CHAO, H):                      # piso em perspectiva simples
        f = (y - CHAO) / float(H - CHAO)
        for x in range(W):
            tabua = (x + int(f * 14)) % 16 < 1
            t.put(x, y, piso_sombra if tabua else piso_cor)
        if y % 7 == 0:
            t.hline(0, W - 1, y, piso_sombra)
    t.hline(0, W - 1, CHAO, "#2b1d12")
    mobilia(t, R)
    t.salvar(f"{OUT}/interior/{nome}.png")
    return t


def _prateleira(t, x0, x1, y, R, cores):
    t.rect(x0, y, x1 - x0, 2, "#8a5a33")
    t.hline(x0, x1 - 1, y, "#b07c45")
    t.hline(x0, x1 - 1, y + 2, "#5a3a22")
    x = x0 + 2
    while x < x1 - 3:
        alt = R.randint(4, 8)
        larg = R.randint(2, 4)
        cor = R.choice(cores)
        t.rect(x, y - alt, larg, alt, cor)
        for xx in range(x, x + larg):
            t.mix(xx, y - alt, "#ffffff", 0.27)
        for yy in range(y - alt, y):
            t.mix(x + larg - 1, yy, "#000000", 0.2)
        x += larg + R.randint(1, 2)


def _balcao(t, x0, x1, topo, cor, cor_luz, cor_sombra):
    t.rect(x0, topo, x1 - x0, CHAO - topo, cor)
    t.hline(x0, x1 - 1, topo, cor_luz)
    t.hline(x0, x1 - 1, topo + 1, cor_luz)
    t.hline(x0, x1 - 1, topo + 2, cor_sombra)
    for x in range(x0, x1, 7):
        t.vline(x, topo + 3, CHAO - 1, cor_sombra)
    t.vline(x0, topo, CHAO - 1, OL)
    t.vline(x1 - 1, topo, CHAO - 1, OL)
    t.hline(x0, x1 - 1, CHAO - 1, "#3a2615")


def mobilia_venda(t, R):
    """Venda do Seu Valdir: prateleiras cheias, varas na parede e o balcao."""
    for y in (46, 66, 86):
        _prateleira(t, 150, 300, y, R, ("#c9503a", "#4f8a45", "#3f6f9c", "#e8c06a", "#b07c45", "#d8dfe2"))
    for i, x in enumerate((24, 36, 48)):  # varas de pesca encostadas
        t.vline(x, 40 + i * 4, CHAO - 1, "#a8743f")
        t.vline(x + 1, 40 + i * 4, CHAO - 1, "#7a4c2b")
        for k in range(5):
            t.put(x + 2 + k, 44 + i * 4 + k * 3, "#d9c27a")
    t.caixa(66, 56, 30, 24, "#b89a63", OL)        # quadro de iscas
    for yy in range(60, 78, 4):
        for xx in range(70, 93, 5):
            t.put(xx, yy, R.choice(("#c9503a", "#e8c06a", "#4f8a45")))
    _balcao(t, 110, 190, 104, "#a3713c", "#c9955a", "#7a4c2b")
    t.caixa(116, 96, 12, 8, "#d8dfe2", "#4a5058")  # balanca
    t.put(122, 94, "#9fb6c2")
    t.caixa(168, 98, 14, 6, "#9c6c3c", "#5a3a22")  # caixa registradora
    t.hline(170, 180, 99, "#e8c06a")
    for x in range(200, 280, 11):                   # caixotes empilhados
        t.caixa(x, 112, 10, 18, "#b07c45", "#5a3a22")
        t.hline(x + 1, x + 8, 120, "#8a5a33")


def mobilia_pescaria(t, R):
    """Pescaria do Zeca: gelo, peixe no balcao, ganchos e a balanca pendurada."""
    for x in range(0, W, 2):  # azulejo ate a meia parede
        for y in range(70, CHAO - 5):
            t.put(x, y, "#e8f0f2" if (x // 8 + y // 8) % 2 else "#d2e2e6")
            t.put(x + 1, y, "#e8f0f2" if (x // 8 + y // 8) % 2 else "#d2e2e6")
    for y in range(70, CHAO - 5, 8):
        t.hline(0, W - 1, y, "#b9ccd2")
    for x in range(0, W, 8):
        t.vline(x, 70, CHAO - 6, "#b9ccd2")
    t.hline(0, W - 1, 70, "#9fb6c2")

    for x in (40, 62, 84):  # ganchos com peixe pendurado
        t.vline(x, 30, 42, "#8a9299")
        t.disco(x, 50, 7.0, "#6f8a9c", sy=0.55)
        t.disco(x - 2, 49, 4.5, "#8aa5b4", sy=0.5)
        t.put(x + 6, 50, "#55707f")
        t.put(x - 8, 48, "#55707f")
        t.put(x - 9, 51, "#55707f")
    t.vline(150, 24, 40, "#8a9299")             # balanca de gancho
    t.caixa(142, 40, 17, 12, "#d8dfe2", "#4a5058")
    t.disco(150, 46, 4.0, "#f4f7f8")
    t.put(150, 44, "#c9503a")

    _balcao(t, 90, 230, 102, "#9fb6c2", "#cfdde3", "#6f8a9c")
    for x in range(96, 224, 9):                  # gelo picado na bancada
        t.put(x, 100, "#f0fbff")
        t.put(x + 3, 101, "#dcf1fa")
    for cx in (112, 140, 170, 200):              # peixes deitados no gelo
        t.disco(cx, 98, 7.5, "#7f9aa8", sy=0.38)
        t.disco(cx - 2, 97, 4.0, "#9cb4c0", sy=0.33)
        t.put(cx + 7, 98, "#5d7684")
        t.put(cx - 9, 97, "#5d7684")
        t.put(cx + 4, 97, "#2b3b44")
    for x in range(240, 300, 14):                # engradados vazios
        t.caixa(x, 110, 13, 20, "#5f8a9c", "#2f4a57")
        t.hline(x + 1, x + 11, 118, "#4a7484")


def mobilia_restaurante(t, R):
    """Restaurante da Dona Maria Ivone: mesas postas, cardapio e o passa-pratos."""
    for x in range(0, W, 2):  # barra de madeira na meia parede
        t.vline(x, 96, CHAO - 6, "#a3713c" if (x // 6) % 2 else "#966634")
    t.hline(0, W - 1, 96, "#c9955a")
    t.hline(0, W - 1, 97, "#7a4c2b")

    t.caixa(26, 36, 44, 34, "#3f4a3c", "#2a1f14")   # cardapio de giz
    for i, y in enumerate(range(44, 66, 5)):
        t.hline(32, 32 + R.randint(14, 30), y, "#e8e4d2")
    t.caixa(86, 40, 26, 20, "#c9a86a", "#6b4325")   # quadro com foto
    t.rect(90, 44, 18, 12, "#9fc9dd")
    t.disco(99, 54, 5.0, "#4f8a45", sy=0.7)

    # passa-pratos da cozinha
    t.caixa(210, 44, 84, 42, "#2b2219", OL)
    t.rect(213, 47, 78, 36, "#6b5a44")
    for x in range(216, 290, 9):                     # panelas no fogo atras
        t.disco(x, 72, 4.0, "#9fa5aa", sy=0.6)
        t.put(x, 67, "#f0d08a")
    t.hline(210, 293, 86, "#c9955a")
    t.hline(210, 293, 87, "#7a4c2b")
    for x in range(214, 290, 13):                    # pratos prontos na boca
        t.disco(x, 84, 4.5, "#f4f0e4", sy=0.4)
        t.disco(x, 84, 2.5, "#e8c06a", sy=0.4)

    for cx in (56, 120, 184):                        # mesas postas na sala
        t.vline(cx, 118, CHAO - 1, "#6b4325")
        t.vline(cx + 1, 118, CHAO - 1, "#55351d")
        t.rect(cx - 13, 112, 28, 6, "#f4f0e4")
        for x in range(cx - 13, cx + 15, 3):
            t.put(x, 113, "#c9503a")
            t.put(x + 1, 116, "#c9503a")
        t.hline(cx - 13, cx + 14, 112, "#ffffff")
        t.hline(cx - 13, cx + 14, 117, "#c9bfa8")
        t.disco(cx - 6, 110, 2.6, "#e8e4d2", sy=0.6)  # prato
        t.put(cx + 5, 108, "#6fa84f")                 # copo
        t.rect(cx + 4, 108, 3, 4, "#9fd0ea")
        for lado in (-20, 18):                        # cadeiras
            t.rect(cx + lado, 114, 5, 2, "#8a5a33")
            t.vline(cx + lado + 2, 116, CHAO - 1, "#6b4325")
            t.rect(cx + lado, 104, 5, 10, "#a3713c")
            t.vline(cx + lado, 104, 113, OL)
            t.vline(cx + lado + 4, 104, 113, OL)


# ------------------------------------------------------ DONA MARIA IVONE

def ivone():
    """Sprite da Dona Maria Ivone, no mesmo tamanho dos outros do hub: 64x104
    em 4x, ou seja 16x26 nativo, ancorado pelos pes."""
    t = Tela(16, 26)
    PELE, PELE_SOMBRA = "#c98f63", "#a8714b"
    VESTIDO, VESTIDO_LUZ, VESTIDO_SOMBRA = "#b2403c", "#cc5a52", "#8a2e2c"
    AVENTAL, AVENTAL_SOMBRA = "#f2ece0", "#d4ccbc"
    CABELO, CABELO_LUZ = "#3a2a22", "#5a4034"

    # saia e corpo
    for y in range(12, 25):
        meia = 3 + (y - 12) * 0.32
        for x in range(int(8 - meia), int(8 + meia) + 1):
            t.put(x, y, VESTIDO_SOMBRA if x > 9 else VESTIDO)
        t.put(int(8 - meia), y, VESTIDO_LUZ)
    # avental por cima
    for y in range(13, 24):
        meia = 2 + (y - 13) * 0.24
        for x in range(int(8 - meia), int(8 + meia) + 1):
            t.put(x, y, AVENTAL_SOMBRA if x > 9 else AVENTAL)
    t.hline(6, 10, 13, "#e2dacb")
    t.put(7, 17, "#c9503a")  # laço do avental
    t.put(9, 17, "#c9503a")

    # bracos: um na cintura, outro segurando a colher
    t.vline(4, 13, 18, PELE_SOMBRA)
    t.vline(12, 13, 17, PELE)
    t.put(13, 18, PELE)
    t.vline(14, 12, 18, "#9fa5aa")   # colher de pau
    t.put(14, 11, "#b89a63")
    t.put(13, 11, "#b89a63")

    # cabeca
    t.disco(8, 8, 3.6, PELE, sy=1.05)
    t.put(6, 9, PELE_SOMBRA)
    t.put(10, 9, PELE_SOMBRA)
    t.put(7, 8, "#2b1d12")           # olhos
    t.put(9, 8, "#2b1d12")
    t.hline(7, 9, 10, "#8a4a3a")     # sorriso
    # cabelo preso em coque
    for x in range(5, 12):
        t.put(x, 4, CABELO)
        t.put(x, 5, CABELO_LUZ if x < 8 else CABELO)
    t.vline(4, 5, 8, CABELO)
    t.vline(12, 5, 8, CABELO)
    t.disco(8, 3, 2.2, CABELO)
    t.put(7, 2, CABELO_LUZ)
    t.put(11, 6, "#f0d08a")          # presilha

    # pes
    t.hline(5, 7, 25, "#4a3018")
    t.hline(9, 11, 25, "#4a3018")

    t.contorno("#2b1d12")
    t.salvar(f"{OUT}/hub/hub_ivone.png", escala=4)
    return t


if __name__ == "__main__":
    import os
    for pasta in ("vila", "interior", "hub"):
        os.makedirs(f"{OUT}/{pasta}", exist_ok=True)
    rua()
    interior("venda", "#c9a97a", "#b08f61", "#a3713c", "#7a4c2b", mobilia_venda)
    interior("pescaria", "#cfdde3", "#b2c4cc", "#8a9ba3", "#6b7d86", mobilia_pescaria)
    interior("restaurante", "#e8cdb4", "#cfae92", "#9c6c3c", "#7a4c2b", mobilia_restaurante)
    ivone()
    print("ok")
