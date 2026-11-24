"""Gera todos os sons do jogo em assets/sons/ (ogg).

    python tools/sons/gerar_sons.py

Duas fontes:

  * Gravacoes de terceiros (tools/sons/originais/, creditos em
    CREDITOS_SONS.md): de cada uma sai so o trecho que o jogo usa, com
    entrada e saida suaves e o volume nivelado com o resto. Os lacos
    (trote, ambiente do lago) ganham emenda cruzada para nao dar estalo
    quando recomecam.
  * Sons sintetizados aqui mesmo, sem licenca nenhuma: a interface (texto,
    cursor, confirmar, moeda), os jingles da pescaria, a chuva, o trovao e
    o mar.

O nivel de cada arquivo e so o ponto de partida; o volume final de cada som
no jogo fica no CATALOGO de scripts/som.gd.

Precisa de numpy e soundfile (pip install numpy soundfile).
"""
import os

import numpy as np
import soundfile as sf

TAXA = 44100
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORIGINAIS = os.path.join(RAIZ, "tools", "sons", "originais")
SAIDA = os.path.join(RAIZ, "assets", "sons")
R = np.random.default_rng(7)


# ------------------------------------------------------------------ apoio

def db(x):
    return 10 ** (x / 20)


def ler(nome):
    """Le um original em mono e na TAXA do jogo."""
    dados, taxa = sf.read(os.path.join(ORIGINAIS, nome), always_2d=True)
    mono = dados.mean(axis=1)
    if taxa != TAXA:
        t_novo = np.arange(int(len(mono) * TAXA / taxa)) / TAXA
        mono = np.interp(t_novo, np.arange(len(mono)) / taxa, mono)
    return mono


def trecho(sinal, ini, fim):
    return sinal[int(ini * TAXA):int(fim * TAXA)].copy()


def bordas(sinal, entrada=0.005, saida=0.05):
    """Entrada e saida em rampa, para nao estalar no corte."""
    s = sinal.copy()
    a, b = int(entrada * TAXA), int(saida * TAXA)
    if a:
        s[:a] *= np.linspace(0, 1, a)
    if b:
        s[-b:] *= np.linspace(1, 0, b) ** 2
    return s


def nivelar(sinal, pico_db=-1.0):
    """Pico no nivel pedido, com um limitador suave para os picos isolados."""
    s = sinal / (np.abs(sinal).max() + 1e-9)
    s = np.tanh(s * 1.6) / np.tanh(1.6)
    return s * db(pico_db)


def nivelar_rms(sinal, rms_db):
    rms = np.sqrt((sinal ** 2).mean()) + 1e-9
    s = sinal * db(rms_db) / rms
    pico = np.abs(s).max()
    if pico > db(-1):
        s = np.tanh(s / db(-1)) * db(-1)
    return s


def laco(sinal, emenda):
    """Fecha um laco: o fim se mistura no comeco, e o arquivo pode recomecar
    sem emenda audivel. Devolve len(sinal) - emenda amostras."""
    x = int(emenda * TAXA)
    corpo = sinal[:-x].copy()
    fade = np.linspace(0, 1, x)
    corpo[:x] = corpo[:x] * np.sqrt(fade) + sinal[-x:] * np.sqrt(1 - fade)
    return corpo


def passa_baixa(sinal, corte):
    """Filtro de um polo (sem scipy)."""
    a = np.exp(-2 * np.pi * corte / TAXA)
    saida = np.empty_like(sinal)
    acc = 0.0
    for i, v in enumerate(sinal):
        acc = (1 - a) * v + a * acc
        saida[i] = acc
    return saida


def passa_alta(sinal, corte):
    return sinal - passa_baixa(sinal, corte)


def t_de(seg):
    return np.arange(int(seg * TAXA)) / TAXA


def onda(freq, seg, forma="quadrada", ciclo=0.5):
    t = t_de(seg)
    if np.isscalar(freq):
        fase = (freq * t) % 1.0
    else:
        fase = np.cumsum(freq) / TAXA % 1.0
    if forma == "quadrada":
        return np.where(fase < ciclo, 1.0, -1.0)
    if forma == "triangulo":
        return 4 * np.abs(fase - 0.5) - 1
    return np.sin(2 * np.pi * fase)


def nota(freq, seg, forma="quadrada", queda=8.0, ciclo=0.5):
    t = t_de(seg)
    env = np.minimum(1, t * 400) * np.exp(-t * queda)
    return onda(freq, seg, forma, ciclo) * env


