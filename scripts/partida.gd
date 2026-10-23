extends Node

## Estado da partida que sobrevive a troca de cena (autoload "Partida").
## Cais e hub (a Loja de Pesca) leem e escrevem aqui. O nome nao e "Jogo" para nao confundir com
## o no $Jogo das cenas de pesca.
##
## Fase 1 e o tutorial (o neto aos 8 anos, pescando no rio com o vo); fase 2 e a
## vila e o acude, anos depois. Os numeros de economia sao os da fase 2,
## aprovados depois do harness (docs/escopo-beta.md,
## secao 5, e tools/harness/harness.mjs, cenario "ajustada").

signal peixe_capturado(especie: Especie, peso: float, valor: int)
signal dinheiro_mudou(valor: int)
signal objetivo_concluido(id: StringName)

## Energia do dia. Lancar gasta (mais quanto mais longe) e brigar com o peixe
## tambem; zerou, o pescador cansa e volta para a Loja de Pesca. Calibrado no
## tools/harness/harness.mjs para uns 8 a 10 lancamentos por dia e para o dia 1
## nao render o bastante para comprar a Vara de Fibra na manha do dia 2.
const ENERGIA_MAX: float = 100.0
const ENERGIA_LANCAMENTO: float = 6.0
const ENERGIA_POR_FORCA: float = 3.0
const ENERGIA_LUTA_POR_S: float = 0.5
const DINHEIRO_INICIAL: int = 80

## Janela da fisgada, em segundos. O Modao aumenta.
const JANELA_FISGADA: float = 0.6
const JANELA_MODAO: float = 0.9
## Altura da zona verde do minijogo. O Cafezinho aumenta.
const ZONA_NORMAL: float = 56.0
const ZONA_CAFEZINHO: float = 72.0
## Chance de beliscada falsa por lancamento, a partir do dia 2.
const CHANCE_FALSA: float = 0.5
## O Peixe Especial so aparece a partir do dia 3.
const CHANCE_ESPECIAL: float = 0.05
const DIA_ESPECIAL: int = 3
## Peso no sorteio, por raridade (Especie.Raridade). A isca de camarao dobra os
## nao comuns.
const PESO_RARIDADE: Array[float] = [1.0, 0.5, 0.25, 0.0]

## Varas: limitam a forca maxima do arremesso, e com isso as especies alcancaveis.
const VARAS: Dictionary = {
	&"bambu": {"nome": "Vara de Bambu", "forca": 45.0, "preco": 50, "dia": 1},
	&"fibra": {"nome": "Vara de Fibra", "forca": 85.0, "preco": 300, "dia": 2},
}

## Consumiveis da loja do Seu Valdir. "quantidade" e quanto vem por compra.
const ITENS: Dictionary = {
	&"camarao": {
		"nome": "Isca de camarão (5)", "preco": 30, "dia": 2, "quantidade": 5,
		"descricao": "Dobra a chance de peixes raros. Gasta uma por lançamento.",
	},
	&"cafezinho": {
		"nome": "Cafezinho", "preco": 70, "dia": 2, "quantidade": 5,
		"descricao": "Barra verde maior por 5 lançamentos.",
	},
	&"modao": {
		"nome": "Modão", "preco": 80, "dia": 2, "quantidade": 5,
		"descricao": "Mais tempo para fisgar e marca a mordida verdadeira, por 5 lançamentos.",
	},
}

## Nome do personagem. O jogador escolhe na tela inicial; se deixar em branco
## fica o padrao. Nos textos, escreva {nome} e deixe nome_em() trocar.
const NOME_PADRAO: String = "Tiago"
## Mais que isso nao cabe na caixa de dialogo nem na placa do hub.
const NOME_MAXIMO: int = 16
## O avo tambem tem nome escolhido na tela inicial; nos textos use {avo}.
const NOME_AVO_PADRAO: String = "Bento"

## Quem compra peixe na vila. "base" multiplica o valor da especie e
## "especialidade" ajusta por peixe: o Zeca revende tudo igual, e o restaurante
## paga bem o peixe de mesa e mal o cascudo, que ninguem quer no prato.
##
## O preco final ainda sobe com o relacionamento (ver BONUS_RELACAO).
const COMPRADORES: Dictionary = {
	&"zeca": {
		"nome": "Zeca",
		"lugar": "Pescaria do Zeca",
		"base": 1.0,
		"especialidade": {},
		"fala_vazio": "Sem peixe, sem negócio! Volta com o balde cheio.",
	},
	&"ivone": {
		"nome": "Dona Maria Ivone",
		"lugar": "Restaurante da Dona Maria Ivone",
		"base": 1.25,
		"especialidade": {"Cascudo": 0.55},
		"fala_vazio": "Balde vazio não vira almoço, meu filho.",
	},
}

