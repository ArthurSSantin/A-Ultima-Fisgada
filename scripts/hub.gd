extends Node2D

## Hub: a Loja de Pesca do avo (docs/design-fase1.md, secao 2). O jogador anda
## pela loja e fala com quem estiver perto com ESPACO:
##
##   Cama          dorme e comeca o proximo dia
##   Dona Marlene  conversa, paga o telhado e recebe o robalo
##   Zeca          compra o balde
##   Seu Aldo      loja, com o catalogo liberado por dia
##   Porta         vai para o cais
##
## A Fase 1 fecha com o telhado pago e um robalo entregue. Os nos sao
## provisorios (ColorRect) ate a arte do hub chegar.

const CENA_CAIS: String = "res://scenes/CaisTeste.tscn"
const ALCANCE: float = 80.0
const BORDA: Vector2 = Vector2(40.0, 1240.0)

const ACOES: Dictionary = {
	&"Cama": "Dormir",
	&"Marlene": "Falar com Dona Marlene",
	&"Zeca": "Vender o balde para o Zeca",
	&"Aldo": "Ver a loja do Seu Aldo",
	&"Saida": "Ir para o cais",
}

var _caixa: CaixaDialogo
var _perto: Node2D = null
var _ocupado: bool = false
var _concluida: bool = false

@onready var _player: Sprite2D = $Player
@onready var _mover: EightDir = $Player/OitoDirecoes
@onready var _estacoes: Node2D = $Estacoes
@onready var _telhado: ColorRect = $Telhado
@onready var _estragos: Node2D = $Estragos
@onready var _quadro_barra: ColorRect = $Quadro/Barra
@onready var _quadro_texto: Label = $Quadro/Texto
@onready var _hud: Label = $UI/Hud
@onready var _objetivo: Label = $UI/Objetivo
@onready var _prompt: Label = $UI/Prompt


func _ready() -> void:
	_caixa = CaixaDialogo.new()
	add_child(_caixa)
	$UI.add_child(BarraEnergia.new())
	_player.position.x = Partida.hub_x
	Partida.hub_x = 640.0
	_atualizar_interface()
	_ao_entrar.call_deferred()


func _process(delta: float) -> void:
	var livre: bool = not (_ocupado or _caixa.ocupada() or _concluida)
	_mover.enabled = livre
	_mover.tick(delta)
	_player.position.x = clampf(_player.position.x, BORDA.x, BORDA.y)
	if Input.is_action_just_pressed(&"mover_esquerda"):
		_player.flip_h = true
	if Input.is_action_just_pressed(&"mover_direita"):
		_player.flip_h = false

	_perto = null
	for estacao: Node2D in _estacoes.get_children():
		if absf(estacao.position.x - _player.position.x) < ALCANCE:
			_perto = estacao

	_atualizar_interface()
	_prompt.visible = livre and _perto != null
	if not livre or _perto == null:
		return
	_prompt.text = "[ESPAÇO] " + ACOES[_perto.name]
	if Input.is_action_just_pressed(&"espaco"):
		_interagir(_perto.name)


func _interagir(estacao: StringName) -> void:
	_ocupado = true
	_mover.velocidade_x = 0.0
	match estacao:
		&"Cama":
			await _cama()
		&"Marlene":
			await _marlene()
		&"Zeca":
			await _zeca()
		&"Aldo":
			await _aldo()
		&"Saida":
			await _saida()
	_ocupado = false
	if Partida.fase_concluida() and not _concluida:
		_fechar_fase()


# ------------------------------ Narrativa ------------------------------

func _ao_entrar() -> void:
	_ocupado = true
	if not Partida.prologo_visto:
		Partida.prologo_visto = true
		await _prologo()
	elif Partida.cansado() and not Partida.balde.is_empty():
		await _caixa.falar("Dona Marlene", ["Voltou! Passa no Zeca pra vender o balde e depois vai descansar."])
	_ocupado = false


