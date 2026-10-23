"""Tiago: sem vara, vara nas costas e vara na mao (bambu e fibra).

Cada pose vira uma folha 4x com 4 quadros de 64x96:
  0 parado | 1 passo (perna da frente) | 2 pernas cruzando | 3 passo (perna de tras)

A ponta da vara na mao fica no pixel (15, 0), que e onde a linha de pesca
comeca no acude.gd (+30, -46 a partir do centro do sprite).
"""
import sys
from PIL import Image

PAL = {
    "O": "#2b1a14",
    "h": "#f6d77c", "H": "#e2b655", "k": "#b8893a",
    "r": "#c0452f", "R": "#8a2c22",
    "c": "#5a3420", "C": "#7d4c2b",
    "s": "#f7cba2", "S": "#e3a87d", "z": "#c4825c",
    "m": "#ee9a82",
    "b": "#64a3e6", "B": "#3f7cc8", "n": "#2b5798",
    "p": "#c9aa76", "P": "#a58554", "q": "#6e5232",
    "w": "#f5f5ef", "W": "#cfd3cd", "v": "#9aa19d",
    "g": "#d9c27a",
    "L": "#6b4428",                                   # alca de couro
}

VARAS = {
    # cor principal, cor de detalhe (no do bambu / passador da fibra), cabo
    "bambu": {"cor": "#e6c266", "det": "#9a742f", "cabo": "#c99a62", "molinete": False},
    "fibra": {"cor": "#1f2f52", "det": "#c9ced4", "cabo": "#c99a62", "molinete": True},
}

HEAD = [
    "................",
    ".....OOOO.......",
    "....OhhhhO......",
    "...OhhhhHHO.....",
    "...ORrrrrRO.....",
    ".OHhhhhhhhhhhO..",
    "..OOkkkkkkkOO...",
    "...OccSSSSSO....",
    "...OcCsssOsO....",
    "...OcSsssOssO...",
    "...OcsssmssO....",
    "....OzsssSO.....",
]
TORSO = [
    ".....OBzzBO.....",
    "....ObbbbBO.....",
    "....ObbbbBO.....",
    "....ObbbBBO.....",
    "....OBBBBnO.....",
    "....OqqqgqO.....",
]
LEGS = {
    "parado": ["....OqPOppO.....", "....OqPOppO.....", "....OWvOwWO.....",
               "....OWvOwWO.....", "....OWWvwwWO....", "....OOOOOOOO...."],
    "passo1": ["...OqPO.OppO....", "...OqPO.OppO....", "...OWvO..OwWO...",
               "..OWvO...OwWO...", "..OWWvO..OwwWO..", "..OOOO...OOOOO.."],
    "passo2": [".....OPppO......", ".....OWwwO......", ".....OWwwO......",
               ".....OWwwwO.....", ".....OOOOOO....."],
    "passo3": ["...OppO.OPqO....", "...OppO.OPqO....", "...OwWO..OWvO...",
               "..OwWO...OWvO...", "..OwwWO..OWWvO..", "..OOOO...OOOOO.."],
}
QUADROS = ["parado", "passo1", "passo2", "passo3"]

# braco da frente balancando (sem vara e vara nas costas)
BRACOS = {
    "baixo": [((6, 13), "n"), ((7, 13), "B"), ((6, 14), "n"), ((7, 14), "B"),
              ((6, 15), "S"), ((7, 15), "s"), ((6, 16), "S"), ((7, 16), "s"),
              ((6, 17), "z"), ((7, 17), "S")],
    "tras": [((6, 13), "n"), ((7, 13), "B"), ((5, 14), "n"), ((6, 14), "B"),
             ((5, 15), "S"), ((6, 15), "s"), ((4, 16), "S"), ((5, 16), "s"),
             ((3, 16), "O"), ((3, 17), "O"), ((4, 17), "z")],
    "frente": [((6, 13), "n"), ((7, 13), "B"), ((7, 14), "n"), ((8, 14), "B"),
               ((8, 15), "S"), ((9, 15), "s"), ((9, 16), "S"), ((10, 16), "s"),
               ((11, 16), "O"), ((11, 15), "O"), ((10, 17), "O"), ((10, 15), "s")],
}
BRACO_DE = {"parado": "baixo", "passo1": "tras", "passo2": "baixo", "passo3": "frente"}

