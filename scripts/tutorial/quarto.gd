extends CenaTutorial

## Cena 1 do tutorial: o quarto do neto, 2002, 5h17. A abertura e automatica:
## o neto acordando (palpebras abrindo no teto), as batidas do vo na porta e
## as primeiras falas em legenda, uns dez segundos sem precisar apertar nada. Depois o neto anda pelo quarto e so sai
## com a vara de bambu. Os posteres abrem de perto quando ele examina.

const CENA_SEGUINTE: String = "res://scenes/tutorial/Cozinha.tscn"
const PERTO: String = "res://assets/sprites/tutorial/cenarios/"

## Abertura no escuro: (segundo, som ou "", quem, fala).
const ABERTURA: Array = [
	[0.3, "batida", "", ""],
	[1.4, "", "Vô", "{nome}. Ô, {nome}."],
	[3.8, "batida", "", ""],
	[4.6, "", "{nome}", "Hmmm..."],
	[6.4, "", "Vô", "O rio não espera ninguém, não."],
]
const DURACAO_ABERTURA: float = 9.2

var _carinhos: int = 0
var _palpebra_cima: TextureRect
var _palpebra_baixo: TextureRect

@onready var _maumau: Sprite2D = $Estacoes/MauMau/Visual
@onready var _vara: Node2D = $Estacoes/Vara
@onready var _vo_na_porta: Sprite2D = $VoNaPorta


func _ao_entrar() -> void:
	Partida.comecar_tutorial()
	QuadroObjetivos.zerar()
	await escurecer(true, 0.01)  # comeca no escuro: so a voz do vo atras da porta
	await _abertura_no_escuro()
	await falar("{nome}", ["Já vou, vô..."])
	await falar("Vô", ["Pega a vara, que eu tô lá na cozinha.", "E não acorda o gato, que ele fica brabo."])
	var sai := create_tween()
	sai.tween_property(_vo_na_porta, "modulate:a", 0.0, 0.6)
	await sai.finished
	_vo_na_porta.visible = false


## A abertura: o neto acordando. Escuro, as batidas, as palpebras abrem um
## pouco no teto embacado, piscam, abrem de vez, o teto fica nitido e desliza
## pra cima revelando o quarto. As falas do vo aparecem sozinhas, em legenda.
func _abertura_no_escuro() -> void:
	var camada := CanvasLayer.new()
	camada.layer = 31
	add_child(camada)
	var olho := Control.new()
	olho.size = Vector2(1280, 720)
	camada.add_child(olho)
	var embacado := TextureRect.new()
	embacado.texture = load(PERTO + "acordar_teto_embacado.png")
	olho.add_child(embacado)
	var nitido := TextureRect.new()
	nitido.texture = load(PERTO + "acordar_teto.png")
	nitido.modulate.a = 0.0
	olho.add_child(nitido)
	_palpebra_cima = TextureRect.new()
	_palpebra_cima.texture = load(PERTO + "palpebra.png")
	olho.add_child(_palpebra_cima)
	_palpebra_baixo = TextureRect.new()
	_palpebra_baixo.texture = _palpebra_cima.texture
	_palpebra_baixo.flip_v = true
	olho.add_child(_palpebra_baixo)
	_abrir_olho(0.0)
	var piscar := create_tween()
	piscar.tween_interval(2.4)
	piscar.tween_method(_abrir_olho, 0.0, 0.25, 0.7)
	piscar.tween_interval(0.9)
	piscar.tween_method(_abrir_olho, 0.25, 0.0, 0.25)
	piscar.tween_interval(0.35)
	piscar.tween_method(_abrir_olho, 0.0, 0.6, 1.0)
	piscar.tween_interval(0.5)
	piscar.tween_method(_abrir_olho, 0.6, 1.0, 1.2)
	piscar.parallel().tween_property(nitido, "modulate:a", 1.0, 1.4)
	var legenda := Label.new()
	var fonte := SystemFont.new()
	fonte.font_names = PackedStringArray(["Arial"])
	legenda.add_theme_font_override("font", fonte)
	legenda.add_theme_font_size_override("font_size", 26)
	legenda.add_theme_color_override("font_color", Color(0.95, 0.92, 0.85))
	legenda.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	legenda.size = Vector2(1280, 60)
	legenda.position = Vector2(0, 330)
	camada.add_child(legenda)
	var hora := Label.new()
	hora.add_theme_font_override("font", fonte)
	hora.add_theme_font_size_override("font_size", 18)
	hora.add_theme_color_override("font_color", Color(0.6, 0.58, 0.55))
	hora.text = "2002. Cinco e dezessete da manhã."
	hora.position = Vector2(40, 660)
	camada.add_child(hora)
	var agora: float = 0.0
	for passo in ABERTURA:
		await esperar(passo[0] - agora)
		agora = passo[0]
		if not String(passo[1]).is_empty():
			tocar(passo[1])
		if not String(passo[3]).is_empty():
			var quem: String = Partida.nome_em(passo[2])
			legenda.text = Partida.nome_em("%s: %s" % [quem, passo[3]])
			legenda.modulate.a = 0.0
			create_tween().tween_property(legenda, "modulate:a", 1.0, 0.3)
	await esperar(DURACAO_ABERTURA - agora)
	# o olho ja esta aberto: as palpebras saem de cena, a cortina sai de tras e
	# o neto abaixa a cabeca: o teto sobe um pouco e some, o quarto aparece
	_palpebra_cima.visible = false
	_palpebra_baixo.visible = false
	await escurecer(false, 0.01)
	var some := create_tween()
	some.tween_property(legenda, "modulate:a", 0.0, 0.4)
	some.parallel().tween_property(hora, "modulate:a", 0.0, 0.4)
	some.parallel().tween_property(olho, "position:y", -180.0, 1.2).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	some.parallel().tween_property(olho, "modulate:a", 0.0, 1.2).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	await some.finished
	camada.queue_free()


