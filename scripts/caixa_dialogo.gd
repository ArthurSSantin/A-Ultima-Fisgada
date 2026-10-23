class_name CaixaDialogo
extends CanvasLayer

## Caixa de dialogo e de escolha usada no hub e no cais. Monta os proprios nos
## para nao depender de cena; troque o visual aqui quando a arte chegar.
##
##   await caixa.falar("Dona Marlene", ["primeira pagina", "segunda"])
##   var i: int = await caixa.escolher("Seu Valdir", "O que vai ser?", ["A", "B"])
##
## ESPACO avanca e confirma, setas para cima e para baixo escolhem, ESC fecha uma
## escolha (devolve -1).
##
## Todo texto que passa por aqui vai antes para Partida.nome_em(), entao os
## dialogos escrevem {nome} e nao precisam saber como o jogador se chama.

signal _respondeu(indice: int)

const COR_FUNDO: Color = Color(0.07, 0.13, 0.28, 0.94)
const COR_TEXTO: Color = Color(0.96, 0.94, 0.86)
const COR_DESTAQUE: Color = Color(1.0, 0.82, 0.35)

var aberta: bool = false

var _painel: PanelContainer
var _nome: Label
var _texto: Label
var _opcoes: Label
var _dica: Label
var _escolhas: Array = []
var _selecionada: int = 0
var _modo_escolha: bool = false
var _fechou_no_quadro: int = -1


func _ready() -> void:
	layer = 10
	var fonte := SystemFont.new()
	fonte.font_names = PackedStringArray(["Arial"])

	_painel = PanelContainer.new()
	var estilo := StyleBoxFlat.new()
	estilo.bg_color = COR_FUNDO
	estilo.set_corner_radius_all(6)
	estilo.set_content_margin_all(18)
	estilo.border_color = COR_DESTAQUE
	estilo.set_border_width_all(2)
	_painel.add_theme_stylebox_override("panel", estilo)
	_painel.position = Vector2(190, 470)
	_painel.size = Vector2(900, 210)
	add_child(_painel)

	var coluna := VBoxContainer.new()
	coluna.add_theme_constant_override("separation", 8)
	_painel.add_child(coluna)

	_nome = _novo_label(fonte, 20, COR_DESTAQUE)
	_texto = _novo_label(fonte, 18, COR_TEXTO)
	_texto.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_texto.custom_minimum_size = Vector2(860, 0)
	_opcoes = _novo_label(fonte, 18, COR_TEXTO)
	_dica = _novo_label(fonte, 13, COR_TEXTO.darkened(0.3))
	_dica.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	for no in [_nome, _texto, _opcoes, _dica]:
		coluna.add_child(no)

	_painel.visible = false


## True enquanto a caixa esta aberta e no quadro em que fechou, para o ESPACO
## que fechou a caixa nao valer tambem para o jogo.
func ocupada() -> bool:
	return aberta or Engine.get_process_frames() == _fechou_no_quadro


func falar(quem: String, paginas: Array) -> void:
	for pagina in paginas:
		_abrir(quem, pagina)
		_modo_escolha = false
		_opcoes.visible = false
		_dica.text = "ESPAÇO continua"
		await _respondeu
	_fechar()


func escolher(quem: String, pergunta: String, opcoes: Array) -> int:
	_abrir(quem, pergunta)
	_modo_escolha = true
	_escolhas = opcoes
	_selecionada = 0
	_opcoes.visible = true
	_dica.text = "Setas escolhem   ESPAÇO confirma   ESC sai"
	_desenhar_opcoes()
	var indice: int = await _respondeu
	_fechar()
	return indice


func _input(evento: InputEvent) -> void:
	if not aberta or evento.is_echo():
		return
	if evento.is_action_pressed(&"espaco"):
		get_viewport().set_input_as_handled()
		_respondeu.emit(_selecionada if _modo_escolha else 0)
	elif _modo_escolha and evento.is_action_pressed(&"ui_cancel"):
		get_viewport().set_input_as_handled()
		_respondeu.emit(-1)
	elif _modo_escolha and evento.is_action_pressed(&"ui_up"):
		_selecionada = wrapi(_selecionada - 1, 0, _escolhas.size())
		_desenhar_opcoes()
	elif _modo_escolha and evento.is_action_pressed(&"ui_down"):
		_selecionada = wrapi(_selecionada + 1, 0, _escolhas.size())
		_desenhar_opcoes()


func _abrir(quem: String, texto: String) -> void:
	aberta = true
	_painel.visible = true
	_nome.text = Partida.nome_em(quem)
	_nome.visible = not quem.is_empty()
	_texto.text = Partida.nome_em(texto)
	# O painel cresce com o texto; ancorado embaixo.
	_painel.reset_size()
	_painel.position.y = 690.0 - _painel.get_combined_minimum_size().y


func _fechar() -> void:
	aberta = false
	_painel.visible = false
	_fechou_no_quadro = Engine.get_process_frames()


func _desenhar_opcoes() -> void:
	var linhas: PackedStringArray = []
	for i in _escolhas.size():
		linhas.append(("> " if i == _selecionada else "   ") + Partida.nome_em(str(_escolhas[i])))
	_opcoes.text = "\n".join(linhas)
	_painel.reset_size()
	_painel.position.y = 690.0 - _painel.get_combined_minimum_size().y


func _novo_label(fonte: Font, tamanho: int, cor: Color) -> Label:
	var label := Label.new()
	label.add_theme_font_override("font", fonte)
	label.add_theme_font_size_override("font_size", tamanho)
	label.add_theme_color_override("font_color", cor)
	return label
