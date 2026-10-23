extends Node2D

## Tela inicial: o titulo e a escolha do nome do personagem.
##
## Os dois nomes vao para Partida.definir_nome(); dali em diante os dialogos
## escrevem {nome} e {avo}, e a CaixaDialogo troca sozinha. Em branco, cada um
## fica com o padrao.
##
## A interface e montada em codigo, como a CaixaDialogo, para a cena guardar so
## o cenario de fundo.
##
## ENTER comeca, de qualquer um dos dois campos. O ESPACO nao serve aqui porque
## no campo de texto ele digita um espaco, que e exatamente o que alguem faz ao
## escrever um nome composto.

const CENA_CASA: String = "res://scenes/tutorial/Quarto.tscn"

const COR_PAPEL: Color = Color(0.96, 0.94, 0.86)
const COR_DOURADO: Color = Color(1.0, 0.82, 0.35)
const COR_FUNDO: Color = Color(0.07, 0.13, 0.28, 0.94)

var _campo: LineEdit
var _campo_avo: LineEdit
var _comecando: bool = false


func _ready() -> void:
	var fonte := SystemFont.new()
	fonte.font_names = PackedStringArray(["Arial"])
	var negrito := SystemFont.new()
	negrito.font_names = PackedStringArray(["Arial"])
	negrito.font_weight = 700

	var camada := CanvasLayer.new()
	camada.layer = 10
	add_child(camada)

	# O cenario do cais fica atras, escurecido, para a tela nao ser uma cor chapada.
	var veu := ColorRect.new()
	veu.color = Color(0.04, 0.07, 0.14, 0.55)
	veu.size = Vector2(1280, 720)
	camada.add_child(veu)

	var titulo := _label(negrito, 64, COR_DOURADO)
	titulo.text = "A ÚLTIMA FISGADA"
	titulo.position = Vector2(0, 96)
	titulo.size = Vector2(1280, 80)
	titulo.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	camada.add_child(titulo)

	var subtitulo := _label(fonte, 22, COR_PAPEL)
	subtitulo.text = "Uma manhã com o vô"
	subtitulo.position = Vector2(0, 176)
	subtitulo.size = Vector2(1280, 30)
	subtitulo.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	camada.add_child(subtitulo)

	var painel := PanelContainer.new()
	var estilo := StyleBoxFlat.new()
	estilo.bg_color = COR_FUNDO
	estilo.set_corner_radius_all(6)
	estilo.set_content_margin_all(24)
	estilo.border_color = COR_DOURADO
	estilo.set_border_width_all(2)
	painel.add_theme_stylebox_override("panel", estilo)
	painel.position = Vector2(370, 272)
	painel.size = Vector2(540, 280)
	camada.add_child(painel)

	var coluna := VBoxContainer.new()
	coluna.add_theme_constant_override("separation", 14)
	painel.add_child(coluna)

	var pergunta := _label(negrito, 20, COR_DOURADO)
	pergunta.text = "Qual o teu nome?"
	coluna.add_child(pergunta)

	_campo = _novo_campo(negrito, Partida.NOME_PADRAO, Partida.nome)
	coluna.add_child(_campo)

	var pergunta_avo := _label(negrito, 20, COR_DOURADO)
	pergunta_avo.text = "E o nome do teu avô, o velho pescador?"
	coluna.add_child(pergunta_avo)

	_campo_avo = _novo_campo(negrito, Partida.NOME_AVO_PADRAO, Partida.nome_avo)
	coluna.add_child(_campo_avo)

	var botao := Button.new()
	botao.text = "Começar"
	botao.add_theme_font_override("font", negrito)
	botao.add_theme_font_size_override("font_size", 20)
	botao.custom_minimum_size = Vector2(452, 44)
	botao.pressed.connect(func() -> void: _comecar(""))
	coluna.add_child(botao)

	var dica := _label(fonte, 14, COR_PAPEL.darkened(0.25))
	dica.text = "ENTER começa   •   em branco, ficam %s e %s" % [Partida.NOME_PADRAO, Partida.NOME_AVO_PADRAO]
	dica.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	coluna.add_child(dica)

	_campo.grab_focus()


## O argumento vem do text_submitted e e ignorado: os dois campos sao lidos
## direto, para o ENTER valer igual em qualquer um deles.
func _comecar(_submetido: String) -> void:
	if _comecando:
		return
	_comecando = true
	Partida.definir_nome(_campo.text, _campo_avo.text)
	get_tree().change_scene_to_file.call_deferred(CENA_CASA)


func _novo_campo(fonte: Font, padrao: String, atual: String) -> LineEdit:
	var campo := LineEdit.new()
	campo.placeholder_text = padrao
	campo.text = atual if atual != padrao else ""
	campo.max_length = Partida.NOME_MAXIMO
	campo.alignment = HORIZONTAL_ALIGNMENT_CENTER
	campo.custom_minimum_size = Vector2(492, 44)
	campo.add_theme_font_override("font", fonte)
	campo.add_theme_font_size_override("font_size", 22)
	campo.text_submitted.connect(_comecar)
	return campo


func _label(fonte: Font, tamanho: int, cor: Color) -> Label:
	var label := Label.new()
	label.add_theme_font_override("font", fonte)
	label.add_theme_font_size_override("font_size", tamanho)
	label.add_theme_color_override("font_color", cor)
	label.add_theme_color_override("font_outline_color", Color(0.05, 0.09, 0.18))
	label.add_theme_constant_override("outline_size", 6)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label