func _prologo() -> void:
	await _caixa.falar("", [
		"Nove meses depois da tempestade, Tiago volta à Loja de Pesca do avô, no litoral de Santa Catarina.",
		"O mar levou Seu Bento antes. A tempestade levou metade da loja depois.",
	])
	await _caixa.falar("Dona Marlene", [
		"Tiago? Meu Deus, menino, quanto tempo!",
		"Olha só o estado disso aqui... o telhado foi todo embora.",
	])
	await _caixa.falar("Tiago", ["Vó, achei a vara do vô no meio dos escombros. Tá inteirinha."])
	await _caixa.falar("Dona Marlene", [
		"Essa eu guardo comigo. Um dia ela volta pras tuas mãos, prometo.",
		"Se tu quer mesmo reerguer a Loja de Pesca do Bento, começa por esse buraco no telhado: são R$ %d." % Partida.TELHADO,
		"E o Bento sempre dizia: a loja só reabre com um robalo na mesa. Me traz um, que eu faço o almoço.",
		"Só não te mata no cais, viu? Quando cansar, volta pra cá, vende os peixes pro Zeca e vai dormir.",
		"O Seu Aldo vende uma vara de bambu baratinha. Depois é só sair pela porta da direita, que dá no cais.",
	])


## Fala da Dona Marlene ao acordar, uma novidade por dia.
func _bom_dia() -> void:
	match Partida.dia:
		2:
			await _caixa.falar("Dona Marlene", [
				"Bom dia! O Seu Aldo abriu o resto da loja: isca de camarão, Cafezinho e o Modão.",
				"E cuidado com as beliscadas. O peixe brinca com a isca antes de morder. Teu avô só puxava na mordida firme.",
				"Ah, e a Vara de Fibra lança mais longe. Lá no fundo tem corvina e robalo.",
			])
		3:
			await _caixa.falar("Dona Marlene", [
				"Bom dia! O pessoal do cais anda falando de um robalo-flecha enorme rondando por aí.",
				"Dizem que ele fica a meia distância, longe dos paratis mas antes do fundo. Quem sabe hoje?",
			])
		_:
			await _caixa.falar("Dona Marlene", ["Bom dia, Tiago! " + _o_que_falta()])


func _o_que_falta() -> String:
	var partes: PackedStringArray = []
	if not Partida.telhado_pago:
		partes.append("faltam R$ %d pro telhado" % maxi(0, Partida.TELHADO - Partida.dinheiro))
	if not Partida.robalo_entregue:
		partes.append("ainda falta o robalo")
	if partes.is_empty():
		return "Tá tudo pronto!"
	return "Pelas minhas contas, " + " e ".join(partes) + "."


func _fechar_fase() -> void:
	_concluida = true
	await _caixa.falar("Dona Marlene", [
		"Telhado novo e robalo na mesa. O Bento ia ficar orgulhoso, Tiago.",
	])
	await _caixa.falar("", [
		"Enquanto os pedreiros tiram as últimas telhas velhas, Tiago encontra um embrulho de lona preso na viga.",
		"É o caderno do avô. Nas páginas, pontos marcados no mapa do litoral... e um nome sublinhado duas vezes: Arvoredo.",
	])
	_tela_final()


func _tela_final() -> void:
	var camada := CanvasLayer.new()
	camada.layer = 20
	add_child(camada)
	var fundo := ColorRect.new()
	fundo.color = Color(0.07, 0.13, 0.28, 0.96)
	fundo.size = Vector2(1280, 720)
	camada.add_child(fundo)

	var linhas: PackedStringArray = [
		"FASE 1 CONCLUÍDA",
		"",
		"Dias de pesca: %d" % Partida.dia,
		"Tempo de jogo: %d min" % roundi(Partida.minutos_jogados()),
		"Peixes pescados: %d" % Partida.total_peixes,
		"Total vendido: R$ %d" % Partida.total_vendido,
		"",
		"Coleção (recorde de peso):",
	]
	for e in Partida.especies:
		if Partida.colecao.has(e.nome):
			var r: Dictionary = Partida.colecao[e.nome]
			linhas.append("%s: %d  (%s kg)" % [e.nome, r.quantidade, C3.num(r.recorde_kg)])
		else:
			linhas.append("%s: ???" % ("Peixe especial" if e.raridade == Especie.Raridade.ESPECIAL else e.nome))
	linhas.append_array(["", "Os pontos do caderno levam ao costão. A história continua na Fase 2."])

	var texto := Label.new()
	texto.text = "\n".join(linhas)
	texto.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	texto.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	texto.size = Vector2(1280, 720)
	texto.add_theme_font_size_override("font_size", 22)
	texto.add_theme_color_override("font_color", Color(0.96, 0.94, 0.86))
	camada.add_child(texto)


