"""Gera as cenas do tutorial (fase 1) em scenes/tutorial/.

    python tools/gerar_cenas_tutorial.py

As cenas a pe tem a mesma forma (fundo, estacoes, neto, UI) e mudam so os
dados; escrever cada .tscn na mao seria repetir tudo oito vezes. Rode de novo
depois de mexer nas posicoes daqui. A pescaria no meio do rio sai da cena do
acude (scenes/Acude.tscn), trocando so o cenario e o roteiro.

Coordenadas em pixels de tela (1280x720). O chao dos pes fica sempre em y 520.
Nos interiores (quarto e cozinha) a camera e duas vezes mais perta: os
personagens entram com escala 2.
"""
import io
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)
T = "res://assets/sprites/tutorial/"
CHAO = 520

_recursos = []


def rec(caminho, tipo="Texture2D"):
    """Registra um ext_resource e devolve o id."""
    for c, t, i in _recursos:
        if c == caminho:
            return i
    i = f"r{len(_recursos) + 1}"
    _recursos.append((caminho, tipo, i))
    return i


def cabecalho():
    linhas = ["[gd_scene format=3]", ""]
    for c, t, i in _recursos:
        linhas.append(f'[ext_resource type="{t}" path="{c}" id="{i}"]')
    linhas += ["", '[sub_resource type="SystemFont" id="negrito"]', 'font_names = PackedStringArray("Arial")',
               "font_weight = 700", ""]
    return "\n".join(linhas) + "\n"


def no(nome, tipo, pai=None, **props):
    s = f'[node name="{nome}" type="{tipo}"' + (f' parent="{pai}"' if pai else "") + "]\n"
    for k, v in props.items():
        s += f"{k} = {v}\n"
    return s + "\n"


def v2(x, y):
    return f"Vector2({x}, {y})"


def sprite_pe(nome, pai, textura, x, escala=1, centro=True, pos=None, regiao=None, extra=None):
    """Sprite com os pes no chao (y 520) e o centro em x."""
    from PIL import Image
    arquivo = textura.replace("res://", "")
    w, h = Image.open(arquivo).size
    if regiao:
        w, h = regiao[2], regiao[3]
    props = {"texture": f'ExtResource("{rec(textura)}")', "centered": "false"}
    if escala != 1:
        props["scale"] = v2(escala, escala)
    props["position"] = pos or v2(x - w * escala / 2, CHAO - h * escala)
    if regiao:
        props["region_enabled"] = "true"
        props["region_rect"] = f"Rect2({regiao[0]}, {regiao[1]}, {regiao[2]}, {regiao[3]})"
    props.update(extra or {})
    return no(nome, "Sprite2D", pai, **props)


def rotulo(nome, pai, texto, y, cor="Color(1, 0.96, 0.86, 1)", tam=15, larg=260):
    return no(nome, "Label", pai, offset_left=-larg / 2, offset_top=y, offset_right=larg / 2, offset_bottom=y + 44,
              **{"theme_override_colors/font_color": cor,
                 "theme_override_colors/font_outline_color": "Color(0.2, 0.12, 0.07, 1)",
                 "theme_override_constants/outline_size": 5,
                 "theme_override_fonts/font": 'SubResource("negrito")',
                 "theme_override_font_sizes/font_size": tam,
                 "text": f'"{texto}"', "horizontal_alignment": 1, "autowrap_mode": 2})


def ui(com_dica=True):
    s = no("UI", "CanvasLayer", ".")
    s += no("Prompt", "Label", "UI", offset_left=340.0, offset_top=600.0, offset_right=940.0, offset_bottom=640.0,
            **{"theme_override_colors/font_color": "Color(1, 0.85, 0.2, 1)",
               "theme_override_colors/font_outline_color": "Color(0.2, 0.12, 0.07, 1)",
               "theme_override_constants/outline_size": 6,
               "theme_override_fonts/font": 'SubResource("negrito")',
               "theme_override_font_sizes/font_size": 20, "horizontal_alignment": 1})
    # a dica fica a direita do quadro de objetivos (canto de cima a esquerda)
    s += no("Dica", "Label", "UI", offset_left=300.0, offset_top=24.0, offset_right=1260.0, offset_bottom=80.0,
            **{"theme_override_colors/font_color": "Color(1, 1, 1, 1)",
               "theme_override_colors/font_outline_color": "Color(0.07, 0.13, 0.28, 1)",
               "theme_override_constants/outline_size": 6,
               "theme_override_fonts/font": 'SubResource("negrito")',
               "theme_override_font_sizes/font_size": 18, "horizontal_alignment": 1, "autowrap_mode": 2})
    return s


