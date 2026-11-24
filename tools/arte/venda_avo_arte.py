"""A venda do avo depois que a Dona Marlene levanta ela.

    cd tools/arte
    python venda_avo_arte.py ../../assets/sprites

Gera duas imagens:
  vila/rua_venda.png       a rua com a venda de pe no lugar da ruina
  interior/venda_avo.png   o interior da venda reaberta

A rua parte da vila/rua.png que ja esta no jogo (ela foi retocada a mao depois
do vila_arte.py), e so o terreno da ruina muda: x 64 a 105 na escala nativa.
Assim as duas versoes da rua batem pixel a pixel no resto.
"""
import os
import sys

from PIL import Image

from px import Tela, hx, rng
from vila_arte import (CHAO, H, OL, W, _balcao, _prateleira, interior, janela_nova,
                       mato, parede_nova, placa, porta_nova, telhas)

OUT = sys.argv[1] if len(sys.argv) > 1 else "."

# Cores do entulho da ruina que ficam espalhadas na terra da rua.
ENTULHO = {hx(c)[:3] for c in ("#a89070", "#a5533c", "#b9a179", "#b06a4e", "#8a5a44", "#8a5a33")}


def _abrir_rua():
    im = Image.open(f"{OUT}/vila/rua.png").convert("RGBA")
    im = im.resize((W, H), Image.NEAREST)
    t = Tela(W, H)
    t.im = im
    t.px = im.load()
    return t


def _varrer_entulho(t, x0, x1):
    """Troca o entulho no chao pela cor de terra mais comum de cada linha."""
    for y in range(CHAO, min(H, CHAO + 12)):
        linha = [t.get(x, y)[:3] for x in range(x1 + 1, x1 + 60)]
        terra = max(set(linha), key=linha.count)
        for x in range(x0, x1 + 1):
            if t.get(x, y)[:3] in ENTULHO:
                t.put(x, y, terra)


