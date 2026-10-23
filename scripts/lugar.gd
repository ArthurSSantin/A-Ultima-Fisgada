extends Node2D

## Um lugar por onde o jogador anda a pe: a rua da vila e cada interior dela.
## Todas essas cenas usam este mesmo script, porque todas funcionam igual —
## anda para os lados e aperta ESPACO no que estiver perto. O que muda e quais
## estacoes a cena tem.
##
## Uma estacao e um Node2D dentro de "Estacoes". O NOME do no e que diz o que
## acontece: esta em ACOES (o texto do aviso) e no match de _interagir(). Para
## pendurar algo novo numa cena, basta criar o no com um nome conhecido.
##
##   Rua da vila   PortaCasa, PortaVenda, PortaPescaria, PortaRestaurante,
##                 RuinaVenda, Cais
##   Casa do avo   Cama, Marlene, Saida
##   Venda         Valdir, Saida
##   Pescaria      Zeca, Saida
##   Restaurante   Ivone, Saida
##
## Os nos de cenario (Telhado, Estragos, Quadro, Objetivo) sao opcionais: so a
## casa do avo tem todos.

const CENA_VILA: String = "res://scenes/Vila.tscn"
const CENA_CAIS: String = "res://scenes/Cais.tscn"

const ALCANCE: float = 80.0

## Portas da rua da vila para os interiores.
const PORTAS: Dictionary = {
	&"PortaCasa": "res://scenes/CasaAvo.tscn",
	&"PortaVenda": "res://scenes/Venda.tscn",
	&"PortaPescaria": "res://scenes/Pescaria.tscn",
	&"PortaRestaurante": "res://scenes/Restaurante.tscn",
}

const ACOES: Dictionary = {
	&"Cama": "Dormir",
	&"Marlene": "Falar com Dona Marlene",
	&"Zeca": "Falar com o Zeca",
	&"Ivone": "Falar com a Dona Maria Ivone",
	&"Valdir": "Ver a venda do Seu Valdir",
	&"Saida": "Voltar para a rua",
	&"PortaCasa": "Entrar na casa do {avo}",
	&"PortaVenda": "Entrar na venda do Seu Valdir",
	&"PortaPescaria": "Entrar na pescaria do Zeca",
	&"PortaRestaurante": "Entrar no restaurante da Dona Maria Ivone",
	&"RuinaVenda": "Olhar a venda do {avo}",
	&"Cais": "Seguir para o cais",
}

## Ate onde o Player anda nesta cena.
@export var borda: Vector2 = Vector2(40.0, 1240.0)
## True so na rua: ela guarda o x do Player para ele voltar no mesmo lugar.
@export var e_a_rua: bool = false
## True so na casa do avo: ela abre o prologo e a fala de bom dia.
@export var abre_o_dia: bool = false

var _caixa: CaixaDialogo
var _perto: Node2D = null
var _ocupado: bool = false
var _concluida: bool = false

@onready var _player: Sprite2D = $Player
@onready var _mover: EightDir = $Player/OitoDirecoes
@onready var _estacoes: Node2D = $Estacoes
@onready var _hud: Label = $UI/Hud
@onready var _prompt: Label = $UI/Prompt
# Opcionais: so existem em algumas cenas.
@onready var _telhado: CanvasItem = get_node_or_null("Telhado")
@onready var _estragos: Node2D = get_node_or_null("Estragos")
@onready var _quadro_barra: ColorRect = get_node_or_null("Quadro/Barra")
@onready var _quadro_texto: Label = get_node_or_null("Quadro/Texto")
@onready var _objetivo: Label = get_node_or_null("UI/Objetivo")


func _ready() -> void:
	_caixa = CaixaDialogo.new()
	add_child(_caixa)
	$UI.add_child(BarraEnergia.new())
	if e_a_rua:
		_player.position.x = Partida.vila_x
	elif abre_o_dia:
		_player.position.x = Partida.hub_x
		Partida.hub_x = 640.0
	_atualizar_interface()
	if abre_o_dia:
		_ao_entrar.call_deferred()


func _process(delta: float) -> void:
	var livre: bool = not (_ocupado or _caixa.ocupada() or _concluida)
	_mover.enabled = livre
	_mover.tick(delta)
	_player.position.x = clampf(_player.position.x, borda.x, borda.y)
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
	_prompt.text = Partida.nome_em("[ESPAÇO] " + ACOES[_perto.name])
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
			await _comprador(&"zeca")
		&"Ivone":
			await _comprador(&"ivone")
		&"Valdir":
			await _valdir()
		&"RuinaVenda":
			await _ruina_da_venda()
		&"Cais":
			await _ir_ao_cais()
		&"Saida":
			_ir_para(CENA_VILA)
		_:
			if PORTAS.has(estacao):
				_entrar(PORTAS[estacao])
	_ocupado = false
	if Partida.fase_concluida() and not _concluida and abre_o_dia:
		_fechar_fase()


