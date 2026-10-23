"""Fase 1, terceira rodada: as animacoes do tutorial.

    cd tools/arte
    python animacoes_arte.py <pasta de saida>

  acordar   o teto do quarto visto da cama (nitido e embacado) e a palpebra;
            no Godot as palpebras abrem, piscam e o embacado some
  cafe      a mesa do cafe de perto em quatro quadros: cheio, primeira
            mordida, pela metade e so as migalhas
  butia     a garrafinha de butia e a garrafa termica com o copinho, de perto,
            e os quadros do vo sentado no bote: mao no bolso, a garrafinha, o
            gole, a termica e o copinho entregue
"""
import math
import os
import sys

from PIL import Image, ImageFilter

from px import Tela
from estilo import OL, poligono, escurecer, gradiente, telhado_por_dentro

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
WI, HI = 160, 90


# ================================================================ ACORDAR

def teto_visto_da_cama():
    """O que o neto ve ao abrir o olho: as telhas por dentro, o caibro, a
    lampada acesa no fio e a luz fria da janela entrando pela esquerda."""
    t = Tela(WI, HI)
    telhado_por_dentro(t, 0, WI, 0, HI, seed=2)
    t.rect(0, 52, WI, 4, "#5a3a22")
    t.hline(0, WI - 1, 52, "#7a4e30")
    t.vline(96, 0, 40, "#2a2420")
    t.rect(94, 40, 5, 3, "#5a4a3a")
    t.disco(96.5, 46, 3, "#fff0b0")
    for y in range(16, 80):
        for x in range(60, 134):
            d = math.hypot(x - 96.5, (y - 46) * 1.2)
            if d < 30:
                t.mix(x, y, "#ffe8a0", .30 * (1 - d / 30))
    for y in range(HI):
        for x in range(50):
            t.mix(x, y, "#9ab0e0", .28 * (1 - x / 50.0))
    return t


def embacar(t, raio=3):
    e = Tela(t.w, t.h)
    e.im.paste(t.im.filter(ImageFilter.GaussianBlur(raio)))
    e.px = e.im.load()
    return e


