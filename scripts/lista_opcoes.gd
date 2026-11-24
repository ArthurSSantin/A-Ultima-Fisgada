class_name ListaOpcoes
extends VBoxContainer

## Lista de opcoes dos menus (inicial, pausa e configuracoes), no mesmo visual
## da CaixaDialogo: a escolhida fica dourada, com o ">" na frente.
##
##     var lista := ListaOpcoes.new()
##     lista.adicionar("Começar")
##     lista.adicionar("Música", func() -> String: return "80%", _mudar_musica)
##     lista.escolheu.connect(_on_escolheu)
##
## Setas para cima e para baixo escolhem; ESPACO ou ENTER confirmam; ESC
## cancela. Uma opcao com `ajustar` e um valor: as setas para os lados chamam
## ajustar(-1) ou ajustar(+1), e confirmar avanca o valor. O mouse tambem
## funciona: passar por cima escolhe, clicar confirma, e numa opcao com valor
## clicar no "<" baixa e no ">" sobe.
##
## So responde enquanto `ativa` e visivel, para um submenu aberto por cima nao
## mexer na lista de baixo.

signal escolheu(indice: int)
signal cancelou

const COR_TEXTO: Color = Color(0.96, 0.94, 0.86)
const COR_DESTAQUE: Color = Color(1.0, 0.82, 0.35)
const COR_APAGADO: Color = Color(0.55, 0.56, 0.58)
const COR_FUNDO: Color = Color(0.07, 0.13, 0.28, 0.96)
const LARGURA_VALOR: float = 170.0

var ativa: bool = true
var tamanho_texto: int = 24

var _itens: Array[Dictionary] = []
var _selecionado: int = 0
var _fonte: Font


func _init() -> void:
	_fonte = Fontes.normal()
	add_theme_constant_override("separation", 6)


## A moldura azul com borda dourada dos menus.
static func moldura(margem: float = 24.0) -> PanelContainer:
	var painel := PanelContainer.new()
	var estilo := StyleBoxFlat.new()
	estilo.bg_color = COR_FUNDO
	estilo.border_color = COR_DESTAQUE
	estilo.set_border_width_all(2)
	estilo.set_corner_radius_all(6)
	estilo.set_content_margin_all(margem)
	painel.add_theme_stylebox_override("panel", estilo)
	return painel


## Acrescenta uma opcao e devolve o indice dela. Com `valor`, a linha mostra o
## que ele devolve do lado direito; com `ajustar`, as setas para os lados
## mudam esse valor.
func adicionar(texto: String, valor: Callable = Callable(), ajustar: Callable = Callable()) -> int:
	var linha := HBoxContainer.new()
	linha.mouse_filter = Control.MOUSE_FILTER_STOP
	linha.add_theme_constant_override("separation", 8)
	add_child(linha)

	var marcador := _label(">")
	marcador.custom_minimum_size.x = 18.0
	linha.add_child(marcador)

	var rotulo := _label(texto)
	rotulo.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	linha.add_child(rotulo)

	var indice: int = _itens.size()
	var valor_label: Label = null
	var setas: Array[Label] = []
	if valor.is_valid():
		if ajustar.is_valid():
			setas.append(_seta("<", indice, -1))
			linha.add_child(setas[0])
		valor_label = _label("")
		valor_label.custom_minimum_size.x = LARGURA_VALOR
		valor_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER if ajustar.is_valid() 			else HORIZONTAL_ALIGNMENT_RIGHT
		linha.add_child(valor_label)
		if ajustar.is_valid():
			setas.append(_seta(">", indice, 1))
			linha.add_child(setas[1])

	_itens.append({
		"linha": linha, "marcador": marcador, "rotulo": rotulo,
		"valor_label": valor_label, "valor": valor, "ajustar": ajustar, "setas": setas,
	})
	linha.mouse_entered.connect(func() -> void: _selecionar(indice))
	linha.gui_input.connect(_clique.bind(indice))
	atualizar()
	return indice


