extends Node2D

## Cais: o ponto de partida da fase 2. Aqui nao se pesca; o jogador so
## atravessa o deck e embarca.
##
##   borda esquerda ... volta para a rua da vila
##   barco .......... abre o mapa e leva para o local escolhido
##
## O barco atende tanto ao ESPACO (chegando perto, como os NPCs do hub) quanto
## ao clique do mouse, que e o jeito que a maioria tenta primeiro.

const ESQUERDA: StringName = &"mover_esquerda"
const DIREITA: StringName = &"mover_direita"
const ESPACO: StringName = &"espaco"

const CENA_VILA: String = "res://scenes/Vila.tscn"

## Encostou na borda esquerda do deck: volta para a rua da vila.
const SAIDA_X: float = 40.0
const BORDA_DIREITA: float = 600.0
## A partir daqui o jogador alcanca o barco.
const ALCANCE_BARCO: float = 540.0

var _ocupado: bool = false
var _saindo: bool = false
var _caixa: CaixaDialogo

@onready var _player: Sprite2D = $Jogo/Player
@onready var _visual: VisualTiago = $Jogo/Player/Visual
@onready var _mover: EightDir = $Jogo/Player/OitoDirecoes
@onready var _barco: Sprite2D = $Jogo/Barco
@onready var _alerta: Label = $Jogo/AlertaBarco
@onready var _placar: Label = $UI/Placar
@onready var _dica: Label = $UI/Dica


func _ready() -> void:
	_caixa = CaixaDialogo.new()
	add_child(_caixa)
	$UI.add_child(BarraEnergia.new())
	_player.position.x = Partida.cais_x
	_visual.na_mao = false
	Partida.cais_visitado = true


func _process(delta: float) -> void:
	if _caixa.ocupada() or _ocupado or _saindo:
		_mover.enabled = false
		_alerta.visible = false
		return

	_mover.enabled = true
	_mover.tick(delta)
	_player.position.x = clampf(_player.position.x, SAIDA_X, BORDA_DIREITA)

	if Input.is_action_just_pressed(ESQUERDA):
		_player.flip_h = true
	if Input.is_action_just_pressed(DIREITA):
		_player.flip_h = false

	# Andou ate a borda esquerda: volta para a rua da vila
	if _player.position.x <= SAIDA_X and Input.is_action_pressed(ESQUERDA):
		_voltar_a_vila()
		return

	_alerta.visible = _perto_do_barco()
	_alerta.position = Vector2(_barco.position.x - 8.0, _barco.position.y - 120.0)

	if _perto_do_barco() and Input.is_action_just_pressed(ESPACO):
		_embarcar()

	_atualizar_interface()


## O clique no barco vale de qualquer lugar do deck: o jogador vai ate ele.
func _unhandled_input(evento: InputEvent) -> void:
	if _caixa.ocupada() or _ocupado or _saindo:
		return
	if not (evento is InputEventMouseButton and evento.pressed
			and evento.button_index == MOUSE_BUTTON_LEFT):
		return
	var tamanho: Vector2 = _barco.texture.get_size()
	var area := Rect2(_barco.position - tamanho * 0.5, tamanho)
	if area.has_point(get_global_mouse_position()):
		get_viewport().set_input_as_handled()
		_player.position.x = BORDA_DIREITA
		_player.flip_h = false
		_embarcar()


func _perto_do_barco() -> bool:
	return _player.position.x >= ALCANCE_BARCO


func _embarcar() -> void:
	if _ocupado:
		return
	_ocupado = true
	if Partida.cansado():
		await _caixa.falar("{nome}", [
			"Hoje não dá mais. Melhor voltar pra vila, vender o balde e dormir.",
		])
		_ocupado = false
		return

	var id: StringName = await MapaLocais.abrir_em(self)
	if id.is_empty():
		_ocupado = false
		return

	var cena: String = Partida.cena_do_local(id)
	if cena.is_empty():
		await _caixa.falar("{nome}", ["Ainda não sei chegar lá."])
		_ocupado = false
		return

	Partida.local = id
	Partida.cais_x = BORDA_DIREITA
	_saindo = true
	get_tree().change_scene_to_file.call_deferred(cena)


func _voltar_a_vila() -> void:
	if _saindo:
		return
	_saindo = true
	Partida.vila_x = 1180.0
	Partida.cais_x = 150.0
	get_tree().change_scene_to_file.call_deferred(CENA_VILA)


func _atualizar_interface() -> void:
	_placar.text = "Dia %d   |   R$ %d   |   Balde: %d peixes" % [
		Partida.dia, Partida.dinheiro, Partida.balde.size(),
	]
	if Partida.cansado():
		_dica.text = "%s está cansado. Volte para a vila." % Partida.nome
	elif _perto_do_barco():
		_dica.text = "ESPAÇO para embarcar e escolher o pesqueiro."
	elif Partida.tutorial():
		_dica.text = "Ande até o barco, na ponta do cais, e aperte ESPAÇO."
	else:
		_dica.text = ""
