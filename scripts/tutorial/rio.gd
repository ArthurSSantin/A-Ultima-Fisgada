extends CenaDePesca

## Cena 5 do tutorial: a pescaria de dentro do bote, parado no meio do rio.
##
## E a mesma cena de pesca do acude (scripts/acude.gd), com o roteiro por cima:
##   - o primeiro lance tem a beliscada do lambari e quem morde e o Teimoso;
##   - depois do Teimoso o vo tira o butiazinho, o neto pede, ganha um
##     cafezinho no lugar: e o primeiro boost (zona verde maior);
##   - o vo comenta cada especie na primeira vez que ela sai;
##   - so da para ir embora com os dois objetivos de pesca cumpridos: um peixe
##     de cada especie do rio e 8 peixes ao todo. Especie que falta aparece
##     mais, para o tutorial nao empacar na sorte.
## A energia nao gasta: no tutorial ninguem cansa.

const CENA_SUBIDA: String = "res://scenes/tutorial/Subida.tscn"
const TEIMOSO: StringName = &"Jundiá filhote"
## Lances do cafezinho que o vo da.
const CAFEZINHOS: int = 4
## Depois de tantos peixes sem especie nova, a proxima e uma que falta.
const PACIENCIA: int = 2

const REPETIDOS: Array[String] = [
	"Mais um.",
	"Esse é dos bons.",
	"Hoje tu tá com sorte, hein.",
	"Vou ter que pedir pra tu me ensinar.",
	"Bota no balde.",
]

var _teimoso_pescado: bool = false
var _comentadas: Array[String] = []
var _desde_novo: int = 0
var _perguntou_casa: bool = false
var _cafe: Label
## O vo do bote nas poses do butia (folha de 5 quadros); troca com o VoSentado.
var _vo_butia: Sprite2D
const POSE: Dictionary = {&"bolso": 0, &"garrafa": 1, &"gole": 2, &"termica": 3, &"entrega": 4}


func _ready() -> void:
	super._ready()
	Partida.vara = &"bambu"
	_placar.visible = false
	for filho in $UI.get_children():
		if filho is BarraEnergia:
			filho.visible = false
	var quadro := QuadroObjetivos.new()
	quadro.a_direita = true
	add_child(quadro)
	_cafe = Label.new()
	var fonte := SystemFont.new()
	fonte.font_names = PackedStringArray(["Arial"])
	fonte.font_weight = 700
	_cafe.add_theme_font_override("font", fonte)
	_cafe.add_theme_font_size_override("font_size", 17)
	_cafe.add_theme_color_override("font_color", Color(1.0, 0.86, 0.6))
	_cafe.add_theme_color_override("font_outline_color", Color(0.2, 0.1, 0.05))
	_cafe.add_theme_constant_override("outline_size", 5)
	_cafe.position = Vector2(1000, 670)
	$UI.add_child(_cafe)
	var sentado: Sprite2D = $Jogo/VoSentado
	_vo_butia = Sprite2D.new()
	_vo_butia.texture = load("res://assets/sprites/tutorial/personagens/vo_butia.png")
	_vo_butia.hframes = 5
	_vo_butia.centered = false
	_vo_butia.position = sentado.position + Vector2(0, -20)
	_vo_butia.visible = false
	sentado.add_sibling(_vo_butia)
	_intro.call_deferred()


func _process(delta: float) -> void:
	Partida.energia = Partida.ENERGIA_MAX
	var cafes: int = Partida.estoque[&"cafezinho"]
	_cafe.visible = cafes > 0
	_cafe.text = "Cafezinho do vô: %d lance%s" % [cafes, "" if cafes == 1 else "s"]
	super._process(delta)


func _intro() -> void:
	await _caixa.falar("", ["No meio do rio o vô recolhe os remos, e o bote fica rodando devagarinho."])
	await _caixa.falar("Vô", ["Minhoca no anzol. Enfia ela inteira, não deixa sobrar pontinha, senão o lambari come e vai embora rindo de ti."])
	await _caixa.falar("{nome}", ["Eca, vô."])
	await _caixa.falar("Vô", ["Eca nada."])
	await _caixa.falar("Vô", ["Segura ESPAÇO pra dar força e solta pra jogar. Não muito longe. O peixe tá ali."])


# ------------------------------------------------------------- o roteiro

func _escolher_especie(f: float) -> Especie:
	if not _teimoso_pescado:
		return Partida.especie(TEIMOSO)
	var faltam: Array[String] = Partida.especies_do_rio_faltando()
	faltam.erase(String(TEIMOSO))
	if not faltam.is_empty() and (_desde_novo >= PACIENCIA or randf() < 0.35):
		return Partida.especie(StringName(faltam.pick_random()))
	var e: Especie = super._escolher_especie(f)
	return e if e else Partida.especie(&"Lambari")