def neto(x, escala, pose_inicial="sem_vara"):
    s = no("Player", "Sprite2D", ".", position=v2(x, CHAO - 48 * escala),
           texture=f'ExtResource("{rec(T + "personagens/neto.png")}")',
           **({"scale": v2(escala, escala)} if escala != 1 else {}))
    s += no("OitoDirecoes", "Node", "Player", script=f'ExtResource("{rec("res://scripts/eight_dir.gd", "Script")}")',
            max_speed=260.0, acceleration=900.0, deceleration=900.0)
    s += no("Visual", "Node", "Player", script=f'ExtResource("{rec("res://scripts/visual_tiago.gd", "Script")}")',
            pasta=f'"{T}personagens/"', prefixo='"neto"')
    return s


def vo_acompanhante(x):
    return no("Vo", "Sprite2D", ".", script=f'ExtResource("{rec("res://scripts/tutorial/acompanhante.gd", "Script")}")',
              position=v2(x, CHAO - 56), texture=f'ExtResource("{rec(T + "personagens/vo.png")}")',
              alvo='NodePath("../Player")')


def cena_a_pe(arquivo, raiz, script, fundo, estacoes, x_neto, escala, borda, alcance, extras_antes=None,
              extras_depois=None):
    """Cena do tutorial a pe. estacoes: (nome, x, rotulo, visual) com visual =
    None ou dict(textura, escala, pos opcional, regiao opcional).
    extras_antes/extras_depois sao funcoes: rodam depois de a lista de
    recursos desta cena ser zerada, para os ids que registram valerem nela."""
    _recursos.clear()
    corpo = no(raiz, "Node2D", None, script=f'ExtResource("{rec(script, "Script")}")',
               borda=v2(*borda), alcance=alcance)
    corpo += no("Fundo", "Sprite2D", ".", texture=f'ExtResource("{rec(fundo)}")', centered="false")
    corpo += extras_antes() if extras_antes else ""
    corpo += no("Estacoes", "Node2D", ".")
    topo_rotulo = -260 if escala == 2 else -160
    for nome, x, texto, visual in estacoes:
        corpo += no(nome, "Node2D", "Estacoes", position=v2(x, CHAO))
        if visual:
            vt = visual["textura"]
            e = visual.get("escala", escala)
            from PIL import Image
            w, h = Image.open(vt.replace("res://", "")).size
            pos = visual.get("pos") or (-w * e / 2, -h * e)
            props = {"texture": f'ExtResource("{rec(vt)}")', "centered": "false", "position": v2(*pos)}
            if e != 1:
                props["scale"] = v2(e, e)
            corpo += no("Visual", "Sprite2D", f"Estacoes/{nome}", **props)
            topo = min(topo_rotulo, pos[1] - 40)
        else:
            topo = topo_rotulo
        corpo += rotulo("Nome", f"Estacoes/{nome}", texto, topo)
    corpo += neto(x_neto, escala)
    corpo += extras_depois() if extras_depois else ""
    corpo += ui()
    io.open(f"scenes/tutorial/{arquivo}", "w", encoding="utf-8", newline="\n").write(cabecalho() + corpo)
    print("scenes/tutorial/" + arquivo)


os.makedirs("scenes/tutorial", exist_ok=True)
S = "res://scripts/tutorial/"

# ------------------------------------------------------------------ quarto
cena_a_pe("Quarto.tscn", "Quarto", S + "quarto.gd", T + "cenarios/quarto.png", [
    ("PosterPai", 64, "Racionais MC's (era do pai)", None),
    ("Cama", 152, "Janela", None),
    ("MauMau", 232, "MauMau", {"textura": T + "bichos/maumau_deitado.png", "pos": (-44, -150)}),
    ("Fotos", 336, "Fotos", None),
    ("PosterCriciuma", 416, "Criciúma, campeão de 91", None),
    ("PosterPele", 504, "Pelé, o Rei", None),
    ("PosterZeze", 592, "Zezé Di Camargo & Luciano", None),
    ("PosterLeonardo", 680, "Leandro & Leonardo", None),
    ("PosterDjavan", 768, "Djavan - Grandes Sucessos", None),
    ("PosterLebron", 856, "LeBron James", None),
    ("Camisa", 960, "Camisa do Criciúma de 91", None),
    ("Prateleira", 1064, "Prateleira", None),
    ("Vara", 1140, "Vara de bambu", {"textura": T + "cenarios/vara_parede.png", "pos": (-8, -416)}),
    ("Porta", 1200, "Cozinha", None),
], x_neto=300, escala=2, borda=(60, 1220), alcance=46,
    extras_depois=lambda: sprite_pe("VoNaPorta", ".", T + "personagens/vo.png", 1246, escala=2))

