class_name QuadroObjetivos
extends CanvasLayer

## O quadro de objetivos do tutorial, no canto de cima a esquerda. Mostra os
## cumpridos (riscados de verde) e o proximo; os dois de pesca aparecem juntos.
## Objetivo que aparece pela primeira vez pisca. TAB esconde e mostra.

const LARGURA: float = 270.0
const COR_FEITO := Color(0.63, 0.59, 0.55)
const COR_PENDENTE := Color(0.96, 0.92, 0.86)
const COR_TITULO := Color(1.0, 0.82, 0.35)

## No canto direito em vez do esquerdo (no rio as barras da pesca ficam a
## esquerda).
var a_direita: bool = false

## Ids que ja apareceram em alguma cena: o pisca e so na primeira vez.
static var _vistos: Array[StringName] = []

var _painel: PanelContainer
var _coluna: VBoxContainer
var _linhas: Dictionary = {}
var _faltam: Label
var _fonte: SystemFont


func _ready() -> void:
	layer = 6
	_fonte = SystemFont.new()
	_fonte.font_names = PackedStringArray(["Arial"])
	_painel = PanelContainer.new()
	var estilo := StyleBoxFlat.new()
	estilo.bg_color = Color(0.08, 0.06, 0.05, 0.72)
	estilo.set_corner_radius_all(6)
	estilo.set_content_margin_all(10)
	_painel.add_theme_stylebox_override("panel", estilo)
	_painel.position = Vector2(12, 12)
	_painel.custom_minimum_size = Vector2(LARGURA, 0)
	_painel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_painel)
	_coluna = VBoxContainer.new()
	_coluna.add_theme_constant_override("separation", 3)
	_painel.add_child(_coluna)
	var titulo := _rotulo(15, COR_TITULO, true)
	titulo.text = "OBJETIVOS   (TAB)"
	_coluna.add_child(titulo)
	for o in Partida.OBJETIVOS:
		var r := _rotulo(15, COR_PENDENTE)
		_coluna.add_child(r)
		_linhas[o.id] = r
		if o.id == &"especies":
			_faltam = _rotulo(13, COR_PENDENTE.darkened(0.25))
			_coluna.add_child(_faltam)
	_atualizar(false)


func _process(_delta: float) -> void:
	_atualizar(true)
	if a_direita:
		_painel.position.x = 1280.0 - 12.0 - _painel.size.x


func _unhandled_input(evento: InputEvent) -> void:
	if evento is InputEventKey and evento.pressed and not evento.echo and evento.keycode == KEY_TAB:
		_painel.visible = not _painel.visible


func _atualizar(piscar: bool) -> void:
	var proximo_achado: bool = false
	for o in Partida.OBJETIVOS:
		var r: Label = _linhas[o.id]
		var feito: bool = Partida.feito(o.id)
		var mostrar: bool = feito
		if not feito and not proximo_achado:
			mostrar = true
			# Os dois de pesca correm juntos: o outro aparece tambem.
			proximo_achado = o.id != &"especies" or Partida.feito(&"peixes")
		r.visible = mostrar
		r.text = ("[x]  " if feito else "[  ]  ") + Partida.texto_objetivo(o)
		r.add_theme_color_override("font_color", COR_FEITO if feito else COR_PENDENTE)
		if mostrar and not o.id in _vistos:
			_vistos.append(o.id)
			if piscar:
				_piscar(r)
	var faltam: Array[String] = Partida.especies_do_rio_faltando()
	_faltam.visible = _linhas[&"especies"].visible and not Partida.feito(&"especies")
	_faltam.text = "      falta: " + ", ".join(faltam).to_lower()


func _piscar(r: Label) -> void:
	var t := create_tween().set_loops(3)
	t.tween_property(r, "modulate", Color(1.6, 1.4, 0.6), 0.18)
	t.tween_property(r, "modulate", Color.WHITE, 0.18)


func _rotulo(tamanho: int, cor: Color, negrito: bool = false) -> Label:
	var r := Label.new()
	var f: Font = _fonte
	if negrito:
		var nf := SystemFont.new()
		nf.font_names = PackedStringArray(["Arial"])
		nf.font_weight = 700
		f = nf
	r.add_theme_font_override("font", f)
	r.add_theme_font_size_override("font_size", tamanho)
	r.add_theme_color_override("font_color", cor)
	r.add_theme_color_override("font_outline_color", Color(0.05, 0.03, 0.02))
	r.add_theme_constant_override("outline_size", 3)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return r


## Reinicia o "ja vi" quando o tutorial comeca de novo.
static func zerar() -> void:
	_vistos.clear()
