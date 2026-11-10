class_name Colecao
extends CanvasLayer

## Tela da colecao: todas as especies do jogo, agrupadas por pesqueiro, com a
## quantidade pescada e o recorde de peso. A especie que o neto ainda nao
## pescou aparece so como sombra, com o nome escondido.
##
##     await Colecao.abrir_em(self)
##
## Monta os proprios nos, como o MapaLocais. A tecla C (acao "colecao"), ESC
## ou ESPACO fecham.

signal _fechou

const COR_FUNDO: Color = Color(0.04, 0.07, 0.14, 0.94)
const COR_PAINEL: Color = Color(0.09, 0.15, 0.24, 1.0)
const COR_TITULO: Color = Color(1.0, 0.82, 0.35)
const COR_TEXTO: Color = Color(0.93, 0.92, 0.86)
const COR_FRACO: Color = Color(0.62, 0.68, 0.74)

const TITULOS: Dictionary = {
	&"rio": "O rio, em 2002",
	&"acude": "Açude",
	&"foz": "Foz e Vila",
	&"arvoredo": "Arvoredo",
}

const COLUNA_X: float = 24.0
const COLUNA_LARGURA: float = 300.0
const COLUNA_ESPACO: float = 10.0
const TOPO: float = 74.0
const LINHA_ALTURA: float = 104.0
const CAIXA_PEIXE: Vector2 = Vector2(110.0, 64.0)

var _fechando: bool = false
var _fonte: SystemFont
var _negrito: SystemFont


static func abrir_em(dono: Node) -> void:
	var tela := Colecao.new()
	dono.add_child(tela)
	await tela._fechou
	tela.queue_free()


func _ready() -> void:
	layer = 14
	_fonte = SystemFont.new()
	_fonte.font_names = PackedStringArray(["Arial"])
	_negrito = SystemFont.new()
	_negrito.font_names = PackedStringArray(["Arial"])
	_negrito.font_weight = 700

	var fundo := ColorRect.new()
	fundo.color = COR_FUNDO
	fundo.size = Vector2(1280, 720)
	add_child(fundo)

	var grupos: Dictionary = {}
	for id in Partida.ORDEM_COLECAO:
		grupos[id] = []
	var total: int = 0
	var pegas: int = 0
	for e in Partida.todas_especies():
		var id: StringName = Partida.local_da_especie(e)
		if grupos.has(id):
			grupos[id].append(e)
			total += 1
			if Partida.colecao.has(e.nome):
				pegas += 1

	var titulo := _label(_negrito, 30, COR_TITULO)
	titulo.text = "Coleção"
	titulo.position = Vector2(COLUNA_X, 18.0)
	add_child(titulo)

	var contagem := _label(_negrito, 20, COR_TEXTO)
	contagem.text = "%d de %d espécies" % [pegas, total]
	contagem.position = Vector2(1280.0 - 360.0, 26.0)
	contagem.size = Vector2(330.0, 30.0)
	contagem.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	add_child(contagem)

	for i in Partida.ORDEM_COLECAO.size():
		var id: StringName = Partida.ORDEM_COLECAO[i]
		var lista: Array = grupos[id]
		lista.sort_custom(func(a: Especie, b: Especie) -> bool:
			return a.raridade < b.raridade or (a.raridade == b.raridade and a.forca_min < b.forca_min))
		_coluna(Vector2(COLUNA_X + i * (COLUNA_LARGURA + COLUNA_ESPACO), TOPO), id, lista)

	var dica := _label(_fonte, 14, COR_FRACO)
	dica.text = "C, ESC ou ESPAÇO fecha"
	dica.position = Vector2(COLUNA_X, 692.0)
	add_child(dica)


func _coluna(origem: Vector2, id: StringName, lista: Array) -> void:
	var cabeca := _label(_negrito, 19, COR_TITULO)
	cabeca.text = TITULOS.get(id, String(id))
	cabeca.position = origem
	add_child(cabeca)

	var aberto: bool = id == &"rio" or Partida.local_liberado(id)
	for k in lista.size():
		var e: Especie = lista[k]
		var y: float = origem.y + 34.0 + k * LINHA_ALTURA
		var painel := ColorRect.new()
		painel.color = COR_PAINEL
		painel.position = Vector2(origem.x, y)
		painel.size = Vector2(COLUNA_LARGURA, LINHA_ALTURA - 8.0)
		add_child(painel)

		var pescou: bool = Partida.colecao.has(e.nome)
		var textura: Texture2D = e.sprite if pescou else e.sombra
		if textura:
			var img := TextureRect.new()
			img.texture = textura
			img.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			img.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			img.position = painel.position + Vector2(8.0, (painel.size.y - CAIXA_PEIXE.y) * 0.5)
			img.size = CAIXA_PEIXE
			if not pescou:
				img.modulate = Color(0.25, 0.3, 0.38, 0.9)
			add_child(img)

		var nome := _label(_negrito, 17, COR_TEXTO if pescou else COR_FRACO)
		nome.position = painel.position + Vector2(CAIXA_PEIXE.x + 18.0, 14.0)
		nome.size = Vector2(COLUNA_LARGURA - CAIXA_PEIXE.x - 24.0, 22.0)
		nome.clip_text = true
		add_child(nome)

		var info := _label(_fonte, 14, COR_FRACO)
		info.position = painel.position + Vector2(CAIXA_PEIXE.x + 18.0, 40.0)
		info.size = Vector2(COLUNA_LARGURA - CAIXA_PEIXE.x - 24.0, 44.0)
		info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		add_child(info)

		if pescou:
			var r: Dictionary = Partida.colecao[e.nome]
			nome.text = e.nome
			info.text = "Pescados: %d\nRecorde: %s" % [r.quantidade, Partida.texto_peso(r.recorde_kg)]
		else:
			nome.text = "???"
			info.text = _pista(e) if aberto else "Lugar ainda não descoberto"


## Uma pista do que falta, sem dizer o nome do peixe.
func _pista(e: Especie) -> String:
	if e.raridade == Especie.Raridade.ESPECIAL:
		return "Dizem que existe..."
	if e.forca_min >= 60.0:
		return "Bem longe, no fundo"
	if e.forca_min >= 30.0:
		return "A meia distância"
	return "Perto da beira"


func _input(evento: InputEvent) -> void:
	if _fechando or evento.is_echo():
		return
	if evento.is_action_pressed(&"colecao") or evento.is_action_pressed(&"ui_cancel") \
			or evento.is_action_pressed(&"espaco"):
		get_viewport().set_input_as_handled()
		_fechando = true
		# Um quadro de folga: sem isso o ESPACO que fechou a tela ainda conta
		# como "acabou de apertar" na cena de baixo e ja interage com algo.
		await get_tree().process_frame
		_fechou.emit()


func _label(fonte: Font, tamanho: int, cor: Color) -> Label:
	var label := Label.new()
	label.add_theme_font_override("font", fonte)
	label.add_theme_font_size_override("font_size", tamanho)
	label.add_theme_color_override("font_color", cor)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label