def salvar(nome, sinal):
    os.makedirs(SAIDA, exist_ok=True)
    caminho = os.path.join(SAIDA, nome + ".ogg")
    # Em blocos: o libsndfile cai gravando vorbis longo de uma vez so.
    with sf.SoundFile(caminho, "w", TAXA, 1, format="OGG", subtype="VORBIS") as arq:
        for i in range(0, len(sinal), 8192):
            arq.write(sinal[i:i + 8192].astype(np.float32))
    rms = 20 * np.log10(np.sqrt((sinal ** 2).mean()) + 1e-9)
    print(f"{nome:15} {len(sinal) / TAXA:6.2f} s   rms {rms:6.1f} dB")


# --------------------------------------------------------- gravacoes

def gravacoes():
    # Lancar: o assobio da vara inteiro (0.29 s), so nivelado.
    salvar("lancamento", nivelar(bordas(ler("lancamento.mp3"), 0.002, 0.04), -3))
    # Isca na agua: o primeiro respingo; o resto era rabo de eco.
    salvar("isca_agua", nivelar(bordas(trecho(ler("isca_agua.mp3"), 0.0, 0.62), 0.002, 0.25), -4))
    # Fisgar: o original chegava a clipar (pico +0.3 dB); fica o tranco curto.
    salvar("fisgada", nivelar(bordas(trecho(ler("fisgada.mp3"), 0.0, 0.55), 0.002, 0.2), -2))
    # Dois latidos seguidos da Pacoca (de 16 s de gravacao).
    salvar("latido", nivelar(bordas(trecho(ler("latido.mp3"), 10.95, 12.35), 0.01, 0.15), -3))
    # Um ciclo e meio de ronrom, sem a respiracao ruidosa do microfone.
    salvar("ronrom", nivelar(bordas(trecho(ler("ronrom.mp3"), 3.6, 6.1), 0.25, 0.5), -4))
    # A bufada mais forte dos 10 s de gravacao.
    salvar("cavalo_bufo", nivelar(bordas(trecho(ler("cavalo_bufo.mp3"), 7.72, 8.62), 0.01, 0.2), -3))
    # Trote em laco: o trecho do meio, onde o passo ja esta regular.
    salvar("cavalo_trote", nivelar_rms(laco(trecho(ler("cavalo_trote.mp3"), 9.0, 21.5), 0.5), -22))
    # Ambiente do lago: 3 minutos viram 40 s em laco (o jogo sorteia de onde
    # comecar, entao a repeticao nao se nota).
    salvar("ambiente_lago", nivelar_rms(laco(trecho(ler("ambiente_lago.mp3"), 20.0, 61.0), 1.0), -26))


# ---------------------------------------------------------- sintetizados

def batida():
    """Tres batidas na porta de madeira: seno grave que morre rapido + estalo."""
    def uma():
        t = t_de(0.12)
        tom = np.sin(2 * np.pi * 115 * t) + 0.5 * np.sin(2 * np.pi * 230 * t)
        return np.exp(-t * 38) * tom + np.exp(-t * 400) * R.uniform(-1, 1, len(t)) * 0.6
    pausa = np.zeros(int(0.16 * TAXA))
    return nivelar(np.concatenate([uma(), pausa, uma(), pausa, uma(), np.zeros(int(0.1 * TAXA))]), -2)


def texto():
    """O 'tic' de cada letra: pulso curto e abafado, para nao cansar.
    O tom de cada personagem vem do pitch_scale (scripts/som.gd)."""
    s = nota(440, 0.045, "quadrada", 70, ciclo=0.25)
    return nivelar(bordas(passa_baixa(s, 2400), 0.001, 0.01), -6)


def cursor():
    return nivelar(bordas(nota(1046, 0.04, "triangulo", 90), 0.001, 0.01), -6)


def confirmar():
    a = nota(784, 0.06, "quadrada", 30, ciclo=0.25)
    b = nota(1175, 0.12, "quadrada", 26, ciclo=0.25)
    return nivelar(bordas(passa_baixa(np.concatenate([a, b]), 3500), 0.001, 0.04), -6)


def moeda():
    """O 'tlin' de dinheiro trocando de mao."""
    a = nota(988, 0.07, "quadrada", 10, ciclo=0.5)
    b = nota(1319, 0.32, "quadrada", 9, ciclo=0.5)
    return nivelar(bordas(passa_baixa(np.concatenate([a, b]), 4000), 0.001, 0.08), -5)


def _arpejo(freqs, dur, ultima):
    partes = [nota(f, dur, "triangulo", 12) * 0.8 + nota(f, dur, "quadrada", 14, 0.25) * 0.25
              for f in freqs[:-1]]
    f = freqs[-1]
    partes.append(nota(f, ultima, "triangulo", 4.5) * 0.8 + nota(f, ultima, "quadrada", 6, 0.25) * 0.25)
    return passa_baixa(np.concatenate(partes), 5000)


