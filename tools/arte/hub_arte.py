"""Loja de Pesca do Bento (hub). Tudo em 1/4 da resolucao, exportado em 4x."""
import math, sys
from px import Tela, rng, gaivota

OUT = sys.argv[1]
OL = "#2e1b12"


def espelha(metades):
    return [m + m[::-1] for m in metades]


# ------------------------------------------------------------------ FUNDO 320x180
def fundo():
    t = Tela(320, 180)
    R = rng(21)
    # forro do telhado (tabuas escuras) e caibros
    for y in range(0, 17):
        c = "#5e3c24" if (y // 4) % 2 == 0 else "#664128"
        t.hline(0, 319, y, c)
        if y % 4 == 3:
            t.hline(0, 319, y, "#4a2e1b")
    for x in range(0, 320, 40):
        t.rect(x + 18, 0, 3, 17, "#4a2e1b"); t.vline(x + 18, 0, 16, "#5a3820")
    # viga mestra
    t.hline(0, 319, 17, "#8a5a33"); t.rect(0, 18, 320, 3, "#6b4428"); t.hline(0, 319, 21, OL)
    for x in range(10, 320, 40):
        t.put(x, 19, "#3a2416"); t.put(x + 1, 19, "#c9b28a")
    # parede de tabuas verticais
    tons = ["#b5814f", "#a9774a", "#bd8955", "#ae7b4c"]
    for i, x in enumerate(range(0, 320, 8)):
        c = tons[(i * 3) % 4]
        t.rect(x, 22, 8, 67, c)
        t.vline(x, 22, 88, "#7d5130")
        t.vline(x + 1, 22, 88, "#c9955f")
        if R.random() < 0.35:
            ky = R.randrange(30, 84)
            t.put(x + 4, ky, "#8a5a33"); t.put(x + 5, ky, "#8a5a33"); t.put(x + 4, ky + 1, "#7d5130")
    for y in range(22, 26):  # sombra sob a viga
        for x in range(320):
            t.mix(x, y, "#3a2416", 0.35 - (y - 22) * 0.08)
    # rodameio e lambri horizontal
    t.hline(0, 319, 89, "#9a6438"); t.hline(0, 319, 90, "#7a4c2b"); t.hline(0, 319, 91, OL)
    for y in range(92, 126):
        k = (y - 92) // 5
        t.hline(0, 319, y, "#8d5c35" if k % 2 == 0 else "#85552f")
        if (y - 92) % 5 == 4:
            t.hline(0, 319, y, "#5e3a20")
    for y in range(92, 126, 5):
        for x in range(R.randrange(20), 320, 37):
            t.vline(x, y, y + 3, "#5e3a20")
    # rodape
    t.hline(0, 319, 126, "#7a4c2b"); t.rect(0, 127, 320, 2, "#5a3820"); t.hline(0, 319, 129, OL)
    # assoalho
    t.hline(0, 319, 130, "#c99258"); t.hline(0, 319, 131, "#b37c48")
    y = 132; k = 0
    while y < 180:
        h = 6 if y < 160 else 7
        base = ["#a8723f", "#9c6838"][k % 2] if y < 156 else ["#8f5e35", "#86562f"][k % 2]
        t.rect(0, y, 320, h, base)
        t.hline(0, 319, y + h - 1, "#6b4428")
        off = (k * 23) % 40
        for x in range(off, 320, 40):
            t.vline(x, y, y + h - 2, "#6b4428")
            t.put(x + 1, y + 1, "#4a2e1b")
        y += h; k += 1
    # tapete listrado perto da cama
    for yy in range(133, 140):
        for xx in range(10, 62):
            if yy in (133, 139) or xx in (10, 61):
                t.put(xx, yy, "#6b3a2a")
            else:
                t.put(xx, yy, ["#c0503a", "#e8d9b0", "#3f7cc8", "#e8d9b0"][((xx - 10) // 4) % 4])
    for xx in range(11, 61, 2):
        t.put(xx, 140, "#e8d9b0")
    # janela com vista do mar
    jx, jy, jw, jh = 148, 40, 32, 28
    t.caixa(jx - 2, jy - 2, jw + 4, jh + 4, "#7a4c2b", OL)
    for yy in range(jy, jy + jh):
        f = (yy - jy) / jh
        c = "#7cc6f2" if f < .35 else ("#a8dcf8" if f < .55 else ("#3c9fd6" if f < .78 else "#2f88c4"))
        t.hline(jx, jx + jw - 1, yy, c)
    for xx in range(jx, jx + jw):  # morro e espuma
        hgt = int(4 * math.exp(-((xx - jx - 22) / 7) ** 2))
        for k in range(hgt):
            t.put(xx, jy + int(jh * .55) - 1 - k, "#4f9a5c")
    t.hline(jx, jx + jw - 1, jy + int(jh * .55), "#e8fbff")
    t.vline(jx + jw // 2, jy, jy + jh - 1, "#7a4c2b"); t.hline(jx, jx + jw - 1, jy + jh // 2, "#7a4c2b")
    t.hline(jx - 3, jx + jw + 2, jy + jh + 2, "#9a6438"); t.hline(jx - 3, jx + jw + 2, jy + jh + 3, OL)
    for yy in range(jy, jy + jh):  # brilho no vidro
        t.mix(jx + 3 + (yy - jy) // 3, yy, "#ffffff", 0.35)
    # rede de pesca na parede, com boias
    for yy in range(30, 62):
        for xx in range(8, 58):
            caida = 4 * math.sin((xx - 8) / 50 * math.pi)
            if yy < 30 + caida:
                continue
            if (xx + yy) % 4 == 0 or (xx - yy) % 4 == 0:
                t.put(xx, yy, "#e6dcc0")
    for xx, yy in ((8, 30), (33, 32), (57, 30)):
        t.put(xx, yy, "#4a4a52"); t.put(xx, yy - 1, "#7a7a84")
    for xx in range(10, 58, 8):
        yy = 62 - int(2 * math.sin((xx - 8) / 50 * math.pi))
        t.rect(xx, yy, 3, 2, "#e0703a"); t.put(xx, yy, "#f29a5e")
    # retrato do Bento
    t.caixa(22, 72, 12, 14, "#d9b45a", "#6b4a1e")
    t.rect(23, 73, 10, 12, "#e9dcc0")
    t.rect(25, 76, 6, 5, "#e3b48c"); t.hline(24, 31, 75, "#d9a84a"); t.hline(25, 30, 74, "#d9a84a")
    t.put(26, 78, "#3a2416"); t.put(29, 78, "#3a2416"); t.hline(26, 29, 80, "#f2f2f2")
    t.rect(24, 81, 8, 4, "#5a7a9a")
    # remos cruzados perto da porta
    for i in range(46):
        x1, y1 = 266 + i * 0.35, 56 + i
        x2, y2 = 282 - i * 0.35, 56 + i
        for (xx, yy) in ((x1, y1), (x2, y2)):
            t.put(xx - 1, yy, OL); t.put(xx, yy, "#d9a86a"); t.put(xx + 1, yy, "#a8743f"); t.put(xx + 2, yy, OL)
    for (xx, yy) in ((281, 96), (267, 96)):
        t.rect(xx - 2, yy, 5, 10, "#d9604a"); t.vline(xx - 2, yy, yy + 9, "#8a2c22"); t.hline(xx - 1, xx + 2, yy + 10, "#8a2c22")
        t.vline(xx + 3, yy, yy + 9, OL); t.vline(xx - 3, yy, yy + 9, OL); t.hline(xx - 2, xx + 2, yy + 11, OL)
    # trofeu: peixe na placa
    t.caixa(188, 58, 22, 9, "#7a4c2b", OL)
    peixe = ["....ggg.........",
             "..gGGGGGgg...g..",
             ".gGwGGGGGGg.gg..",
             "gGGGGGGGGGGgg...",
             ".gGGGGGGGGg.gg..",
             "..gggggggg...g.."]
    t.mapa(191, 59, peixe, {"g": "#4a6b3a", "G": "#7aa85a", "w": "#ffffff"})
    # lampioes pendurados com halo quente
    for lx in (138, 236):
        for yy in range(64):
            for xx in range(lx - 16, lx + 18):
                d = math.hypot(xx - lx - .5, (yy - 30) * 1.2)
                if d < 15 and 22 <= yy:
                    t.mix(xx, yy, "#ffd98a", 0.22 * (1 - d / 15))
        t.vline(lx, 21, 26, "#4a4a52")
        t.caixa(lx - 2, 27, 5, 6, "#ffe08a", OL); t.put(lx, 29, "#fff6d0"); t.put(lx, 30, "#ffc94a")
        t.hline(lx - 3, lx + 3, 26, OL); t.hline(lx - 2, lx + 2, 33, OL)
    # capacho na porta
    t.rect(287, 131, 22, 3, "#8a6a3a"); t.hline(287, 308, 133, "#5e4524")
    for xx in range(288, 308, 2):
        t.put(xx, 132, "#a8864e")
    t.salvar(f"{OUT}/hub_fundo.png")
    return t


# ------------------------------------------------------------------ BURACO NO TELHADO 185x28 (em x=70)
def buraco():
    t = Tela(185, 112 // 4 + 1)
    R = rng(33)
    # contorno do buraco: largo no forro, descendo pela viga no meio
    def dentro(x, y):
        borda_top = 0
        lx = 4 + 3 * math.sin(y / 3.0)
        rx = 180 - 4 * math.sin(y / 2.5 + 1)
        if y >= 17:
            lx, rx = 34 + 2 * math.sin(y), 150 + 2 * math.cos(y)
        if y >= 21:
            lx, rx = 40 + (y - 21) * 2, 146 - (y - 21) * 2
        return lx <= x <= rx
    for y in range(28):
        for x in range(185):
            if dentro(x, y):
                f = y / 28
                c = "#8fd3ff" if f < .3 else ("#a6ddff" if f < .6 else "#bfe7ff")
                t.put(x, y, c)
    # nuvenzinha e gaivota no buraco
    for cx, cy, r in ((60, 7, 3), (64, 6, 4), (69, 7, 3)):
        t.disco(cx, cy, r, "#ffffff")
    t.hline(57, 72, 9, "#d6ecfa")
    gaivota(t, 120, 12)
    # telhas quebradas na borda (vistas por baixo) e lascas de madeira
    for y in range(28):
        for x in range(185):
            if not dentro(x, y):
                continue
            viz = [dentro(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if not all(viz):
                t.put(x, y, "#e0aa6c")
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if not dentro(x + dx, y + dy):
                        t.put(x + dx, y + dy, OL)
    # telhas quebradas presas na borda do buraco, saindo para dentro dele;
    # comprimentos diferentes para a borda ficar irregular
    def borda(y, lado):
        xs = [x for x in range(185) if dentro(x, y)]
        return (xs[0] if lado < 0 else xs[-1]) if xs else None
    TELHA = ("#c46a46", "#a34e33", "#7e3a28")
    for lado, y0, comp, alt in ((-1, 1, 7, 3), (-1, 6, 4, 2), (-1, 10, 6, 3),
                                (1, 2, 6, 3), (1, 7, 3, 2), (1, 12, 5, 3)):
        for k in range(alt):
            x0 = borda(y0 + k, lado)
            if x0 is None:
                continue
            n = comp - k  # cada fileira um pouco mais curta: ponta quebrada
            for i in range(n):
                t.put(x0 - lado * i, y0 + k, TELHA[min(k, 2)])
            t.put(x0 - lado * n, y0 + k, OL)  # ponta
        x0 = borda(y0 + alt, lado)
        if x0 is not None:
            for i in range(comp - alt + 1):
                t.put(x0 - lado * i, y0 + alt, OL)  # sombra embaixo da telha
    # pedaco da viga quebrada, pendurado em diagonal
    for i in range(36):
        x, y = 2 + i, 17 + i * 0.30
        for k in range(4):
            t.put(x, y + k, ["#8a5a33", "#6b4428", "#6b4428", OL][k])
    t.put(38, 28, OL)
    t.salvar(f"{OUT}/hub_buraco.png")
    return t


def luz():
    """raios de sol entrando pelo buraco (semi-transparentes)"""
    t = Tela(200, 130)
    for y in range(22, 130):
        for x in range(200):
            for x0, w in ((40, 26), (95, 18), (140, 22)):
                cx = x0 + (y - 22) * 0.35
                if abs(x - cx) < w / 2 * (1 + (y - 22) / 220):
                    a = 0.20 * (1 - (y - 22) / 140)
                    t.put(x, y, (255, 236, 170, int(255 * a)))
    t.salvar(f"{OUT}/hub_luz.png")


def balde_goteira():
    t = Tela(10, 14)
    t.caixa(1, 7, 8, 7, "#aab3bb", "#4a5058"); t.hline(2, 7, 8, "#cfd6dc"); t.vline(2, 9, 12, "#8d969e")
    t.hline(2, 7, 9, "#4fb5e3"); t.hline(1, 8, 6, "#4a5058"); t.put(0, 6, "#4a5058"); t.put(9, 6, "#4a5058")
    t.put(5, 1, "#8fd3ff"); t.put(5, 2, "#4fb5e3"); t.put(5, 3, "#4fb5e3"); t.put(4, 3, "#8fd3ff")
    t.salvar(f"{OUT}/hub_balde.png")


def telhado_novo():
    t = Tela(185, 22)
    R = rng(44)
    for y in range(0, 17):
        c = "#d4a56c" if (y // 4) % 2 == 0 else "#c99a62"
        t.hline(0, 184, y, c)
        if y % 4 == 3:
            t.hline(0, 184, y, "#9a6438")
    for x in range(0, 185, 12):
        for y in (1, 5, 9, 13):
            t.put(x + 3, y, "#5a4a3a")
    t.hline(0, 184, 17, "#c48d52"); t.rect(0, 18, 185, 3, "#a8743f"); t.hline(0, 184, 21, OL)
    t.vline(0, 0, 21, OL); t.vline(184, 0, 21, OL)
    t.salvar(f"{OUT}/hub_telhado.png")


# ------------------------------------------------------------------ ESTACOES
def cama():
    t = Tela(38, 18)
    W1, W2, W3 = "#a8743f", "#8c5c30", "#6b4428"
    t.rect(1, 0, 4, 18, W2); t.vline(1, 0, 17, W1); t.caixa(0, 0, 6, 18, None, OL) if False else None
    for y in range(0, 18):
        t.put(0, y, OL); t.put(5, y, OL)
    t.hline(0, 5, 0, OL); t.put(2, 1, "#c48d52"); t.put(3, 1, "#c48d52")
    t.rect(33, 6, 4, 12, W2); t.vline(33, 6, 17, W1)
    for y in range(6, 18):
        t.put(32, y, OL); t.put(37, y, OL)
    t.hline(32, 37, 6, OL)
    t.rect(6, 7, 26, 4, "#f2ece0"); t.hline(6, 31, 7, "#ffffff"); t.hline(6, 31, 10, "#d8cfc0")
    t.rect(6, 4, 7, 4, "#ffffff"); t.hline(6, 12, 3, OL); t.vline(13, 4, 6, OL); t.hline(7, 12, 7, "#dcd6ea")
    # colcha de retalhos
    cores = ["#c0503a", "#3f7cc8", "#f2c94c", "#5aa63a", "#e88fb0", "#e8d9b0"]
    for y in range(8, 14):
        for x in range(13, 33):
            t.put(x, y, cores[((x - 13) // 4 + (y - 8) // 3 * 2) % 6])
    t.hline(13, 32, 8, "#ffffff") if False else None
    t.hline(12, 33, 14, OL); t.vline(12, 8, 14, OL)
    for x in range(13, 33):
        t.put(x, 13, ["#8a3020", "#2b5798", "#c9a030", "#3d7d2a", "#b86a88", "#c0b088"][((x - 13) // 4 + 2) % 6])
    t.rect(6, 14, 26, 2, W2); t.hline(6, 31, 14, W1); t.hline(6, 31, 16, OL)
    t.rect(7, 16, 2, 2, W3); t.rect(29, 16, 2, 2, W3)
    t.salvar(f"{OUT}/hub_cama.png")


def marlene():
    pal = {"O": OL, "h": "#d4d1da", "H": "#a8a4b2", "s": "#f2c39a", "S": "#dda07a", "z": "#b97d5c",
           "g": "#6a5070", "m": "#ee9a82", "d": "#b06aa8", "D": "#8e4f8a", "a": "#f4efe6", "A": "#d9d0c4",
           "k": "#5a3a2a", "f": "#f7d36b"}
    L = espelha([
        "......OO",
        ".....Ohh",
        "....OOOh",
        "...OhhhH",
        "..OhhhhH",
        "..OhHsss",
        "..OhSsss",
        "..Osgggs",
        "..OsgOgs",
        "..Ossssz",
        "..Osmsss",
        "...OsssO",
        "....Ozss",
        ".....OOz",
        "...OODdd",
        "..ODddaa",
        "..ODdfaa",
        ".ODODdaa",
        ".ODODaAa",
        ".OsODaaa",
        "..OODaaa",
        "..ODdfaa",
        "..ODdddd",
        "...OOdOO",
        "....OsO.",
        "....OkO.",
    ])
    t = Tela(16, 26); t.mapa(0, 0, L, pal)
    for x, y in ((4, 21), (11, 17), (10, 22), (5, 15)):
        t.put(x, y, "#f7d36b")
    t.salvar(f"{OUT}/hub_marlene.png")


def zeca():
    t = Tela(40, 34)
    pal = {"O": OL, "c": "#2f8f8a", "C": "#23716d", "b": "#1d5c58", "h": "#2a1a14", "s": "#c98b5e",
           "S": "#a86f48", "z": "#8a5636", "t": "#f4f4ee", "T": "#d6d6cc", "y": "#f2c94c", "Y": "#d4a72c", "w": "#ffffff"}
    L = espelha([
        "....OOOO",
        "...OcccC",
        "..OccccC",
        "..ObbbbB",
        "..Ohssss",
        "..OsOsss",
        "..Ossssz",
        "..OSsssO",
        "...OSsss",
        "....OOzz",
        "..OssOtt",
        ".OssOyyt",
        ".OsSOyyy",
        ".OsSOyyy",
        ".OzzOyYy",
        ".OssOyyy",
    ])
    pal["B"] = "#16484a"
    t.mapa(12, 0, L, pal)
    # balcao
    W1, W2, W3 = "#d9a265", "#b97f48", "#8c5a30"
    t.hline(0, 39, 12, OL); t.hline(0, 39, 13, W1); t.rect(0, 14, 40, 2, W2); t.hline(0, 39, 16, OL)
    for x in range(1, 39):
        for y in range(17, 32):
            t.put(x, y, "#a06a3c" if (x // 6) % 2 == 0 else "#946236")
    for x in range(0, 40, 6):
        t.vline(x, 17, 31, "#6b4325")
    t.vline(0, 12, 33, OL); t.vline(39, 12, 33, OL)
    t.rect(1, 32, 38, 1, "#5a3820"); t.hline(0, 39, 33, OL)
    t.rect(14, 21, 12, 6, "#e8d9b0"); t.caixa(14, 21, 12, 6, None, "#6b4325") if False else None
    for x in range(14, 26):
        t.put(x, 21, "#6b4325"); t.put(x, 26, "#6b4325")
    t.vline(14, 21, 26, "#6b4325"); t.vline(25, 21, 26, "#6b4325")
    for x in range(16, 24, 2):  # desenho de peixinho na placa
        pass
    t.hline(17, 21, 23, "#3f7cc8"); t.hline(16, 22, 24, "#3f7cc8"); t.put(23, 23, "#3f7cc8"); t.put(23, 25, "#3f7cc8"); t.put(18, 23, "#ffffff")
    # balanca
    t.rect(3, 9, 8, 3, "#9aa3ab"); t.hline(3, 10, 8, "#cfd6dc"); t.hline(2, 11, 12, "#5a6068")
    t.disco(7, 5, 2.6, "#e8eef2"); t.put(7, 5, "#c0453a"); t.put(8, 4, "#c0453a"); t.vline(7, 7, 8, "#5a6068")
    # caixa de gelo com rabos de peixe
    t.caixa(27, 7, 10, 6, "#f4f8fb", "#5a7080"); t.hline(28, 35, 8, "#3f7cc8")
    for x, c in ((29, "#7aa85a"), (32, "#9aa3ab"), (35, "#d4a72c")):
        t.put(x, 6, c); t.put(x - 1, 5, c); t.put(x + 1, 5, c)
    t.salvar(f"{OUT}/hub_zeca.png")


def aldo():
    t = Tela(40, 62)
    # estante ao fundo
    t.rect(2, 0, 36, 38, "#6e4628"); t.caixa(1, 0, 38, 38, None, OL) if False else None
    for y in range(0, 38):
        t.put(1, y, OL); t.put(38, y, OL)
    t.hline(1, 38, 0, OL)
    for sy in (12, 25):
        t.hline(2, 37, sy, "#a8743f"); t.hline(2, 37, sy + 1, "#5a3820")
    # potes de isca, caixas de anzol e carreteis
    itens = [(4, "#c0503a"), (9, "#5aa63a"), (14, "#f2c94c"), (19, "#3f7cc8")]
    for x, c in itens:
        t.caixa(x, 6, 4, 6, "#dff1f7", "#4a5a66"); t.rect(x + 1, 8, 2, 3, c); t.hline(x, x + 3, 5, "#8a6a3a")
    for x in (25, 31):
        t.caixa(x, 7, 5, 5, "#e8d9b0", "#6b4a1e"); t.put(x + 2, 9, "#9aa3ab")
    for x, c in ((5, "#e0703a"), (11, "#4fb5e3"), (17, "#ffffff"), (23, "#f2c94c")):
        t.disco(x + 1.5, 21.5, 2.4, c); t.put(int(x + 1), 21, "#5a3820")
    t.caixa(28, 18, 8, 7, "#3f7cc8", "#1f3c66"); t.hline(29, 34, 20, "#ffffff")
    # varas encostadas
    for x, c in ((3, "#e0bb5e"), (6, "#c0503a"), (35, "#3f7cc8")):
        t.vline(x, 0, 40, c); t.vline(x + 1, 0, 40, "#4a2e1b") if False else None
        t.put(x, 30, "#2b2b30"); t.put(x, 31, "#2b2b30")
    # Seu Aldo atras do balcao
    pal = {"O": OL, "s": "#f0c39b", "S": "#d9a07a", "z": "#b77d5a", "w": "#f2f2f2", "W": "#cfcfd6",
           "m": "#ffffff", "M": "#d8d8de", "g": "#3a3a4a", "e": "#e8e4d8", "E": "#c9c3b3",
           "v": "#d9822f", "V": "#b06422", "k": "#f2cf63"}
    L = espelha([
        "....OOOO",
        "...Ossss",
        "..OsSsss",
        "..Owssss",
        "..Owgggs",
        "..OwgOgs",
        "..Ossssz",
        "..OsMmmm",
        "..OsMmmO",
        "...OsssO",
        "....OOzz",
        "..OOvVeE",
        ".OvvVvee",
        ".OvVvvek",
        ".OsVvvee",
    ])
    t.mapa(12, 22, L, pal)
    for y in range(22, 37):
        for x in range(12, 28):
            pass
    t.put(13 + 1, 22 + 2, "#ffffff")
    # balcao da loja
    W1, W2 = "#d9a265", "#b97f48"
    t.hline(0, 39, 36, OL); t.hline(0, 39, 37, W1); t.rect(0, 38, 40, 2, W2); t.hline(0, 39, 40, OL)
    for x in range(1, 39):
        for y in range(41, 60):
            t.put(x, y, "#a06a3c" if (x // 5) % 2 == 0 else "#946236")
    for x in range(0, 40, 5):
        t.vline(x, 41, 59, "#6b4325")
    t.vline(0, 36, 61, OL); t.vline(39, 36, 61, OL)
    t.rect(1, 60, 38, 1, "#5a3820"); t.hline(0, 39, 61, OL)
    # placa "anzol" pintada
    t.caixa(13, 45, 14, 9, "#2f4a3a", "#6b4325")
    for k in range(4):
        t.put(21, 47 + k, "#e8e8e8")
    t.put(20, 51, "#e8e8e8"); t.put(19, 50, "#e8e8e8"); t.put(19, 49, "#e8e8e8"); t.put(22, 47, "#e8e8e8")
    # coisas no balcao: pote de minhoca e anzois
    t.caixa(4, 31, 6, 5, "#c99a62", "#5a3a22"); t.hline(5, 8, 32, "#8a5a33")
    t.put(6, 30, "#e88fb0"); t.put(7, 29, "#e88fb0")
    t.caixa(30, 32, 6, 4, "#9aa3ab", "#4a5058")
    t.salvar(f"{OUT}/hub_aldo.png")


def porta():
    t = Tela(22, 40)
    t.rect(0, 0, 22, 40, "#7a4c2b")
    for y in range(40):
        t.put(0, y, OL); t.put(21, y, OL)
    t.hline(0, 21, 0, OL); t.hline(1, 20, 1, "#9a6438")
    for x in range(3, 19):
        for y in range(3, 40):
            t.put(x, y, "#9c6838" if ((x - 3) // 4) % 2 == 0 else "#8f5e35")
    for x in range(3, 19, 4):
        t.vline(x, 3, 39, "#6b4428")
    t.hline(2, 19, 2, OL); t.vline(2, 2, 39, OL); t.vline(19, 2, 39, OL)
    # janelinha com luz do dia
    t.caixa(7, 7, 8, 8, "#bfe9fb", OL); t.vline(11, 8, 13, "#6b4428"); t.hline(8, 13, 11, "#6b4428")
    t.put(8, 8, "#ffffff"); t.put(9, 8, "#ffffff"); t.put(8, 9, "#ffffff")
    # travessas e macaneta
    t.hline(3, 18, 20, "#6b4428"); t.hline(3, 18, 30, "#6b4428")
    t.rect(16, 23, 2, 2, "#d9c27a"); t.put(16, 24, "#8a7340")
    # ferradura da sorte
    t.put(10, 4, "#9aa3ab"); t.put(12, 4, "#9aa3ab"); t.put(10, 5, "#9aa3ab"); t.put(12, 5, "#9aa3ab"); t.put(11, 6, "#9aa3ab")
    t.salvar(f"{OUT}/hub_porta.png")


def quadro():
    t = Tela(66, 42)
    for x in (14, 51):  # cordinha pendurando a lousa na viga
        t.vline(x, 0, 7, "#c9b28a"); t.put(x, 0, "#7a7a84")
    t.rect(0, 8, 66, 34, "#8a5a33")
    for y in range(8, 42):
        t.put(0, y, OL); t.put(65, y, OL)
    t.hline(0, 65, 8, OL); t.hline(0, 65, 41, OL); t.hline(1, 64, 9, "#b07a48")
    t.rect(3, 11, 60, 28, "#2f4a3a")
    t.hline(2, 63, 10, "#5a3820"); t.vline(2, 10, 39, "#5a3820"); t.vline(63, 10, 39, "#a06a3c"); t.hline(2, 63, 39, "#a06a3c")
    R = rng(55)
    for _ in range(30):  # marcas de giz
        x, y = R.randrange(4, 62), R.randrange(12, 38)
        t.mix(x, y, "#ffffff", 0.08); t.mix(x + 1, y, "#ffffff", 0.05)
    t.put(14, 8, "#d9c27a"); t.put(51, 8, "#d9c27a")
    t.rect(6, 39, 5, 1, "#f4f4ee"); t.rect(52, 39, 3, 1, "#f2c94c")
    t.salvar(f"{OUT}/hub_quadro.png")


if __name__ == "__main__":
    fundo(); buraco(); luz(); balde_goteira(); telhado_novo()
    cama(); marlene(); zeca(); aldo(); porta(); quadro()
    print("ok")
