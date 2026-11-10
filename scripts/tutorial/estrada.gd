extends CenaTutorial

## A estrada de chao entre a casa e o rio, tres telas de largura. O jogador
## conduz o Alexandre com as setas e a camera vai junto; o vo acompanha no
## Apollo. As conversas saem por trecho do caminho. Na ida (madrugada) a casa
## fica a esquerda e o rio a direita; na volta (manha, Partida.volta_do_rio)
## o caminho e o mesmo, ao contrario, e termina na chegada em casa.
##
## A volta e depois do temporal: chove fino e o vento derrubou arvores na
## estrada. Passada a bergamoteira, um relampago assusta o Alexandre, que
## dispara sozinho para casa, e o jogador pula os troncos com ESPACO. Nada de
## conversa enquanto ele corre: a fala do vo fica antes e depois. Bater num
## tronco nao perde nada, o cavalo so para, recua e tenta de novo.

const CENA_CAIS: String = "res://scenes/tutorial/CaisRio.tscn"
const CENA_FIM: String = "res://scenes/tutorial/Fim.tscn"
const MANHA: Texture2D = preload("res://assets/sprites/tutorial/cenarios/estrada_longa_manha.png")
const LARGURA: float = 3840.0
## Porteira e bergamoteira do Seu Arlindo, em pixels de tela (o desenho tem
## elas em 1/3 e 2/3 da largura).
const X_PORTEIRA: float = 1280.0
const X_BERGAMOTEIRA: float = 2560.0
const TEMPO_QUADRO: float = 0.14

const TRONCO: Texture2D = preload("res://assets/sprites/tutorial/cenarios/tronco_caido.png")
const GALHOS: Texture2D = preload("res://assets/sprites/tutorial/cenarios/galhos.png")
const POCA: Texture2D = preload("res://assets/sprites/tutorial/cenarios/poca.png")
## Os troncos da corrida, do primeiro ao ultimo (a volta anda para a
## esquerda). Comecam espacados e vao ficando juntos.
const TRONCOS_X: Array[float] = [2240.0, 1860.0, 1520.0, 1230.0, 970.0]
## Linha do chao da estrada, onde fica a base do tronco.
const CHAO_Y: float = 548.0
## Passou daqui na volta, com a bergamota pega, o Alexandre dispara.
const X_LARGADA: float = 2560.0
## Daqui para a esquerda o Alexandre ja se acalmou.
const X_CHEGADA: float = 760.0
const VEL_CORRIDA: float = 250.0
const VEL_ACELERA: float = 90.0
const VEL_FREIA: float = 120.0
const DURACAO_PULO: float = 0.75
const ALTURA_PULO: float = 80.0
## Tronco perto demais e o cavalo baixo demais: bateu. Com esses numeros, na
## velocidade normal, da para apertar ESPACO com o tronco de 40 a 150 px a
## frente (uns 0,4 s de janela).
const ALCANCE_TRONCO: float = 30.0
const ALTURA_LIVRE: float = 18.0
const TEMPO_TROPECO: float = 0.9
const RECUO: float = 90.0

var _volta: bool = false
var _feitos: Array[StringName] = []
var _x_anterior: float = 0.0
var _relogio: float = 0.0
var _quadro: int = 0
## O trote em loop: sobe quando o cavalo anda, some quando ele para.
var _trote: AudioStreamPlayer

var _temporal: Temporal
## A corrida: 0 antes, 1 correndo, 2 depois.
var _corrida: int = 0
var _troncos: Array[Sprite2D] = []
var _passados: int = 0
var _batidas: int = 0
var _pulo: float = 0.0
var _tropeco: float = 0.0

@onready var _vo: Sprite2D = $Vo


func _ready() -> void:
	_volta = Partida.volta_do_rio
	if _volta:
		$Fundo.texture = MANHA
		_player.position.x = LARGURA - 260.0
		_player.flip_h = true
		_vo.position.x = LARGURA - 160.0
		_vo.flip_h = true
		_montar_estrago()
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
	if _volta:
		await falar("Vô", [
			"Bah, olha o estrago. O temporal passou por aqui enquanto a gente pescava.",
			"Derrubou árvore na estrada. E o Alexandre não gosta de trovão.",
			"Se ele disparar, segura firme. Quando chegar num tronco, aperta ESPAÇO que ele pula.",
		])


