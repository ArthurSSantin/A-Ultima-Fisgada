"""Sons do tutorial, sintetizados (sem arquivo de terceiros, sem licenca).

    python tools/sons/gerar_sons.py assets/sons

Sao placeholders honestos: soam como o que sao, mas sinteticos. Quando houver
gravacao de verdade, e so trocar o .wav com o mesmo nome.

  batida.wav   tres batidinhas na porta de madeira (o vo acordando o neto)
  ronrom.wav   o MauMau ronronando no carinho
  latido.wav   dois latidos da Pacoca
  ploc.wav     a boia caindo na agua
"""
import math
import os
import random
import struct
import sys
import wave

TAXA = 22050
OUT = sys.argv[1] if len(sys.argv) > 1 else "."


def salvar(nome, amostras):
    pico = max(1e-6, max(abs(a) for a in amostras))
    with wave.open(os.path.join(OUT, nome), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TAXA)
        w.writeframes(b"".join(struct.pack("<h", int(a / pico * 0.85 * 32767)) for a in amostras))


def silencio(seg):
    return [0.0] * int(seg * TAXA)


def batida():
    """Pancada surda na madeira: seno grave que morre rapido, mais um estalo."""
    R = random.Random(1)
    um = []
    for i in range(int(0.12 * TAXA)):
        t = i / TAXA
        env = math.exp(-t * 38)
        um.append(env * (math.sin(2 * math.pi * 115 * t) + .5 * math.sin(2 * math.pi * 230 * t))
                  + math.exp(-t * 400) * R.uniform(-1, 1) * .6)
    return um + silencio(.16) + um + silencio(.16) + um + silencio(.2)


def ronrom():
    """Ruido grave modulado a ~26 Hz (as vibracoes do ronrom), em ciclos de
    respiracao: a expiracao mais forte que a inspiracao."""
    R = random.Random(2)
    saida, baixa = [], 0.0
    dur = 2.4
    for i in range(int(dur * TAXA)):
        t = i / TAXA
        baixa += (R.uniform(-1, 1) - baixa) * 0.06          # passa-baixa simples
        vib = (0.5 + 0.5 * math.sin(2 * math.pi * 26 * t)) ** 3
        fase = (t % 1.2) / 1.2
        resp = 0.55 + 0.45 * math.sin(math.pi * fase) * (1.0 if fase > .45 else .6)
        env = min(1, t * 4, (dur - t) * 4)
        saida.append(baixa * vib * resp * env)
    return saida


def latido():
    """'Au': tom com harmonicos que cai de ~620 para ~380 Hz, mais um sopro
    de ruido no ataque."""
    R = random.Random(3)

    def um(alt):
        s, fase = [], 0.0
        d = 0.17
        for i in range(int(d * TAXA)):
            t = i / TAXA
            f = (620 - 240 * (t / d)) * alt
            fase += 2 * math.pi * f / TAXA
            env = min(1, t * 120) * math.exp(-t * 14)
            tom = math.sin(fase) + .55 * math.sin(2 * fase) + .3 * math.sin(3 * fase) + .15 * math.sin(4 * fase)
            s.append(env * (tom + R.uniform(-1, 1) * .5 * math.exp(-t * 40)))
        return s

    return um(1.0) + silencio(.13) + um(1.08) + silencio(.15)


def ploc():
    """Gota: seno que sobe rapido de tom e some."""
    s, fase = [], 0.0
    for i in range(int(0.14 * TAXA)):
        t = i / TAXA
        f = 300 + 900 * (1 - math.exp(-t * 60))
        fase += 2 * math.pi * f / TAXA
        s.append(math.sin(fase) * math.exp(-t * 34) * min(1, t * 300))
    return s + silencio(.05)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for nome, gerar in (("batida.wav", batida), ("ronrom.wav", ronrom), ("latido.wav", latido),
                        ("ploc.wav", ploc)):
        salvar(nome, gerar())
    print("ok")