# braco segurando a vara na frente do peito
BRACO_VARA = [((6, 13), "n"), ((7, 13), "B"), ((7, 14), "B"), ((8, 14), "n"),
              ((8, 15), "S"), ((9, 15), "s"), ((10, 15), "s"), ((9, 16), "z"),
              ((10, 14), "S"), ((11, 14), "s"), ((11, 15), "S"),
              ((12, 14), "O"), ((12, 15), "O"), ((10, 16), "O"), ((11, 16), "O"), ((8, 16), "O")]


def vara_na_mao(v):
    """pixels da vara da mao (11,15) ate a ponta (15,0), mais o cabo abaixo da mao"""
    d = VARAS[v]
    px = {}
    for i, y in enumerate(range(0, 14)):
        x = round(11 + (15 - y) * 4 / 15)
        px[(x, y)] = d["det"] if i % 4 == 2 else d["cor"]
    px[(10, 17)] = d["cabo"]
    if d["molinete"]:
        px.update({(12, 16): "#9aa3ab", (13, 16): "#5a6068", (12, 17): "#5a6068", (13, 15): "#cfd6dc"})
    return px


def vara_nas_costas(v):
    """vara presa nas costas: sobe por tras do ombro e passa por cima do chapeu"""
    d = VARAS[v]
    px = {}
    for i, y in enumerate(range(0, 22)):
        x = round(1 + y * 0.14)
        px[(x, y)] = d["det"] if i % 4 == 1 else d["cor"]
    px[(4, 21)] = d["cabo"]; px[(3, 20)] = d["cabo"]
    if d["molinete"]:
        px.update({(1, 17): "#9aa3ab", (2, 17): "#5a6068", (1, 18): "#5a6068", (0, 17): "#cfd6dc"})
    return px


ALCA = [((5, 13), "L"), ((6, 14), "L"), ((7, 15), "L"), ((8, 16), "L")]


def cor(c):
    c = PAL.get(c, c).lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def quadro(pernas, pose, vara=None):
    bob = 1 if pernas == "passo2" else 0
    grid = {}
    if pose == "costas":  # atras do corpo
        for (x, y), c in vara_nas_costas(vara).items():
            grid[(x, y + bob)] = c
    for y, row in enumerate(HEAD + TORSO + LEGS[pernas]):
        for x, ch in enumerate(row):
            if ch != ".":
                grid[(x, y + bob)] = ch
    if pose == "costas":
        for (x, y), c in ALCA:
            grid[(x, y + bob)] = c
    if pose == "mao":
        for (x, y), c in vara_na_mao(vara).items():
            grid[(x, y + bob)] = c
        for (x, y), c in BRACO_VARA:
            grid[(x, y + bob)] = c
    else:
        for (x, y), c in BRACOS[BRACO_DE[pernas]]:
            grid[(x, y + bob)] = c
    im = Image.new("RGBA", (16, 24), (0, 0, 0, 0))
    for (x, y), c in grid.items():
        if 0 <= x < 16 and 0 <= y < 24:
            im.putpixel((x, y), cor(c))
    return im


def folha(pose, vara=None):
    f = Image.new("RGBA", (64 * 4, 96))
    for i, q in enumerate(QUADROS):
        f.alpha_composite(quadro(q, pose, vara).resize((64, 96), Image.NEAREST), (64 * i, 0))
    return f


if __name__ == "__main__":
    out = sys.argv[1]
    poses = {"tiago_sem_vara": ("sem", None)}
    for v in VARAS:
        poses[f"tiago_costas_{v}"] = ("costas", v)
        poses[f"tiago_mao_{v}"] = ("mao", v)
    for nome, (pose, v) in poses.items():
        folha(pose, v).save(f"{out}/{nome}.png")
    quadro("parado", "sem").resize((64, 96), Image.NEAREST).save(f"{out}/tiago.png")
    print("ok")
