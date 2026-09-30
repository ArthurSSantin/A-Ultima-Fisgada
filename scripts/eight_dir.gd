class_name EightDir
extends Node

## Porte do behavior "8 Direções" (EightDir) do Construct 3, com as propriedades
## que o Player tem no layout CaisTeste:
##
##   max-speed 200 | acceleration 600 | deceleration 500
##   directions "left-right" | set-angle "no" | default-controls true
##
## Quem se move e o no pai. O tick e chamado pela folha de eventos em vez de um
## _process proprio porque no C3 os behaviors sao atualizados antes dos eventos
## de cada tick, e a folha depende dessa ordem (ela corrige o X do Player logo
## depois do movimento).

@export var max_speed: float = 200.0
@export var acceleration: float = 600.0
@export var deceleration: float = 500.0
@export var enabled: bool = true
@export var acao_esquerda: StringName = &"mover_esquerda"
@export var acao_direita: StringName = &"mover_direita"

## Velocidade horizontal em pixels por segundo. Como no C3, ela e preservada
## enquanto o behavior esta desabilitado: ao reabilitar, o movimento retoma de
## onde parou.
var velocidade_x: float = 0.0

@onready var _alvo: Node2D = get_parent()


func tick(delta: float) -> void:
	if not enabled:
		return

	var direcao: float = 0.0
	if Input.is_action_pressed(acao_esquerda):
		direcao -= 1.0
	if Input.is_action_pressed(acao_direita):
		direcao += 1.0

	if is_zero_approx(direcao):
		# Sem entrada (ou as duas setas juntas): desacelera ate parar.
		if velocidade_x > 0.0:
			velocidade_x = maxf(velocidade_x - deceleration * delta, 0.0)
		elif velocidade_x < 0.0:
			velocidade_x = minf(velocidade_x + deceleration * delta, 0.0)
	else:
		# Com entrada sempre vale a aceleracao, mesmo contra o movimento atual.
		velocidade_x += acceleration * delta * direcao

	velocidade_x = clampf(velocidade_x, -max_speed, max_speed)
	_alvo.position.x += velocidade_x * delta
