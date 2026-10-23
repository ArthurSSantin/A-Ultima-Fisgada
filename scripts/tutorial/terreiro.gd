extends CenaTutorial

## Cena 3 do tutorial: o terreiro, ainda de madrugada. A Pacoca quer brincar
## (carinho e bolinha), o vo espera, e a saida e montar no Alexandre.

const CENA_SEGUINTE: String = "res://scenes/tutorial/Estrada.tscn"
const BOLINHA: Texture2D = preload("res://assets/sprites/tutorial/bichos/bolinha.png")

var _bergamotas: bool = false

@onready var _pacoca: Node2D = $Estacoes/Pacoca
@onready var _visual_pacoca: Sprite2D = $Estacoes/Pacoca/Visual


func _ao_entrar() -> void:
	await escurecer(false, 0.6)
	som("latido")
	await falar("", ["A Paçoca vem correndo do galpão, abanando o rabo inteiro."])
	await falar("Vô", ["Vai lá buscar o Alexandre. Ele gosta de ti, deixa tu montar sem fazer manha."])


func _dica_atual() -> String:
	return "Os cavalos esperam no palanque. Monte no Alexandre quando quiser ir."


func _acao(nome: StringName) -> String:
	match nome:
		&"Pacoca": return "Brincar com a Paçoca"
		&"Alexandre": return "Montar no Alexandre"
		&"Apollo": return "Olhar o Apollo"
		&"Bergamoteira": return "Pegar bergamota"
	return "Olhar"


func _interagir(nome: StringName) -> void:
	match nome:
		&"Pacoca":
			await _brincar()
		&"Varal":
			await falar("", ["O varal da vó, com a roupa de ontem ainda úmida do sereno."])
		&"Galinhas":
			await falar("", ["As galinhas já ciscando. Uma delas olha torto pra {nome}, como sempre."])
		&"Apollo":
			som("cavalo_bufo")
			await falar("Vô", ["Esse aqui é o Apollo. Mais velho que tu. Mais teimoso que eu."])
		&"Bergamoteira":
			if _bergamotas:
				await falar("", ["O bolso já tá cheio."])
			else:
				_bergamotas = true
				await falar("", ["{nome} enfia duas bergamotas no bolso. Uma é pro vô."])
		&"Latoes":
			await falar("", ["Os latões de leite esperando o caminhão da cooperativa."])
		&"Alexandre":
			await _montar()


func _brincar() -> void:
	var i: int = await escolher("Paçoca", "A Paçoca senta e espera, toda dengosa.", ["Fazer carinho", "Jogar a bolinha", "Deixar"])
	if i == 0:
		await _carinho()
	elif i == 1:
		await _bolinha()


func _carinho() -> void:
	_visual_pacoca.texture = load(BICHOS + "pacoca_carinho.png")
	som("latido")
	var cabeca: Vector2 = _pacoca.global_position + Vector2(10, -60)
	coracao(cabeca)
	balao("Au! Au!", cabeca + Vector2(0, -60))
	await esperar(1.8)
	_visual_pacoca.texture = load(BICHOS + "pacoca_em_pe.png")


## O neto joga, a Pacoca corre atras, pega e volta com a bolinha na boca.
func _bolinha() -> void:
	var origem: float = _pacoca.position.x
	var destino: float = minf(_player.position.x + 380.0, borda.y + 20.0)
	var bola := Sprite2D.new()
	bola.texture = BOLINHA
	bola.position = _player.position + Vector2(20, -50)
	add_child(bola)
	var voo := create_tween()
	voo.tween_property(bola, "position:x", destino, 0.8)
	voo.parallel().tween_property(bola, "position:y", bola.position.y - 90, 0.4).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
	voo.parallel().tween_property(bola, "position:y", 516.0, 0.4).set_delay(0.4).set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_QUAD)

	_visual_pacoca.flip_h = false
	await _correr(destino, 0.9)
	bola.queue_free()
	_visual_pacoca.texture = load(BICHOS + "pacoca_bolinha.png")
	_visual_pacoca.flip_h = true
	await esperar(0.3)
	await _correr(origem, 0.9, "pacoca_bolinha.png")
	_visual_pacoca.flip_h = false
	await _carinho()


func _correr(ate: float, segundos: float, parada: String = "") -> void:
	var tween := create_tween()
	tween.tween_property(_pacoca, "position:x", ate, segundos)
	var quadro: int = 0
	while tween.is_running():
		if parada.is_empty():
			_visual_pacoca.texture = load(BICHOS + ("pacoca_correndo1.png" if quadro % 2 == 0 else "pacoca_correndo2.png"))
		quadro += 1
		await esperar(0.12)


func _montar() -> void:
	await falar("{nome}", ["Bom dia, Alexandre."])
	som("cavalo_bufo")
	await falar("", ["O Alexandre bufa e encosta a cabeça no ombro dele."])
	await falar("Vô", ["Tá vendo? Ele gosta."])
	var i: int = await escolher("", "", ["Montar", "Ainda não"])
	if i != 0:
		return
	await falar("Vô", ["Pé no estribo... isso. Segura na rédea, não na crina."])
	Partida.concluir(&"montar")
	ir_para(CENA_SEGUINTE)