# ------------------------------ Estacoes ------------------------------

func _cama() -> void:
	if Partida.tem_vara() and not Partida.cansado():
		var i: int = await _caixa.escolher("", "Tiago ainda tem energia para pescar hoje. Dormir mesmo assim?", ["Dormir", "Ainda não"])
		if i != 0:
			return
	elif not Partida.balde.is_empty():
		var i: int = await _caixa.escolher("", "Ainda tem peixe no balde. O Zeca só compra fresco! Dormir mesmo assim?", ["Dormir", "Ainda não"])
		if i != 0:
			return
	Partida.dormir()
	await _escurecer()
	await _caixa.falar("", ["Dia %d" % Partida.dia])
	await _bom_dia()


func _marlene() -> void:
	var opcoes: Array = ["Conversar"]
	var acoes: Array[StringName] = [&"conversar"]
	if not Partida.telhado_pago:
		opcoes.append("Pagar o telhado (R$ %d)" % Partida.TELHADO)
		acoes.append(&"telhado")
	if not Partida.robalo_entregue and Partida.tem_robalo_no_balde():
		opcoes.append("Entregar um robalo")
		acoes.append(&"robalo")
	opcoes.append("Tchau")
	acoes.append(&"sair")

	var i: int = await _caixa.escolher("Dona Marlene", "Diz, meu filho.", opcoes)
	var acao: StringName = acoes[i] if i >= 0 else &"sair"
	match acao:
		&"conversar":
			await _caixa.falar("Dona Marlene", [_conselho(), _o_que_falta()])
		&"telhado":
			if Partida.pagar_telhado():
				await _caixa.falar("Dona Marlene", ["Vou chamar o pessoal hoje mesmo! Telhado novo, enfim."])
			else:
				await _caixa.falar("Dona Marlene", ["Ainda faltam R$ %d, Tiago. Mais uns dias de mar." % (Partida.TELHADO - Partida.dinheiro)])
		&"robalo":
			Partida.entregar_robalo()
			await _caixa.falar("Dona Marlene", ["Que robalo bonito! Igualzinho os que o Bento trazia. Esse vai pro almoço da reabertura."])


func _conselho() -> String:
	if not Partida.tem_vara():
		return "Passa no Seu Aldo e compra a vara de bambu. Sem vara não tem pescaria."
	if not Partida.cansado():
		if Partida.dia >= 2 and not (&"fibra" in Partida.varas_compradas):
			return "Com a de bambu tu não chega no robalo. Junta pra Vara de Fibra do Seu Aldo."
		return "O cais é ali pela porta da direita. Volta quando cansar."
	if not Partida.balde.is_empty():
		return "Vende o balde pro Zeca antes de dormir."
	return "Já tá tarde. Vai dormir, amanhã tem mais."


func _zeca() -> void:
	if Partida.balde.is_empty():
		await _caixa.falar("Zeca", ["Sem peixe, sem negócio! Volta com o balde cheio."])
		return

	var guardar: bool = false
	if not Partida.robalo_entregue and Partida.tem_robalo_no_balde():
		var i: int = await _caixa.escolher("Zeca", "Opa, tem robalo aí! Dona Marlene não queria um?", ["Vender tudo menos um robalo", "Vender tudo", "Deixa pra depois"])
		if i < 0 or i == 2:
			return
		guardar = i == 0

	var vendidos: Array[Dictionary] = Partida.vender_balde(guardar)
	var linhas: PackedStringArray = []
	var total: int = 0
	for peixe in vendidos:
		linhas.append("%s, %s kg ........ R$ %d" % [peixe.especie.nome, C3.num(peixe.peso), peixe.valor])
		total += peixe.valor
	linhas.append("Total: R$ %d" % total)
	await _caixa.falar("Zeca", ["\n".join(linhas), "Tá aqui teu dinheiro. Agora tu tem R$ %d." % Partida.dinheiro])


