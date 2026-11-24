extends Node2D

## Menu inicial: Começar, Novo jogo, Coleção, Configurações e Sair.
##
##   Começar ......... sem save, pede os nomes e comeca no quarto (Fase 1);
##                     com save, abre o mapa com os lugares da Fase 2 por onde
##                     o neto ja passou, e o jogador escolhe onde continuar
##   Novo jogo ....... so aparece com save; confirma, pede os nomes e comeca
##                     do zero (o save so e apagado quando o quarto abre)
##   Coleção ......... a colecao do save, sem entrar no jogo
##   Configurações ... volume, resolucao e modo janela (TelaConfig)
##
## Os nomes vao para Partida.definir_nome(); dali em diante os dialogos
## escrevem {nome} e {avo}, e a CaixaDialogo troca sozinha. Em branco, cada um
## fica com o padrao. ENTER confirma os nomes (o ESPACO digita espaco, para
## nome composto) e ESC volta ao menu.
##
## A interface e montada em codigo, como a CaixaDialogo, para a cena guardar so
## o cenario de fundo.

const CENA_CASA: String = "res://scenes/tutorial/Quarto.tscn"

const COR_PAPEL: Color = Color(0.96, 0.94, 0.86)
const COR_DOURADO: Color = Color(1.0, 0.82, 0.35)

enum Opcao { COMECAR, NOVO, COLECAO, CONFIG, SAIR }

var _tem_save: bool = false
var _camada: CanvasLayer
var _menu: Control
var _lista: ListaOpcoes
var _opcoes: Array[Opcao] = []
var _resumo: Label
var _nomes: PanelContainer
var _campo: LineEdit
var _campo_avo: LineEdit
var _caixa: CaixaDialogo
var _saindo: bool = false


func _ready() -> void:
	get_tree().paused = false
	_tem_save = Partida.carregar()
	if Partida.demo_final() and (not _tem_save or Partida.velho_pescado):
		# Demonstracao do final: toda vez que o menu abre sem partida (ou
		# depois de ver o final), a historia volta pronta para o Arvoredo.
		Partida.preparar_demo_final()
		_tem_save = Partida.salvar()
	if not _tem_save:
		# Sem save, o que ficou na memoria e uma manha com o vo pela metade.
		Partida.comecar_tutorial()

	_camada = CanvasLayer.new()
	_camada.layer = 10
	add_child(_camada)

	# O cenario do cais fica atras, escurecido, para a tela nao ser uma cor chapada.
	var veu := ColorRect.new()
	veu.color = Color(0.04, 0.07, 0.14, 0.55)
	veu.size = Vector2(1280, 720)
	_camada.add_child(veu)

	var titulo := _label(Fontes.negrito(), 72, COR_DOURADO)
	titulo.text = "A ÚLTIMA FISGADA"
	titulo.position = Vector2(0, 92)
	titulo.size = Vector2(1280, 80)
	titulo.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_camada.add_child(titulo)

	var subtitulo := _label(Fontes.normal(), 26, COR_PAPEL)
	subtitulo.text = "Uma história de pesca, memória e de aprender a ficar"
	subtitulo.position = Vector2(0, 172)
	subtitulo.size = Vector2(1280, 30)
	subtitulo.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_camada.add_child(subtitulo)

	_montar_menu()
	_montar_nomes()

	_caixa = CaixaDialogo.new()
	add_child(_caixa)


# ------------------------------- Menu -------------------------------

func _montar_menu() -> void:
	_menu = VBoxContainer.new()
	_menu.add_theme_constant_override("separation", 10)
	_camada.add_child(_menu)

	var painel: PanelContainer = ListaOpcoes.moldura(22.0)
	_menu.add_child(painel)
	_lista = ListaOpcoes.new()
	_lista.tamanho_texto = 28
	_lista.custom_minimum_size.x = 300.0
	painel.add_child(_lista)

	_opcoes = [Opcao.COMECAR]
	if _tem_save:
		_opcoes.append(Opcao.NOVO)
	_opcoes.append_array([Opcao.COLECAO, Opcao.CONFIG, Opcao.SAIR])
	for opcao in _opcoes:
		_lista.adicionar(_texto_da_opcao(opcao))
	_lista.escolheu.connect(func(i: int) -> void: _escolheu(_opcoes[i]))

	_resumo = _label(Fontes.normal(), 18, COR_PAPEL.darkened(0.15))
	_resumo.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_resumo.text = _texto_do_resumo()
	_menu.add_child(_resumo)

	var dica := _label(Fontes.normal(), 16, COR_PAPEL.darkened(0.3))
	dica.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	dica.text = "Setas escolhem   ESPAÇO confirma"
	_menu.add_child(dica)

	_menu.reset_size()
	_menu.position = Vector2(640.0 - _menu.size.x * 0.5, 262.0)


func _texto_da_opcao(opcao: Opcao) -> String:
	match opcao:
		Opcao.COMECAR:
			return "Continuar" if _tem_save else "Começar"
		Opcao.NOVO:
			return "Novo jogo"
		Opcao.COLECAO:
			return "Coleção"
		Opcao.CONFIG:
			return "Configurações"
	return "Sair"


func _texto_do_resumo() -> String:
	if not _tem_save:
		return "Nenhuma partida salva"
	var resumo: String = "%s  •  Dia %d  •  R$ %d" % [Partida.nome, Partida.dia, Partida.dinheiro]
	if Partida.velho_pescado:
		resumo += "  •  história concluída"
	if Partida.demo_final():
		resumo += "\nDemonstração do final: Continuar → Arvoredo e lance com força 80 ou mais"
	return resumo


