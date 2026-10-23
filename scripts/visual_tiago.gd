class_name VisualTiago
extends Node

## Escolhe o sprite do Tiago (no pai, um Sprite2D) conforme a vara:
##
##   sem vara        tiago_sem_vara.png
##   vara comprada   tiago_costas_<vara>.png, a vara presa nas costas
##   perto da agua   tiago_mao_<vara>.png, a vara na mao (na_mao = true)
##
## Cada folha tem 4 quadros de 64x96: parado, passo, pernas cruzando e o outro
## passo. A caminhada anda pelos quadros enquanto o pai de fato muda de X: pela
## velocidade do EightDir ele andaria parado na borda (o X e travado depois do
## movimento) e durante os dialogos (a cena para, mas a velocidade fica).
## Usa hframes; C3.caixa mede um quadro so, entao a sobreposicao continua 64x96.

## De onde vem as folhas e o prefixo do nome. O Tiago adulto usa o padrao; o
## neto do tutorial usa as folhas dele ("neto_sem_vara.png" e cia).
@export var pasta: String = "res://assets/sprites/tiago/"
@export var prefixo: String = "tiago"
const QUADROS: int = 4
const CAMINHADA: Array[int] = [1, 2, 3, 2]
const TEMPO_QUADRO: float = 0.13
const VELOCIDADE_MINIMA: float = 20.0

## Vara na mao em vez de nas costas. O cais liga perto da zona de pesca.
var na_mao: bool = false

var _pose: String = ""
var _relogio: float = 0.0
var _passo: int = 0
## X do pai no quadro anterior. NAN ate o primeiro quadro, porque a cena so
## posiciona o Player no proprio _ready, que roda depois do deste no.
var _x_anterior: float = NAN

@onready var _sprite: Sprite2D = get_parent()


func _process(delta: float) -> void:
	var pose: String = _pose_atual()
	if pose != _pose:
		_pose = pose
		_sprite.texture = load(pasta + "%s_%s.png" % [prefixo, pose])
		_sprite.hframes = QUADROS

	var x: float = _sprite.position.x
	var andando: bool = not is_nan(_x_anterior) and delta > 0.0 \
		and absf(x - _x_anterior) / delta > VELOCIDADE_MINIMA
	_x_anterior = x
	if andando:
		_relogio += delta
		if _relogio >= TEMPO_QUADRO:
			_relogio -= TEMPO_QUADRO
			_passo = (_passo + 1) % CAMINHADA.size()
	else:
		_relogio = 0.0
		_passo = 0
	_sprite.frame = CAMINHADA[_passo] if andando else 0


func _pose_atual() -> String:
	if not Partida.tem_vara():
		return "sem_vara"
	return ("mao_" if na_mao else "costas_") + String(Partida.vara)