func _aldo() -> void:
	while true:
		var opcoes: Array = []
		var acoes: Array = []
		for id: StringName in Partida.VARAS:
			var v: Dictionary = Partida.VARAS[id]
			if id in Partida.varas_compradas:
				opcoes.append("%s (já tem)" % v.nome)
			elif not Partida.disponivel(v.dia):
				opcoes.append("%s (chega no dia %d)" % [v.nome, v.dia])
			else:
				opcoes.append("%s, R$ %d: lança até %d de força" % [v.nome, v.preco, v.forca])
			acoes.append([&"vara", id])
		for id: StringName in Partida.ITENS:
			var item: Dictionary = Partida.ITENS[id]
			if not Partida.disponivel(item.dia):
				opcoes.append("%s (chega no dia %d)" % [item.nome, item.dia])
			else:
				opcoes.append("%s, R$ %d (tem %d)" % [item.nome, item.preco, Partida.estoque[id]])
			acoes.append([&"item", id])
		opcoes.append("Sair")
		acoes.append([&"sair", &""])

		var i: int = await _caixa.escolher("Seu Aldo", "Tu tem R$ %d. O que vai ser?" % Partida.dinheiro, opcoes)
		if i < 0 or acoes[i][0] == &"sair":
			return
		await _comprar(acoes[i][0], acoes[i][1])


func _comprar(tipo: StringName, id: StringName) -> void:
	var dados: Dictionary = Partida.VARAS[id] if tipo == &"vara" else Partida.ITENS[id]
	if tipo == &"vara" and id in Partida.varas_compradas:
		await _caixa.falar("Seu Aldo", ["Essa tu já tem, rapaz."])
	elif not Partida.disponivel(dados.dia):
		await _caixa.falar("Seu Aldo", ["Essa ainda não chegou. Volta no dia %d." % dados.dia])
	elif Partida.dinheiro < dados.preco:
		await _caixa.falar("Seu Aldo", ["Faltam R$ %d pra essa." % (dados.preco - Partida.dinheiro)])
	elif tipo == &"vara":
		Partida.comprar_vara(id)
		await _caixa.falar("Seu Aldo", ["%s! Lança até %d de força. Boa pescaria." % [dados.nome, dados.forca]])
	else:
		Partida.comprar_item(id)
		await _caixa.falar("Seu Aldo", ["%s. %s" % [dados.nome, dados.descricao]])


func _saida() -> void:
	if not Partida.tem_vara():
		await _caixa.falar("Tiago", ["Preciso de uma vara antes de ir pro cais. O Seu Aldo deve ter alguma."])
	elif Partida.cansado():
		await _caixa.falar("Tiago", ["Tô morto de cansaço. Melhor vender o balde e dormir."])
	else:
		get_tree().change_scene_to_file.call_deferred(CENA_CAIS)


func _escurecer() -> void:
	var camada := CanvasLayer.new()
	camada.layer = 5
	var tela := ColorRect.new()
	tela.color = Color(0, 0, 0, 0)
	tela.size = Vector2(1280, 720)
	camada.add_child(tela)
	add_child(camada)
	var tween := create_tween()
	tween.tween_property(tela, "color:a", 1.0, 0.5)
	tween.tween_interval(0.3)
	tween.tween_property(tela, "color:a", 0.0, 0.5)
	await tween.finished
	camada.queue_free()


# ------------------------------ Interface ------------------------------

func _atualizar_interface() -> void:
	var vara: String = Partida.VARAS[Partida.vara].nome if Partida.tem_vara() else "sem vara"
	_hud.text = "Dia %d   |   R$ %d   |   Balde: %d peixes   |   %s" % [
		Partida.dia, Partida.dinheiro, Partida.balde.size(), vara,
	]

	_telhado.visible = Partida.telhado_pago
	_estragos.visible = not Partida.telhado_pago
	var guardado: float = 1.0 if Partida.telhado_pago else clampf(float(Partida.dinheiro) / Partida.TELHADO, 0.0, 1.0)
	_quadro_barra.size.x = 220.0 * guardado
	_quadro_texto.text = "Telhado: %s\nRobalo: %s" % [
		"pronto!" if Partida.telhado_pago else "R$ %d / %d" % [mini(Partida.dinheiro, Partida.TELHADO), Partida.TELHADO],
		"entregue!" if Partida.robalo_entregue else "falta entregar",
	]

	_objetivo.text = "Objetivos da Fase 1\n%s Pagar o telhado (R$ %d)\n%s Entregar um robalo à Dona Marlene" % [
		"[x]" if Partida.telhado_pago else "[  ]", Partida.TELHADO,
		"[x]" if Partida.robalo_entregue else "[  ]",
	]