## Quanto cada nivel de relacionamento aumenta o preco daquele comprador.
const BONUS_RELACAO: float = 0.10
## Quanto cada comprador paga de gorjeta ao fechar um pedido, por nivel.
const PREMIO_MISSAO: Array[int] = [60, 120, 200]

## Pedidos de cada comprador, um por nivel de relacionamento. Cumprir o da vez
## sobe o nivel e libera o proximo. "kg_min" 0 e pedido so de quantidade.
const MISSOES: Dictionary = {
	&"zeca": [
		{"especie": "Tilápia", "n": 4, "kg_min": 0.0, "pedido": "Me traz 4 tilápias que eu fecho a encomenda da pousada."},
		{"especie": "Cascudo", "n": 3, "kg_min": 0.0, "pedido": "O pessoal do sítio quer 3 cascudos pra limpar o tanque deles."},
		{"especie": "Carpa", "n": 1, "kg_min": 4.0, "pedido": "Queria uma carpa de 4 kg pra cima, dessas de botar na vitrine."},
	],
	&"ivone": [
		{"especie": "Tilápia", "n": 1, "kg_min": 1.0, "pedido": "Me arruma uma tilápia de 1 kg pra cima? Filé bom precisa de peixe graúdo."},
		{"especie": "Carpa", "n": 2, "kg_min": 0.0, "pedido": "Duas carpas e eu faço a moqueca de sábado."},
		{"especie": "Jundiá", "n": 1, "kg_min": 5.0, "pedido": "Um jundiá de 5 kg pra cima. Esse eu sirvo na mesa do prefeito."},
	],
}

## As duas obras que o avo deixou. A casa e o objetivo da fase 2; a venda e
## extra, libera depois da casa e conta como bônus na tela final.
const OBRAS: Dictionary = {
	&"casa": {
		"nome": "Casa do {avo}",
		"preco": 800,
		"descricao": "Telhado novo e o barraco de pé outra vez.",
	},
	&"venda": {
		"nome": "Venda do {avo}",
		"preco": 1200,
		"descricao": "Reabrir a venda da família, do jeito que ele deixou.",
	},
}

const ESPECIES_DIR: String = "res://dados/especies/"

## Objetivos do tutorial, na ordem do quadro do canto da tela. Os dois de
## pesca correm juntos; "Bora pra casa" so aparece com os dois cumpridos.
const OBJETIVOS: Array[Dictionary] = [
	{"id": &"vara", "texto": "Pegar a vara de bambu"},
	{"id": &"cafe", "texto": "Tomar café com a vó"},
	{"id": &"montar", "texto": "Montar no Alexandre"},
	{"id": &"rio", "texto": "Chegar no rio com o vô"},
	{"id": &"especies", "texto": "Um peixe de cada espécie (%d/%d)"},
	{"id": &"peixes", "texto": "Pescar %d peixes (%d/%d)"},
	{"id": &"cais", "texto": "Voltar com o vô pro cais"},
	{"id": &"casa", "texto": "Levar os cavalos de volta pra casa"},
]
const ESPECIES_DO_RIO: Array[String] = ["Lambari", "Cará", "Joaninha", "Jundiá filhote"]
const PEIXES_DO_RIO: int = 8

## Locais de pesca, escolhidos no barco do cais. "pino" e onde o alfinete cai
## no mapa, em fracao da imagem (ver assets/sprites/ui/mapa.png). Um local com
## "oculto" nao aparece no mapa: e so virar a chave quando a fase liberar.
const LOCAIS: Dictionary = {
	&"acude": {
		"nome": "Açude do Seu Bento",
		"cena": "res://scenes/Acude.tscn",
		"descricao": "Água parada e esverdeada, represada no rio. Tilápia e cascudo na beira, carpa e jundiá no fundo. Dizem que tem um jundiá bem maior lá embaixo.",
		"pino": Vector2(0.29, 0.47),
		"oculto": false,
	},
	&"rio": {
		"nome": "Volta do Rio",
		"cena": "",
		"descricao": "Correnteza forte entre as pedras.",
		"pino": Vector2(0.59, 0.65),
		"oculto": true,
	},
	&"foz": {
		"nome": "Foz e Vila",
		"cena": "",
		"descricao": "Onde a água doce encontra o mar.",
		"pino": Vector2(0.70, 0.79),
		"oculto": true,
	},
	&"arvoredo": {
		"nome": "Arvoredo",
		"cena": "",
		"descricao": "As ilhas do caderno do avô.",
		"pino": Vector2(0.93, 0.28),
		"oculto": true,
	},
}

