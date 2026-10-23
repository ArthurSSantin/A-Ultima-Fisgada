class_name MapaLocais
extends CanvasLayer

## Tela de escolher para onde pescar, aberta pelo barco do cais.
##
##     var id: StringName = await MapaLocais.abrir_em(self)
##     if not id.is_empty():
##         ir_para(Partida.LOCAIS[id].cena)
##
## Monta os proprios nos, como a CaixaDialogo, para nao depender de cena. So
## entram no mapa os locais que Partida.locais_abertos() devolve: um local
## ainda oculto nao vira alfinete nenhum, nem aparece acinzentado.
##
## Setas andam de alfinete em alfinete, ESPACO confirma e ESC sai. O mouse
## tambem funciona: passar por cima destaca e clicar confirma.

signal _escolheu(id: StringName)

const COR_PAPEL: Color = Color(0.91, 0.85, 0.69)
const COR_TINTA: Color = Color(0.22, 0.17, 0.10)
const COR_DESTAQUE: Color = Color(0.76, 0.31, 0.23)

const MAPA: Texture2D = preload("res://assets/sprites/ui/mapa.png")
const PINO: Texture2D = preload("res://assets/sprites/ui/pino.png")
const PINO_ATIVO: Texture2D = preload("res://assets/sprites/ui/pino_ativo.png")
const PINO_SOMBRA: Texture2D = preload("res://assets/sprites/ui/pino_sombra.png")

## Canto superior esquerdo do mapa na tela; o tamanho vem da textura.
const ORIGEM: Vector2 = Vector2(240.0, 110.0)

var _locais: Array[Dictionary] = []
var _pinos: Array[TextureRect] = []
var _selecionado: int = 0
var _nome: Label
var _descricao: Label
var _fechando: bool = false


## Abre o mapa como filho de `dono` e devolve o id escolhido, ou &"" se saiu.
static func abrir_em(dono: Node) -> StringName:
	var mapa := MapaLocais.new()
	dono.add_child(mapa)
	var id: StringName = await mapa._escolheu
	mapa.queue_free()
	return id


func _ready() -> void:
	layer = 12
	_locais = Partida.locais_abertos()

	var fonte := SystemFont.new()
	fonte.font_names = PackedStringArray(["Arial"])
	var negrito := SystemFont.new()
	negrito.font_names = PackedStringArray(["Arial"])
	negrito.font_weight = 700

	var fundo := ColorRect.new()
	fundo.color = Color(0.04, 0.07, 0.14, 0.82)
	fundo.size = Vector2(1280, 720)
	add_child(fundo)

	var folha := TextureRect.new()
	folha.texture = MAPA
	folha.position = ORIGEM
	add_child(folha)

	var titulo := _label(negrito, 26, COR_TINTA)
	titulo.text = "Para onde hoje?"
	titulo.position = ORIGEM + Vector2(24.0, 18.0)
	add_child(titulo)

	for i in _locais.size():
		var local: Dictionary = _locais[i]
		var ponto: Vector2 = ORIGEM + Vector2(
			local.pino.x * MAPA.get_width(), local.pino.y * MAPA.get_height()
		)
		var sombra := TextureRect.new()
		sombra.texture = PINO_SOMBRA
		sombra.position = ponto - Vector2(PINO_SOMBRA.get_width() * 0.5, 0.0)
		add_child(sombra)

		var pino := TextureRect.new()
		pino.texture = PINO
		# A ponta do alfinete e que marca o lugar, nao o centro dele.
		pino.position = ponto - Vector2(PINO.get_width() * 0.5, PINO.get_height())
		pino.mouse_filter = Control.MOUSE_FILTER_STOP
		pino.mouse_entered.connect(_selecionar.bind(i))
		pino.gui_input.connect(_clique_no_pino.bind(i))
		add_child(pino)
		_pinos.append(pino)

		var nome := _label(negrito, 16, COR_TINTA)
		nome.text = local.nome
		nome.position = ponto + Vector2(-60.0, 8.0)
		nome.size = Vector2(120.0, 20.0)
		nome.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		add_child(nome)

	var rodape := ColorRect.new()
	rodape.color = Color(0.07, 0.13, 0.28, 0.92)
	rodape.position = Vector2(ORIGEM.x, ORIGEM.y + MAPA.get_height() + 10.0)
	rodape.size = Vector2(MAPA.get_width(), 86.0)
	add_child(rodape)

	_nome = _label(negrito, 22, Color(1.0, 0.82, 0.35))
	_nome.position = rodape.position + Vector2(18.0, 10.0)
	add_child(_nome)

	_descricao = _label(fonte, 16, COR_PAPEL)
	_descricao.position = rodape.position + Vector2(18.0, 38.0)
	_descricao.size = Vector2(MAPA.get_width() - 36.0, 40.0)
	_descricao.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_descricao)

	var dica := _label(fonte, 13, COR_PAPEL.darkened(0.25))
	dica.text = "Setas escolhem   ESPAÇO embarca   ESC volta"
	dica.position = rodape.position + Vector2(MAPA.get_width() - 320.0, 60.0)
	add_child(dica)

	_selecionar(0)


func _input(evento: InputEvent) -> void:
	if _fechando or evento.is_echo():
		return
	if evento.is_action_pressed(&"espaco"):
		get_viewport().set_input_as_handled()
		_confirmar()
	elif evento.is_action_pressed(&"ui_cancel"):
		get_viewport().set_input_as_handled()
		_fechar(&"")
	elif evento.is_action_pressed(&"ui_right") or evento.is_action_pressed(&"ui_down"):
		_selecionar(wrapi(_selecionado + 1, 0, maxi(_locais.size(), 1)))
	elif evento.is_action_pressed(&"ui_left") or evento.is_action_pressed(&"ui_up"):
		_selecionar(wrapi(_selecionado - 1, 0, maxi(_locais.size(), 1)))


func _clique_no_pino(evento: InputEvent, indice: int) -> void:
	if evento is InputEventMouseButton and evento.pressed \
			and evento.button_index == MOUSE_BUTTON_LEFT:
		_selecionar(indice)
		_confirmar()


func _selecionar(indice: int) -> void:
	if _locais.is_empty():
		_nome.text = "Nenhum lugar no mapa"
		_descricao.text = "O caderno do avô ainda não marcou ponto nenhum."
		return
	_selecionado = indice
	for i in _pinos.size():
		_pinos[i].texture = PINO_ATIVO if i == indice else PINO
	_nome.text = _locais[indice].nome
	_descricao.text = _locais[indice].descricao


func _confirmar() -> void:
	if _locais.is_empty():
		_fechar(&"")
		return
	_fechar(_locais[_selecionado].id)


func _fechar(id: StringName) -> void:
	if _fechando:
		return
	_fechando = true
	_escolheu.emit(id)


func _label(fonte: Font, tamanho: int, cor: Color) -> Label:
	var label := Label.new()
	label.add_theme_font_override("font", fonte)
	label.add_theme_font_size_override("font_size", tamanho)
	label.add_theme_color_override("font_color", cor)
	label.add_theme_color_override("font_outline_color", Color(0.96, 0.92, 0.82, 0.8))
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label