## Abertura das palpebras: 0 fechado, 1 aberto. Cada uma tem 424 px de
## altura; fechadas, elas se cruzam no meio da tela.
func _abrir_olho(abertura: float) -> void:
	var altura: float = 424.0
	_palpebra_cima.position.y = -altura * abertura
	_palpebra_baixo.position.y = 720.0 - altura + altura * abertura


func _dica_atual() -> String:
	if not Partida.tem_vara():
		return "Setas andam, ESPAÇO examina. A vara de bambu tá perto da porta."
	return "A cozinha é pela porta da direita."


func _acao(nome: StringName) -> String:
	match nome:
		&"Cama": return "Olhar pela janela"
		&"MauMau": return "Falar com o MauMau"
		&"Fotos": return "Olhar as fotos"
		&"Vara": return "Pegar a vara de bambu"
		&"Prateleira": return "Mexer na prateleira"
		&"Porta": return "Ir para a cozinha"
		&"PosterPai", &"PosterCriciuma", &"PosterZeze", &"PosterLeonardo", &"PosterDjavan", \
				&"PosterPele", &"PosterLebron":
			return "Olhar o pôster"
	return "Olhar"


func _interagir(nome: StringName) -> void:
	match nome:
		&"Cama":
			await falar("", ["Lá fora ainda tá escuro. A neblina deitada em cima dos morros."])
		&"MauMau":
			await _maumau_()
		&"Fotos":
			await _fotos()
		&"PosterPai":
			await de_perto(load(PERTO + "poster_racionais_perto.png"), "", [
				"Era do pai. A mãe não deixava ele pendurar na sala, então ele pendurou aqui, quando o quarto ainda era dele.",
				"O vô nunca tirou.",
			])
		&"PosterZeze":
			await de_perto(load(PERTO + "poster_zeze_perto.png"), "", [
				"A vó canta \"É o Amor\" lavando a louça. Errando a letra.",
			])
		&"PosterLeonardo":
			await de_perto(load(PERTO + "poster_leonardo_perto.png"), "", [
				"Ganhou na rifa da festa da igreja. O vô diz que é música de corno.",
				"Mas canta junto.",
			])
		&"PosterDjavan":
			await de_perto(load(PERTO + "poster_djavan_perto.png"), "", [
				"Esse era da mãe. Ninguém nunca entendeu direito o que ele canta, mas é bonito.",
			])
		&"PosterCriciuma":
			await de_perto(load(PERTO + "poster_criciuma_perto.png"), "", [
				"Campeão da Copa do Brasil. O vô gritou tanto que ficou três dias sem voz.",
			])
		&"PosterPele":
			await de_perto(load(PERTO + "poster_pele_perto.png"), "", [
				"Pelé, na Copa de 70. O vô diz que viu ele jogar.",
			])
			await falar("{nome}", ["No rádio, vô. Tu ouviu no rádio."])
		&"PosterLebron":
			await de_perto(load(PERTO + "poster_lebron_perto.png"), "", [
				"Veio numa revista que o tio trouxe de Floripa. Um guri do colégio, lá dos Estados Unidos.",
				"Ninguém aqui sabe quem é. Ainda.",
			])
		&"Camisa":
			await de_perto(load(PERTO + "camisa_1991_perto.png"), "", [
				"A camisa de 91. Ainda fica grande. O vô diz que é pra crescer dentro dela.",
			])
		&"Prateleira":
			var i: int = await escolher("", "Na prateleira:", ["O toca-fitas", "O barquinho de madeira", "Deixar"])
			if i == 0:
				await falar("", ["O toca-fitas. Tem uma fita do Leandro & Leonardo enroscada lá dentro faz um mês."])
			elif i == 1:
				await falar("", ["O barquinho que o vô fez de um toco de canela. A vela é um pedaço de lençol velho."])
		&"Vara":
			await _pegar_vara()
		&"Porta":
			if not Partida.tem_vara():
				await falar("{nome}", ["Faltou a vara."])
			else:
				ir_para(CENA_SEGUINTE)


