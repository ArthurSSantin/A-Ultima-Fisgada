class_name CaixaDialogo
extends CanvasLayer

## Caixa de dialogo e de escolha usada em todas as cenas. Monta os proprios
## nos para nao depender de cena.
##
##   await caixa.falar("Dona Marlene", ["primeira pagina", "segunda"])
##   var i: int = await caixa.escolher("Seu Valdir", "O que vai ser?", ["A", "B"])
##
## ESPACO avanca e confirma, setas para cima e para baixo escolhem, ESC fecha uma
## escolha (devolve -1). O texto aparece letra a letra, com o "tic" na voz de
## quem fala (Som.letra); ESPACO no meio mostra a pagina inteira de uma vez.
##
## A caixa tem lugar fixo: largura e margens iguais em todas as cenas, rodape
## sempre na mesma linha (Y_BASE) e altura minima de tres linhas, para nao
## pular de tamanho de uma pagina para outra. So uma pagina maior que isso (o
## recibo da venda, uma escolha com muitas opcoes) faz a caixa crescer, e ela
## cresce para cima. O nome de quem fala vai numa plaquinha sobre a borda.
##
## Um "\t" no texto pula para a COLUNA_TAB: e o que alinha os precos do recibo.
##
## Todo texto que passa por aqui vai antes para Partida.nome_em(), entao os
## dialogos escrevem {nome} e nao precisam saber como o jogador se chama.
##
## Os testes ligam Engine.set_meta(&"texto_instantaneo", true) para o texto
## sair inteiro, sem a maquina de escrever.

signal _respondeu(indice: int)

const COR_FUNDO: Color = Color(0.07, 0.13, 0.28, 0.94)
const COR_TEXTO: Color = Color(0.96, 0.94, 0.86)
const COR_DESTAQUE: Color = Color(1.0, 0.82, 0.35)
const COR_DICA: Color = Color(0.67, 0.66, 0.6)

const X: float = 190.0
const LARGURA: float = 900.0
## Linha de baixo da caixa, a mesma em todas as cenas.
const Y_BASE: float = 690.0
const MARGEM: float = 20.0
const TAMANHO_TEXTO: int = 18
const LINHAS_MINIMAS: int = 3
const ALTURA_OPCAO: float = 28.0
const COLUNA_TAB: float = 400.0
## Letras por segundo da maquina de escrever.
const VELOCIDADE: float = 60.0

var aberta: bool = false

var _painel: Panel
var _placa: PanelContainer
var _nome: Label
var _texto: Label
var _dica: Label
var _marcador: Label
var _opcoes: Array[Label] = []
var _escolhas: Array = []
var _selecionada: int = 0
var _modo_escolha: bool = false
var _fechou_no_quadro: int = -1
var _quem: String = ""
var _letras: float = 0.0
var _total_letras: int = 0
var _fonte: Font


func _ready() -> void:
	layer = 10
	_fonte = Fontes.normal()

	_painel = Panel.new()
	_painel.add_theme_stylebox_override("panel", _estilo())
	_painel.position = Vector2(X, Y_BASE)
	_painel.size = Vector2(LARGURA, 0.0)
	_painel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_painel)

	_texto = _novo_label(TAMANHO_TEXTO, COR_TEXTO)
	_texto.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_texto.position = Vector2(MARGEM, MARGEM - 2.0)
	_texto.size = Vector2(LARGURA - MARGEM * 2.0, 0.0)
	_texto.tab_stops = PackedFloat32Array([COLUNA_TAB])
	# as palavras ja nascem na linha certa, sem pular enquanto sao escritas
	_texto.visible_characters_behavior = TextServer.VC_CHARS_AFTER_SHAPING
	_painel.add_child(_texto)

	_dica = _novo_label(13, COR_DICA)
	_dica.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_painel.add_child(_dica)

	_marcador = _novo_label(TAMANHO_TEXTO, COR_DESTAQUE)
	_marcador.text = ">"
	_painel.add_child(_marcador)

	_placa = PanelContainer.new()
	var estilo_placa: StyleBoxFlat = _estilo()
	estilo_placa.content_margin_left = 14.0
	estilo_placa.content_margin_right = 14.0
	estilo_placa.content_margin_top = 2.0
	estilo_placa.content_margin_bottom = 3.0
	_placa.add_theme_stylebox_override("panel", estilo_placa)
	_placa.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_placa)
	_nome = _novo_label(19, COR_DESTAQUE)
	_placa.add_child(_nome)

	_painel.visible = false
	_placa.visible = false


## True enquanto a caixa esta aberta e no quadro em que fechou, para o ESPACO
## que fechou a caixa nao valer tambem para o jogo.
func ocupada() -> bool:
	return aberta or Engine.get_process_frames() == _fechou_no_quadro


func falar(quem: String, paginas: Array) -> void:
	for pagina in paginas:
		_modo_escolha = false
		_escolhas = []
		_abrir(quem, pagina)
		await _respondeu
	_fechar()


func escolher(quem: String, pergunta: String, opcoes: Array) -> int:
	_modo_escolha = true
	_escolhas = opcoes
	_selecionada = 0
	_abrir(quem, pergunta)
	var indice: int = await _respondeu
	_fechar()
	return indice