var nome: String = NOME_PADRAO
var nome_avo: String = NOME_AVO_PADRAO
var dinheiro: int = DINHEIRO_INICIAL
var dia: int = 1
var fase: int = 1
var energia: float = ENERGIA_MAX
## Vara em uso; vazia ate comprar a primeira.
var vara: StringName = &""
var varas_compradas: Array[StringName] = []
## Quantos lancamentos ainda tem de cada consumivel.
var estoque: Dictionary = {&"camarao": 0, &"cafezinho": 0, &"modao": 0}
## Obras ja pagas (chaves de OBRAS). A casa fecha a fase; a venda e extra.
var obras_pagas: Array[StringName] = []
var jundia_entregue: bool = false
## Nivel de relacionamento com cada comprador, de 0 ao tamanho de MISSOES.
var relacao: Dictionary = {&"zeca": 0, &"ivone": 0}
## Para a fala de abertura so aparecer uma vez.
var prologo_visto: bool = false

## Memorias do tutorial que a fase 2 le de volta.
var tomou_cafe: bool = false
## O neto soltou o Teimoso, o jundia filhote do rabo mordido. Se soltou, o
## Jundia Gigante do acude e ele, com a mesma marca.
var teimoso_solto: bool = false
var teimoso_reencontrado: bool = false
## Anotacoes do neto, como as do caderno do vo: a primeira e o primeiro peixe.
var diario: Array[String] = []
var cais_visitado: bool = false
## Objetivos do tutorial ja cumpridos (ids de OBJETIVOS).
var objetivos_feitos: Array[StringName] = []
## O tutorial esta na volta: o cais e a estrada mudam de sentido.
var volta_do_rio: bool = false
## Local de pesca escolhido no barco; vale ate o jogador trocar no mapa.
var local: StringName = &"acude"
## Onde o Player aparece ao entrar em cada cena. O hub coloca o jogador perto da
## porta quando ele volta do cais, e o cais perto do barco quando ele desembarca.
var hub_x: float = 640.0
var cais_x: float = 150.0
## Onde o Player reaparece ao voltar para a rua da vila.
var vila_x: float = 400.0

## Peixes pescados e ainda nao vendidos: [{especie, peso, valor}].
var balde: Array[Dictionary] = []
## Por nome de especie: {quantidade, recorde_kg}.
var colecao: Dictionary = {}
var total_peixes: int = 0
var total_vendido: int = 0
var inicio_ms: int = 0

var especies: Array[Especie] = []


func _ready() -> void:
	inicio_ms = Time.get_ticks_msec()
	carregar_especies()


## Especies da fase atual (cada .tres diz a fase dele).
func carregar_especies() -> void:
	especies.clear()
	for arquivo in DirAccess.get_files_at(ESPECIES_DIR):
		# No build exportado os .tres aparecem com sufixo .remap.
		var caminho: String = ESPECIES_DIR + arquivo.trim_suffix(".remap")
		if caminho.ends_with(".tres"):
			var especie: Especie = load(caminho)
			if especie.fase == fase:
				especies.append(especie)


## Passa para outra fase. A fase 2 se passa anos depois do tutorial: o neto
## chega sem vara, sem dinheiro e sem peixe, e so as memorias (nomes, Teimoso,
## diario e a colecao do que ele pescou) vem junto.
func iniciar_fase(nova: int) -> void:
	fase = nova
	dia = 1
	energia = ENERGIA_MAX
	dinheiro = DINHEIRO_INICIAL
	vara = &""
	varas_compradas.clear()
	estoque = {&"camarao": 0, &"cafezinho": 0, &"modao": 0}
	balde.clear()
	obras_pagas.clear()
	jundia_entregue = false
	relacao = {&"zeca": 0, &"ivone": 0}
	prologo_visto = false
	hub_x = 640.0
	vila_x = 400.0
	cais_x = 150.0
	inicio_ms = Time.get_ticks_msec()
	carregar_especies()


