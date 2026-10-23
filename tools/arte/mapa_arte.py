"""Mapa de pergaminho da tela de escolher para onde pescar.

Desenha so o fundo: os alfinetes dos locais entram por cima, em codigo
(scripts/mapa_locais.gd), para um local oculto simplesmente nao aparecer.

    cd tools/arte
    python mapa_arte.py ../../assets/sprites/ui
"""
import math
import sys

from px import Tela, rng

OUT = sys.argv[1] if len(sys.argv) > 1 else "."

W, H = 200, 120

PAPEL = "#e9d9b0"
PAPEL_CLARO = "#f3e7c6"
PAPEL_SOMBRA = "#d6c293"
TINTA = "#5a4428"
TINTA_FRACA = "#8a7149"
AGUA = "#9fc4c0"
AGUA_FUNDA = "#7facaa"
MATA = "#8aa472"
SERRA = "#b6a37c"


def papel(t):
    """Pergaminho: base clara, manchas de idade e bordas gastas."""
    t.rect(0, 0, W, H, PAPEL)
    R = rng(4)
    for _ in range(420):  # granulado
        x, y = R.randrange(W), R.randrange(H)
        t.put(x, y, PAPEL_CLARO if R.random() < 0.5 else PAPEL_SOMBRA)
    for _ in range(14):  # manchas de cafe
        cx, cy, r = R.randrange(W), R.randrange(H), R.uniform(3, 9)
        for y in range(int(cy - r), int(cy + r) + 1):
            for x in range(int(cx - r), int(cx + r) + 1):
                d = math.hypot(x - cx, y - cy)
                if d <= r and R.random() < 0.35 - d / (r * 4):
                    t.mix(x, y, "#c9ab74", 0.35)
    # borda queimada
    for x in range(W):
        for k in range(R.randint(1, 3)):
            t.put(x, k, PAPEL_SOMBRA)
            t.put(x, H - 1 - k, PAPEL_SOMBRA)
    for y in range(H):
        for k in range(R.randint(1, 3)):
            t.put(k, y, PAPEL_SOMBRA)
            t.put(W - 1 - k, y, PAPEL_SOMBRA)
    t.hline(0, W - 1, 0, "#c0a879"); t.hline(0, W - 1, H - 1, "#c0a879")
    t.vline(0, 0, H - 1, "#c0a879"); t.vline(W - 1, 0, H - 1, "#c0a879")


def mar(t):
    """O oceano no canto direito, com a linha da costa e as ilhas do Arvoredo."""
    def costa(y):
        return 150 + 9 * math.sin(y / 13.0) + 4 * math.sin(y / 5.0 + 1)

    for y in range(1, H - 1):
        c = costa(y)
        for x in range(int(c), W - 1):
            t.put(x, y, AGUA_FUNDA if x > c + 22 else AGUA)
        t.put(int(c), y, TINTA)
    # hachura de mar antigo: linhas paralelas acompanhando a costa
    for y in range(2, H - 2, 3):
        c = int(costa(y))
        for k in (4, 9):
            for x in range(c + k, min(W - 2, c + k + 1)):
                t.put(x, y, AGUA_FUNDA)
    # ilhas do Arvoredo, o gancho da Fase 2
    for cx, cy, r in ((186, 34, 3.4), (192, 42, 2.2), (181, 46, 1.8)):
        t.disco(cx, cy, r, MATA, sy=0.8)
        t.disco(cx, cy, r - 1, "#9fb882", sy=0.8)