## Muda o texto de uma opcao (o "Começar" que vira "Continuar", por exemplo).
func renomear(indice: int, texto: String) -> void:
	_itens[indice].rotulo.text = texto


func selecionar(indice: int) -> void:
	_selecionado = clampi(indice, 0, maxi(_itens.size() - 1, 0))
	atualizar()


## Redesenha a selecao e os valores.
func atualizar() -> void:
	for i in _itens.size():
		var item: Dictionary = _itens[i]
		var cor: Color = COR_DESTAQUE if i == _selecionado else COR_TEXTO
		item.marcador.modulate.a = 1.0 if i == _selecionado else 0.0
		item.marcador.add_theme_color_override("font_color", COR_DESTAQUE)
		item.rotulo.add_theme_color_override("font_color", cor)
		if item.valor_label:
			item.valor_label.text = item.valor.call()
			item.valor_label.add_theme_color_override("font_color", cor)
		for seta: Label in item.setas:
			seta.add_theme_color_override("font_color", cor)


func _input(evento: InputEvent) -> void:
	if not ativa or not is_visible_in_tree() or _itens.is_empty():
		return
	if evento.is_action_pressed(&"ui_up", true):
		_aceitar(evento)
		_selecionar(wrapi(_selecionado - 1, 0, _itens.size()))
	elif evento.is_action_pressed(&"ui_down", true):
		_aceitar(evento)
		_selecionar(wrapi(_selecionado + 1, 0, _itens.size()))
	elif evento.is_action_pressed(&"ui_left", true):
		_aceitar(evento)
		_ajustar(-1)
	elif evento.is_action_pressed(&"ui_right", true):
		_aceitar(evento)
		_ajustar(1)
	elif evento.is_echo():
		return
	elif evento.is_action_pressed(&"espaco") or evento.is_action_pressed(&"ui_accept"):
		_aceitar(evento)
		_confirmar()
	elif evento.is_action_pressed(&"ui_cancel"):
		_aceitar(evento)
		Som.tocar("cursor")
		cancelou.emit()


func _aceitar(_evento: InputEvent) -> void:
	get_viewport().set_input_as_handled()


func _selecionar(indice: int) -> void:
	if indice == _selecionado:
		return
	_selecionado = indice
	Som.tocar("cursor")
	atualizar()


func _ajustar(direcao: int) -> void:
	var ajustar: Callable = _itens[_selecionado].ajustar
	if not ajustar.is_valid():
		return
	ajustar.call(direcao)
	Som.tocar("cursor")
	atualizar()


func _confirmar() -> void:
	if _itens[_selecionado].ajustar.is_valid():
		_ajustar(1)
		return
	Som.tocar("confirmar")
	escolheu.emit(_selecionado)


## O "<" e o ">" de uma opcao com valor: clicar baixa ou sobe.
func _seta(texto: String, indice: int, direcao: int) -> Label:
	var seta := _label(texto)
	seta.custom_minimum_size.x = 22.0
	seta.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	seta.mouse_filter = Control.MOUSE_FILTER_STOP
	seta.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	seta.mouse_entered.connect(func() -> void: _selecionar(indice))
	seta.gui_input.connect(func(evento: InputEvent) -> void:
		if ativa and evento is InputEventMouseButton and evento.pressed 				and evento.button_index == MOUSE_BUTTON_LEFT:
			get_viewport().set_input_as_handled()
			_selecionar(indice)
			_ajustar(direcao))
	return seta


func _clique(evento: InputEvent, indice: int) -> void:
	if not ativa:
		return
	if evento is InputEventMouseButton and evento.pressed and evento.button_index == MOUSE_BUTTON_LEFT:
		get_viewport().set_input_as_handled()
		_selecionar(indice)
		# Numa opcao com valor, quem muda sao o "<" e o ">".
		if not _itens[indice].ajustar.is_valid():
			_confirmar()


func _label(texto: String) -> Label:
	var label := Label.new()
	label.text = texto
	label.add_theme_font_override("font", _fonte)
	label.add_theme_font_size_override("font_size", tamanho_texto)
	label.add_theme_color_override("font_color", COR_TEXTO)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label
