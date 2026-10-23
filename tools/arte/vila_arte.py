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


# ------------------------------------------------------------------- A RUA

def rua():
    t = Tela(W, H)
    R = rng(17)
    ceu_da_vila(t)
    chao_de_terra(t, R)

    # --- casa do avo, detonada: parede manchada, lona e telhado faltando ---
    parede(t, 12, 58, 86, "#c9b188", "#ab9068")
    for i in range(10):  # telhado so pela metade
        y = 86 - i
        recuo = int(i * 46 / 20.0)
        for x in range(12 + recuo, 36 - recuo // 2):
            t.put(x, y, "#9c4b36" if x % 4 else "#8a3f2c")
        t.put(12 + recuo, y, OL)
    for x in range(36, 60):  # lona azul no lugar do resto do telhado
        for y in range(78, 88):
            if y > 78 + (x - 36) // 6:
                t.put(x, y, "#3f6f9c" if (x + y) % 3 else "#4d82b4")
    t.hline(36, 59, 78, "#2d5275")
    for _ in range(40):  # manchas de enchente na parede
        x, y = R.randrange(13, 58), R.randrange(100, CHAO - 1)
        t.put(x, y, "#9c8460")
    t.hline(13, 57, 112, "#a08866")  # marca d'agua
    porta(t, 35)
    janela(t, 20, 96, 7, 6, "#5f7f8f")
    for x in range(44, 56, 3):  # tabuas pregadas na janela quebrada
        t.vline(x, 94, 104, "#8a5a33")
    placa(t, 35, 90, 26, "#b89a63")

    # --- ruina da venda do avo: meia parede e o balcao sob a lona ---
    for x in range(68, 102):
        altura = 104 + int(6 * math.sin((x - 68) / 5.0)) + (10 if x > 88 else 0)
        for y in range(altura, CHAO):
            t.put(x, y, "#b9a179" if x % 5 else "#9c8460")
        t.put(x, altura, OL)
    for _ in range(26):  # entulho no chao
        x, y = R.randrange(66, 104), R.randrange(CHAO, CHAO + 8)
        t.hline(x, x + R.randint(1, 3), y, R.choice(("#a89070", "#8a5a33", "#b9a179")))
    for x in range(70, 92):  # lona cinza cobrindo o balcao
        for y in range(112, 124):
            if y > 112 + abs(x - 81) // 3:
                t.put(x, y, "#8e9299" if (x + y) % 3 else "#a3a7ad")
    t.hline(70, 91, 112, "#5f6368")
    t.rect(94, 118, 8, 12, "#7a4c2b")  # mourão de pé, sozinho
    t.vline(94, 118, 129, OL)

    # --- venda do Seu Valdir: casa de madeira com varanda ---
    parede(t, 112, 158, 84, "#c08a4e", "#a3713c", tabuas=True)
    telhado(t, 110, 160, 84, 12, "#8a3f2c", "#a84f36")
    porta(t, 136)
    janela(t, 120, 94)
    janela(t, 152, 94)
    placa(t, 136, 88, 34, "#d9b06a")
    t.caixa(114, 120, 9, 9, "#b07c45", "#5a3a22")
    t.caixa(148, 122, 8, 7, "#9c6c3c", "#5a3a22")
    t.hline(149, 154, 124, "#7a4c2b")

    # --- pescaria do Zeca: alvenaria clara, toldo listrado e caixa de gelo ---
    parede(t, 166, 210, 88, "#d8dfe2", "#bcc5c9")
    telhado(t, 164, 212, 88, 10, "#3f6f9c", "#5188b4")
    for x in range(164, 213):  # toldo listrado
        t.put(x, 100, "#2f5f8a" if (x // 4) % 2 else "#f0f3f5")
        t.put(x, 101, "#2f5f8a" if (x // 4) % 2 else "#dde4e8")
        t.put(x, 102, "#24455f")
    porta(t, 189, 16, "#5a7f99")
    janela(t, 174, 108, 9, 8, "#8fd0d8")
    janela(t, 204, 108, 9, 8, "#8fd0d8")
    placa(t, 189, 92, 30, "#9fc9dd")
    t.caixa(168, 118, 11, 11, "#9fb6c2", "#4a5058")  # caixa de gelo
    t.hline(169, 177, 120, "#dceef5")
    for x in range(170, 177, 2):
        t.put(x, 122, "#6fb7cf")
    for i, x in enumerate((206, 209)):  # dois peixes pendurados
        t.vline(x, 104, 108, "#8a7340")
        t.disco(x, 112, 3.0, "#6f8a9c", sy=0.7)
        t.put(x - 3, 112, "#55707f")

    # --- restaurante da Dona Maria Ivone: reboco rosa e mesinhas na calcada ---
    parede(t, 218, 272, 82, "#e8b9a8", "#cf9a88")
    telhado(t, 216, 274, 82, 13, "#9c4b36", "#bd6048")
    porta(t, 245, 16, "#7a4c2b")
    janela(t, 228, 100, 11, 10, "#ffe8b8")
    janela(t, 262, 100, 11, 10, "#ffe8b8")
    placa(t, 245, 86, 40, "#f0d08a")
    for cx in (223, 268):  # mesinhas com toalha xadrez
        t.vline(cx, 122, CHAO - 1, "#6b4325")
        t.rect(cx - 4, 119, 9, 3, "#f4f0e4")
        for x in range(cx - 4, cx + 5, 2):
            t.put(x, 120, "#c9503a")
        t.put(cx - 5, 121, "#d8d4c6")
        t.put(cx + 5, 121, "#d8d4c6")
    t.rect(238, 118, 3, 4, "#6fa84f")  # vaso na porta
    t.disco(239, 116, 3.0, "#4f8a45", sy=0.9)

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
