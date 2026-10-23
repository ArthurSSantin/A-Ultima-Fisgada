extends CenaTutorial

## Cena 2 do tutorial: o cafe na cozinha da Vo Marlene. E objetivo: sem
## sentar a mesa a vo nao deixa sair.

const CENA_SEGUINTE: String = "res://scenes/tutorial/Terreiro.tscn"


func _ao_entrar() -> void:
	await escurecer(false, 0.6)
	await falar("Vó", ["Olha quem acordou. Achei que ia ter que te levar no colo."])
	await falar("{nome}", ["Bença, vó."])
	await falar("Vó", ["Deus te abençoe. Senta aí e come alguma coisa antes de ir."])
	await falar("Vô", ["Come rápido, que o peixe tá com fome."])
	await falar("Vó", ["O peixe tá com fome e o guri não?"])


func _dica_atual() -> String:
	if not Partida.tomou_cafe:
		return "O café está na mesa. A porta da direita dá no terreiro."
	return "A porta da direita dá no terreiro."


func _acao(nome: StringName) -> String:
	match nome:
		&"Marlene": return "Falar com a vó"
		&"Mesa": return "Sentar e tomar café"
		&"Porta": return "Sair para o terreiro"
	return "Olhar"


func _interagir(nome: StringName) -> void:
	match nome:
		&"Marlene":
			if Partida.tomou_cafe:
				await falar("Vó", ["Cuida do teu vô lá no rio, viu? Ele se empolga e esquece da hora do almoço."])
			else:
				await falar("Vó", ["Senta e come, menino. Ninguém pesca de barriga vazia."])
		&"Mesa":
			await _cafe()
		&"Fogao":
			await falar("", ["O fogão a lenha estala. A chaleira chia baixinho. Tá quentinho aqui."])
		&"Tigela":
			await falar("", ["A tigela do MauMau, vazia. Ele sabe que ainda é cedo."])
		&"Panelas":
			await falar("", ["As panelas da vó, areadas até brilhar."])
		&"Radio":
			await falar("", ["O rádio, baixinho, na previsão do tempo: sol no Vale, neblina cedo."])
		&"Filtro":
			await falar("", ["Água fresquinha do filtro de barro."])
		&"Calendario":
			await falar("", ["A folhinha de 2002, com uma foto da Seleção do penta. A vó risca os dias com caneta azul."])
		&"Geladeira":
			await falar("", ["A geladeira, com os ímãs de propaganda da venda do vô."])
		&"Porta":
			if not Partida.tomou_cafe:
				await falar("Vó", ["Ei! Vai sair de barriga vazia? Volta aqui."])
				return
			ir_para(CENA_SEGUINTE)


## A mesa de perto. Cada ESPACO e uma mordida: o pao diminui, a xicara baixa,
## ate sobrar so migalha. O aviso na tela diz o que apertar.
func _comer() -> void:
	var camada := CanvasLayer.new()
	camada.layer = 9
	add_child(camada)
	var mesa := TextureRect.new()
	mesa.texture = load("res://assets/sprites/tutorial/cenarios/cafe_0.png")
	mesa.modulate.a = 0.0
	camada.add_child(mesa)
	var aviso := Label.new()
	var fonte := SystemFont.new()
	fonte.font_names = PackedStringArray(["Arial"])
	fonte.font_weight = 700
	aviso.add_theme_font_override("font", fonte)
	aviso.add_theme_font_size_override("font_size", 26)
	aviso.add_theme_color_override("font_color", Color(1, 0.85, 0.2))
	aviso.add_theme_color_override("font_outline_color", Color(0.2, 0.12, 0.07))
	aviso.add_theme_constant_override("outline_size", 7)
	aviso.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	aviso.size = Vector2(1280, 50)
	aviso.position = Vector2(0, 640)
	camada.add_child(aviso)
	await create_tween().tween_property(mesa, "modulate:a", 1.0, 0.3).finished
	for etapa in range(1, 4):
		aviso.text = "[ESPAÇO] Comer  (%d/3)" % etapa
		var pisca := create_tween().set_loops()
		pisca.tween_property(aviso, "modulate:a", 0.45, 0.45)
		pisca.tween_property(aviso, "modulate:a", 1.0, 0.45)
		while not Input.is_action_just_pressed(&"espaco"):
			await get_tree().process_frame
		pisca.kill()
		aviso.modulate.a = 1.0
		mesa.texture = load("res://assets/sprites/tutorial/cenarios/cafe_%d.png" % etapa)
		await get_tree().process_frame
	aviso.text = ""
	await esperar(0.8)
	await create_tween().tween_property(mesa, "modulate:a", 0.0, 0.3).finished
	camada.queue_free()


func _cafe() -> void:
	if Partida.tomou_cafe:
		await falar("", ["Só sobraram as migalhas da cuca."])
		return
	Partida.tomou_cafe = true
	Partida.concluir(&"cafe")
	await _comer()
	await falar("", ["Café com leite, pão com chimia e um pedaço de cuca ainda morna."])
	await falar("Vó", ["Café com leite, que café puro é coisa de véio."])
	await falar("Vô", ["Eu tomo puro."])
	await falar("Vó", ["Pois é."])
	await falar("", ["O vô ri dentro da xícara."])
	await falar("Vó", ["Toma, embrulhei dois pão pra levar. Um é teu, o outro é do teu vô, e não deixa ele comer os dois."])