# ------------------------------ Navegacao ------------------------------

func _entrar(cena: String) -> void:
	Partida.vila_x = _player.position.x
	_ir_para(cena)


func _ir_para(cena: String) -> void:
	get_tree().change_scene_to_file.call_deferred(cena)


func _ir_ao_cais() -> void:
	if not Partida.tem_vara():
		await _caixa.falar("{nome}", [
			"Preciso de uma vara antes de ir pro cais. O Seu Valdir deve ter alguma.",
		])
	elif Partida.cansado():
		await _caixa.falar("{nome}", ["Tô morto de cansaço. Melhor vender o balde e dormir."])
	else:
		Partida.vila_x = _player.position.x
		Partida.cais_x = 150.0
		_ir_para(CENA_CAIS)


# ------------------------------ Narrativa ------------------------------

func _ao_entrar() -> void:
	_ocupado = true
	if not Partida.prologo_visto:
		Partida.prologo_visto = true
		await _prologo()
	_ocupado = false


func _prologo() -> void:
	await _caixa.falar("", [
		"Nove meses depois da enchente, {nome} volta à vila do avô, na beira do açude.",
		"O rio levou Seu {avo} antes. A enchente levou a casa e a venda dele depois.",
	])
	await _caixa.falar("Dona Marlene", [
		"{nome}? Meu Deus, menino, quanto tempo!",
		"Olha só o estado disso aqui... o telhado foi todo embora.",
	])
	await _caixa.falar("{nome}", ["Vó, achei a vara do vô no meio dos escombros. Tá inteirinha."])
	await _caixa.falar("Dona Marlene", [
		"Essa eu guardo comigo. Um dia ela volta pras tuas mãos, prometo.",
		"Se tu quer mesmo reerguer o que o {avo} deixou, começa pela casa: são R$ %d." % Partida.OBRAS[&"casa"].preco,
		"E o {avo} sempre dizia: a família só janta direito com um jundiá na mesa. Me traz um.",
		"Lá fora tu tem a venda do Seu Valdir pra comprar, e dois lugares pra vender peixe: a pescaria do Zeca e o restaurante da Maria Ivone.",
		"Eles pagam diferente, e quem cumpre os pedidos deles passa a receber melhor. Vê qual te serve.",
	])


## Fala da Dona Marlene ao acordar, uma novidade por dia.
func _bom_dia() -> void:
	match Partida.dia:
		2:
			await _caixa.falar("Dona Marlene", [
				"Bom dia! O Seu Valdir abriu o resto da venda: isca de camarão, Cafezinho e o Modão.",
				"E cuidado com as beliscadas. O peixe brinca com a isca antes de morder. Teu avô só puxava na mordida firme.",
				"Ah, e a Vara de Fibra lança mais longe. Lá no fundo do açude tem carpa e jundiá.",
			])
		3:
			await _caixa.falar("Dona Marlene", [
				"Bom dia! O pessoal do açude anda falando de um jundiá gigante rondando por aí.",
				"Dizem que ele fica a meia distância, longe das tilápias mas antes do fundo. Quem sabe hoje?",
			])
		_:
			await _caixa.falar("Dona Marlene", ["Bom dia, {nome}! " + _o_que_falta()])


func _o_que_falta() -> String:
	var partes: PackedStringArray = []
	if not Partida.obra_paga(&"casa"):
		var falta: int = maxi(0, Partida.OBRAS[&"casa"].preco - Partida.dinheiro)
		partes.append("faltam R$ %d pra casa" % falta)
	if not Partida.jundia_entregue:
		partes.append("ainda falta o jundiá")
	if partes.is_empty():
		return "Tá tudo pronto!"
	return "Pelas minhas contas, " + " e ".join(partes) + "."