def captura():
    """Peixe no balde: tres notas subindo (do-mi-sol)."""
    return nivelar(bordas(_arpejo([523, 659, 784], 0.075, 0.42), 0.001, 0.12), -5)


def conquista():
    """Especie nova, trofeu, recorde, objetivo cumprido: o arpejo inteiro."""
    s = _arpejo([523, 659, 784, 1047, 1319], 0.075, 0.7)
    # um brilho por cima da ultima nota
    brilho = np.zeros_like(s)
    b = nota(2637, 0.5, "seno", 7) * 0.12
    ini = len(s) - int(0.7 * TAXA)
    brilho[ini:ini + len(b)] = b
    return nivelar(bordas(s + brilho, 0.001, 0.2), -5)


def escapou():
    """O peixe foi embora: duas notas descendo, deslizando no fim."""
    a = nota(392, 0.13, "triangulo", 9)
    dur = 0.32
    f = np.linspace(330, 262, int(dur * TAXA))
    t = t_de(dur)
    b = onda(f, dur, "triangulo") * np.minimum(1, t * 400) * np.exp(-t * 6)
    return nivelar(bordas(np.concatenate([a, b]), 0.001, 0.1), -6)


def mordida():
    """O 'bloop' da isca afundando quando o peixe morde."""
    dur = 0.16
    t = t_de(dur)
    f = 260 + 520 * (t / dur) ** 0.6
    tom = onda(f, dur, "seno") * np.exp(-t * 22) * np.minimum(1, t * 600)
    agua = passa_alta(R.uniform(-1, 1, len(t)), 900) * np.exp(-t * 35) * 0.35
    return nivelar(bordas(tom + agua, 0.001, 0.04), -3)


def carretilha():
    """Um 'tec' da carretilha; o jogo repete enquanto o jogador recolhe."""
    t = t_de(0.03)
    clique = passa_alta(R.uniform(-1, 1, len(t)), 2500) * np.exp(-t * 300)
    corpo = np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 220) * 0.6
    return nivelar(bordas(clique + corpo, 0.0005, 0.005), -4)


def chuva():
    """Chuva forte em laco: chiado abafado + gotas soltas."""
    seg = 12.5
    n = int(seg * TAXA)
    chiado = passa_baixa(passa_alta(R.uniform(-1, 1, n), 400), 5000)
    chiado *= 1 + 0.15 * np.sin(2 * np.pi * t_de(seg) / 2.5)
    gotas = np.zeros(n)
    for _ in range(int(seg * 40)):
        i = R.integers(0, n - 2000)
        d = t_de(0.02)
        gotas[i:i + len(d)] += R.uniform(0.2, 1) * np.sin(2 * np.pi * R.uniform(1800, 4200) * d) * np.exp(-d * 260)
    return nivelar_rms(laco(chiado + gotas * 0.35, 0.5), -24)


def trovao():
    """Estalo seco e o ronco rolando longe."""
    seg = 4.0
    n = int(seg * TAXA)
    t = t_de(seg)
    estalo = passa_alta(R.uniform(-1, 1, n), 600) * np.exp(-t * 18) * 0.7
    ronco = passa_baixa(passa_baixa(R.uniform(-1, 1, n), 140), 140) * 9
    rolagem = 0.6 + 0.4 * np.sin(2 * np.pi * t * 1.7 + R.uniform(0, 6)) * np.sin(2 * np.pi * t * 0.6)
    env = np.minimum(1, t * 12) * np.exp(-t * 0.9)
    return nivelar(bordas(estalo + ronco * rolagem * env, 0.001, 0.8), -3)


def mar():
    """Ondas quebrando na praia, em laco de 16 s (duas ondas de 8 s)."""
    seg = 16.0
    n = int(seg * TAXA)
    t = t_de(seg + 1.0)
    base = R.uniform(-1, 1, len(t))
    grave = passa_baixa(base, 350)
    agudo = passa_baixa(passa_alta(base, 1200), 6000)
    fase = (t % 8.0) / 8.0
    onda_env = np.clip(np.sin(np.pi * np.clip((fase - 0.1) / 0.55, 0, 1)), 0, 1) ** 2
    espuma = np.clip(np.sin(np.pi * np.clip((fase - 0.35) / 0.5, 0, 1)), 0, 1) ** 3
    s = grave * (0.35 + 0.65 * onda_env) * 4 + agudo * espuma * 0.5
    return nivelar_rms(laco(s, 1.0), -26)


if __name__ == "__main__":
    gravacoes()
    for gerador in (batida, texto, cursor, confirmar, moeda, captura, conquista,
                    escapou, mordida, carretilha, chuva, trovao, mar):
        salvar(gerador.__name__, gerador())
