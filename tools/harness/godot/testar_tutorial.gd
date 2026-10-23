extends SceneTree

## Teste de ponta a ponta do tutorial (fase 1) com o teclado simulado: a
## abertura automatica no quarto, carinho no MauMau, o poster do pai, a vara,
## o cafe obrigatorio, a bolinha da Pacoca, montar no Alexandre, a estrada
## conduzida ate o rio, o Teimoso, o butiazinho que vira cafezinho, os 8 peixes
## com as 4 especies, a subida, a volta a cavalo e a passagem para a fase 2.
##
## Uso: godot --headless --fixed-fps 60 --path . -s tools/harness/godot/testar_tutorial.gd

var _falhas: int = 0


func _initialize() -> void:
	_rodar.call_deferred()


func _rodar() -> void:
	var partida: Node = root.get_node("Partida")
	partida.definir_nome("Tiago", "Bento")
	change_scene_to_file("res://scenes/tutorial/Quarto.tscn")
	await _quadros(5)

	# Quarto: a abertura no escuro corre sozinha
	var quarto: Node = current_scene
	_conferir(quarto.name == "Quarto", "comeca no quarto")
	var gasto: float = 0.0
	while not quarto._caixa.aberta and gasto < 14.0:
		await process_frame
		gasto += 1.0 / 60.0
	_conferir(gasto > 7.0 and gasto < 12.0, "a abertura no escuro corre sozinha (%.1f s)" % gasto)
	await _fechar_falas(quarto)
	_conferir(not partida.tem_vara(), "a vara ainda esta na parede")
	await _ir_e_apertar(quarto, "Porta")
	await _fechar_falas(quarto)
	_conferir(current_scene == quarto, "sem a vara a porta nao abre")

	await _ir_e_apertar(quarto, "MauMau")
	await _escolher(quarto, 0)          # fazer carinho
	await _quadros(150)
	await _fechar_falas(quarto)
	_conferir(quarto._carinhos == 1, "fez carinho no MauMau")

	await _ir_e_apertar(quarto, "PosterPai")
	await _quadros(20)
	var perto: bool = false
	for filho in quarto.get_children():
		perto = perto or (filho is CanvasLayer and filho.layer == 9)
	_conferir(perto, "o poster do pai abre de perto")
	await _fechar_falas(quarto)

	await _ir_e_apertar(quarto, "Vara")
	await _fechar_falas(quarto)
	_conferir(partida.tem_vara() and partida.vara == &"bambu", "pegou a vara de bambu")
	_conferir(partida.feito(&"vara"), "objetivo da vara cumprido")
	_conferir(not quarto.get_node("Estacoes/Vara").visible, "a vara sumiu da parede")

	var cozinha: Node = await _sair_por(quarto, "Porta", "Cozinha")
	_conferir(cozinha != null, "foi para a cozinha")

	# Cozinha: sem cafe a vo nao deixa sair
	await _fechar_falas(cozinha)
	await _ir_e_apertar(cozinha, "Porta")
	await _fechar_falas(cozinha)
	_conferir(current_scene == cozinha, "sem cafe a vo nao deixa sair")
	await _ir_e_apertar(cozinha, "Mesa")
	await _quadros(30)
	var mordidas: int = 0
	while not partida.tomou_cafe or mordidas < 3:
		await _apertar(&"espaco")      # cada ESPACO e uma mordida
		await _quadros(6)
		mordidas += 1
		if mordidas > 10:
			break
	await _fechar_falas(cozinha)
	_conferir(partida.tomou_cafe and partida.feito(&"cafe"), "tomou cafe com a vo")
	var terreiro: Node = await _sair_por(cozinha, "Porta", "Terreiro")
	_conferir(terreiro != null, "saiu para o terreiro")

	# Terreiro: a bolinha da Pacoca
	var pacoca: Node2D = terreiro.get_node("Estacoes/Pacoca")
	var origem: float = pacoca.position.x
	await _ir_e_apertar(terreiro, "Pacoca")
	await _escolher(terreiro, 1)        # jogar a bolinha
	var longe: float = origem
	for i in 90:
		await process_frame
		longe = maxf(longe, pacoca.position.x)
	await _quadros(240)
	await _fechar_falas(terreiro)
	_conferir(longe > origem + 150.0, "a Pacoca correu atras da bolinha (%.0f px)" % (longe - origem))
	_conferir(absf(pacoca.position.x - origem) < 2.0, "e voltou com ela")

	# Alexandre -> estrada conduzida -> cais
	await _ir_e_apertar(terreiro, "Alexandre")
	await _escolher(terreiro, 0)        # montar
	await _passar_ate("Estrada")
	var estrada: Node = current_scene
	_conferir(estrada.name == "Estrada" and partida.feito(&"montar"), "montou no Alexandre e pegou a estrada")
	await _fechar_falas(estrada)
	var vo_longe: float = 0.0
	Input.action_press(&"mover_direita")
	for i in 120:
		await process_frame
	vo_longe = estrada.get_node("Player").position.x - estrada.get_node("Vo").position.x
	Input.action_release(&"mover_direita")
	_conferir(vo_longe > 60.0 and vo_longe < 320.0, "o vo vem atras no Apollo (%.0f px)" % vo_longe)
	await _cavalgar(&"mover_direita", "CaisRio")
	_conferir(current_scene != null and current_scene.name == "CaisRio", "conduziu o Alexandre ate o cais do rio")
	var cais: Node = current_scene
	await _fechar_falas(cais)
	await _ir_e_apertar(cais, "Bote")
	await _passar_ate("Descida")
	_conferir(current_scene.name == "Descida", "embarcou e desceu o rio")
	await _passar_ate("MeioDoRio")
	var rio: Node = current_scene
	_conferir(rio.name == "MeioDoRio", "parou no meio do rio")
	_conferir(partida.feito(&"rio"), "objetivo de chegar no rio cumprido")
	_conferir(partida.fase == 1 and partida.especie(&"Lambari") != null, "especies do rio carregadas")
	await _fechar_falas(rio)

	# O primeiro lance: beliscada do lambari, depois a mordida do Teimoso
	Input.action_press(&"espaco")
	await _quadros(18)
	Input.action_release(&"espaco")
	await _esperar_estado(rio, 2, 4.0)
	_conferir(rio._tem_falsa, "o primeiro lance tem a beliscada do lambari")
	var viu_beliscada: bool = false
	gasto = 0.0
	while rio.estado != 3 and gasto < 10.0:
		viu_beliscada = viu_beliscada or rio._beliscando
		await process_frame
		gasto += 1.0 / 60.0
	_conferir(viu_beliscada, "a boia tremeu antes da mordida")
	_conferir(rio.estado == 3 and rio.especie.nome == "Jundiá filhote", "quem morde e o Teimoso")
	await _apertar(&"espaco")
	_conferir(rio.estado == 4, "fisgou e entrou no minijogo")
	rio.minijogo.progresso = 99.9
	rio.minijogo.peixe_pos = rio.minijogo.zona_pos + 10.0
	await _esperar_estado(rio, 5, 4.0)
	await _escolher(rio, 0)             # soltar o Teimoso
	_conferir(partida.teimoso_solto, "soltou o Teimoso")
	# a cena do butia tem pausas (as poses do vo) entre as falas
	var t_butia: int = 0
	var viu_pose: bool = false
	while partida.estoque[&"cafezinho"] == 0 and t_butia < 3000:
		viu_pose = viu_pose or rio._vo_butia.visible
		if rio._caixa.aberta and not rio._caixa._modo_escolha:
			await _apertar(&"espaco")
		else:
			await process_frame
		t_butia += 1
	_conferir(viu_pose, "o vo faz as poses do butia no bote")
	await _fechar_falas(rio)
	_conferir(not rio._vo_butia.visible, "e volta a sentar normal")
	_conferir(partida.estoque[&"cafezinho"] == 4, "o vo negou o butiazinho e deu cafezinho (4 lances)")
	_conferir(partida.diario.size() == 1, "o primeiro peixe foi pro diario")
	_conferir(not partida.pesca_do_rio_completa(), "um peixe so nao libera a volta")

	# Pesca ate cumprir os dois objetivos: 8 peixes e um de cada especie
	var lances: int = 0
	while not rio._caixa._modo_escolha and lances < 30:
		await _pescar_um(rio)
		lances += 1
	_conferir(partida.total_peixes >= 8, "pescou 8 peixes (%d em %d lances)" % [partida.total_peixes, lances])
	_conferir(partida.especies_do_rio_faltando().is_empty(), "pegou um de cada especie do rio")
	_conferir(partida.pesca_do_rio_completa(), "objetivos de pesca cumpridos")
	_conferir(partida.estoque[&"cafezinho"] == 0, "o cafezinho acabou nos lances")
	await _escolher(rio, 1)             # bora pra casa
	await _passar_ate("Subida")
	_conferir(current_scene.name == "Subida", "subiu o rio de volta")
	await _passar_ate("CaisRio")
	cais = current_scene
	_conferir(cais.name == "CaisRio" and partida.volta_do_rio, "voltou pro cais")
	await _fechar_falas(cais)
	_conferir(partida.feito(&"cais"), "objetivo do cais cumprido")
	_conferir(cais.get_node("Estacoes/Alexandre").visible, "os cavalos ficaram esperando no cais")
	await _ir_e_apertar(cais, "Alexandre")
	await _passar_ate("Estrada")
	estrada = current_scene
	_conferir(estrada.name == "Estrada" and estrada.get_node("Fundo").texture.resource_path.ends_with("manha.png"),
		"montou de novo e pegou a estrada de manha")
	await _fechar_falas(estrada)
	await _cavalgar(&"mover_esquerda", "Fim")
	_conferir(current_scene != null and current_scene.name == "Fim", "voltou a cavalo pra casa")
	_conferir(partida.diario.size() == 2, "pegou as bergamotas do Seu Arlindo")
	await _quadros(320)
	_conferir(partida.feito(&"casa"), "chegou em casa com os cavalos")
	await _passar_ate("CasaAvo", 90.0)
	_conferir(current_scene.name == "CasaAvo", "o tutorial termina e a fase 2 comeca na casa do avo")
	_conferir(partida.fase == 2 and partida.especie(&"Tilápia") != null, "fase 2 com as especies do acude")
	_conferir(not partida.tem_vara() and partida.dinheiro == partida.DINHEIRO_INICIAL,
		"a fase 2 comeca sem vara e com o dinheiro inicial")
	_conferir(partida.teimoso_solto, "a memoria do Teimoso atravessa as fases")

	print("FALHAS ", _falhas)
	quit(1 if _falhas > 0 else 0)


