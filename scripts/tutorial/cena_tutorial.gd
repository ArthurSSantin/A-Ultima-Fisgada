class_name CenaTutorial
extends Node2D

## Base das cenas a pe do tutorial (fase 1): quarto, cozinha, terreiro e cais
## do rio. Cuida de andar, das estacoes, do nome que so aparece de perto, da
## caixa de dialogo, dos sons, dos baloes e da troca de cena. Cada cena so
## escreve as proprias falas, sobrescrevendo:
##
##   _ao_entrar()        o que acontece quando a cena abre (pode ser await)
##   _acao(nome)         o texto do aviso "[ESPACO] ..." de cada estacao
##   _interagir(nome)    o que a estacao faz (pode ser await)
##   _dica_atual()       a dica do canto de cima, se houver
##
## Uma estacao e um Node2D dentro de "Estacoes"; o filho "Nome" (Label) e a
## etiqueta, que fica escondida e so aparece quando o neto chega perto. E assim
## que os posteres mostram o nome sem precisar de letra legivel no desenho.

const SONS: String = "res://assets/sons/"
const BICHOS: String = "res://assets/sprites/tutorial/bichos/"
const CORACAO: Texture2D = preload("res://assets/sprites/tutorial/bichos/coracao.png")

## Ate onde o neto anda nesta cena.
@export var borda: Vector2 = Vector2(40.0, 1240.0)
## Gravacoes longas (CREDITOS_SONS.md): de onde ate onde tocar cada uma,
## [inicio em s, duracao em s, volume em dB].
const TRECHOS: Dictionary = {
	"latido": [10.9, 1.5, -2.0],        # dois latidos seguidos
	"ronrom": [3.6, 2.4, 0.0],
	"cavalo_bufo": [7.75, 0.9, -3.0],    # a bufada mais forte da gravacao
}

## Distancia, em pixels de tela, para uma estacao valer.
@export var alcance: float = 60.0

var _caixa: CaixaDialogo
var _perto: Node2D = null
var _ocupado: bool = false
var _saindo: bool = false

@onready var _player: Sprite2D = $Player
@onready var _mover: EightDir = $Player/OitoDirecoes
@onready var _estacoes: Node2D = $Estacoes
@onready var _prompt: Label = $UI/Prompt
@onready var _dica: Label = $UI/Dica


func _ready() -> void:
	_caixa = CaixaDialogo.new()
	add_child(_caixa)
	add_child(QuadroObjetivos.new())
	for estacao in _estacoes.get_children():
		var nome: Label = estacao.get_node_or_null("Nome")
		if nome:
			nome.text = Partida.nome_em(nome.text)
			nome.visible = false
	_comecar.call_deferred()


func _comecar() -> void:
	_ocupado = true
	await _ao_entrar()
	_ocupado = false


func _process(delta: float) -> void:
	var livre: bool = not (_ocupado or _caixa.ocupada() or _saindo)
	_mover.enabled = livre
	_mover.tick(delta)
	_player.position.x = clampf(_player.position.x, borda.x, borda.y)
	if livre and Input.is_action_just_pressed(&"mover_esquerda"):
		_player.flip_h = true
	if livre and Input.is_action_just_pressed(&"mover_direita"):
		_player.flip_h = false

	_perto = null
	var melhor: float = alcance
	for estacao: Node2D in _estacoes.get_children():
		if not estacao.visible:
			continue
		var d: float = absf(estacao.position.x - _player.position.x)
		if d < melhor:
			melhor = d
			_perto = estacao
	for estacao in _estacoes.get_children():
		var nome: Label = estacao.get_node_or_null("Nome")
		if nome:
			nome.visible = livre and estacao == _perto

	_prompt.visible = livre and _perto != null
	if _prompt.visible:
		_prompt.text = Partida.nome_em("[ESPAÇO] " + _acao(_perto.name))
		if Input.is_action_just_pressed(&"espaco"):
			_interagir_e_liberar(_perto.name)
	_dica.text = Partida.nome_em(_dica_atual()) if livre else ""


func _interagir_e_liberar(nome: StringName) -> void:
	_ocupado = true
	_mover.velocidade_x = 0.0
	await _interagir(nome)
	_ocupado = false


# ------------------------------------------------------------- para sobrescrever

func _ao_entrar() -> void:
	pass


func _acao(_nome: StringName) -> String:
	return "Examinar"


func _interagir(_nome: StringName) -> void:
	pass


func _dica_atual() -> String:
	return ""


# ----------------------------------------------------------------- ajudantes

func falar(quem: String, paginas: Array) -> void:
	await _caixa.falar(quem, paginas)