## Guarda o nome escolhido, ja aparado. Em branco volta para o padrao.
func definir_nome(escolhido: String, avo: String = "") -> void:
	nome = _aparar(escolhido, NOME_PADRAO)
	nome_avo = _aparar(avo, NOME_AVO_PADRAO)


func _aparar(escrito: String, padrao: String) -> String:
	var limpo: String = escrito.strip_edges()
	return limpo.left(NOME_MAXIMO) if not limpo.is_empty() else padrao


## Troca o marcador {nome} pelo nome do personagem. A CaixaDialogo chama isto
## sozinha, entao os dialogos so precisam escrever {nome}.
func nome_em(texto: String) -> String:
	return texto.replace("{nome}", nome).replace("{avo}", nome_avo)


# ------------------------------- Pesca -------------------------------

func forca_maxima() -> float:
	if vara.is_empty():
		return VARAS[&"bambu"].forca
	return VARAS[vara].forca


func tem_vara() -> bool:
	return not vara.is_empty()


## O primeiro dia da vila (fase 2) ensina o acude: so sai tilapia, que e
## calma. O tutorial do rio (fase 1) tem roteiro proprio, nao passa por aqui.
func tutorial() -> bool:
	return fase == 2 and dia == 1


func sortear_especie(forca: float, camarao: bool) -> Especie:
	if tutorial():
		return especie(&"Tilápia")

	var especial: Especie = null
	for e in especies:
		if e.raridade == Especie.Raridade.ESPECIAL and e.alcancavel(forca):
			especial = e
	var chance: float = CHANCE_ESPECIAL * (2.0 if camarao else 1.0)
	if especial and dia >= DIA_ESPECIAL and randf() < chance:
		return especial

	var candidatas: Array[Especie] = []
	var pesos: Array[float] = []
	for e in especies:
		if e.raridade != Especie.Raridade.ESPECIAL and e.alcancavel(forca):
			candidatas.append(e)
			var mult: float = 2.0 if camarao and e.raridade != Especie.Raridade.COMUM else 1.0
			pesos.append(PESO_RARIDADE[e.raridade] * mult)
	if candidatas.is_empty():
		return especie(&"Tilápia")

	var total: float = 0.0
	for p in pesos:
		total += p
	var r: float = randf() * total
	for i in candidatas.size():
		r -= pesos[i]
		if r <= 0.0:
			return candidatas[i]
	return candidatas[-1]


## Peso do peixe. A forca do arremesso so da a tendencia: o peso sai sorteado
## em volta dela, com o espalhamento da especie (Especie.desvio_peso), e por
## isso o mesmo arremesso rende pesos diferentes. Arremessos no alto da faixa
## ainda podem render um exemplar trofeu, acima do peso_max da especie; a isca
## de camarao dobra essa chance.
func sortear_peso(e: Especie, forca: float, camarao: bool = false) -> float:
	var centro: float = e.fracao(forca)
	var t: float = clampf(centro + randfn(0.0, e.desvio_peso), 0.0, 1.0)
	var peso: float = lerpf(e.peso_min, e.peso_max, t)

	var chance: float = e.chance_trofeu * (2.0 if camarao else 1.0)
	if centro >= Especie.FRACAO_TROFEU and randf() < chance:
		peso = e.peso_max * (1.0 + randf_range(0.1, maxf(e.bonus_trofeu, 0.1)))

	return arredondar_peso(peso)


## Peixe de menos de 1 kg arredonda nas dezenas de grama (o lambari pesa uns
## 50 g); dali pra cima, nos 100 g.
static func arredondar_peso(peso: float) -> float:
	if peso < 1.0:
		return maxf(roundf(peso * 100.0) / 100.0, 0.01)
	return roundf(peso * 10.0) / 10.0


## O peso como aparece na tela: "50 g" ou "1,4 kg".
static func texto_peso(peso: float) -> String:
	if peso < 1.0:
		return "%d g" % roundi(peso * 1000.0)
	return "%s kg" % C3.num(peso).replace(".", ",")


func especie(nome: StringName) -> Especie:
	for e in especies:
		if StringName(e.nome) == nome:
			return e
	return null


## Locais que ja podem aparecer no mapa, cada um com o proprio id junto.
func locais_abertos() -> Array[Dictionary]:
	var abertos: Array[Dictionary] = []
	for id: StringName in LOCAIS:
		var dados: Dictionary = LOCAIS[id]
		if not dados.oculto:
			var item: Dictionary = dados.duplicate()
			item["id"] = id
			abertos.append(item)
	return abertos


