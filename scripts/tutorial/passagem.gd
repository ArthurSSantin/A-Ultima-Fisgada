extends Node2D

## Cena de passagem do tutorial: o "Comboio" (o bote com os dois) atravessa o
## cenario enquanto eles conversam. Nao tem controle: e ESPACO para passar as
## falas. Conversa curta, que no bote o vo fala pouco.
##
##   descida  descendo o rio ate o ponto de pesca
##   subida   voltando para o cais: o vo para de remar um pouco
## Quando o comboio vai da direita para a esquerda ele e espelhado.

@export var roteiro: StringName = &"descida"
@export var cena_seguinte: String = ""
## De onde o comboio sai, onde para enquanto conversam e para onde vai.
@export var x_entrada: float = -260.0
@export var x_conversa: float = 560.0
@export var x_saida: float = 1500.0
## No barco o comboio balanca; a cavalo, sacoleja no passo.
@export var balanco: float = 3.0

var _caixa: CaixaDialogo
var _tempo: float = 0.0
var _base_y: float = 0.0

@onready var _comboio: Node2D = $Comboio


func _ready() -> void:
	_caixa = CaixaDialogo.new()
	add_child(_caixa)
	_base_y = _comboio.position.y
	_comboio.position.x = x_entrada
	if x_saida < x_entrada:
		_comboio.scale.x = -1.0
	add_child(QuadroObjetivos.new())
	_rodar.call_deferred()


func _process(delta: float) -> void:
	_tempo += delta
	_comboio.position.y = _base_y + sin(_tempo * 2.2) * balanco


func _rodar() -> void:
	var cortina := ColorRect.new()
	cortina.color = Color.BLACK
	cortina.size = Vector2(1280, 720)
	var camada := CanvasLayer.new()
	camada.layer = 30
	camada.add_child(cortina)
	add_child(camada)
	var tween := create_tween()
	tween.tween_property(cortina, "color:a", 0.0, 0.8)
	tween.parallel().tween_property(_comboio, "position:x", x_conversa, 3.2)
	await tween.finished

	if roteiro == &"subida":
		await _subida()
	else:
		await _descida()

	tween = create_tween()
	tween.tween_property(_comboio, "position:x", x_saida, 3.0)
	tween.parallel().tween_property(cortina, "color:a", 1.0, 0.8).set_delay(2.2)
	await tween.finished
	get_tree().change_scene_to_file.call_deferred(cena_seguinte)


func _falar(quem: String, paginas: Array) -> void:
	await _caixa.falar(quem, paginas)


func _descida() -> void:
	await _falar("", ["O vô rema sem pressa. A neblina ainda corre por cima da água."])
	await _falar("{nome}", ["Vô, tem jacaré aqui?"])
	await _falar("Vô", ["Tinha. Hoje tem tu. Os jacaré foram embora de medo."])
	await _falar("Vô", ["Aqui. Aqui que dá peixe."])
	Partida.concluir(&"rio")


func _subida() -> void:
	await _falar("", ["Subindo o rio, o vô para de remar um pouco."])
	await _falar("{nome}", ["Por que tu parou, vô?"])
	await _falar("Vô", ["Por nada. Só olhando.", "Eu queria lembrar dessa manhã."])
	await _falar("{nome}", ["Mas a gente vem de novo amanhã."])
	await _falar("Vô", ["É. Amanhã a gente vem."])
	await _falar("", ["E volta a remar."])