# --------------------------------------------------------------- apoio

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


func _ir_e_apertar(cena: Node, estacao: String) -> void:
	await _ate_livre(cena)
	cena.get_node("Player").position.x = cena.get_node("Estacoes/" + estacao).position.x
	await _quadros(3)
	await _apertar(&"espaco")


func _ate_livre(cena: Node) -> void:
	var t: int = 0
	while t < 600 and is_instance_valid(cena) and (cena._caixa.aberta or cena._ocupado):
		if cena._caixa.aberta and not cena._caixa._modo_escolha:
			await _apertar(&"espaco")
		else:
			await process_frame
		t += 1


## Passa as falas ate a cena ficar livre. Escolha nao e respondida aqui.
func _fechar_falas(cena: Node) -> void:
	var paradas: int = 0
	while paradas < 6:
		await _quadros(2)
		if not is_instance_valid(cena) or not cena.is_inside_tree():
			return
		if cena._caixa.aberta and not cena._caixa._modo_escolha:
			paradas = 0
			await _apertar(&"espaco")
		elif cena._caixa.aberta or cena.get(&"_ocupado"):
			paradas = 0
		else:
			paradas += 1


## Passa as falas ate aparecer uma escolha e responde a opcao "indice".
func _escolher(cena: Node, indice: int) -> void:
	var t: int = 0
	while t < 3000:
		await _quadros(2)
		t += 1
		if cena._caixa.aberta and cena._caixa._modo_escolha:
			for i in indice:
				await _apertar(&"ui_down")
			await _apertar(&"espaco")
			return
		if cena._caixa.aberta:
			await _apertar(&"espaco")
	print("FALHA nao apareceu a escolha esperada")
	_falhas += 1