def rio_e_acude(t):
    """O rio que desce da serra, o acude represado nele e a vila na foz."""
    pontos = []
    for i in range(60):
        f = i / 59.0
        x = 18 + f * 132 + 8 * math.sin(f * 7.0)
        y = 10 + f * 86 + 5 * math.sin(f * 4.0 + 1)
        pontos.append((x, y))
    for i, (x, y) in enumerate(pontos):
        largura = 1 if i < 24 else 2
        for k in range(largura):
            t.put(x, y + k, AGUA)
            t.put(x + 1, y + k, AGUA)
        t.put(x, y - 1, AGUA_FUNDA)

    # o acude: uma lagoa represada na curva do rio
    for y in range(-7, 8):
        for x in range(-12, 13):
            if (x / 12.0) ** 2 + (y / 7.0) ** 2 <= 1:
                t.put(58 + x, 56 + y, AGUA)
            if (x / 12.0) ** 2 + (y / 7.0) ** 2 <= 0.62:
                t.put(58 + x, 56 + y, AGUA_FUNDA)
    for ang in range(0, 360, 6):  # contorno do acude
        a = math.radians(ang)
        t.put(58 + 12 * math.cos(a), 56 + 7 * math.sin(a), TINTA)
    t.hline(68, 73, 56, "#a8926a")  # a barragem

    # serra e mata, em simbolos de mapa
    R = rng(8)
    for cx, cy, r in ((34, 24, 4), (46, 18, 5), (28, 38, 3.5), (96, 22, 4.5),
                      (112, 34, 3.5), (40, 78, 4), (96, 86, 4.5), (122, 70, 3.5)):
        for i in range(int(r) + 1):  # montanha: dois tracos em V invertido
            t.put(cx - i, cy + i, SERRA)
            t.put(cx + i, cy + i, SERRA)
        t.put(cx, cy - 1, "#9c8a63")
    for _ in range(70):  # matinha
        x, y = R.randrange(10, 146), R.randrange(6, H - 8)
        if t.get(x, y)[:3] != (159, 196, 192) and R.random() < 0.6:
            t.put(x, y, MATA)
            t.put(x, y - 1, "#9fb882")

    # vila na foz do rio e a estrada de chao
    t.rect(140, 94, 3, 3, "#c98b63"); t.rect(145, 97, 3, 3, "#c98b63")
    t.hline(139, 149, 93, TINTA_FRACA)
    for x in range(60, 142, 4):
        t.hline(x, x + 1, 62 + int(8 * math.sin(x / 22.0)), TINTA_FRACA)


def rosa_dos_ventos(t, cx, cy, r=9):
    for k in range(r):
        t.put(cx, cy - k, TINTA if k < r - 2 else "#8a2f1e")
        t.put(cx, cy + k, TINTA_FRACA)
        t.put(cx - k, cy, TINTA_FRACA)
        t.put(cx + k, cy, TINTA_FRACA)
    for k in range(1, r - 3):
        t.put(cx - k, cy - k, "#a89066")
        t.put(cx + k, cy - k, "#a89066")
        t.put(cx - k, cy + k, "#a89066")
        t.put(cx + k, cy + k, "#a89066")
    t.disco(cx, cy, 2.2, PAPEL_CLARO)
    t.disco(cx, cy, 1.2, TINTA)
    t.put(cx, cy - r - 2, "#8a2f1e")
    t.put(cx - 1, cy - r - 1, "#8a2f1e")
    t.put(cx + 1, cy - r - 1, "#8a2f1e")


def pino(cor, cor_escura, brilho="#ffffff"):
    """Alfinete de mapa: gota com a ponta embaixo, 7x11 nativo."""
    t = Tela(7, 11)
    for y in range(0, 6):            # cabeca redonda
        for x in range(7):
            if ((x - 3) / 3.1) ** 2 + ((y - 3) / 3.1) ** 2 <= 1:
                t.put(x, y, cor if y > 1 or x in (2, 3, 4) else cor)
    for y in range(5, 10):           # ponta
        meia = max(0, 3 - (y - 4))
        for x in range(3 - meia, 3 + meia + 1):
            t.put(x, y, cor_escura if y > 7 else cor)
    t.put(3, 10, cor_escura)
    t.put(2, 2, brilho); t.put(3, 2, brilho)   # brilho
    t.put(3, 4, cor_escura)
    t.contorno("#3a2414")
    return t


def sombra_pino():
    t = Tela(9, 4)
    for x in range(9):
        for y in range(4):
            if ((x - 4) / 4.2) ** 2 + ((y - 2) / 1.8) ** 2 <= 1:
                t.put(x, y, "#5a442866")
    return t


if __name__ == "__main__":
    t = Tela(W, H)
    papel(t)
    mar(t)
    rio_e_acude(t)
    rosa_dos_ventos(t, 24, 100)
    t.salvar(f"{OUT}/mapa.png", escala=4)
    pino("#c9503a", "#8a2f1e").salvar(f"{OUT}/pino.png", escala=4)
    pino("#f2c14e", "#b98a1f").salvar(f"{OUT}/pino_ativo.png", escala=4)
    sombra_pino().salvar(f"{OUT}/pino_sombra.png", escala=4)
    print(f"mapa: {W * 4}x{H * 4}  + pinos")
