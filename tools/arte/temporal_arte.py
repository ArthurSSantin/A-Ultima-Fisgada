"""O estrago do temporal na estrada da volta (1/4 da resolucao, exportado em 4x).

    cd tools/arte
    python temporal_arte.py ../../assets/sprites/tutorial/cenarios

- tronco_caido.png: arvore caida atravessando a estrada, que o Alexandre
  pula. A ponta quebrada fica virada para a camera, com os aneis da madeira.
- galhos.png: galhos e folhas arrancados pelo vento, so de enfeite no chao.
- poca.png: poca de chuva na terra da estrada.
"""
import math
import sys

from px import Tela, rng

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
OL = "#2a1d14"


def folhas(t, cx, cy, r, R):
    """Tufo de folha molhada, verde escuro com brilho de chuva."""
    t.disco(cx, cy, r, "#2f5f33", sy=0.8)
    t.disco(cx - r * 0.3, cy - r * 0.3, r * 0.6, "#3f7a42", sy=0.8)
    for _ in range(int(r * 2)):
        x, y = cx + R.uniform(-r, r), cy + R.uniform(-r * .6, r * .6)
        if t.get(int(x), int(y))[3]:
            t.put(x, y, R.choice(["#5b9a55", "#244a28", "#9cc7a0"]))


def tronco_caido():
    t = Tela(34, 22)
    R = rng(81)
    base, topo = 20, 13            # o tronco deitado, de lado
    # galhos quebrados apontando para cima, com folha
    for x0, alt, dx in ((8, 8, -2), (15, 10, 1), (22, 7, 2)):
        for k in range(alt):
            t.put(x0 + dx * k / alt, topo - k, "#5a3a22")
            t.put(x0 + 1 + dx * k / alt, topo - k, "#6e4a2c")
        folhas(t, x0 + dx, topo - alt, 3.2, R)
    # o corpo do tronco: casca escura, molhada, com sulcos
    for x in range(2, 28):
        for y in range(topo, base):
            f = (y - topo) / (base - topo)
            cor = "#7a5233" if f < .25 else ("#64432a" if f < .7 else "#4a3220")
            if (x * 3 + y) % 7 == 0:
                cor = "#3e2a1b"
            t.put(x, y, cor)
        if x % 4 == 0:
            t.put(x, topo, "#9a6c45")
    # a ponta quebrada, virada para a camera: os aneis
    cx, cy = 28, (topo + base) / 2 - .5
    t.disco(cx, cy, 3.6, "#d9b37a", sy=1.0)
    t.disco(cx, cy, 2.4, "#c49a62", sy=1.0)
    t.disco(cx, cy, 1.1, "#a87c4a", sy=1.0)
    for a in range(0, 360, 50):  # lascas da quebra
        x = cx + math.cos(math.radians(a)) * 4.2
        y = cy + math.sin(math.radians(a)) * 4.2
        t.put(x, y, "#e6c992")
    # a raiz arrancada do outro lado, com terra presa
    for k in range(6):
        t.put(1 - k // 3, topo + 1 + k, "#5a3a22")
        t.put(2, base - k // 2, "#5a3a22")
    t.rect(0, base - 3, 3, 3, "#6b4a2e")
    # agua escorrendo e a sombra no chao molhado
    for x in range(4, 27, 5):
        t.put(x, base, "#9fb7c4")
    t.contorno(OL)
    for x in range(1, 33):
        if not t.get(x, base + 1)[3]:
            t.put(x, base + 1, "#3a2a1c88")
    t.salvar(f"{OUT}/tronco_caido.png")


def galhos():
    t = Tela(24, 8)
    R = rng(83)
    for x0, y0, L in ((2, 6, 9), (10, 5, 7), (15, 6, 8)):
        for k in range(L):
            t.put(x0 + k, y0 - (k % 3 == 0), "#5a3a22")
        folhas(t, x0 + L, y0 - 2, 1.8, R)
    for _ in range(10):
        t.put(R.randrange(24), R.randrange(4, 8), R.choice(["#3f7a42", "#6b8f3a", "#8a6a2a"]))
    t.salvar(f"{OUT}/galhos.png")


def poca():
    t = Tela(26, 6)
    t.disco(13, 3, 12, "#5f7f8f", sy=0.22)
    t.disco(12, 2.6, 9, "#7d9eae", sy=0.18)
    for x in (6, 11, 17):
        t.hline(x, x + 2, 3, "#b9d3de")  # o ceu refletido
    t.disco(13, 3, 12.5, None, sy=0.24)
    t.salvar(f"{OUT}/poca.png")


if __name__ == "__main__":
    tronco_caido(); galhos(); poca()
    print("ok")