func escolher(quem: String, pergunta: String, opcoes: Array) -> int:
	return await _caixa.escolher(quem, pergunta, opcoes)


func ir_para(cena: String) -> void:
	if _saindo:
		return
	_saindo = true
	await escurecer(true)
	get_tree().change_scene_to_file.call_deferred(cena)


func esperar(segundos: float) -> void:
	await get_tree().create_timer(segundos).timeout


func tocar(som: String) -> void:
	var p := AudioStreamPlayer.new()
	p.stream = load(SONS + som + ".wav")
	add_child(p)
	p.play()
	p.finished.connect(p.queue_free)


## Toca so o trecho bom de uma gravacao longa (TRECHOS), com o fim suave.
func som(nome: String) -> void:
	var t: Array = TRECHOS[nome]
	var p := AudioStreamPlayer.new()
	p.stream = load(SONS + nome + ".mp3")
	p.volume_db = t[2]
	add_child(p)
	p.play(t[0])
	var fim := create_tween()
	fim.tween_interval(maxf(t[1] - 0.25, 0.0))
	fim.tween_property(p, "volume_db", -40.0, 0.25)
	fim.tween_callback(p.queue_free)


## Balao de fala curto sobre um ponto da tela (o "rrrrr" do gato, o latido).
func balao(texto: String, ponto: Vector2, segundos: float = 1.6) -> void:
	var camada := CanvasLayer.new()
	camada.layer = 8
	add_child(camada)
	var painel := PanelContainer.new()
	var estilo := StyleBoxFlat.new()
	estilo.bg_color = Color(0.99, 0.97, 0.92)
	estilo.border_color = Color(0.24, 0.17, 0.12)
	estilo.set_border_width_all(3)
	estilo.set_corner_radius_all(10)
	estilo.set_content_margin_all(8)
	painel.add_theme_stylebox_override("panel", estilo)
	var rotulo := Label.new()
	rotulo.text = texto
	var fonte := SystemFont.new()
	fonte.font_names = PackedStringArray(["Arial"])
	fonte.font_weight = 700
	rotulo.add_theme_font_override("font", fonte)
	rotulo.add_theme_font_size_override("font_size", 20)
	rotulo.add_theme_color_override("font_color", Color(0.24, 0.17, 0.12))
	painel.add_child(rotulo)
	camada.add_child(painel)
	painel.position = ponto
	var tween := create_tween()
	tween.tween_property(painel, "position:y", ponto.y - 16, segundos)
	tween.parallel().tween_property(painel, "modulate:a", 0.0, segundos * 0.4).set_delay(segundos * 0.6)
	tween.finished.connect(camada.queue_free)


## Mostra uma imagem grande no meio da tela (o poster de perto) enquanto as
## falas passam; fecha sozinha no fim.
func de_perto(textura: Texture2D, quem: String, paginas: Array) -> void:
	var camada := CanvasLayer.new()
	camada.layer = 9
	add_child(camada)
	var fundo := ColorRect.new()
	fundo.color = Color(0, 0, 0, 0.55)
	fundo.size = Vector2(1280, 720)
	camada.add_child(fundo)
	var quadro := TextureRect.new()
	quadro.texture = textura
	quadro.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	quadro.position = Vector2(640 - textura.get_width() * 0.5, 60)
	camada.add_child(quadro)
	camada.offset.y = 0
	quadro.modulate.a = 0.0
	create_tween().tween_property(quadro, "modulate:a", 1.0, 0.25)
	await falar(quem, paginas)
	camada.queue_free()


func coracao(ponto: Vector2) -> void:
	var c := Sprite2D.new()
	c.texture = CORACAO
	c.position = ponto
	add_child(c)
	var tween := create_tween()
	tween.tween_property(c, "position:y", ponto.y - 40, 1.2)
	tween.parallel().tween_property(c, "modulate:a", 0.0, 0.5).set_delay(0.7)
	tween.finished.connect(c.queue_free)


## Cortina preta: entra (true) ou sai (false).
func escurecer(entrar: bool = true, segundos: float = 0.5) -> void:
	var camada := get_node_or_null("Cortina") as CanvasLayer
	if not camada:
		camada = CanvasLayer.new()
		camada.name = "Cortina"
		camada.layer = 30
		var tela := ColorRect.new()
		tela.name = "Tela"
		tela.color = Color(0, 0, 0, 0 if entrar else 1)
		tela.size = Vector2(1280, 720)
		tela.mouse_filter = Control.MOUSE_FILTER_IGNORE
		camada.add_child(tela)
		add_child(camada)
	var tela: ColorRect = camada.get_node("Tela")
	var tween := create_tween()
	tween.tween_property(tela, "color:a", 1.0 if entrar else 0.0, segundos)
	await tween.finished
