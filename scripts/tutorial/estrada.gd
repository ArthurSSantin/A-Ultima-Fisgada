extends CenaTutorial

## A estrada de chao entre a casa e o rio, tres telas de largura. O jogador
## conduz o Alexandre com as setas e a camera vai junto; o vo acompanha no
## Apollo. As conversas saem por trecho do caminho. Na ida (madrugada) a casa
## fica a esquerda e o rio a direita; na volta (manha, Partida.volta_do_rio)
## o caminho e o mesmo, ao contrario, e termina na chegada em casa.

const CENA_CAIS: String = "res://scenes/tutorial/CaisRio.tscn"
const CENA_FIM: String = "res://scenes/tutorial/Fim.tscn"
const MANHA: Texture2D = preload("res://assets/sprites/tutorial/cenarios/estrada_longa_manha.png")
const LARGURA: float = 3840.0
## Porteira e bergamoteira do Seu Arlindo, em pixels de tela (o desenho tem
## elas em 1/3 e 2/3 da largura).
const X_PORTEIRA: float = 1280.0
const X_BERGAMOTEIRA: float = 2560.0
const TEMPO_QUADRO: float = 0.14

var _volta: bool = false
var _feitos: Array[StringName] = []
var _x_anterior: float = 0.0
var _relogio: float = 0.0
var _quadro: int = 0
## O trote em loop: sobe quando o cavalo anda, some quando ele para.
var _trote: AudioStreamPlayer

@onready var _vo: Sprite2D = $Vo


func _ready() -> void:
	_volta = Partida.volta_do_rio
	if _volta:
		$Fundo.texture = MANHA
		_player.position.x = LARGURA - 260.0
		_player.flip_h = true
		_vo.position.x = LARGURA - 160.0
		_vo.flip_h = true
	_x_anterior = _player.position.x
	super._ready()


func _ao_entrar() -> void:
	var faixa: AudioStreamMP3 = load(SONS + "cavalo_trote.mp3")
	faixa.loop = true
	_trote = AudioStreamPlayer.new()
	_trote.stream = faixa
	_trote.volume_db = -60.0
	add_child(_trote)
	_trote.play()
	await escurecer(false, 0.8)
	som("cavalo_bufo")


func _process(delta: float) -> void:
	super._process(delta)
	# quatro quadros de passo enquanto o cavalo anda
	var andou: bool = absf(_player.position.x - _x_anterior) > 0.5
	_x_anterior = _player.position.x
	if andou:
		_relogio += delta
		if _relogio >= TEMPO_QUADRO:
			_relogio -= TEMPO_QUADRO
			_quadro = (_quadro + 1) % 4
	else:
		_quadro = 0
	_player.frame = _quadro
	if _trote:
		var alvo: float = -6.0 if andou else -60.0
		_trote.volume_db = move_toward(_trote.volume_db, alvo, delta * (90.0 if andou else 60.0))
	if not (_ocupado or _caixa.ocupada() or _saindo):
		_conferir_trechos()


func _dica_atual() -> String:
	if _volta:
		return "← → conduzem o Alexandre. A casa é pra lá ←"
	return "← → conduzem o Alexandre. O rio é pro lado do sol →"


## Cada trecho dispara uma vez, quando o cavalo passa do ponto no sentido da
## viagem. Voltar para tras na largada rende uma bronca do vo.
func _conferir_trechos() -> void:
	var x: float = _player.position.x
	var pedidos: Array[StringName] = []
	if not _volta:
		if x > 520.0:
			pedidos.append(&"devagar")
		if x > X_PORTEIRA - 80.0:
			pedidos.append(&"porteira")
		if x > X_BERGAMOTEIRA - 120.0:
			pedidos.append(&"arlindo")
		if x <= borda.x + 4.0 and Input.is_action_pressed(&"mover_esquerda"):
			pedidos.append(&"pra_tras")
	else:
		if x < X_BERGAMOTEIRA + 140.0:
			pedidos.append(&"bergamota")
		if x < X_PORTEIRA + 200.0:
			pedidos.append(&"redea")
		if x >= borda.y - 4.0 and Input.is_action_pressed(&"mover_direita"):
			pedidos.append(&"pra_tras")
	# uma conversa por vez; a chegada so depois de todas as do caminho
	for id in pedidos:
		if not id in _feitos:
			_trecho(id)
			return
	if not _volta and x >= borda.y - 4.0:
		_chegar(CENA_CAIS)
	elif _volta and x <= borda.x + 4.0:
		_chegar(CENA_FIM)


func _trecho(id: StringName) -> void:
	_feitos.append(id)
	_ocupado = true
	_mover.velocidade_x = 0.0
	await _conversa(id)
	_ocupado = false


func _chegar(cena: String) -> void:
	if _saindo:
		return
	ir_para(cena)


func _conversa(id: StringName) -> void:
	match id:
		&"devagar":
			await falar("Vô", ["Devagar. Não precisa correr, o rio não sai do lugar."])
		&"porteira":
			await falar("{nome}", ["Vô, o Apollo é mais rápido que o Alexandre?"])
			await falar("Vô", ["Era. Hoje ele só é mais grande."])
		&"arlindo":
			await falar("Vô", ["Ó, ali é do Seu Arlindo. Na volta, se ninguém tiver olhando..."])
			await falar("{nome}", ["Vô!"])
			await falar("Vô", ["Que foi? Bergamota no chão é de quem achar."])
		&"pra_tras":
			if _volta:
				await falar("Vô", ["Ué, vai voltar pro rio? A casa é pra lá, piá."])
			else:
				await falar("Vô", ["Esqueceu alguma coisa? O rio é pra lá, piá."])
		&"bergamota":
			await falar("{nome}", ["Vô, a gente pode pegar bergamota?"])
			await falar("Vô", ["Que bergamota?"])
			await falar("{nome}", ["A do Seu Arlindo! Tu falou!"])
			await falar("Vô", ["Eu não falei nada."])
			await esperar(0.6)
			await falar("Vô", ["...Pega duas. Uma pra vó."])
			await falar("", ["{nome} se estica da sela e arranca duas bergamotas do galho."])
			Partida.diario.append("Duas bergamotas do Seu Arlindo. Uma pra vó.")
		&"redea":
			await falar("Vô", ["O Alexandre tá andando melhor contigo. Ele gosta de quem não puxa a rédea à toa."])
