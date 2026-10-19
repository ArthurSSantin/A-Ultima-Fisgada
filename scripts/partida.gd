extends Node

## Estado da partida que sobrevive a troca de cena (autoload "Partida").
## Cais e hub (a Loja de Pesca) leem e escrevem aqui. O nome nao e "Jogo" para nao confundir com
## o no $Jogo da cena CaisTeste.
##
## Os numeros sao os da Fase 1 aprovados depois do harness (docs/escopo-beta.md,
## secao 5, e tools/harness/harness.mjs, cenario "ajustada").

signal peixe_capturado(especie: Especie, peso: float, valor: int)
signal dinheiro_mudou(valor: int)

## Energia do dia. Lancar gasta (mais quanto mais longe) e brigar com o peixe
## tambem; zerou, Tiago cansa e volta para a Loja de Pesca. Calibrado no
## tools/harness/harness.mjs para uns 8 a 10 lancamentos por dia e para o dia 1
## nao render o bastante para comprar a Vara de Fibra na manha do dia 2.
const ENERGIA_MAX: float = 100.0
const ENERGIA_LANCAMENTO: float = 6.0
const ENERGIA_POR_FORCA: float = 3.0
const ENERGIA_LUTA_POR_S: float = 0.5
const TELHADO: int = 800
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

## Consumiveis da loja do Seu Aldo. "quantidade" e quanto vem por compra.
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

const ESPECIES_DIR: String = "res://dados/especies/"

var dinheiro: int = DINHEIRO_INICIAL
var dia: int = 1
var fase: int = 1
var energia: float = ENERGIA_MAX
## Vara em uso; vazia ate comprar a primeira.
var vara: StringName = &""
var varas_compradas: Array[StringName] = []
## Quantos lancamentos ainda tem de cada consumivel.
var estoque: Dictionary = {&"camarao": 0, &"cafezinho": 0, &"modao": 0}
var telhado_pago: bool = false
var robalo_entregue: bool = false
## Para a fala de abertura so aparecer uma vez.
var prologo_visto: bool = false
var cais_visitado: bool = false
## Onde o Player aparece ao entrar no hub; o cais muda para perto da porta.
var hub_x: float = 640.0

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
	for arquivo in DirAccess.get_files_at(ESPECIES_DIR):
		# No build exportado os .tres aparecem com sufixo .remap.
		var caminho: String = ESPECIES_DIR + arquivo.trim_suffix(".remap")
		if caminho.ends_with(".tres"):
			var especie: Especie = load(caminho)
			if especie.fase == fase:
				especies.append(especie)


# ------------------------------- Pesca -------------------------------

func forca_maxima() -> float:
	if vara.is_empty():
		return VARAS[&"bambu"].forca
	return VARAS[vara].forca


func tem_vara() -> bool:
	return not vara.is_empty()


## Dia 1 e o tutorial: so sai parati, que e calmo.
func tutorial() -> bool:
	return dia == 1


func sortear_especie(forca: float, camarao: bool) -> Especie:
	if tutorial():
		return especie(&"Parati")

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
		return especie(&"Parati")

	var total: float = 0.0
	for p in pesos:
		total += p
	var r: float = randf() * total
	for i in candidatas.size():
		r -= pesos[i]
		if r <= 0.0:
			return candidatas[i]
	return candidatas[-1]


## Peso pela forca dentro da faixa da especie, com um pouco de variacao.
func sortear_peso(e: Especie, forca: float) -> float:
	var t: float = clampf(e.fracao(forca) + randfn(0.0, 0.1), 0.0, 1.0)
	return roundf(lerpf(e.peso_min, e.peso_max, t) * 10.0) / 10.0


func especie(nome: StringName) -> Especie:
	for e in especies:
		if StringName(e.nome) == nome:
			return e
	return null


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

## Vende o balde e devolve o que foi vendido. Com guardar_robalo, um robalo
## fica no balde para entregar a Dona Marlene.
func vender_balde(guardar_robalo: bool = false) -> Array[Dictionary]:
	var vendidos: Array[Dictionary] = []
	var guardados: Array[Dictionary] = []
	for peixe in balde:
		if guardar_robalo and guardados.is_empty() and peixe.especie.nome == "Robalo":
			guardados.append(peixe)
			continue
		vendidos.append(peixe)
		_somar_dinheiro(peixe.valor)
		total_vendido += peixe.valor
	balde = guardados
	return vendidos


func disponivel(dia_minimo: int) -> bool:
	return dia >= dia_minimo


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


func pagar_telhado() -> bool:
	if telhado_pago or dinheiro < TELHADO:
		return false
	_somar_dinheiro(-TELHADO)
	telhado_pago = true
	return true


func tem_robalo_no_balde() -> bool:
	for peixe in balde:
		if peixe.especie.nome == "Robalo":
			return true
	return false


func entregar_robalo() -> bool:
	for i in balde.size():
		if balde[i].especie.nome == "Robalo":
			balde.remove_at(i)
			robalo_entregue = true
			return true
	return false


func fase_concluida() -> bool:
	return telhado_pago and robalo_entregue


func dormir() -> void:
	dia += 1
	energia = ENERGIA_MAX


func minutos_jogados() -> float:
	return (Time.get_ticks_msec() - inicio_ms) / 60000.0


func _somar_dinheiro(valor: int) -> void:
	dinheiro += valor
	dinheiro_mudou.emit(dinheiro)