func _tem_beliscada() -> bool:
	if not _teimoso_pescado:
		return true  # o primeiro peixe ensina: o lambari belisca, o jundia morde
	return randf() < 0.4


func _texto_da_dica() -> String:
	match estado:
		0:
			if not _teimoso_pescado:
				return "Vô: Segura ESPAÇO pra dar força, e solta pra jogar."
			return ""
		1, 2:
			if _beliscando:
				return "Vô: Calma. Isso aí é lambari roubando. Espera afundar de verdade."
			return "Vô: Agora espera."
		3:
			return "Vô: Agora, guri! Puxa! (ESPAÇO)"
		4:
			return "Vô: Segura firme! Não precisa brigar com ele.\n(segure ESPAÇO pra subir a barra verde, solte pra descer)"
		6:
			return "Vô: Escapou. Joga de novo."
	return ""


func _depois_da_captura() -> void:
	await _esperar(1.6)
	if estado != 5:
		return
	_aviso.text = ""
	var nova: bool = especie != null and not especie.nome in _comentadas
	_desde_novo = 0 if nova else _desde_novo + 1
	if especie and StringName(especie.nome) == TEIMOSO and not _teimoso_pescado:
		await _primeiro_peixe()
		await _butiazinho()
	else:
		await _outro_peixe()
	Partida.conferir_pesca_do_rio()
	if Partida.pesca_do_rio_completa():
		await _fim_da_pescaria()
	if estado == 5 and not _saindo:
		estado = 7


func _primeiro_peixe() -> void:
	_teimoso_pescado = true
	_comentadas.append(String(TEIMOSO))
	await _caixa.falar("{nome}", ["Vô! Vô, eu peguei!"])
	await _caixa.falar("Vô", ["Pera, pera... olha o bigode. É jundiá."])
	await _caixa.falar("{nome}", ["Ele é pequeno."])
	await _caixa.falar("Vô", ["É filhote. Cuidado com o ferrão do lado, que pica e dói o dia inteiro."])
	await _caixa.falar("Vô", ["Olha o rabo dele. Falta um pedaço. Já brigou com alguém, esse aí."])
	await _caixa.falar("{nome}", ["Ele é teimoso."])
	await _caixa.falar("Vô", ["Pois então é Teimoso o nome dele."])

	var i: int = await _caixa.escolher("", "E o Teimoso?", ["Soltar o Teimoso", "Levar pra casa"])
	if i != 1:
		Partida.teimoso_solto = true
		if not Partida.balde.is_empty():
			Partida.balde.pop_back()
		_peixe.visible = false
		await _caixa.falar("Vô", ["Vai lá, cresce. Daqui uns anos a gente se vê."])
	else:
		await _caixa.falar("Vô", ["Tá bom. Mas jundiá desse tamanho a vó não vai nem conseguir limpar."])
	Partida.diario.append("Jundiá, 200 g, com o vô. Faltava um pedaço do rabo. O nome dele é Teimoso.")


## O primeiro boost: o neto quer provar o butiazinho e ganha um cafezinho. O vo
## faz as poses de verdade (tira a garrafinha, da o gole, abre a termica e
## entrega o copinho) e os dois aparecem de perto.
func _butiazinho() -> void:
	_posar(&"bolso")
	await _esperar(0.5)
	_posar(&"garrafa")
	await _caixa.falar("", ["O vô tira uma garrafinha do bolso da jaqueta..."])
	_posar(&"gole")
	await _esperar(0.9)
	await _caixa.falar("", ["...e dá um gole."])
	_posar(&"garrafa")
	await _caixa.falar("{nome}", ["Que que é isso, vô?"])
	await _de_perto("res://assets/sprites/tutorial/cenarios/butia_perto.png", "Vô", ["Butiazinho."])
	await _caixa.falar("{nome}", ["Deixa eu provar?"])
	await _caixa.falar("Vô", ["Tá loco. Isso aqui é remédio de véio."])
	await _caixa.falar("{nome}", ["Remédio pra quê?"])
	await _caixa.falar("Vô", ["Pro frio. Pra dor nas costas. Pra quando a vó reclama."])
	await _caixa.falar("{nome}", ["Ah, vô, só um pouquinho..."])
	await _caixa.falar("Vô", ["Não."])
	_posar(&"bolso")
	await _esperar(0.4)
	_posar(&"termica")
	await _caixa.falar("", ["Ele guarda a garrafinha e abre a garrafa térmica."])
	_posar(&"entrega")
	await _caixa.falar("Vô", ["Toma. Isso aqui é que é bom. Café da vó."])
	await _caixa.falar("{nome}", ["Tá quente!"])
	await _caixa.falar("Vô", ["Assopra. Café deixa a gente esperto. Tu vai ver o peixe antes dele te ver."])
	Partida.estoque[&"cafezinho"] += CAFEZINHOS
	await _de_perto("res://assets/sprites/tutorial/cenarios/cafezinho_perto.png", "",
		["Ganhou: Cafezinho do vô. A barra verde fica maior nos próximos %d lances." % CAFEZINHOS])
	_posar(&"")
	await _caixa.falar("Vô", ["E não conta pra vó que eu te dei café puro."])