func _process(delta: float) -> void:
	super._process(delta)
	if _corrida == 1 and not _saindo:
		_correr(delta)
		_dica.text = "ESPAÇO: o Alexandre pula o tronco!     ← corre     → segura"
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
	if _volta and _corrida == 2:
		return "← A casa é pra lá. O Alexandre já se acalmou."
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
		if _corrida == 2:
			pedidos.append(&"redea")
		if x >= borda.y - 4.0 and Input.is_action_pressed(&"mover_direita"):
			pedidos.append(&"pra_tras")
	# uma conversa por vez; a chegada so depois de todas as do caminho
	for id in pedidos:
		if not id in _feitos:
			_trecho(id)
			return
	if _volta and _corrida == 0 and &"bergamota" in _feitos and x < X_LARGADA:
		_largar()
		return
	if not _volta and x >= borda.y - 4.0:
		_chegar(CENA_CAIS)
	elif _volta and _corrida == 2 and x <= borda.x + 4.0:
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
			if _batidas == 0:
				await falar("Vô", ["Nem um tropeço! O Alexandre confia em ti, piá."])
			else:
				await falar("Vô", ["Tudo inteiro? Ele se assusta, mas não larga quem segura firme."])
			await falar("Vô", ["Ele gosta de quem não puxa a rédea à toa."])


# ------------------------------- a corrida -------------------------------

## Os troncos, os galhos e as pocas do temporal, e a chuva por cima.
func _montar_estrago() -> void:
	_temporal = Temporal.new()
	add_child(_temporal)
	var indice: int = _player.get_index()
	for x in [3300.0, 2900.0, 2100.0, 1400.0, 640.0, 380.0]:
		_enfeite(POCA, Vector2(x, 612.0), indice)
	for x in [3050.0, 2400.0, 1700.0, 1100.0, 520.0]:
		_enfeite(GALHOS, Vector2(x, 588.0), indice)
	for x in TRONCOS_X:
		_troncos.append(_enfeite(TRONCO, Vector2(x, CHAO_Y), indice))


func _enfeite(textura: Texture2D, base: Vector2, indice: int) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = textura
	s.position = base - Vector2(0.0, textura.get_height() * 0.5)
	add_child(s)
	move_child(s, indice)  # atras do cavalo
	return s


## O relampago assusta o Alexandre e ele dispara para casa.
func _largar() -> void:
	_corrida = 1
	_ocupado = true  # sem conversa e sem o mover das setas durante a corrida
	_mover.velocidade_x = 0.0
	_player.flip_h = true
	som("cavalo_bufo")
	_vo.velocidade = VEL_CORRIDA + VEL_ACELERA + 40.0
	await _temporal.relampago()


func _correr(delta: float) -> void:
	# pulo: um arco simples, so no desenho (a camera nao pula junto)
	if _pulo > 0.0:
		_pulo = maxf(_pulo - delta, 0.0)
	elif _tropeco <= 0.0 and Input.is_action_just_pressed(&"espaco"):
		_pulo = DURACAO_PULO
	var altura: float = sin(PI * (1.0 - _pulo / DURACAO_PULO)) * ALTURA_PULO if _pulo > 0.0 else 0.0
	_player.offset.y = -altura

	if _tropeco > 0.0:
		_tropeco -= delta
	else:
		var vel: float = VEL_CORRIDA
		if Input.is_action_pressed(&"mover_esquerda"):
			vel += VEL_ACELERA
		if Input.is_action_pressed(&"mover_direita"):
			vel -= VEL_FREIA
		_player.position.x -= vel * delta

	# o tronco da vez: passou por cima, ou bateu
	if _passados < _troncos.size():
		var tx: float = _troncos[_passados].position.x
		var dx: float = _player.position.x - tx
		if dx < -ALCANCE_TRONCO:
			_passados += 1
		elif absf(dx) < ALCANCE_TRONCO and altura < ALTURA_LIVRE and _tropeco <= 0.0:
			_bater(tx)

	# o vo pula junto quando passa por cima de um tronco
	var vo_alt: float = 0.0
	for t in _troncos:
		var d: float = absf(_vo.position.x - t.position.x)
		if d < 70.0:
			vo_alt = maxf(vo_alt, cos(d / 70.0 * PI * 0.5) * ALTURA_PULO * 0.8)
	_vo.offset.y = -vo_alt

	if _passados >= _troncos.size() and _player.position.x < X_CHEGADA and altura == 0.0:
		_acalmar()


func _bater(x_tronco: float) -> void:
	_batidas += 1
	_tropeco = TEMPO_TROPECO
	_pulo = 0.0
	_player.position.x = x_tronco + ALCANCE_TRONCO + RECUO
	som("cavalo_bufo")
	var tween := create_tween()
	tween.tween_property(_player, "offset:x", 6.0, 0.05)
	tween.tween_property(_player, "offset:x", -6.0, 0.08)
	tween.tween_property(_player, "offset:x", 0.0, 0.05)


func _acalmar() -> void:
	_corrida = 2
	_ocupado = false
	_player.offset = Vector2.ZERO
	_vo.offset = Vector2.ZERO
	_vo.velocidade = 240.0
	if _batidas == 0:
		Partida.diario.append("Na volta do temporal, o Alexandre pulou todos os troncos da estrada.")
	else:
		Partida.diario.append("Na volta do temporal, o Alexandre pulou %d troncos e tropeçou em %d." % [_troncos.size(), _batidas])