# ----------------------------------------------------------------- cozinha
cena_a_pe("Cozinha.tscn", "Cozinha", S + "cozinha.gd", T + "cenarios/cozinha.png", [
    ("Fogao", 112, "Fogão a lenha", None),
    ("Tigela", 256, "Tigela do MauMau", None),
    ("Marlene", 340, "Vó", {"textura": T + "personagens/marlene_jovem.png"}),
    ("Panelas", 528, "Panelas", None),
    ("Mesa", 664, "Mesa do café", None),
    ("Radio", 790, "Rádio", None),
    ("Filtro", 852, "Filtro de barro", None),
    ("Calendario", 900, "Folhinha", None),
    ("Geladeira", 984, "Geladeira", None),
    ("Porta", 1184, "Terreiro", None),
], x_neto=170, escala=2, borda=(80, 1220), alcance=46,
    extras_antes=lambda: sprite_pe("VoNaMesa", ".", T + "personagens/vo.png", 734, escala=2))

# ---------------------------------------------------------------- terreiro
cena_a_pe("Terreiro.tscn", "Terreiro", S + "terreiro.gd", T + "cenarios/saida.png", [
    ("Pacoca", 470, "Paçoca", {"textura": T + "bichos/pacoca_em_pe.png", "pos": (-36, -46)}),
    ("Varal", 560, "Varal", None),
    ("Galinhas", 612, "Galinhas", None),
    ("Alexandre", 780, "Alexandre", {"textura": T + "personagens/alexandre.png"}),
    ("Apollo", 960, "Apollo", {"textura": T + "personagens/apollo.png"}),
    ("Bergamoteira", 1072, "Bergamoteira", None),
    ("Latoes", 1130, "Latões de leite", None),
], x_neto=220, escala=1, borda=(60, 1180), alcance=40,
    extras_depois=lambda: vo_acompanhante(140))

# -------------------------------------------------------------------- cais
cena_a_pe("CaisRio.tscn", "CaisRio", S + "cais_rio.gd", T + "cenarios/cais_rio.png", [
    ("Alexandre", 110, "Alexandre", {"textura": T + "personagens/alexandre.png"}),
    ("Apollo", 262, "Apollo", {"textura": T + "personagens/apollo.png"}),
    ("Bote", 830, "Bote do vô", {"textura": T + "personagens/bote.png", "pos": (20, -36)}),
], x_neto=380, escala=1, borda=(60, 836), alcance=50,
    extras_depois=lambda: vo_acompanhante(300))


# --------------------------------------------------------------- passagens
def passagem(arquivo, raiz, fundo, roteiro, seguinte, comboio, entrada, conversa, saida, balanco):
    _recursos.clear()
    corpo = no(raiz, "Node2D", None, script=f'ExtResource("{rec(S + "passagem.gd", "Script")}")',
               roteiro=f'&"{roteiro}"', cena_seguinte=f'"{seguinte}"', x_entrada=entrada, x_conversa=conversa,
               x_saida=saida, balanco=balanco)
    corpo += no("Fundo", "Sprite2D", ".", texture=f'ExtResource("{rec(fundo)}")', centered="false")
    corpo += no("Comboio", "Node2D", ".")
    for nome, textura, pos, regiao in comboio:
        props = {"texture": f'ExtResource("{rec(textura)}")', "centered": "false", "position": v2(*pos)}
        if regiao:
            props["region_enabled"] = "true"
            props["region_rect"] = "Rect2(%d, %d, %d, %d)" % regiao
        corpo += no(nome, "Sprite2D", "Comboio", **props)
    io.open(f"scenes/tutorial/{arquivo}", "w", encoding="utf-8", newline="\n").write(cabecalho() + corpo)
    print("scenes/tutorial/" + arquivo)


