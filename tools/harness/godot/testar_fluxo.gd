extends SceneTree

## Teste de ponta a ponta da Fase 1 com o teclado simulado: prologo na casa do
## avo, rua da vila, compra da vara na venda, ida ao cais, barco ate o acude,
## um lancamento ate a captura, fim do dia, venda do balde nos dois
## compradores, pedido entregue, sono e fechamento da fase.
##
## Uso: godot --headless --fixed-fps 60 --path . -s tools/harness/godot/testar_fluxo.gd
##
## Sai com codigo 1 se alguma verificacao falhar.

var _falhas: int = 0


func _initialize() -> void:
	_rodar.call_deferred()


func _rodar() -> void:
	var partida: Node = root.get_node("Partida")
	partida.definir_nome("Tiago", "Bento")
	partida.iniciar_fase(2)  # o jogo comeca no tutorial; aqui testamos a vila
	change_scene_to_file("res://scenes/CasaAvo.tscn")
	await _quadros(5)

	# Prologo, na casa detonada
	var casa: Node = current_scene
	_conferir(casa.name == "CasaAvo", "comeca na casa do avo")
	_conferir(casa._caixa.aberta, "prologo abre sozinho")
	await _fechar_dialogos(casa)

	# Sai para a rua
	var vila: Node = await _ir_para(casa, "Saida", "Vila")
	_conferir(vila != null, "saiu da casa para a rua da vila")

	# Sem vara o cais nao deixa seguir
	await _ir_e_apertar(vila, "Cais")
	await _fechar_dialogos(vila)
	_conferir(current_scene == vila, "sem vara nao vai ao cais")

	# Venda do Seu Valdir: compra a Vara de Bambu (primeira opcao)
	var venda: Node = await _ir_para(vila, "PortaVenda", "Venda")
	_conferir(venda != null, "entrou na venda do Seu Valdir")
	await _ir_e_apertar(venda, "Valdir")
	await _apertar(&"espaco")
	await _apertar(&"espaco")
	await _apertar(&"ui_cancel")
	_conferir(partida.vara == &"bambu", "comprou a vara de bambu")
	_conferir(partida.dinheiro == 30, "pagou R$ 50 (tem %d)" % partida.dinheiro)
	vila = await _ir_para(venda, "Saida", "Vila")
	_conferir(vila != null, "voltou da venda para a rua")

	# Rua -> cais -> barco -> mapa -> acude
	await _ir_e_apertar(vila, "Cais")
	await _quadros(5)
	_conferir(current_scene.name == "Cais", "a rua leva ao cais")
	current_scene.get_node("Jogo/Player").position.x = 600.0
	await _quadros(2)
	await _apertar(&"espaco")      # chama o barco: abre o mapa
	await _quadros(3)
	await _apertar(&"espaco")      # confirma o acude, o primeiro alfinete
	await _quadros(5)
	var acude: Node = current_scene
	_conferir(acude.name == "Acude", "o barco levou ao acude")

	# Um lancamento: carrega a forca e solta
	acude.get_node("Jogo/Player").position.x = 572.0
	await _quadros(2)
	Input.action_press(&"espaco")
	await _quadros(20)
	Input.action_release(&"espaco")
	await _esperar_estado(acude, 3, 8.0)
	_conferir(acude.estado == 3, "o peixe mordeu")
	_conferir(partida.energia < partida.ENERGIA_MAX, "lancar gastou energia (%.1f)" % partida.energia)
	_conferir(acude.especie.nome == "Tilápia", "dia 1 so tem tilapia")
	await _apertar(&"espaco")
	_conferir(acude.estado == 4, "fisgou e entrou no minijogo")
	acude.minijogo.progresso = 99.9
	acude.minijogo.peixe_pos = acude.minijogo.zona_pos + 10.0
	await _esperar_estado(acude, 0, 5.0)
	_conferir(partida.balde.size() == 1, "peixe foi para o balde")

	# Fim do dia: acaba a energia e o barco leva direto para casa
	partida.energia = 0.0
	await _quadros(3)
	await _fechar_dialogos(acude)
	await _quadros(5)
	casa = current_scene
	_conferir(casa.name == "CasaAvo", "sem energia, volta para casa")
	await _fechar_dialogos(casa)

	# Compradores: a Dona Maria Ivone paga mais pela tilapia que o Zeca
	var peixe: Dictionary = partida.balde[0]
	var no_zeca: int = partida.preco_de(&"zeca", peixe)
	var na_ivone: int = partida.preco_de(&"ivone", peixe)
	_conferir(na_ivone > no_zeca, "restaurante paga mais pela tilapia (%d > %d)" % [na_ivone, no_zeca])
	var cascudo: Dictionary = {"especie": partida.especie(&"Cascudo"), "peso": 1.0, "valor": 40}
	_conferir(partida.preco_de(&"ivone", cascudo) < partida.preco_de(&"zeca", cascudo),
		"restaurante paga menos pelo cascudo")

	# Vende o balde na pescaria do Zeca
	vila = await _ir_para(casa, "Saida", "Vila")
	var pescaria: Node = await _ir_para(vila, "PortaPescaria", "Pescaria")
	_conferir(pescaria != null, "entrou na pescaria do Zeca")
	var antes: int = partida.dinheiro
	await _ir_e_apertar(pescaria, "Zeca")
	await _apertar(&"espaco")      # primeira opcao: vender o balde
	await _fechar_dialogos(pescaria)
	_conferir(partida.balde.is_empty() and partida.dinheiro > antes,
		"vendeu o balde no Zeca (R$ %d)" % partida.dinheiro)

	# Pedido do Zeca: 4 tilapias sobem o relacionamento para o nivel 1
	for i in 4:
		partida.registrar_captura(partida.especie(&"Tilápia"), 0.8)
	_conferir(partida.pode_entregar(&"zeca"), "da para entregar o pedido do Zeca")
	var bonus_antes: int = partida.bonus_em_porcento(&"zeca")
	await _ir_e_apertar(pescaria, "Zeca")
	await _apertar(&"ui_down")     # pula "vender o balde"
	await _apertar(&"espaco")      # entregar o pedido
	await _fechar_dialogos(pescaria)
	_conferir(partida.relacao[&"zeca"] == 1, "pedido do Zeca subiu a relacao para 1")
	_conferir(partida.bonus_em_porcento(&"zeca") > bonus_antes, "o Zeca passou a pagar mais")
	_conferir(partida.balde.is_empty(), "as 4 tilapias sairam do balde")

	# Restaurante da Dona Maria Ivone
	vila = await _ir_para(pescaria, "Saida", "Vila")
	var restaurante: Node = await _ir_para(vila, "PortaRestaurante", "Restaurante")
	_conferir(restaurante != null, "entrou no restaurante da Dona Maria Ivone")
	partida.registrar_captura(partida.especie(&"Tilápia"), 1.4)
	_conferir(partida.pode_entregar(&"ivone"), "da para entregar o pedido da Ivone")
	await _ir_e_apertar(restaurante, "Ivone")
	await _apertar(&"ui_down")
	await _apertar(&"espaco")      # entregar o pedido
	await _fechar_dialogos(restaurante)
	_conferir(partida.relacao[&"ivone"] == 1, "pedido da Ivone subiu a relacao para 1")

	# Dorme
	vila = await _ir_para(restaurante, "Saida", "Vila")
	casa = await _ir_para(vila, "PortaCasa", "CasaAvo")
	await _ir_e_apertar(casa, "Cama")
	await _fechar_dialogos(casa)
	_conferir(partida.dia == 2 and partida.energia == partida.ENERGIA_MAX,
		"dormiu e comecou o dia 2 com energia cheia")
	_conferir(partida.disponivel(partida.ITENS[&"cafezinho"].dia), "cafezinho liberado no dia 2")

	# Fechamento: dinheiro da obra e um jundia no balde
	partida.dinheiro = 900
	partida.registrar_captura(partida.especie(&"Jundiá"), 4.0)
	await _ir_e_apertar(casa, "Marlene")
	await _apertar(&"ui_down")
	await _apertar(&"espaco")      # pagar a casa
	await _fechar_dialogos(casa)
	_conferir(partida.obra_paga(&"casa"), "pagou a reforma da casa")
	_conferir(partida.obra_liberada(&"venda"), "a venda do avo liberou depois da casa")

	await _ir_e_apertar(casa, "Marlene")
	await _apertar(&"ui_down")
	await _apertar(&"ui_down")
	await _apertar(&"espaco")      # entregar o jundia
	await _fechar_dialogos(casa)
	_conferir(partida.fase_concluida(), "fase concluida")
	_conferir(casa._concluida, "tela final apareceu")

	# Sorteio: com a fibra no dia 3 aparecem carpa e jundia
	partida.dia = 3
	var vistos: Dictionary = {}
	for i in 2000:
		var e: Especie = partida.sortear_especie(randf_range(6.0, 85.0), false)
		vistos[e.nome] = vistos.get(e.nome, 0) + 1
	print("sorteio com a fibra, dia 3: ", vistos)
	for nome in ["Tilápia", "Cascudo", "Carpa", "Jundiá", "Jundiá Gigante"]:
		_conferir(vistos.has(nome), "sorteio alcanca " + nome)
	vistos.clear()
	for i in 2000:
		var e: Especie = partida.sortear_especie(randf_range(6.0, 45.0), false)
		vistos[e.nome] = vistos.get(e.nome, 0) + 1
	print("sorteio com o bambu, dia 3: ", vistos)
	_conferir(not vistos.has("Carpa") and not vistos.has("Jundiá"), "bambu nao alcanca carpa nem jundia")

	print("FALHAS ", _falhas)
	quit(1 if _falhas > 0 else 0)


