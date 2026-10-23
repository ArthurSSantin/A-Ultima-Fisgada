class_name Acompanhante
extends Sprite2D

## O vo andando junto com o neto: fica sempre um passo atras dele, vira para o
## lado em que anda e balanca de leve a cada passo. A pe nao tem quadro de
## caminhada (o balanco da conta a essa distancia); montado no Apollo, a folha
## tem quatro quadros de passo (hframes) e eles andam enquanto ele anda.

@export var alvo: NodePath
## Quanto fica para tras do neto, em pixels de tela.
@export var distancia: float = 80.0
@export var velocidade: float = 240.0

var _passo: float = 0.0
var _relogio: float = 0.0

@onready var _neto: Sprite2D = get_node(alvo)


func _process(delta: float) -> void:
	var atras: float = distancia if _neto.flip_h else -distancia
	var dx: float = _neto.position.x + atras - position.x
	if absf(dx) > 6.0:
		position.x += signf(dx) * minf(absf(dx), velocidade * delta)
		flip_h = dx < 0.0
		_passo += delta * 9.0
		if hframes > 1:
			_relogio += delta
			if _relogio >= 0.14:
				_relogio -= 0.14
				frame = (frame + 1) % hframes
		else:
			offset.y = -absf(sin(_passo)) * 2.0
	else:
		flip_h = _neto.flip_h
		offset.y = 0.0
		if hframes > 1:
			frame = 0