func _escolheu(opcao: Opcao) -> void:
	if _saindo:
		return
	_lista.ativa = false
	match opcao:
		Opcao.COMECAR:
			if _tem_save:
				await _escolher_lugar()
			else:
				_mostrar_nomes()
				return
		Opcao.NOVO:
			if await _confirmar_novo_jogo():
				_mostrar_nomes()
				return
		Opcao.COLECAO:
			_menu.visible = false
			await Colecao.abrir_em(self)
			_menu.visible = true
		Opcao.CONFIG:
			_menu.visible = false
			await TelaConfig.abrir_em(self)
			_menu.visible = true
		Opcao.SAIR:
			get_tree().quit()
	if not _saindo:
		_lista.ativa = true


## O mapa do menu: so os lugares por onde o neto ja passou.
func _escolher_lugar() -> void:
	var lugares: Array[Dictionary] = Partida.lugares_abertos()
	if lugares.is_empty():
		# Save sem lugar marcado: comeca pela vila, que e onde a Fase 2 abre.
		Partida.visitar(&"vila")
		lugares = Partida.lugares_abertos()
	_menu.visible = false
	var id: StringName = await MapaLocais.abrir_com(self, lugares, "Onde continuar?",
		"Setas escolhem   ESPAÇO vai   ESC volta")
	_menu.visible = true
	if id.is_empty():
		return
	_ir_para(Partida.entrar_em(id))


func _confirmar_novo_jogo() -> bool:
	_menu.visible = false
	var i: int = await _caixa.escolher("",
		"Começar do zero? A partida salva de %s (dia %d) vai ser apagada." % [Partida.nome, Partida.dia],
		["Não, voltar", "Sim, começar de novo"])
	_menu.visible = true
	return i == 1


# ------------------------------- Nomes -------------------------------

func _montar_nomes() -> void:
	var fonte: Font = Fontes.normal()
	var negrito: Font = Fontes.negrito()

	_nomes = ListaOpcoes.moldura(24.0)
	_nomes.position = Vector2(370, 262)
	_nomes.size = Vector2(540, 280)
	_nomes.visible = false
	_camada.add_child(_nomes)

	var coluna := VBoxContainer.new()
	coluna.add_theme_constant_override("separation", 14)
	_nomes.add_child(coluna)

	var pergunta := _label(negrito, 24, COR_DOURADO)
	pergunta.text = "Qual o teu nome?"
	coluna.add_child(pergunta)

	_campo = _novo_campo(negrito, Partida.NOME_PADRAO)
	coluna.add_child(_campo)

	var pergunta_avo := _label(negrito, 24, COR_DOURADO)
	pergunta_avo.text = "E o nome do teu avô, o velho pescador?"
	coluna.add_child(pergunta_avo)

	_campo_avo = _novo_campo(negrito, Partida.NOME_AVO_PADRAO)
	coluna.add_child(_campo_avo)

	var botao := Button.new()
	botao.text = "Começar"
	botao.add_theme_font_override("font", negrito)
	botao.add_theme_font_size_override("font_size", 24)
	botao.custom_minimum_size = Vector2(452, 44)
	botao.pressed.connect(func() -> void: _comecar(""))
	coluna.add_child(botao)

	var dica := _label(fonte, 16, COR_PAPEL.darkened(0.25))
	dica.text = "ENTER começa   •   ESC volta   •   em branco, ficam %s e %s" % [
		Partida.NOME_PADRAO, Partida.NOME_AVO_PADRAO,
	]
	dica.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	coluna.add_child(dica)


func _mostrar_nomes() -> void:
	_menu.visible = false
	_nomes.visible = true
	_campo.text = ""
	_campo_avo.text = ""
	_campo.grab_focus()


func _input(evento: InputEvent) -> void:
	if _nomes.visible and not _saindo and evento.is_action_pressed(&"ui_cancel"):
		get_viewport().set_input_as_handled()
		Som.tocar("cursor")
		_nomes.visible = false
		_menu.visible = true
		_lista.ativa = true


## O argumento vem do text_submitted e e ignorado: os dois campos sao lidos
## direto, para o ENTER valer igual em qualquer um deles.
func _comecar(_submetido: String) -> void:
	if _saindo:
		return
	Som.tocar("confirmar")
	# Comecar de novo apaga o save: a partida nova so volta a salvar quando
	# chegar na Fase 2.
	Partida.apagar_save()
	Partida.definir_nome(_campo.text, _campo_avo.text)
	_ir_para(CENA_CASA)


func _ir_para(cena: String) -> void:
	_saindo = true
	get_tree().change_scene_to_file.call_deferred(cena)


func _novo_campo(fonte: Font, padrao: String) -> LineEdit:
	var campo := LineEdit.new()
	campo.placeholder_text = padrao
	campo.max_length = Partida.NOME_MAXIMO
	campo.alignment = HORIZONTAL_ALIGNMENT_CENTER
	campo.custom_minimum_size = Vector2(492, 44)
	campo.add_theme_font_override("font", fonte)
	campo.add_theme_font_size_override("font_size", 26)
	campo.text_submitted.connect(_comecar)
	return campo


func _label(fonte: Font, tamanho: int, cor: Color) -> Label:
	var label := Label.new()
	label.add_theme_font_override("font", fonte)
	label.add_theme_font_size_override("font_size", tamanho)
	label.add_theme_color_override("font_color", cor)
	label.add_theme_color_override("font_outline_color", Color(0.05, 0.09, 0.18))
	label.add_theme_constant_override("outline_size", 3)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label