func cena_do_local(id: StringName) -> String:
	return LOCAIS[id].cena if LOCAIS.has(id) else ""


func cansado() -> bool:
	return energia <= 0.0


func gastar_energia(valor: float) -> void:
	energia = maxf(energia - valor, 0.0)


## Gasta a energia do lancamento e devolve os bonus que valem para ele.
func usar_lancamento(forca: float) -> Dictionary:
	gastar_energia(ENERGIA_LANCAMENTO + ENERGIA_POR_FORCA * forca / 100.0)
	var ativos: Dictionary = {}
	for item in estoque:
		ativos[item] = estoque[item] > 0
		if estoque[item] > 0:
			estoque[item] -= 1
	return ativos


## Devolve true se o peso bateu o recorde da especie.
func registrar_captura(e: Especie, peso: float) -> bool:
	var valor: int = e.valor_para(peso)
	balde.append({"especie": e, "peso": peso, "valor": valor})
	total_peixes += 1
	var registro: Dictionary = colecao.get(e.nome, {"quantidade": 0, "recorde_kg": 0.0})
	var recorde: bool = registro.quantidade > 0 and peso > registro.recorde_kg
	registro.quantidade += 1
	registro.recorde_kg = maxf(registro.recorde_kg, peso)
	colecao[e.nome] = registro
	peixe_capturado.emit(e, peso, valor)
	return recorde


# ------------------------------- Hub -------------------------------

## Quanto este comprador paga por um peixe do balde, ja com a especialidade
## dele e o relacionamento de agora.
func preco_de(comprador: StringName, peixe: Dictionary) -> int:
	var dados: Dictionary = COMPRADORES[comprador]
	var fator: float = dados.base * dados.especialidade.get(peixe.especie.nome, 1.0)
	fator *= 1.0 + BONUS_RELACAO * relacao[comprador]
	return maxi(1, roundi(peixe.valor * fator))


## Vende o balde para um comprador e devolve o que saiu, cada item com o preco
## que ele pagou. Com guardar_jundia, um jundia fica para a Dona Marlene.
func vender_balde_para(comprador: StringName, guardar_jundia: bool = false) -> Array[Dictionary]:
	var vendidos: Array[Dictionary] = []
	var guardados: Array[Dictionary] = []
	for peixe in balde:
		if guardar_jundia and guardados.is_empty() and _serve_para_marlene(peixe.especie):
			guardados.append(peixe)
			continue
		var pago: int = preco_de(comprador, peixe)
		var registro: Dictionary = peixe.duplicate()
		registro["pago"] = pago
		vendidos.append(registro)
		_somar_dinheiro(pago)
		total_vendido += pago
	balde = guardados
	return vendidos


# --------------------------- Relacionamento ---------------------------

## Pedido da vez de um comprador, ou {} quando ja cumpriu todos.
func missao_ativa(comprador: StringName) -> Dictionary:
	var nivel: int = relacao[comprador]
	var lista: Array = MISSOES[comprador]
	return lista[nivel] if nivel < lista.size() else {}


## Peixes do balde que servem para o pedido da vez.
func _peixes_do_pedido(comprador: StringName) -> Array[int]:
	var indices: Array[int] = []
	var pedido: Dictionary = missao_ativa(comprador)
	if pedido.is_empty():
		return indices
	for i in balde.size():
		if balde[i].especie.nome == pedido.especie and balde[i].peso >= pedido.kg_min:
			indices.append(i)
			if indices.size() == pedido.n:
				break
	return indices


func pode_entregar(comprador: StringName) -> bool:
	var pedido: Dictionary = missao_ativa(comprador)
	return not pedido.is_empty() and _peixes_do_pedido(comprador).size() == pedido.n


## Entrega o pedido: tira os peixes do balde, sobe o nivel e paga a gorjeta.
## Devolve {nivel, premio}; nivel 0 significa que nao deu para entregar.
func entregar_missao(comprador: StringName) -> Dictionary:
	if not pode_entregar(comprador):
		return {"nivel": 0, "premio": 0}
	var indices: Array[int] = _peixes_do_pedido(comprador)
	indices.reverse()  # de tras para a frente, para os indices nao andarem
	for i in indices:
		balde.remove_at(i)
	var nivel: int = relacao[comprador] + 1
	relacao[comprador] = nivel
	var premio: int = PREMIO_MISSAO[mini(nivel - 1, PREMIO_MISSAO.size() - 1)]
	_somar_dinheiro(premio)
	return {"nivel": nivel, "premio": premio}