## Troca o vo sentado pelo quadro da pose; pose vazia volta ao normal.
func _posar(pose: StringName) -> void:
	var sentado: Sprite2D = $Jogo/VoSentado
	sentado.visible = pose.is_empty()
	_vo_butia.visible = not pose.is_empty()
	if not pose.is_empty():
		_vo_butia.frame = POSE[pose]


## A imagem grande no meio da tela enquanto a fala passa (como os posteres).
func _de_perto(caminho: String, quem: String, paginas: Array) -> void:
	var camada := CanvasLayer.new()
	camada.layer = 9
	add_child(camada)
	var quadro := TextureRect.new()
	quadro.texture = load(caminho)
	quadro.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	quadro.position = Vector2(640 - quadro.texture.get_width() * 0.5, 80)
	camada.add_child(quadro)
	await _caixa.falar(quem, paginas)
	camada.queue_free()


func _outro_peixe() -> void:
	var nome_especie: String = especie.nome if especie else ""
	if nome_especie in _comentadas:
		await _caixa.falar("Vô", [REPETIDOS.pick_random()])
		return
	_comentadas.append(nome_especie)
	match nome_especie:
		"Lambari":
			await _caixa.falar("Vô", ["Lambari. Anda tudo junto, num bolo. Onde tem um tem cinquenta."])
			await _caixa.falar("{nome}", ["Ele é pequeninho."])
			await _caixa.falar("Vô", ["É. Mas é ele que rouba tua minhoca o dia inteiro.", "E serve de isca pra peixe grande. A traíra adora."])
		"Cará":
			await _caixa.falar("Vô", ["Cará. Cuidado com a espinha das costas, ó, que fura."])
			await _caixa.falar("Vô", ["Esse é bicho de família. O pai e a mãe ficam cuidando dos filhotes, nadando em volta.", "Se tu chega perto, eles vêm pra cima."])
			await _caixa.falar("{nome}", ["Que nem a vó."])
			await _caixa.falar("Vô", ["(rindo) Que nem a vó."])
		"Joaninha":
			await _caixa.falar("{nome}", ["Vô! Olha a cor dele!"])
			await _caixa.falar("Vô", ["Joaninha. Faz tempo que eu não pego uma."])
			await _caixa.falar("Vô", ["Fica entocada nas pedras, esperando passar coisa pra comer. Peixe caçador, pequeno e brabo.", "E tem uma coisa: nunca vi duas da mesma cor. Cada uma é de um jeito."])
			await _caixa.falar("{nome}", ["Posso levar pra vó ver?"])
			await _caixa.falar("Vô", ["Pode. Ela vai dizer que é bonita demais pra comer."])
		_:
			await _caixa.falar("Vô", ["Olha só."])


func _fim_da_pescaria() -> void:
	if not _perguntou_casa:
		_perguntou_casa = true
		await _caixa.falar("Vô", ["Bah. Tá bom por hoje."])
		await _caixa.falar("{nome}", ["Já?"])
		await _caixa.falar("Vô", ["A vó vai querer limpar peixe antes do almoço. E o Alexandre tá lá amarrado esperando."])
	var i: int = await _caixa.escolher("Vô", "E aí?", ["Mais um, vô!", "Bora pra casa"])
	if i == 1:
		_saindo = true
		Partida.volta_do_rio = true
		await _caixa.falar("Vô", ["Bora."])
		get_tree().change_scene_to_file.call_deferred(CENA_SUBIDA)
	elif _perguntou_casa:
		await _caixa.falar("Vô", ["Só mais um, então."])


func _tocar(som: String) -> void:
	var p := AudioStreamPlayer.new()
	p.stream = load("res://assets/sons/%s.wav" % som)
	add_child(p)
	p.play()
	p.finished.connect(p.queue_free)