func _sair_por(cena: Node, estacao: String, esperada: String) -> Node:
	await _ir_e_apertar(cena, estacao)
	await _passar_ate(esperada)
	return current_scene if current_scene.name == esperada else null


## Passa falas (de qualquer cena que aparecer) ate a cena "nome" entrar.
func _passar_ate(nome: String, limite: float = 40.0) -> void:
	var gasto: float = 0.0
	while gasto < limite:
		if current_scene and current_scene.name == nome:
			await _quadros(3)
			return
		var c: Node = current_scene
		if c and c.get(&"_caixa") and c._caixa.aberta and not c._caixa._modo_escolha:
			await _apertar(&"espaco")
			gasto += 4.0 / 60.0
		else:
			await process_frame
			gasto += 1.0 / 60.0


## Segura a seta ate a cena "destino" entrar, passando as falas do caminho.
func _cavalgar(seta: StringName, destino: String) -> void:
	var gasto: float = 0.0
	Input.action_press(seta)
	while gasto < 60.0 and not (current_scene and current_scene.name == destino):
		var c: Node = current_scene
		if c and c.get(&"_caixa") and c._caixa.aberta and not c._caixa._modo_escolha:
			await _apertar(&"espaco")
			gasto += 4.0 / 60.0
		else:
			await process_frame
			gasto += 1.0 / 60.0
	Input.action_release(seta)
	await _quadros(3)


## Um lance inteiro: lanca, espera morder, fisga, ganha o minijogo e passa as
## falas. Para quando a pesca volta ao inicio ou aparece a escolha de ir embora.
func _pescar_um(rio: Node) -> void:
	await _fechar_falas(rio)
	if rio._caixa._modo_escolha:
		return
	Input.action_press(&"espaco")
	await _quadros(18)
	Input.action_release(&"espaco")
	await _esperar_estado(rio, 3, 12.0)
	if rio.estado != 3:
		return
	await _apertar(&"espaco")
	rio.minijogo.progresso = 99.9
	rio.minijogo.peixe_pos = rio.minijogo.zona_pos + 10.0
	await _esperar_estado(rio, 5, 4.0)
	var t: int = 0
	while t < 2000 and rio.estado != 0 and not rio._caixa._modo_escolha:
		if rio._caixa.aberta:
			await _apertar(&"espaco")
		else:
			await process_frame
		t += 1


func _esperar_estado(cena: Node, estado: int, limite: float) -> void:
	var gasto: float = 0.0
	while cena.estado != estado and gasto < limite:
		await process_frame
		gasto += 1.0 / 60.0