def palpebra():
    """Palpebra de cima (a de baixo e ela espelhada): preto, borda em arco e
    um filete avermelhado, como luz atravessando a pele."""
    t = Tela(WI, HI // 2 + 8)
    for x in range(WI):
        curva = int(8 * (1 - ((x - WI / 2) / (WI / 2)) ** 2))
        fim = t.h - 8 + curva
        for y in range(fim):
            t.put(x, y, "#050304")
        t.put(x, fim, "#3a1a1a")
        t.put(x, fim + 1, "#1a0a0a")
    return t


def quadro_acordar(abertura, borrado):
    """Para a prancha: abertura de 0 (fechado) a 1 (aberto)."""
    q = Tela(WI, HI)
    q.colar(embacar(teto_visto_da_cama(), 3) if borrado else teto_visto_da_cama(), 0, 0)
    p = palpebra()
    fecha = int((HI // 2 + 8) * (1 - abertura))
    q.colar(p, 0, fecha - p.h)
    baixo = Tela(p.w, p.h)
    baixo.im.paste(p.im.transpose(Image.FLIP_TOP_BOTTOM))
    baixo.px = baixo.im.load()
    q.colar(baixo, 0, HI - fecha)
    return q


# =================================================================== CAFE

def mesa_do_cafe(etapa=0):
    """A mesa de perto: toalha xadrez, a xicara esmaltada de cafe com leite,
    o pao com chimia de uva, a cuca de banana e a mao do neto. Etapa 0 a 3."""
    t = Tela(WI, HI)
    gradiente(t, 0, 0, WI, 30, ["#5a3a28", "#6b4530", "#7a5238"])
    for y in range(28, HI):
        for x in range(WI):
            a = (x // 8 + y // 8) % 2
            b = (x // 8) % 2 and (y // 8) % 2
            t.put(x, y, "#e8e0d4" if not a else ("#a83a2e" if b else "#c84a3a"))
    escurecer(t, 0, 28, WI - 1, 32, .25)
    # xicara: o cafe com leite baixa a cada etapa
    t.disco(46, 74, 15, "#d8d0c4", sy=.35)
    t.rect(36, 50, 20, 22, "#f4f1ea")
    t.disco(46, 50, 10, "#f4f1ea", sy=.35)
    nivel = [0, 0, 2, 4][etapa]
    t.disco(46, 50, 8.5, "#e8e2d8", sy=.3)
    if etapa < 3:
        t.disco(46, 50 + nivel, 8.5 - nivel, "#a87850", sy=.3)
    t.rect(56, 55, 5, 9, "#f4f1ea"); t.rect(57, 57, 3, 5, "#c84a3a")
    t.hline(36, 55, 54, "#2a5ab0")
    escurecer(t, 50, 51, 55, 71, .12)
    if etapa < 3:
        for i, (dx, dy) in enumerate(((0, 0), (2, -4), (0, -8), (-2, -12))):
            t.mix(44 + dx, 42 + dy, "#ffffff", .5 - i * .1)
            t.mix(48 - dx, 40 + dy, "#ffffff", .4 - i * .08)
    # prato com o pao de chimia, comido da direita pra esquerda
    t.disco(100, 72, 24, "#f4f1ea", sy=.32)
    t.disco(100, 72, 20, "#e2dcd0", sy=.28)
    pao = [32, 24, 14, 0][etapa]
    if pao:
        t.rect(84, 62, pao, 9, "#e8b870")
        t.rect(84, 61, pao, 3, "#7a2a4a")
        t.hline(84, 84 + pao - 1, 60, "#c8904a")
        if etapa in (1, 2):
            for dy in range(0, 10, 3):
                t.disco(84 + pao, 63 + dy, 1.6, "#e2dcd0")
    if etapa:
        for x, y in ((94, 70), (101, 72), (108, 69), (97, 74), (112, 73)):
            t.put(x, y, "#c8904a")
    # pedaco de cuca de banana com farofa (some no fim)
    if etapa < 3:
        t.rect(124, 58, 16, 12, "#e8c070")
        for x in range(124, 140, 2):
            t.put(x, 57, "#f2e0b0"); t.put(x + 1, 58, "#d8a050")
        t.rect(124, 66, 16, 2, "#f2d870")
    # a mao do neto: no pao (etapa 1) e na xicara (etapa 2)
    if etapa in (1, 2):
        mx, my = (118, 60) if etapa == 1 else (66, 58)
        poligono(t, [(mx, my), (mx + 10, my - 2), (WI, my + 6), (WI, my + 16), (mx + 4, my + 8)], "#f7cba2")
        t.hline(mx + 1, mx + 8, my + 3, "#e3a87d")
        poligono(t, [(mx + 20, my + 2), (WI, my - 2), (WI, my + 18), (mx + 22, my + 14)], "#7cc45e")
    return t


# ================================================================== BUTIA

def garrafinha_de_butia():
    """A garrafinha de bolso do vo: vidro, a cachaca cor de mel com os
    butias laranja boiando e a rolha de cortica."""
    t = Tela(56, 56)
    cx = 28
    poligono(t, [(cx - 9, 18), (cx + 9, 18), (cx + 10, 50), (cx - 10, 50)], "#d8e8e4")
    t.rect(cx - 4, 10, 8, 9, "#d8e8e4")
    t.rect(cx - 4, 5, 8, 6, "#b88a52"); t.hline(cx - 4, cx + 3, 5, "#d8a868")
    poligono(t, [(cx - 8, 24), (cx + 8, 24), (cx + 9, 49), (cx - 9, 49)], "#d8a040")
    t.hline(cx - 8, cx + 8, 24, "#f2c860")
    for x, y in ((cx - 4, 34), (cx + 3, 30), (cx, 42), (cx - 5, 44), (cx + 5, 40)):
        t.disco(x, y, 3, "#f2862a"); t.put(x - 1, y - 1, "#ffb860")
    t.vline(cx - 7, 19, 48, "#ffffff")
    t.vline(cx - 6, 20, 30, "#f4fbfa")
    t.contorno(OL)
    return t


def termica_e_copinho():
    """A garrafa termica xadrez da vo e a tampa que vira copinho, fumegando."""
    t = Tela(56, 56)
    t.rect(8, 14, 16, 36, "#c84a3a")
    for y in range(14, 50, 4):
        t.hline(8, 23, y, "#e8e0d4")
    for x in range(8, 24, 4):
        t.vline(x, 14, 49, "#a83a2e")
    t.rect(10, 8, 12, 6, "#3a3a44"); t.rect(12, 5, 8, 3, "#5a5a66")
    t.rect(24, 22, 3, 14, "#3a3a44")
    t.disco(40, 46, 9, "#d8d0c4", sy=.3)
    poligono(t, [(32, 32), (48, 32), (46, 46), (34, 46)], "#3a3a44")
    t.disco(40, 32, 8, "#3a3a44", sy=.3)
    t.disco(40, 32, 6.5, "#4a2a18", sy=.3)
    for i in range(5):
        t.mix(38 + (i % 2) * 2, 28 - i * 4, "#ffffff", .55 - i * .1)
        t.mix(42 - (i % 2) * 2, 26 - i * 4, "#ffffff", .45 - i * .08)
    t.contorno(OL)
    return t


VO_SENTADO = [
    ".....OOOO.......", "....OhhhhO......", "...OhhhhHHO.....", "...ORrrrrRO.....",
    ".OHhhhhhhhhhhO..", "..OOkkkkkkkOO...", "...OYYSSSSSO....", "...OYysssOsO....",
    "...OYSsssOssO...", "...OyyyyyysO....", "....OYyyyYO.....", ".....OxyyxO.....",
    "....OxXxXxXO....", "...OxXxXxXxXO...", "...OXxXxXxXxO...", "...OxXxXxXxXO...",
    "...OXxXxXxXnO...", "....OLLLgLLO....",
]
PAL_VO = {"O": OL, "h": "#f6d77c", "H": "#e2b655", "k": "#b8893a", "r": "#c0452f", "R": "#8a2c22",
          "s": "#e8b48a", "S": "#cf9268", "z": "#a8704c", "m": "#c9806a",
          "y": "#e4e2dc", "Y": "#b8b5ae", "x": "#b8433a", "X": "#7a2a26", "n": "#5a1e1c",
          "j": "#41557a", "J": "#2f3f5c", "L": "#5a3a22", "g": "#d9c27a"}
POSES_BUTIA = ["bolso", "garrafa", "gole", "termica", "entrega"]


def vo_butia(pose):
    """O vo sentado no bote, da cintura pra cima (16x24). Muda o braco e o que
    ele segura; no gole a cabeca vai um pixel pra tras."""
    t = Tela(16, 24)
    corpo = Tela(16, 24)
    corpo.mapa(0, 5, VO_SENTADO, PAL_VO)
    if pose == "gole":
        cabeca = corpo.im.crop((0, 5, 16, 16))
        corpo.im.paste((0, 0, 0, 0), (0, 5, 16, 16))
        corpo.im.paste(cabeca, (-1, 4), cabeca)
        corpo.px = corpo.im.load()
    t.colar(corpo, 0, 0)
    pele, manga = "#e8b48a", "#7a2a26"
    vidro, mel, laranja = "#d8e8e4", "#d8a040", "#f2862a"
    if pose == "bolso":
        t.rect(10, 18, 2, 3, manga); t.put(10, 21, pele)
    elif pose == "garrafa":
        t.rect(11, 15, 2, 4, manga); t.rect(12, 13, 2, 2, pele)
        t.rect(13, 9, 2, 5, vidro); t.rect(13, 11, 2, 3, mel); t.put(13, 12, laranja)
    elif pose == "gole":
        t.rect(11, 13, 2, 4, manga); t.rect(11, 11, 2, 2, pele)
        poligono(t, [(9, 9), (14, 6), (15, 8), (10, 11)], vidro)
        t.put(12, 8, mel); t.put(13, 8, laranja)
    elif pose == "termica":
        t.rect(11, 16, 2, 3, manga); t.rect(12, 14, 2, 2, pele)
        t.rect(12, 7, 3, 7, "#c84a3a"); t.hline(12, 14, 9, "#e8e0d4"); t.rect(12, 6, 3, 1, "#3a3a44")
        t.put(15, 13, "#4a2a18"); t.put(15, 15, "#4a2a18")
    elif pose == "entrega":
        t.rect(11, 16, 3, 2, manga); t.rect(14, 16, 1, 2, pele)
        t.rect(14, 14, 2, 2, "#3a3a44")
        t.mix(14, 12, "#ffffff", .6); t.mix(15, 10, "#ffffff", .4)
    return t


def folha_vo_butia(escala=4):
    quadros = [vo_butia(p) for p in POSES_BUTIA]
    folha = Image.new("RGBA", (16 * escala * len(quadros), 24 * escala), (0, 0, 0, 0))
    for i, q in enumerate(quadros):
        folha.alpha_composite(q.im.resize((16 * escala, 24 * escala), Image.NEAREST), (16 * escala * i, 0))
    return folha


def salvar(t, nome, escala=4):
    os.makedirs(os.path.dirname(f"{OUT}/{nome}"), exist_ok=True)
    t.salvar(f"{OUT}/{nome}", escala=escala)


if __name__ == "__main__":
    salvar(teto_visto_da_cama(), "cenarios/acordar_teto.png", escala=8)
    salvar(embacar(teto_visto_da_cama(), 3), "cenarios/acordar_teto_embacado.png", escala=8)
    salvar(palpebra(), "cenarios/palpebra.png", escala=8)
    for etapa in range(4):
        salvar(mesa_do_cafe(etapa), f"cenarios/cafe_{etapa}.png", escala=8)
    salvar(garrafinha_de_butia(), "cenarios/butia_perto.png", escala=6)
    salvar(termica_e_copinho(), "cenarios/cafezinho_perto.png", escala=6)
    os.makedirs(f"{OUT}/personagens", exist_ok=True)
    folha_vo_butia().save(f"{OUT}/personagens/vo_butia.png")
    print("ok")
