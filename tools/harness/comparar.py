"""Compara a taxa de captura medida no Godot com a do harness em Node.

Uso: python tools/harness/comparar.py godot.txt node.txt

Cada arquivo tem uma linha "RESULTADO {json}". Para cada jogador e peso, roda um
teste z de duas proporcoes e marca as diferencas significativas (|z| > 2,58,
cerca de 99%).
"""

import json
import math
import sys


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            if linha.startswith("RESULTADO "):
                return json.loads(linha[len("RESULTADO "):])
    raise SystemExit(f"sem linha RESULTADO em {caminho}")


def z_duas_proporcoes(p1, n1, p2, n2):
    p = (p1 * n1 + p2 * n2) / (n1 + n2)
    erro = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return 0.0 if erro == 0 else (p1 - p2) / erro


def main():
    godot, node = carregar(sys.argv[1]), carregar(sys.argv[2])
    rotulos = (sys.argv[3], sys.argv[4]) if len(sys.argv) > 4 else ("Godot", "Node")
    print(f"| Jogador | Peso | {rotulos[0]} | {rotulos[1]} | Duração {rotulos[0]} / {rotulos[1]} | z | |")
    print("|---|---|---|---|---|---|---|")
    divergentes = 0
    for chave in sorted(godot, key=lambda c: (c.split("|")[0], float(c.split("|")[1]))):
        g, n = godot[chave], node[chave]
        z = z_duas_proporcoes(g["taxa"], g["n"], n["taxa"], n["n"])
        marca = "DIVERGE" if abs(z) > 2.58 else "ok"
        divergentes += marca == "DIVERGE"
        jogador, peso = chave.split("|")
        print(
            f"| {jogador} | {peso} kg | {g['taxa']:.0%} | {n['taxa']:.0%} "
            f"| {g['duracao']:.1f}s / {n['duracao']:.1f}s | {z:+.2f} | {marca} |"
        )
    print(f"\n{divergentes} de {len(godot)} células divergem com 99% de confiança.")


if __name__ == "__main__":
    main()
