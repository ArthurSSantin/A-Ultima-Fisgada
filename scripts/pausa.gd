extends Node

## Menu de pausa (autoload "Pausa"): ESC em qualquer cena do jogo para tudo e
## abre Continuar, Coleção, Configurações e Voltar ao menu.
##
## So abre com um ESC que ninguem usou: a escolha da CaixaDialogo, o mapa e a
## colecao fecham com ESC e marcam o evento como tratado antes de chegar aqui.
## Na tela inicial e na tela final nao ha pausa.
##
## Na Fase 2, voltar ao menu salva a partida. Na Fase 1 nao ha save, e o menu
## avisa que a manha com o vo recomeca do quarto.

const CENA_INICIO: String = "res://scenes/Inicio.tscn"
## Cenas sem pausa.
const SEM_PAUSA: Array[String] = [CENA_INICIO]

var _camada: CanvasLayer = null
var _lista: ListaOpcoes
var _aviso: Label


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func aberta() -> bool:
	return _camada != null


func _unhandled_input(evento: InputEvent) -> void:
	if evento.is_echo() or not evento.is_action_pressed(&"ui_cancel"):
		return
	if aberta():
		return  # a ListaOpcoes cuida do ESC enquanto o menu esta aberto
	var cena: Node = get_tree().current_scene
	if cena == null or cena.scene_file_path in SEM_PAUSA or _tem_tela_final(cena):
		return
	get_viewport().set_input_as_handled()
	abrir()


func abrir() -> void:
	if aberta():
		return
	get_tree().paused = true
	Som.tocar("confirmar")

	_camada = CanvasLayer.new()
	_camada.layer = 25
	add_child(_camada)

	var veu := ColorRect.new()
	veu.color = Color(0.03, 0.05, 0.1, 0.62)
	veu.size = Vector2(1280, 720)
	_camada.add_child(veu)

	var painel: PanelContainer = ListaOpcoes.moldura(28.0)
	_camada.add_child(painel)
	var coluna := VBoxContainer.new()
	coluna.add_theme_constant_override("separation", 16)
	painel.add_child(coluna)

	var titulo := Label.new()
	titulo.text = "Pausa"
	titulo.add_theme_font_override("font", Fontes.negrito())
	titulo.add_theme_font_size_override("font_size", 38)
	titulo.add_theme_color_override("font_color", ListaOpcoes.COR_DESTAQUE)
	titulo.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	coluna.add_child(titulo)

	_lista = ListaOpcoes.new()
	_lista.custom_minimum_size.x = 380.0
	coluna.add_child(_lista)
	_lista.adicionar("Continuar")
	_lista.adicionar("Coleção")
	_lista.adicionar("Configurações")
	_lista.adicionar("Voltar ao menu")
	_lista.escolheu.connect(_escolheu)
	_lista.cancelou.connect(fechar)

	_aviso = Label.new()
	_aviso.add_theme_font_override("font", Fontes.normal())
	_aviso.add_theme_font_size_override("font_size", 16)
	_aviso.add_theme_color_override("font_color", ListaOpcoes.COR_APAGADO)
	_aviso.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_aviso.text = "A partida é salva ao voltar ao menu." if Partida.fase >= 2 \
		else "A manhã com o vô não é salva:\nvoltar ao menu recomeça do quarto."
	coluna.add_child(_aviso)

	painel.reset_size()
	painel.position = (Vector2(1280, 720) - painel.size) * 0.5


func fechar() -> void:
	if not aberta():
		return
	_camada.queue_free()
	_camada = null
	get_tree().paused = false


func _escolheu(indice: int) -> void:
	match indice:
		0:
			fechar()
		1:
			await _submenu(func() -> void: await Colecao.abrir_em(self))
		2:
			await _submenu(func() -> void: await TelaConfig.abrir_em(self))
		3:
			Partida.salvar()
			fechar()
			get_tree().change_scene_to_file(CENA_INICIO)


## Abre uma tela no lugar do menu e devolve o controle a ele quando ela fecha.
func _submenu(abrir_tela: Callable) -> void:
	_lista.ativa = false
	_camada.visible = false
	await abrir_tela.call()
	if aberta():
		_camada.visible = true
		_lista.ativa = true


## A tela final (TelaFinal) entra por cima da cena do Arvoredo; nela ESC nao
## pausa.
func _tem_tela_final(cena: Node) -> bool:
	for filho in cena.get_children():
		if filho is TelaFinal:
			return true
	return false
