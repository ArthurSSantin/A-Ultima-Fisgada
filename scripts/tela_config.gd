class_name TelaConfig
extends CanvasLayer

## Tela de configuracoes, aberta pelo menu inicial e pelo menu de pausa:
##
##     await TelaConfig.abrir_em(self)
##
## Cada mudanca vale na hora (Config.aplicar_*) e e gravada ao sair. Funciona
## com o jogo pausado.

signal _fechou

var _lista: ListaOpcoes
var _i_resolucao: int = -1


static func abrir_em(dono: Node) -> void:
	var tela := TelaConfig.new()
	dono.add_child(tela)
	await tela._fechou
	tela.queue_free()


func _ready() -> void:
	layer = 30
	process_mode = Node.PROCESS_MODE_ALWAYS

	var fundo := ColorRect.new()
	fundo.color = Color(0.03, 0.05, 0.1, 0.78)
	fundo.size = Vector2(1280, 720)
	add_child(fundo)

	var painel: PanelContainer = ListaOpcoes.moldura(28.0)
	add_child(painel)
	var coluna := VBoxContainer.new()
	coluna.add_theme_constant_override("separation", 16)
	painel.add_child(coluna)

	var titulo := Label.new()
	titulo.text = "Configurações"
	titulo.add_theme_font_override("font", Fontes.negrito())
	titulo.add_theme_font_size_override("font_size", 34)
	titulo.add_theme_color_override("font_color", ListaOpcoes.COR_DESTAQUE)
	titulo.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	coluna.add_child(titulo)

	_lista = ListaOpcoes.new()
	_lista.custom_minimum_size.x = 560.0
	coluna.add_child(_lista)
	_lista.adicionar("Volume geral",
		func() -> String: return Config.texto_volume(Config.volume_geral),
		func(d: int) -> void:
			Config.volume_geral = _passo(Config.volume_geral, d)
			Config.aplicar_som())
	_lista.adicionar("Música",
		func() -> String: return Config.texto_volume(Config.volume_musica),
		func(d: int) -> void:
			Config.volume_musica = _passo(Config.volume_musica, d)
			Config.aplicar_som())
	_lista.adicionar("Efeitos e ambiente",
		func() -> String: return Config.texto_volume(Config.volume_efeitos),
		func(d: int) -> void:
			Config.volume_efeitos = _passo(Config.volume_efeitos, d)
			Config.aplicar_som())
	_lista.adicionar("Modo",
		func() -> String: return "Tela cheia" if Config.tela_cheia else "Janela",
		func(_d: int) -> void:
			Config.tela_cheia = not Config.tela_cheia
			Config.aplicar_tela())
	_i_resolucao = _lista.adicionar("Resolução da janela",
		func() -> String: return Config.texto_resolucao(Config.resolucao),
		_mudar_resolucao)
	_lista.adicionar("Voltar")
	_lista.escolheu.connect(func(_i: int) -> void: _fechar())
	_lista.cancelou.connect(_fechar)

	var dica := Label.new()
	dica.text = "Setas escolhem e mudam   ESPAÇO confirma   ESC volta"
	dica.add_theme_font_override("font", Fontes.normal())
	dica.add_theme_font_size_override("font_size", 16)
	dica.add_theme_color_override("font_color", ListaOpcoes.COR_APAGADO)
	dica.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	coluna.add_child(dica)

	painel.reset_size()
	painel.position = (Vector2(1280, 720) - painel.size) * 0.5


## Em tela cheia a resolucao da janela nao vale; muda assim mesmo e fica
## guardada para quando voltar ao modo janela.
func _mudar_resolucao(d: int) -> void:
	var possiveis: Array[int] = Config.resolucoes_possiveis()
	var atual: int = maxi(possiveis.find(Config.resolucao), 0)
	Config.resolucao = possiveis[wrapi(atual + d, 0, possiveis.size())]
	Config.aplicar_tela()


static func _passo(volume: float, direcao: int) -> float:
	return clampf(snappedf(volume + direcao * Config.PASSO_VOLUME, 0.01), 0.0, 1.0)


func _fechar() -> void:
	Config.salvar()
	_fechou.emit()