func _maumau_() -> void:
	var i: int = await escolher("MauMau", "O MauMau abre um olho só.", ["Fazer carinho", "Deixar ele dormir"])
	if i != 0:
		return
	_carinhos += 1
	var deitado: Texture2D = _maumau.texture
	_maumau.texture = load(BICHOS + "maumau_carinho.png")
	som("ronrom")
	var cabeca: Vector2 = _maumau.global_position + Vector2(48, -6)
	coracao(cabeca)
	balao("rrrrrr...", cabeca + Vector2(10, -70), 2.0)
	await esperar(2.2)
	_maumau.texture = deitado
	if _carinhos == 1:
		await falar("", ["O MauMau ronrona, se espreguiça e volta a dormir. Acordar, nem pensar."])


func _fotos() -> void:
	var i: int = await escolher("", "No criado-mudo e na parede:", ["A foto do pai e da mãe", "A foto com o vô", "Deixar"])
	if i == 0:
		await falar("", ["O pai de bigode e a mãe rindo de alguma coisa que ficou fora da foto."])
		var j: int = await escolher("", "", ["Olhar mais um pouco", "Deixar quieto"])
		if j == 0:
			await esperar(1.2)
			await falar("", ["..."])
			await falar("", ["{nome} ajeita o porta-retrato do jeitinho que a vó deixa."])
	elif i == 1:
		await falar("", ["{nome} pequeno, de boné, e o vô segurando um peixe quase do tamanho do menino."])
		await falar("{nome}", ["Vô, esse peixe era desse tamanho mesmo?"])
		await falar("Vô", ["Ô! Eu tô ouvindo daqui, hein!"])


func _pegar_vara() -> void:
	Partida.vara = &"bambu"
	_vara.visible = false
	Partida.concluir(&"vara")
	await falar("", ["A vara que o vô fez. Tem um nó torto bem no meio."])
	await falar("Vô", ["É ali que ela fica forte!"])
	await falar("{nome}", ["Como é que tu ouviu, vô?!"])