# --------------------------------- apoio ---------------------------------

## Anda ate a estacao, aperta ESPACO e espera a cena nova entrar. Devolve a
## cena de destino, ou null se ela nao veio.
func _ir_para(cena: Node, estacao: String, esperada: String) -> Node:
	await _ir_e_apertar(cena, estacao)
	await _quadros(6)
	if current_scene.name != esperada:
		return null
	await _fechar_dialogos(current_scene)
	return current_scene


func _ir_e_apertar(cena: Node, estacao: String) -> void:
	cena.get_node("Player").position.x = cena.get_node("Estacoes/" + estacao).position.x
	await _quadros(2)
	await _apertar(&"espaco")


func _esperar_estado(cena: Node, estado: int, limite: float) -> void:
	var gasto: float = 0.0
	while cena.estado != estado and gasto < limite:
		await process_frame
		gasto += 1.0 / 60.0


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
	# Fecha o que abrir ate a cena ficar livre (a casa tambem espera a tela
	# escurecer quando dorme).
	var fechada: int = 0
	while fechada < 4:
		await _quadros(2)
		if not is_instance_valid(cena) or not cena.is_inside_tree():
			return
		if cena._caixa.aberta:
			fechada = 0
			# Menu de escolha so fecha com ESC. Com ESPACO ele escolhe uma
			# opcao e volta a abrir, e a venda e a loja ficariam em laco.
			await _apertar(&"ui_cancel" if cena._caixa._modo_escolha else &"espaco")
		elif cena.get(&"_ocupado"):
			fechada = 0
		else:
			fechada += 1