func _fechar_fase() -> void:
	_concluida = true
	await _caixa.falar("Dona Marlene", [
		"Casa de pé e jundiá na mesa. O {avo} ia ficar orgulhoso, {nome}.",
	])
	await _caixa.falar("", [
		"Enquanto os pedreiros tiram as últimas telhas velhas, {nome} encontra um embrulho de lona preso na viga.",
		"É o caderno do avô. Nas páginas, pontos marcados rio abaixo, até o mar... e um nome sublinhado duas vezes: Arvoredo.",
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
		"FASE 2 CONCLUÍDA",
		"",
		"Dias de pesca: %d" % Partida.dia,
		"Tempo de jogo: %d min" % roundi(Partida.minutos_jogados()),
		"Peixes pescados: %d" % Partida.total_peixes,
		"Total vendido: R$ %d" % Partida.total_vendido,
		"",
	]
	for id: StringName in Partida.COMPRADORES:
		linhas.append("%s: relação nível %d (+%d%% no preço)" % [
			Partida.COMPRADORES[id].nome, Partida.relacao[id], Partida.bonus_em_porcento(id),
		])
	linhas.append("Venda do %s: %s" % [
		Partida.nome_avo, "reaberta!" if Partida.obra_paga(&"venda") else "ainda de pé só na lembrança",
	])
	linhas.append_array(["", "Coleção (recorde de peso):"])
	for e in Partida.especies:
		if Partida.colecao.has(e.nome):
			var r: Dictionary = Partida.colecao[e.nome]
			linhas.append("%s: %d  (%s kg)" % [e.nome, r.quantidade, C3.num(r.recorde_kg)])
		else:
			linhas.append("%s: ???" % ("Peixe especial" if e.raridade == Especie.Raridade.ESPECIAL else e.nome))
	linhas.append_array(["", "Os pontos do caderno descem o rio até o litoral. A história continua na Fase 3."])

	var texto := Label.new()
	texto.text = Partida.nome_em("\n".join(linhas))
	texto.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	texto.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	texto.size = Vector2(1280, 720)
	texto.add_theme_font_size_override("font_size", 20)
	texto.add_theme_color_override("font_color", Color(0.96, 0.94, 0.86))
	camada.add_child(texto)


# ------------------------------ Estacoes ------------------------------

func _cama() -> void:
	if Partida.tem_vara() and not Partida.cansado():
		var i: int = await _caixa.escolher("", "{nome} ainda tem energia para pescar hoje. Dormir mesmo assim?", ["Dormir", "Ainda não"])
		if i != 0:
			return
	elif not Partida.balde.is_empty():
		var i: int = await _caixa.escolher("", "Ainda tem peixe no balde. Ninguém compra peixe de ontem! Dormir mesmo assim?", ["Dormir", "Ainda não"])
		if i != 0:
			return
	Partida.dormir()
	await _escurecer()
	await _caixa.falar("", ["Dia %d" % Partida.dia])
	await _bom_dia()


func _marlene() -> void:
	var opcoes: Array = ["Conversar"]
	var acoes: Array = [&"conversar"]
	for id: StringName in Partida.OBRAS:
		if not Partida.obra_paga(id) and Partida.obra_liberada(id):
			var obra: Dictionary = Partida.OBRAS[id]
			opcoes.append("Pagar: %s (R$ %d)" % [Partida.nome_em(obra.nome), obra.preco])
			acoes.append(id)
	if not Partida.jundia_entregue and Partida.tem_jundia_no_balde():
		opcoes.append("Entregar um jundiá")
		acoes.append(&"jundia")
	opcoes.append("Tchau")
	acoes.append(&"sair")

	var i: int = await _caixa.escolher("Dona Marlene", "Diz, meu filho.", opcoes)
	var acao: StringName = acoes[i] if i >= 0 else &"sair"
	match acao:
		&"conversar":
			await _caixa.falar("Dona Marlene", [_conselho(), _o_que_falta()])
		&"jundia":
			Partida.entregar_jundia()
			await _caixa.falar("Dona Marlene", [
				"Que jundiá bonito! Igualzinho os que o {avo} trazia. Esse vai pro almoço da reabertura.",
			])
		&"sair":
			pass
		_:
			await _pagar_obra(acao)


func _pagar_obra(id: StringName) -> void:
	var obra: Dictionary = Partida.OBRAS[id]
	if Partida.pagar_obra(id):
		if id == &"casa":
			await _caixa.falar("Dona Marlene", [
				"Vou chamar o pessoal hoje mesmo! Telhado novo, enfim.",
				"Agora, quando sobrar, a gente levanta a venda do {avo} também.",
			])
		else:
			await _caixa.falar("Dona Marlene", [
				"A venda do {avo} de portas abertas outra vez. Nem em sonho, menino.",
			])
	else:
		var falta: int = obra.preco - Partida.dinheiro
		await _caixa.falar("Dona Marlene", [
			"Ainda faltam R$ %d, {nome}. Mais uns dias de açude." % falta,
		])


func _conselho() -> String:
	if not Partida.tem_vara():
		return "Passa na venda do Seu Valdir e compra a vara de bambu. Sem vara não tem pescaria."
	if not Partida.cansado():
		if Partida.dia >= 2 and not (&"fibra" in Partida.varas_compradas):
			return "Com a de bambu tu não chega no jundiá. Junta pra Vara de Fibra do Seu Valdir."
		return "O cais fica no fim da rua. O barco te leva pro açude."
	if not Partida.balde.is_empty():
		return "Vende o balde antes de dormir, no Zeca ou na Dona Maria Ivone."
	return "Já tá tarde. Vai dormir, amanhã tem mais."


func _ruina_da_venda() -> void:
	if Partida.obra_paga(&"venda"):
		await _caixa.falar("", [
			"A venda do {avo}, de pé outra vez. A placa velha voltou pro lugar, lixada e repintada.",
		])
	elif Partida.obra_liberada(&"venda"):
		await _caixa.falar("", [
			"O que sobrou da venda do {avo}: meia parede e o balcão debaixo da lona.",
			"A Dona Marlene disse que levanta ela por R$ %d, agora que a casa está de pé." % Partida.OBRAS[&"venda"].preco,
		])
	else:
		await _caixa.falar("", [
			"O que sobrou da venda do {avo}: meia parede e o balcão debaixo da lona.",
			"Uma coisa de cada vez. Primeiro a casa.",
		])


# ---------------------------- Compradores ----------------------------

## Zeca e Dona Maria Ivone funcionam igual: compram o balde por precos
## diferentes e tem um pedido da vez que sobe o relacionamento.
func _comprador(id: StringName) -> void:
	while true:
		var dados: Dictionary = Partida.COMPRADORES[id]
		var pedido: Dictionary = Partida.missao_ativa(id)
		var opcoes: Array = []
		var acoes: Array = []

		if not Partida.balde.is_empty():
			opcoes.append("Vender o balde (%d peixes, R$ %d)" % [
				Partida.balde.size(), _total_do_balde(id),
			])
			acoes.append(&"vender")
		if Partida.pode_entregar(id):
			opcoes.append("Entregar o pedido: %s" % _texto_do_pedido(pedido))
			acoes.append(&"entregar")
		opcoes.append("Conversar")
		acoes.append(&"conversar")
		opcoes.append("Tchau")
		acoes.append(&"sair")

		var i: int = await _caixa.escolher(dados.nome, _cabecalho(id), opcoes)
		var acao: StringName = acoes[i] if i >= 0 else &"sair"
		if acao == &"sair":
			return
		elif acao == &"vender":
			await _vender_para(id)
		elif acao == &"entregar":
			await _entregar_pedido(id)
		else:
			await _caixa.falar(dados.nome, [_fala_do_comprador(id)])


## Linha de cima da conversa: o que ele paga e o pedido da vez.
func _cabecalho(id: StringName) -> String:
	var bonus: int = Partida.bonus_em_porcento(id)
	var linha: String = "Nível %d contigo. " % Partida.relacao[id]
	if bonus > 0:
		linha += "Pago %d%% acima do normal." % bonus
	elif bonus < 0:
		linha += "Pago %d%% do normal." % (100 + bonus)
	else:
		linha += "Pago o preço de tabela."
	var pedido: Dictionary = Partida.missao_ativa(id)
	if not pedido.is_empty():
		linha += "\nPedido da vez: " + _texto_do_pedido(pedido)
	return linha


func _texto_do_pedido(pedido: Dictionary) -> String:
	if pedido.is_empty():
		return "nenhum"
	if pedido.kg_min > 0.0:
		return "%d %s de %s kg ou mais" % [pedido.n, pedido.especie, C3.num(pedido.kg_min)]
	return "%d %s" % [pedido.n, pedido.especie]


func _total_do_balde(id: StringName) -> int:
	var total: int = 0
	for peixe in Partida.balde:
		total += Partida.preco_de(id, peixe)
	return total


func _fala_do_comprador(id: StringName) -> String:
	var pedido: Dictionary = Partida.missao_ativa(id)
	if not pedido.is_empty():
		return pedido.pedido
	if id == &"zeca":
		return "Tu já me atendeu em tudo que eu pedi. Pode trazer o que pescar que eu pago bem."
	return "Minha cozinha não fecha mais sem o teu peixe, meu filho."


func _vender_para(id: StringName) -> void:
	var dados: Dictionary = Partida.COMPRADORES[id]
	if Partida.balde.is_empty():
		await _caixa.falar(dados.nome, [dados.fala_vazio])
		return

	var guardar: bool = false
	if not Partida.jundia_entregue and Partida.tem_jundia_no_balde():
		var i: int = await _caixa.escolher(dados.nome,
			"Opa, tem jundiá aí! A Dona Marlene não queria um?",
			["Vender tudo menos um jundiá", "Vender tudo", "Deixa pra depois"])
		if i < 0 or i == 2:
			return
		guardar = i == 0

	var vendidos: Array[Dictionary] = Partida.vender_balde_para(id, guardar)
	var linhas: PackedStringArray = []
	var total: int = 0
	for peixe in vendidos:
		linhas.append("%s, %s ........ R$ %d" % [peixe.especie.nome, Partida.texto_peso(peixe.peso), peixe.pago])
		total += peixe.pago
	linhas.append("Total: R$ %d" % total)
	await _caixa.falar(dados.nome, [
		"\n".join(linhas),
		"Tá aqui teu dinheiro. Agora tu tem R$ %d." % Partida.dinheiro,
	])


func _entregar_pedido(id: StringName) -> void:
	var dados: Dictionary = Partida.COMPRADORES[id]
	var resultado: Dictionary = Partida.entregar_missao(id)
	if resultado.nivel == 0:
		return
	var falas: PackedStringArray = [
		"É isso aí! Toma R$ %d pelo trabalho." % resultado.premio,
		"Subimos pro nível %d. Daqui pra frente eu te pago %d%% acima do normal." % [
			resultado.nivel, Partida.bonus_em_porcento(id),
		],
	]
	var proximo: Dictionary = Partida.missao_ativa(id)
	if not proximo.is_empty():
		falas.append(proximo.pedido)
	else:
		falas.append("E não tenho mais pedido nenhum. Tu já me atendeu em tudo.")
	await _caixa.falar(dados.nome, falas)


# ------------------------------- Venda -------------------------------

func _valdir() -> void:
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

		var i: int = await _caixa.escolher("Seu Valdir", "Tu tem R$ %d. O que vai ser?" % Partida.dinheiro, opcoes)
		if i < 0 or acoes[i][0] == &"sair":
			return
		await _comprar(acoes[i][0], acoes[i][1])


func _comprar(tipo: StringName, id: StringName) -> void:
	var dados: Dictionary = Partida.VARAS[id] if tipo == &"vara" else Partida.ITENS[id]
	if tipo == &"vara" and id in Partida.varas_compradas:
		await _caixa.falar("Seu Valdir", ["Essa tu já tem, rapaz."])
	elif not Partida.disponivel(dados.dia):
		await _caixa.falar("Seu Valdir", ["Essa ainda não chegou. Volta no dia %d." % dados.dia])
	elif Partida.dinheiro < dados.preco:
		await _caixa.falar("Seu Valdir", ["Faltam R$ %d pra essa." % (dados.preco - Partida.dinheiro)])
	elif tipo == &"vara":
		Partida.comprar_vara(id)
		await _caixa.falar("Seu Valdir", ["%s! Lança até %d de força. Boa pescaria." % [dados.nome, dados.forca]])
	else:
		Partida.comprar_item(id)
		await _caixa.falar("Seu Valdir", ["%s. %s" % [dados.nome, dados.descricao]])


# ------------------------------ Interface ------------------------------

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


func _atualizar_interface() -> void:
	var vara: String = Partida.VARAS[Partida.vara].nome if Partida.tem_vara() else "sem vara"
	_hud.text = "Dia %d   |   R$ %d   |   Balde: %d peixes   |   %s" % [
		Partida.dia, Partida.dinheiro, Partida.balde.size(), vara,
	]

	var casa_pronta: bool = Partida.obra_paga(&"casa")
	if _telhado:
		_telhado.visible = casa_pronta
	if _estragos:
		_estragos.visible = not casa_pronta
	if _quadro_barra:
		var preco: int = Partida.OBRAS[&"casa"].preco
		var guardado: float = 1.0 if casa_pronta else clampf(float(Partida.dinheiro) / preco, 0.0, 1.0)
		_quadro_barra.size.x = 220.0 * guardado
		_quadro_texto.text = "Casa: %s\nJundiá: %s" % [
			"pronta!" if casa_pronta else "R$ %d / %d" % [mini(Partida.dinheiro, preco), preco],
			"entregue!" if Partida.jundia_entregue else "falta entregar",
		]

	if _objetivo:
		_objetivo.text = "Objetivos da Fase 2\n%s Reconstruir a casa (R$ %d)\n%s Entregar um jundiá à Dona Marlene" % [
			"[x]" if casa_pronta else "[  ]", Partida.OBRAS[&"casa"].preco,
			"[x]" if Partida.jundia_entregue else "[  ]",
		]
