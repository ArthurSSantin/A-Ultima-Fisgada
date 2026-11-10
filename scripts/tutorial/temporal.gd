class_name Temporal
extends Node

## O temporal de verao da volta do rio: escurece a cena e poe chuva fina na
## frente de tudo. Vai na estrada e no cais, so na volta (Partida.volta_do_rio).
##
##     add_child(Temporal.new())
##
## relampago() clareia a tela por um instante, que e o susto que faz o
## Alexandre disparar na estrada.

const COR_CENA: Color = Color(0.74, 0.78, 0.88)
const GOTAS: int = 140
const VENTO: float = -0.28   # a chuva cai inclinada, puxada pelo vento

var _chuva: _Chuva
var _clarao: ColorRect


func _ready() -> void:
	var escuro := CanvasModulate.new()
	escuro.color = COR_CENA
	get_parent().add_child.call_deferred(escuro)

	var camada := CanvasLayer.new()
	camada.layer = 3
	add_child(camada)
	_chuva = _Chuva.new()
	camada.add_child(_chuva)
	_clarao = ColorRect.new()
	_clarao.color = Color(1, 1, 1, 0)
	_clarao.size = Vector2(1280, 720)
	_clarao.mouse_filter = Control.MOUSE_FILTER_IGNORE
	camada.add_child(_clarao)


func relampago() -> void:
	var tween := create_tween()
	tween.tween_property(_clarao, "color:a", 0.75, 0.05)
	tween.tween_property(_clarao, "color:a", 0.0, 0.12)
	tween.tween_property(_clarao, "color:a", 0.45, 0.05)
	tween.tween_property(_clarao, "color:a", 0.0, 0.35)
	await tween.finished


class _Chuva:
	extends Node2D

	var _gotas: Array[Vector3] = []  # x, y, velocidade

	func _ready() -> void:
		for i in GOTAS:
			_gotas.append(Vector3(randf() * 1400.0, randf() * 720.0, randf_range(620.0, 900.0)))

	func _process(delta: float) -> void:
		for i in _gotas.size():
			var g: Vector3 = _gotas[i]
			g.y += g.z * delta
			g.x += g.z * VENTO * delta
			if g.y > 720.0:
				g = Vector3(randf() * 1400.0, -20.0, g.z)
			_gotas[i] = g
		queue_redraw()

	func _draw() -> void:
		for g in _gotas:
			var p := Vector2(g.x, g.y)
			draw_line(p, p + Vector2(VENTO, 1.0) * 14.0, Color(0.82, 0.88, 0.96, 0.55), 2.0)