# ------------------------------------------------------- estrada a cavalo
# O jogador conduz o Alexandre (folha de 4 quadros de 152x220) com a camera
# junto; o vo vem atras no Apollo (176x232). A estrada tem tres telas.
_recursos.clear()
corpo = no("Estrada", "Node2D", None, script=f'ExtResource("{rec(S + "estrada.gd", "Script")}")',
           borda=v2(120.0, 3720.0), alcance=40.0)
corpo += no("Fundo", "Sprite2D", ".", texture=f'ExtResource("{rec(T + "cenarios/estrada_longa.png")}")',
            centered="false")
corpo += no("Estacoes", "Node2D", ".")
corpo += no("Vo", "Sprite2D", ".", script=f'ExtResource("{rec(S + "acompanhante.gd", "Script")}")',
            position=v2(60, CHAO - 116), texture=f'ExtResource("{rec(T + "personagens/apollo_montado.png")}")',
            hframes=4, alvo='NodePath("../Player")', distancia=170.0, velocidade=320.0)
corpo += no("Player", "Sprite2D", ".", position=v2(240, CHAO - 110),
            texture=f'ExtResource("{rec(T + "personagens/alexandre_montado.png")}")', hframes=4)
corpo += no("OitoDirecoes", "Node", "Player", script=f'ExtResource("{rec("res://scripts/eight_dir.gd", "Script")}")',
            max_speed=300.0, acceleration=700.0, deceleration=900.0)
corpo += no("Camera", "Camera2D", "Player", limit_left=0, limit_right=3840, limit_top=0, limit_bottom=720,
            position=v2(0, -50), position_smoothing_enabled="true", position_smoothing_speed=6.0)
corpo += ui()
io.open("scenes/tutorial/Estrada.tscn", "w", encoding="utf-8", newline="\n").write(cabecalho() + corpo)
print("scenes/tutorial/Estrada.tscn")

# no bote: os dois cortados na borda do bote (y 508), o bote por cima
passagem("Descida.tscn", "Descida", T + "cenarios/rio_de_passagem.png", "descida",
         "res://scenes/tutorial/MeioDoRio.tscn", [
             ("VoSentado", T + "personagens/vo.png", (-136 + 64 - 32, 508 - 84), (0, 0, 64, 84)),
             ("NetoSentado", T + "personagens/neto.png", (-136 + 196 - 32, 508 - 70), (0, 0, 64, 70)),
             ("Bote", T + "personagens/bote.png", (-136, 484), None),
         ], entrada=-300, conversa=640, saida=1600, balanco=3.0)

# a volta rio acima, para o cais: o mesmo bote espelhado, da direita pra esquerda
passagem("Subida.tscn", "Subida", T + "cenarios/rio_de_passagem.png", "subida",
         "res://scenes/tutorial/CaisRio.tscn", [
             ("VoSentado", T + "personagens/vo.png", (-136 + 64 - 32, 508 - 84), (0, 0, 64, 84)),
             ("NetoSentado", T + "personagens/neto.png", (-136 + 196 - 32, 508 - 70), (0, 0, 64, 70)),
             ("Bote", T + "personagens/bote.png", (-136, 484), None),
         ], entrada=1600, conversa=640, saida=-400, balanco=3.0)

# --------------------------------------------------------------------- fim
_recursos.clear()
corpo = no("Fim", "Node2D", None, script=f'ExtResource("{rec(S + "fim.gd", "Script")}")')
corpo += no("Fundo", "Sprite2D", ".", texture=f'ExtResource("{rec(T + "cenarios/saida_manha.png")}")', centered="false")
corpo += no("Marlene", "Sprite2D", ".", texture=f'ExtResource("{rec(T + "personagens/marlene_jovem.png")}")',
            position=v2(330, CHAO - 44))
# chegam montados (folhas de 4 quadros) e apeiam: os cavalos parados ficam na
# cerca e os dois descem na frente deles
corpo += no("Alexandre", "Sprite2D", ".", texture=f'ExtResource("{rec(T + "personagens/alexandre.png")}")',
            position=v2(680, CHAO - 66), flip_h="true")
corpo += no("Apollo", "Sprite2D", ".", texture=f'ExtResource("{rec(T + "personagens/apollo.png")}")',
            position=v2(900, CHAO - 72), flip_h="true")
