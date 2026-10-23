extends Node2D

## Fim do tutorial: os dois chegam em casa de manha montados, apeiam e deixam
## os cavalos na cerca; a vo no portao desconfia do cafe puro. Depois a tela
## escurece, entram as duas frases do neto ja adulto e o titulo do jogo, e a
## fase 2 comeca anos depois, na casa do avo.

const CENA_FASE_2: String = "res://scenes/CasaAvo.tscn"
const CENA_INICIO: String = "res://scenes/Inicio.tscn"

var _caixa: CaixaDialogo

@onready var _neto: Sprite2D = $Neto
@onready var _vo: Sprite2D = $Vo
@onready var _alexandre: Sprite2D = $AlexandreMontado
@onready var _apollo: Sprite2D = $ApolloMontado
@onready var _alexandre_parado: Sprite2D = $Alexandre
@onready var _apollo_parado: Sprite2D = $Apollo


func _ready() -> void:
	_caixa = CaixaDialogo.new()
	add_child(_caixa)
	_rodar.call_deferred()


func _rodar() -> void:
	var camada := CanvasLayer.new()
	camada.layer = 30
	add_child(camada)
	var tela := ColorRect.new()
	tela.color = Color.BLACK
	tela.size = Vector2(1280, 720)
	camada.add_child(tela)

	_neto.visible = false
	_vo.visible = false
	_alexandre_parado.visible = false
	_apollo_parado.visible = false
	var trote := AudioStreamPlayer.new()
	var faixa: AudioStreamMP3 = load("res://assets/sons/cavalo_trote.mp3")
	faixa.loop = true
	trote.stream = faixa
	trote.volume_db = -8.0
	add_child(trote)
	trote.play()
	var chegada := create_tween()
	chegada.tween_property(tela, "color:a", 0.0, 1.0)
	chegada.parallel().tween_property(_alexandre, "position:x", 680.0, 3.6)
	chegada.parallel().tween_property(_apollo, "position:x", 900.0, 3.6)
	while chegada.is_running():
		_alexandre.frame = (_alexandre.frame + 1) % 4
		_apollo.frame = (_apollo.frame + 1) % 4
		await get_tree().create_timer(0.14).timeout
	_alexandre.frame = 0
	_apollo.frame = 0
	await create_tween().tween_property(trote, "volume_db", -60.0, 0.4).finished
	trote.queue_free()
	var bufo := AudioStreamPlayer.new()
	bufo.stream = load("res://assets/sons/cavalo_bufo.mp3")
	bufo.volume_db = -3.0
	add_child(bufo)
	bufo.play(7.75)
	get_tree().create_timer(0.9).timeout.connect(bufo.queue_free)
	await get_tree().create_timer(0.4).timeout
	# apeiam: os cavalos ficam parados na cerca e os dois descem do lado
	_alexandre.visible = false
	_apollo.visible = false
	_alexandre_parado.visible = true
	_apollo_parado.visible = true
	_neto.visible = true
	_vo.visible = true
	Partida.concluir(&"casa")
	await get_tree().create_timer(0.5).timeout

	await _caixa.falar("Vó", ["E aí, pegaram alguma coisa?"])
	await _caixa.falar("{nome}", ["Peguei um monte, vó! Um jundiá com o rabo comido, e uma joaninha, e..."])
	await _caixa.falar("Vô", ["Pegou mais que eu. Vou me aposentar."])
	await _caixa.falar("Vó", ["E tu, tomou café puro de novo, né?"])
	await _caixa.falar("", ["O neto e o vô se olham."])
	await _caixa.falar("{nome}", ["...Não."])
	await _caixa.falar("Vó", ["Hum."])
	await _caixa.falar("", ["A vó entra. O vô pisca pro neto."])

	var escuro := create_tween()
	escuro.tween_property(tela, "color:a", 1.0, 2.0)
	await escuro.finished

	var rotulos: Array[Label] = []
	for texto in ["Naquele tempo, eu achava que o mais importante era aprender a pescar.",
			"Só depois eu entendi que ele estava me ensinando a ficar."]:
		var rotulo := _rotulo(texto, 22, Color(0.95, 0.93, 0.86))
		rotulo.position.y = 300 + rotulos.size() * 48
		rotulo.modulate.a = 0.0
		camada.add_child(rotulo)
		rotulos.append(rotulo)
		var aparece := create_tween()
		aparece.tween_property(rotulo, "modulate:a", 1.0, 1.6)
		await aparece.finished
		await get_tree().create_timer(1.8).timeout
	await get_tree().create_timer(1.5).timeout
	var some := create_tween()
	for r in rotulos:
		some.parallel().tween_property(r, "modulate:a", 0.0, 1.2)
	await some.finished

	var titulo := _rotulo("A ÚLTIMA FISGADA", 64, Color(1.0, 0.82, 0.35), true)
	titulo.position.y = 300
	titulo.modulate.a = 0.0
	camada.add_child(titulo)
	var t1 := create_tween()
	t1.tween_property(titulo, "modulate:a", 1.0, 2.0)
	t1.tween_interval(2.5)
	t1.tween_property(titulo, "modulate:a", 0.0, 1.5)
	await t1.finished

	# O build so da Fase 1 (export "Windows Fase 1", feature so_tutorial)
	# termina aqui e volta para a tela inicial.
	if OS.has_feature("so_tutorial"):
		await _fim_do_tutorial(camada)
		return

	var depois := _rotulo("Muitos anos depois...", 24, Color(0.85, 0.83, 0.78))
	depois.position.y = 330
	depois.modulate.a = 0.0
	camada.add_child(depois)
	var t2 := create_tween()
	t2.tween_property(depois, "modulate:a", 1.0, 1.2)
	t2.tween_interval(1.6)
	t2.tween_property(depois, "modulate:a", 0.0, 1.0)
	await t2.finished

	Partida.iniciar_fase(2)
	get_tree().change_scene_to_file.call_deferred(CENA_FASE_2)


func _fim_do_tutorial(camada: CanvasLayer) -> void:
	var fim := _rotulo("Fim da Fase 1", 30, Color(1.0, 0.82, 0.35), true)
	fim.position.y = 300
	var obrigado := _rotulo("A história continua no jogo completo. Obrigado por jogar!", 20, Color(0.85, 0.83, 0.78))
	obrigado.position.y = 352
	for r in [fim, obrigado]:
		r.modulate.a = 0.0
		camada.add_child(r)
	var t := create_tween()
	t.tween_property(fim, "modulate:a", 1.0, 1.2)
	t.parallel().tween_property(obrigado, "modulate:a", 1.0, 1.2)
	t.tween_interval(3.5)
	t.tween_property(fim, "modulate:a", 0.0, 1.0)
	t.parallel().tween_property(obrigado, "modulate:a", 0.0, 1.0)
	await t.finished
	get_tree().change_scene_to_file.call_deferred(CENA_INICIO)


func _rotulo(texto: String, tamanho: int, cor: Color, negrito: bool = false) -> Label:
	var fonte := SystemFont.new()
	fonte.font_names = PackedStringArray(["Arial"])
	if negrito:
		fonte.font_weight = 700
	var r := Label.new()
	r.text = Partida.nome_em(texto)
	r.size = Vector2(1280, 60)
	r.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	r.add_theme_font_override("font", fonte)
	r.add_theme_font_size_override("font_size", tamanho)
	r.add_theme_color_override("font_color", cor)
	return r
