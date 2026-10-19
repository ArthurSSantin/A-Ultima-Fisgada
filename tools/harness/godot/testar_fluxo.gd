extends SceneTree

## Teste de ponta a ponta da Fase 1 com o teclado simulado: prologo no hub,
## compra da vara, ida ao cais, um lancamento ate a captura, fim do dia, venda,
## sono e fechamento da fase com o telhado e o robalo.
##
## Uso: godot --headless --fixed-fps 60 --path . -s tools/harness/godot/testar_fluxo.gd
##
## Sai com codigo 1 se alguma verificacao falhar.

var _falhas: int = 0


func _initialize() -> void:
	_rodar.call_deferred()


func _rodar() -> void:
	var partida: Node = root.get_node("Partida")
	change_scene_to_file("res://scenes/Hub.tscn")
	await _quadros(5)

	# Prologo
	var hub: Node = current_scene
	_conferir(hub.name == "Hub", "comeca no hub")
	_conferir(hub._caixa.aberta, "prologo abre sozinho")
	await _fechar_dialogos(hub)

	# Sem vara a porta nao abre
	await _ir_e_apertar(hub, "Saida")
	await _fechar_dialogos(hub)
	_conferir(current_scene == hub, "sem vara nao vai ao cais")

	# Loja: compra a Vara de Bambu (primeira opcao)
	await _ir_e_apertar(hub, "Aldo")
	await _apertar(&"espaco")
	await _apertar(&"espaco")
	await _apertar(&"ui_cancel")
	_conferir(partida.vara == &"bambu", "comprou a vara de bambu")
	_conferir(partida.dinheiro == 30, "pagou R$ 50 (tem %d)" % partida.dinheiro)

	# Vai ao cais
	await _ir_e_apertar(hub, "Saida")
	await _quadros(5)
	var cais: Node = current_scene
	_conferir(cais.name == "CaisTeste", "entrou no cais")

	# Um lancamento: carrega a forca e solta
	cais.get_node("Jogo/Player").position.x = 555.0
	await _quadros(2)
	Input.action_press(&"espaco")
	await _quadros(20)
	Input.action_release(&"espaco")
	await _esperar_estado(cais, 3, 8.0)
	_conferir(cais.estado == 3, "o peixe mordeu")
	_conferir(partida.energia < partida.ENERGIA_MAX, "lancar gastou energia (%.1f)" % partida.energia)
	_conferir(cais.especie.nome == "Parati", "dia 1 so tem parati")
	await _apertar(&"espaco")
	_conferir(cais.estado == 4, "fisgou e entrou no minijogo")
	cais.minijogo.progresso = 99.9
	cais.minijogo.peixe_pos = cais.minijogo.zona_pos + 10.0
	await _esperar_estado(cais, 0, 5.0)
	_conferir(partida.balde.size() == 1, "peixe foi para o balde")

	# Fim do dia: acaba a energia e volta para o hub
	partida.energia = 0.0
	await _quadros(3)
	await _fechar_dialogos(cais)
	await _quadros(5)
	hub = current_scene
	_conferir(hub.name == "Hub", "voltou ao hub no fim do dia")
	await _fechar_dialogos(hub)

	# Vende o balde
	var antes: int = partida.dinheiro
	await _ir_e_apertar(hub, "Zeca")
	await _fechar_dialogos(hub)
	_conferir(partida.balde.is_empty() and partida.dinheiro > antes, "vendeu o balde (R$ %d)" % partida.dinheiro)

	# Dorme
	await _ir_e_apertar(hub, "Cama")
	await _fechar_dialogos(hub)
	_conferir(partida.dia == 2 and partida.energia == partida.ENERGIA_MAX, "dormiu e comecou o dia 2 com energia cheia")

	# Loja do dia 2 tem os bonus
	_conferir(partida.disponivel(partida.ITENS[&"cafezinho"].dia), "cafezinho liberado no dia 2")

	# Fechamento: dinheiro do telhado e um robalo no balde
	partida.dinheiro = 900
	partida.registrar_captura(partida.especie(&"Robalo"), 4.0)
	await _ir_e_apertar(hub, "Zeca")
	await _apertar(&"espaco")  # vender tudo menos um robalo
	await _fechar_dialogos(hub)
	_conferir(partida.tem_robalo_no_balde(), "zeca guardou o robalo")

	await _ir_e_apertar(hub, "Marlene")
	await _apertar(&"ui_down")
	await _apertar(&"espaco")  # pagar o telhado
	await _fechar_dialogos(hub)
	_conferir(partida.telhado_pago, "pagou o telhado")
	await _ir_e_apertar(hub, "Marlene")
	await _apertar(&"ui_down")
	await _apertar(&"espaco")  # entregar o robalo
	await _fechar_dialogos(hub)
	_conferir(partida.fase_concluida(), "fase concluida")
	_conferir(hub._concluida, "tela final apareceu")

	# Sorteio: com a fibra no dia 3 aparecem corvina e robalo
	partida.dia = 3
	var vistos: Dictionary = {}
	for i in 2000:
		var e: Especie = partida.sortear_especie(randf_range(6.0, 85.0), false)
		vistos[e.nome] = vistos.get(e.nome, 0) + 1
	print("sorteio com a fibra, dia 3: ", vistos)
	for nome in ["Parati", "Tainha", "Corvina", "Robalo", "Robalo-Flecha"]:
		_conferir(vistos.has(nome), "sorteio alcanca " + nome)
	vistos.clear()
	for i in 2000:
		var e: Especie = partida.sortear_especie(randf_range(6.0, 45.0), false)
		vistos[e.nome] = vistos.get(e.nome, 0) + 1
	print("sorteio com o bambu, dia 3: ", vistos)
	_conferir(not vistos.has("Corvina") and not vistos.has("Robalo"), "bambu nao alcanca corvina nem robalo")

	print("FALHAS ", _falhas)
	quit(1 if _falhas > 0 else 0)


func _conferir(ok: bool, o_que: String) -> void:
	print(("ok    " if ok else "FALHA ") + o_que)
	if not ok:
		_falhas += 1


func _quadros(n: int) -> void:
	for i in n:
		await process_frame


func _apertar(acao: StringName) -> void:
	var ev := InputEventAction.new()
	ev.action = acao
	ev.pressed = true
	Input.parse_input_event(ev)
	await _quadros(2)
	ev = InputEventAction.new()
	ev.action = acao
	ev.pressed = false
	Input.parse_input_event(ev)
	await _quadros(2)


func _fechar_dialogos(cena: Node) -> void:
	# Fecha o que abrir ate a cena ficar livre (o hub tambem espera a tela
	# escurecer quando dorme).
	var fechada: int = 0
	while fechada < 4:
		await _quadros(2)
		if not is_instance_valid(cena) or not cena.is_inside_tree():
			return
		if cena._caixa.aberta:
			fechada = 0
			await _apertar(&"espaco")
		elif cena.get(&"_ocupado"):
			fechada = 0
		else:
			fechada += 1


func _ir_e_apertar(hub: Node, estacao: String) -> void:
	hub.get_node("Player").position.x = hub.get_node("Estacoes/" + estacao).position.x
	await _quadros(2)
	await _apertar(&"espaco")


func _esperar_estado(cais: Node, estado: int, segundos: float) -> void:
	var limite: int = Time.get_ticks_msec() + int(segundos * 1000.0)
	while cais.estado != estado and Time.get_ticks_msec() < limite:
		await process_frame
