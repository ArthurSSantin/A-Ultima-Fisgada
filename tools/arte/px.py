"""Mini biblioteca de pixel art: desenha em resolucao nativa e exporta em 4x."""
import random
from PIL import Image


def hx(c):
    if isinstance(c, tuple):
        return c if len(c) == 4 else c + (255,)
    c = c.lstrip("#")
    a = int(c[6:8], 16) if len(c) == 8 else 255
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), a)


class Tela:
    def __init__(s, w, h, fundo=None):
        s.w, s.h = w, h
        s.im = Image.new("RGBA", (w, h), hx(fundo) if fundo else (0, 0, 0, 0))
        s.px = s.im.load()

    def put(s, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < s.w and 0 <= y < s.h and c is not None:
            s.px[x, y] = hx(c)

    def mix(s, x, y, c, a):
        """mistura a cor c por cima com opacidade a (0..1)"""
        x, y = int(x), int(y)
        if 0 <= x < s.w and 0 <= y < s.h:
            r, g, b, al = s.px[x, y]
            cr, cg, cb, _ = hx(c)
            s.px[x, y] = (round(r + (cr - r) * a), round(g + (cg - g) * a), round(b + (cb - b) * a), max(al, 255 if a >= 1 else al))

    def get(s, x, y):
        if 0 <= x < s.w and 0 <= y < s.h:
            return s.px[x, y]
        return (0, 0, 0, 0)

    def rect(s, x, y, w, h, c):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                s.put(xx, yy, c)

    def hline(s, x0, x1, y, c):
        for x in range(int(x0), int(x1) + 1):
            s.put(x, y, c)

    def vline(s, x, y0, y1, c):
        for y in range(int(y0), int(y1) + 1):
            s.put(x, y, c)

    def caixa(s, x, y, w, h, fill, ol):
        s.rect(x, y, w, h, fill)
        s.hline(x, x + w - 1, y, ol); s.hline(x, x + w - 1, y + h - 1, ol)
        s.vline(x, y, y + h - 1, ol); s.vline(x + w - 1, y, y + h - 1, ol)

    def disco(s, cx, cy, r, c, sy=1.0):
        for y in range(int(cy - r * sy) - 1, int(cy + r * sy) + 2):
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                if ((x + .5 - cx) / r) ** 2 + ((y + .5 - cy) / (r * sy)) ** 2 <= 1:
                    s.put(x, y, c)

    def mapa(s, x0, y0, linhas, pal):
        """desenha um sprite a partir de linhas de caracteres ('.' = vazio)"""
        for y, row in enumerate(linhas):
            for x, ch in enumerate(row):
                if ch != "." and ch != " ":
                    s.put(x0 + x, y0 + y, pal[ch])

    def colar(s, outra, x0, y0):
        s.im.alpha_composite(outra.im, (int(x0), int(y0)))
        s.px = s.im.load()

    def contorno(s, c, so_vazio=True):
        """contorno externo de 1 px em volta de tudo que e opaco"""
        alvo = []
        for y in range(s.h):
            for x in range(s.w):
                if s.px[x, y][3] == 0:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        if s.get(x + dx, y + dy)[3] > 0:
                            alvo.append((x, y)); break
        for x, y in alvo:
            s.put(x, y, c)

    def salvar(s, caminho, escala=4):
        s.im.resize((s.w * escala, s.h * escala), Image.NEAREST).save(caminho)

    def salvar_1x(s, caminho):
        s.im.save(caminho)


def faixas(t, x0, y0, w, cores_alturas, dither=True):
    """faixas horizontais (cor, altura); com dither xadrez de 1 linha na transicao"""
    y = y0
    prev = None
    for cor, alt in cores_alturas:
        for i in range(alt):
            for x in range(x0, x0 + w):
                if dither and prev and i == 0 and (x + y) % 2 == 0:
                    t.put(x, y, prev)
                else:
                    t.put(x, y, cor)
            y += 1
        prev = cor
    return y


def rng(seed):
    return random.Random(seed)


def gaivota(t, x, y):
    """gaivota de 5 px vista de longe, usada no ceu do cais e no buraco do hub"""
    for dx, dy in ((0, 0), (1, -1), (2, 0), (3, -1), (4, 0)):
        t.put(x + dx, y + dy, "#3d4658")