## Quanto este comprador paga a mais que o normal, em porcentagem, para mostrar
## na conversa.
func bonus_em_porcento(comprador: StringName) -> int:
	return roundi((COMPRADORES[comprador].base * (1.0 + BONUS_RELACAO * relacao[comprador]) - 1.0) * 100.0)


func disponivel(dia_minimo: int) -> bool:
	return dia >= dia_minimo


# ------------------------------ Tutorial ------------------------------

## Zera o que o tutorial anota, para quem comeca de novo pela tela inicial.
func comecar_tutorial() -> void:
	objetivos_feitos.clear()
	volta_do_rio = false
	tomou_cafe = false
	teimoso_solto = false
	teimoso_reencontrado = false
	diario.clear()
	colecao.clear()
	balde.clear()
	total_peixes = 0
	estoque = {&"camarao": 0, &"cafezinho": 0, &"modao": 0}
	vara = &""


func concluir(id: StringName) -> void:
	if id in objetivos_feitos:
		return
	objetivos_feitos.append(id)
	objetivo_concluido.emit(id)


func feito(id: StringName) -> bool:
	return id in objetivos_feitos


func especies_do_rio_faltando() -> Array[String]:
	var faltam: Array[String] = []
	for nome_especie in ESPECIES_DO_RIO:
		if not colecao.has(nome_especie):
			faltam.append(nome_especie)
	return faltam


## Confere os dois objetivos de pesca depois de cada peixe.
func conferir_pesca_do_rio() -> void:
	if especies_do_rio_faltando().is_empty():
		concluir(&"especies")
	if total_peixes >= PEIXES_DO_RIO:
		concluir(&"peixes")


func pesca_do_rio_completa() -> bool:
	return feito(&"especies") and feito(&"peixes")


func texto_objetivo(o: Dictionary) -> String:
	match o.id:
		&"especies":
			var pegas: int = ESPECIES_DO_RIO.size() - especies_do_rio_faltando().size()
			return o.texto % [pegas, ESPECIES_DO_RIO.size()]
		&"peixes":
			return o.texto % [PEIXES_DO_RIO, mini(total_peixes, PEIXES_DO_RIO), PEIXES_DO_RIO]
	return o.texto


func comprar_vara(id: StringName) -> bool:
	var v: Dictionary = VARAS[id]
	if id in varas_compradas or dinheiro < v.preco or not disponivel(v.dia):
		return false
	_somar_dinheiro(-v.preco)
	varas_compradas.append(id)
	if forca_maxima() <= v.forca or vara.is_empty():
		vara = id
	return true


func comprar_item(id: StringName) -> bool:
	var item: Dictionary = ITENS[id]
	if dinheiro < item.preco or not disponivel(item.dia):
		return false
	_somar_dinheiro(-item.preco)
	estoque[id] += item.quantidade
	return true


# ------------------------------- Obras -------------------------------

func obra_paga(id: StringName) -> bool:
	return id in obras_pagas


## A venda so entra na lista depois que a casa esta de pe.
func obra_liberada(id: StringName) -> bool:
	return id == &"casa" or obra_paga(&"casa")


func pagar_obra(id: StringName) -> bool:
	var obra: Dictionary = OBRAS[id]
	if obra_paga(id) or not obra_liberada(id) or dinheiro < obra.preco:
		return false
	_somar_dinheiro(-obra.preco)
	obras_pagas.append(id)
	return true


## O Jundia Gigante tambem serve de entrega: e jundia do mesmo jeito.
func _serve_para_marlene(e: Especie) -> bool:
	return e.nome.begins_with("Jundiá")


func tem_jundia_no_balde() -> bool:
	for peixe in balde:
		if _serve_para_marlene(peixe.especie):
			return true
	return false


func entregar_jundia() -> bool:
	for i in balde.size():
		if _serve_para_marlene(balde[i].especie):
			balde.remove_at(i)
			jundia_entregue = true
			return true
	return false


func fase_concluida() -> bool:
	return obra_paga(&"casa") and jundia_entregue


func dormir() -> void:
	dia += 1
	energia = ENERGIA_MAX


func minutos_jogados() -> float:
	return (Time.get_ticks_msec() - inicio_ms) / 60000.0


func _somar_dinheiro(valor: int) -> void:
	dinheiro += valor
	dinheiro_mudou.emit(dinheiro)