func _process(delta: float) -> void:
	if not aberta or _escrito():
		return
	var antes: int = int(_letras)
	_letras = minf(_letras + VELOCIDADE * delta, _total_letras)
	_texto.visible_characters = int(_letras)
	for i in range(antes, int(_letras)):
		if _texto.text.substr(i, 1).strip_edges() != "":
			Som.letra(_quem)
			break
	if _escrito():
		_ao_terminar_de_escrever()


func _input(evento: InputEvent) -> void:
	if not aberta or evento.is_echo():
		return
	if evento.is_action_pressed(&"espaco"):
		get_viewport().set_input_as_handled()
		if not _escrito():
			_mostrar_tudo()
		elif _modo_escolha:
			Som.tocar("confirmar")
			_respondeu.emit(_selecionada)
		else:
			_respondeu.emit(0)
	elif _modo_escolha and evento.is_action_pressed(&"ui_cancel"):
		get_viewport().set_input_as_handled()
		_respondeu.emit(-1)
	elif _modo_escolha and _escrito() and evento.is_action_pressed(&"ui_up"):
		_mover_selecao(-1)
	elif _modo_escolha and _escrito() and evento.is_action_pressed(&"ui_down"):
		_mover_selecao(1)


func _abrir(quem: String, texto: String) -> void:
	if not aberta:
		Som.abafar_musica(true)
	aberta = true
	_quem = quem
	_nome.text = Partida.nome_em(quem)
	_texto.text = Partida.nome_em(texto)
	_texto.visible_characters = 0
	_total_letras = _texto.get_total_character_count()
	_letras = 0.0
	_montar_opcoes()
	_arrumar()
	_painel.visible = true
	_placa.visible = not quem.is_empty()
	if Engine.get_meta(&"texto_instantaneo", false):
		_mostrar_tudo()
	else:
		_dica.visible = false
		_mostrar_opcoes(false)


func _fechar() -> void:
	aberta = false
	_painel.visible = false
	_placa.visible = false
	_fechou_no_quadro = Engine.get_process_frames()
	Som.abafar_musica(false)


func _escrito() -> bool:
	return _letras >= _total_letras


func _mostrar_tudo() -> void:
	_letras = _total_letras
	_texto.visible_characters = -1
	_ao_terminar_de_escrever()


## As opcoes e a dica so aparecem com a pergunta inteira na tela.
func _ao_terminar_de_escrever() -> void:
	_dica.visible = true
	_dica.text = "Setas escolhem   ESPAÇO confirma   ESC sai" if _modo_escolha else "ESPAÇO continua"
	_mostrar_opcoes(_modo_escolha)


func _montar_opcoes() -> void:
	for o in _opcoes:
		o.queue_free()
	_opcoes.clear()
	for opcao in _escolhas:
		var label := _novo_label(TAMANHO_TEXTO, COR_TEXTO)
		label.text = Partida.nome_em(str(opcao))
		_painel.add_child(label)
		_opcoes.append(label)


func _mostrar_opcoes(sim: bool) -> void:
	for o in _opcoes:
		o.visible = sim
	_marcador.visible = sim and not _opcoes.is_empty()
	if sim:
		_desenhar_selecao()


func _mover_selecao(passo: int) -> void:
	_selecionada = wrapi(_selecionada + passo, 0, _escolhas.size())
	Som.tocar("cursor")
	_desenhar_selecao()


func _desenhar_selecao() -> void:
	for i in _opcoes.size():
		_opcoes[i].add_theme_color_override("font_color", COR_DESTAQUE if i == _selecionada else COR_TEXTO)
	if not _opcoes.is_empty():
		_marcador.position = Vector2(MARGEM + 4.0, _opcoes[_selecionada].position.y)


## Mede o texto e posiciona tudo a partir de Y_BASE. Medir aqui, com o texto
## e as opcoes ja definidos, e o que mantem a caixa do tamanho certo.
func _arrumar() -> void:
	var altura_linha: float = _texto.get_line_height()
	var linhas: int = maxi(_texto.get_line_count(), 1)
	var y: float = _texto.position.y + linhas * altura_linha
	if not _opcoes.is_empty():
		y += 10.0
		for o in _opcoes:
			o.position = Vector2(MARGEM + 26.0, y)
			y += ALTURA_OPCAO
	var minimo: float = _texto.position.y + LINHAS_MINIMAS * altura_linha
	y = maxf(y, minimo)
	_dica.size = Vector2(LARGURA - MARGEM * 2.0, 20.0)
	_dica.position = Vector2(MARGEM, y + 4.0)
	var altura: float = _dica.position.y + 20.0 + MARGEM - 6.0
	_painel.size = Vector2(LARGURA, altura)
	_painel.position = Vector2(X, Y_BASE - altura)
	_placa.reset_size()
	_placa.position = Vector2(X + 18.0, _painel.position.y - _placa.size.y + 6.0)


func _estilo() -> StyleBoxFlat:
	var estilo := StyleBoxFlat.new()
	estilo.bg_color = COR_FUNDO
	estilo.border_color = COR_DESTAQUE
	estilo.set_border_width_all(2)
	estilo.set_corner_radius_all(6)
	return estilo


func _novo_label(tamanho: int, cor: Color) -> Label:
	var label := Label.new()
	label.add_theme_font_override("font", _fonte)
	label.add_theme_font_size_override("font_size", tamanho)
	label.add_theme_color_override("font_color", cor)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label