corpo += no("AlexandreMontado", "Sprite2D", ".",
            texture=f'ExtResource("{rec(T + "personagens/alexandre_montado.png")}")',
            position=v2(1500, CHAO - 110), flip_h="true", hframes=4)
corpo += no("ApolloMontado", "Sprite2D", ".", texture=f'ExtResource("{rec(T + "personagens/apollo_montado.png")}")',
            position=v2(1720, CHAO - 116), flip_h="true", hframes=4)
corpo += no("Neto", "Sprite2D", ".", texture=f'ExtResource("{rec(T + "personagens/neto.png")}")',
            position=v2(560, CHAO - 48), flip_h="true")
corpo += no("Vo", "Sprite2D", ".", texture=f'ExtResource("{rec(T + "personagens/vo.png")}")',
            position=v2(790, CHAO - 56), flip_h="true")
io.open("scenes/tutorial/Fim.tscn", "w", encoding="utf-8", newline="\n").write(cabecalho() + corpo)
print("scenes/tutorial/Fim.tscn")

# ------------------------------------------------- pescaria no meio do rio
s = io.open("scenes/Acude.tscn", encoding="utf-8").read()
s = s.replace('path="res://scripts/acude.gd"', 'path="res://scripts/tutorial/rio.gd"')
for chave in ("tex_ceu", "tex_agua", "tex_barranco", "tex_estrutura"):
    s = re.sub(r'\[ext_resource [^\n]*id="%s"\]\n' % chave, "", s)
    s = re.sub(r'\[node name="\w+" type="Sprite2D" parent="Jogo"\]\nposition = Vector2\([^)]*\)\n'
               r'texture = ExtResource\("%s"\)\n\n' % chave, "", s)
s = s.replace('[ext_resource type="Texture2D" path="res://assets/sprites/tiago/tiago.png" id="tex_player"]',
              f'[ext_resource type="Texture2D" path="{T}personagens/neto.png" id="tex_player"]\n'
              f'[ext_resource type="Texture2D" path="{T}cenarios/meio_do_rio.png" id="tex_rio"]\n'
              f'[ext_resource type="Texture2D" path="{T}personagens/vo.png" id="tex_vo"]\n'
              f'[ext_resource type="Texture2D" path="{T}personagens/bote.png" id="tex_bote"]')
s = s.replace('[node name="Acude" type="Node2D"]', '[node name="MeioDoRio" type="Node2D"]')
s = s.replace('''[node name="ZonaPesca" type="Sprite2D" parent="Jogo"]''',
              '''[node name="Fundo" type="Sprite2D" parent="Jogo"]
texture = ExtResource("tex_rio")
centered = false

[node name="ZonaPesca" type="Sprite2D" parent="Jogo"]''')
s = s.replace("position = Vector2(572, 400)\nscale = Vector2(0.52, 0.36)", "position = Vector2(530, 474)")
s = s.replace('text = "< Voltar ao cais"', 'text = ""')
s = s.replace('''[node name="Player" type="Sprite2D" parent="Jogo"]
position = Vector2(240, 392)''', '''[node name="Player" type="Sprite2D" parent="Jogo"]
position = Vector2(530, 474)''')
s = s.replace('''max_speed = 200.0
acceleration = 600.0
deceleration = 500.0''', '''max_speed = 0.0
acceleration = 0.0
deceleration = 500.0''')
s = s.replace('''[node name="Visual" type="Node" parent="Jogo/Player"]
script = ExtResource("script_visual_tiago")''', f'''[node name="Visual" type="Node" parent="Jogo/Player"]
script = ExtResource("script_visual_tiago")
pasta = "{T}personagens/"
prefixo = "neto"

[node name="VoSentado" type="Sprite2D" parent="Jogo"]
texture = ExtResource("tex_vo")
centered = false
position = Vector2(366, 424)
region_enabled = true
region_rect = Rect2(0, 0, 64, 84)

[node name="Bote" type="Sprite2D" parent="Jogo"]
texture = ExtResource("tex_bote")
centered = false
position = Vector2(334, 484)''')
assert "tex_ceu" not in s and "tex_rio" in s and "VoSentado" in s
io.open("scenes/tutorial/MeioDoRio.tscn", "w", encoding="utf-8", newline="\n").write(s)
print("scenes/tutorial/MeioDoRio.tscn")