def venda_de_pe(t):
    R = rng(41)
    # reboco amarelo com barra de tijolo a vista no pe da parede
    parede_nova(t, R, 66, 103, 90, "#e6c886", "#f0d69c", "#c9a866")
    for x in range(67, 103):
        for y in range(117, CHAO - 1):
            fiada = (y - 117) // 3
            tijolo = (y - 117) % 3 == 2 or (x + (fiada % 2) * 3) % 6 == 0
            t.put(x, y, "#8a4a36" if tijolo else "#b0603f")
    t.hline(67, 102, 116, "#f4ead8")
    telhas(t, 66, 103, 89, 12, "#9c4b36", "#bd6048", "#7a3526")
    placa(t, 85, 93, 30, "#d9b06a")

    # vitrine com a mercadoria atras do vidro e um toldo verde e branco
    t.rect(70, 104, 15, 10, "#9fd0ea")
    for x in range(70, 85):
        t.mix(x, 104, "#ffffff", 0.45)
    for k in range(8):
        t.mix(71 + k, 112 - k, "#ffffff", 0.3)
    t.hline(70, 84, 109, "#8a5a33")
    for x, c in ((71, "#c9503a"), (74, "#e8c06a"), (77, "#4f8a45"), (80, "#3f6f9c"), (83, "#c9503a")):
        t.rect(x, 106, 2, 3, c)
    t.vline(77, 104, 113, "#3f7d5c")
    t.hline(69, 85, 103, OL)
    t.vline(69, 103, 114, OL)
    t.vline(85, 103, 114, OL)
    t.hline(68, 86, 114, "#f4ead8")
    t.hline(68, 86, 115, "#5c3a1c")
    for x in range(68, 87):
        listra = (x // 3) % 2
        t.put(x, 100, "#2a5a40")
        t.put(x, 101, "#3f7d5c" if listra else "#f4ead8")
        if x % 3 != 1:
            t.put(x, 102, "#3f7d5c" if listra else "#e2dccb")

    porta_nova(t, 95, 17, 9, "#3f7d5c", "#5a9a74", "#2a5a40")
    t.rect(70, 124, 12, 2, "#9c6c3c")  # banquinho na frente da vitrine
    t.hline(70, 81, 124, "#c9955a")
    t.vline(71, 126, CHAO - 1, "#5a3a22")
    t.vline(80, 126, CHAO - 1, "#5a3a22")
    t.rect(86, 123, 3, 5, "#a5533c")  # vaso com flor entre a vitrine e a porta
    t.disco(87, 121, 2.5, "#4f8a45", sy=0.9)
    t.put(87, 119, "#f0d08a")
    mato(t, R, 67, 103, 4)


def rua_com_a_venda():
    t = _abrir_rua()
    _varrer_entulho(t, 62, 108)
    venda_de_pe(t)
    t.salvar(f"{OUT}/vila/rua_venda.png")


def mobilia_venda_avo(t, R):
    """Interior da venda reaberta. Mural de peixes (x 78-134, abre a colecao),
    balcao com o radio, o caderno e a boia do avo (x 160-240) e prateleiras
    ainda meio vazias. A vara de bambu antiga fica sobre a saida."""
    t.caixa(78, 34, 56, 52, "#8a5a33", OL)
    t.rect(80, 36, 52, 48, "#efe2c2")
    for i in range(9):
        fx, fy = 83 + (i % 3) * 17, 39 + (i // 3) * 15
        t.caixa(fx, fy, 14, 12, "#f8f2e2", "#6b4325")
        cor = R.choice(("#6f8a9c", "#8a9c6f", "#9c7a5a", "#5a7a8a", "#b0a070"))
        t.disco(fx + 6, fy + 6, 3.5, cor, sy=0.55)
        t.put(fx + 10, fy + 5, cor)
        t.put(fx + 10, fy + 7, cor)
        t.put(fx + 4, fy + 5, "#2b1d12")
    t.caixa(80, 23, 52, 10, "#b07c45", OL)  # tabuleta do mural (o nome e um Label)
    t.hline(81, 130, 24, "#c9955a")
    t.hline(81, 130, 31, "#8a5a33")

    t.caixa(192, 40, 16, 20, "#6b4325", OL)  # retrato do avo
    t.rect(194, 42, 12, 16, "#c9b48a")
    t.disco(200, 48, 3.0, "#8a6a4a")
    t.rect(196, 52, 9, 6, "#4f6f8a")
    t.hline(197, 203, 45, "#e8e0d0")

    _balcao(t, 160, 240, 104, "#8a5a33", "#b07c45", "#5a3a22")
    t.caixa(168, 98, 14, 6, "#9c6c3c", "#5a3a22")  # radio
    t.put(171, 100, "#e8c06a")
    t.hline(174, 179, 100, "#2b1d12")
    t.vline(180, 92, 97, "#2b1d12")
    t.rect(214, 100, 10, 4, "#4a6a3a")  # caderno
    t.hline(214, 223, 100, "#6a8a5a")
    t.vline(219, 100, 103, "#c9b27a")
    t.disco(232, 101, 2.5, "#e8743b")  # boia
    t.put(231, 100, "#f4a070")

    _prateleira(t, 256, 312, 52, R, ("#c9503a", "#4f8a45", "#3f6f9c", "#e8c06a"))
    _prateleira(t, 256, 290, 74, R, ("#b07c45", "#d8dfe2"))
    t.rect(256, 96, 56, 2, "#8a5a33")
    t.hline(256, 311, 96, "#b07c45")

    t.hline(18, 66, 28, "#d9bc7a")  # vara de bambu antiga em dois pregos
    t.hline(18, 66, 29, "#a8743f")
    for x in range(26, 66, 10):  # nos do bambu
        t.vline(x, 28, 29, "#8a5a33")
    t.put(66, 30, "#e8e0d0")  # ponta da linha
    t.vline(66, 30, 36, "#e8e0d0")
    for x in (24, 58):
        t.rect(x, 27, 2, 4, "#5a3a22")


if __name__ == "__main__":
    os.makedirs(f"{OUT}/interior", exist_ok=True)
    rua_com_a_venda()
    interior("venda_avo", "#e8d2a0", "#cdb47e", "#9c6c3c", "#7a4c2b", mobilia_venda_avo)
    print("ok")
