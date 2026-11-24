class_name Hud
extends RefCounted

## O lugar fixo de cada texto da interface, igual em todas as cenas:
##
##   topo, no meio ..... placar (dia, dinheiro, balde), numa faixa escura;
##                       logo abaixo, empilhadas, a dica e o aviso da cena
##   canto de cima ..... os objetivos, numa faixa escura (QuadroObjetivos no
##                       tutorial, o Objetivo das cenas da vila)
##   embaixo, no meio .. o aviso de "[ESPACO] ...", na mesma linha de base da
##                       CaixaDialogo (CaixaDialogo.Y_BASE)
##
##     Hud.vestir(_placar)                     # uma vez, no _ready
##     Hud.empilhar([_placar, _dica, _aviso])  # depois de mudar os textos
##
## Faixa vazia nao aparece: sem texto, o fundo fica transparente.

const MARGEM: float = 12.0
const ESPACO_ENTRE: float = 8.0
const COR_FAIXA: Color = Color(0.08, 0.06, 0.05, 0.72)


## O fundo das faixas da interface (placar, objetivos, aviso de acao).
static func faixa(vertical: float = 4.0, horizontal: float = 14.0) -> StyleBoxFlat:
	var estilo := StyleBoxFlat.new()
	estilo.bg_color = COR_FAIXA
	estilo.set_corner_radius_all(6)
	estilo.content_margin_left = horizontal
	estilo.content_margin_right = horizontal
	estilo.content_margin_top = vertical
	estilo.content_margin_bottom = vertical + 1.0
	return estilo


## Poe a faixa atras de um Label; ele passa a ter o tamanho do proprio texto.
static func vestir(label: Label, vertical: float = 4.0, horizontal: float = 14.0) -> void:
	label.add_theme_stylebox_override("normal", faixa(vertical, horizontal))
	label.autowrap_mode = TextServer.AUTOWRAP_OFF
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE


## Empilha os textos no topo da tela, centralizados, um embaixo do outro. Os
## invisiveis e os vazios nao ocupam lugar.
static func empilhar(labels: Array) -> void:
	var y: float = MARGEM
	for label: Label in labels:
		_esconder_faixa(label)
		if label.visible and not label.text.is_empty():
			y = _centralizar(label, y) + ESPACO_ENTRE


## Faixa no canto de cima a direita.
static func no_canto(label: Label) -> void:
	_esconder_faixa(label)
	label.reset_size()
	label.position = Vector2(1280.0 - MARGEM - label.size.x, MARGEM)


## Faixa embaixo, no meio, com a base na mesma linha da caixa de dialogo.
static func no_rodape(label: Label) -> void:
	_esconder_faixa(label)
	label.reset_size()
	label.position = Vector2(640.0 - label.size.x * 0.5, CaixaDialogo.Y_BASE - label.size.y)


## Centraliza na horizontal a partir de `y` e devolve onde o texto termina.
static func _centralizar(label: Label, y: float) -> float:
	if label.autowrap_mode == TextServer.AUTOWRAP_OFF:
		label.reset_size()
		label.position = Vector2(640.0 - label.size.x * 0.5, y)
		return y + label.size.y
	# texto que quebra linha guarda a largura da cena e so desce
	label.position = Vector2(640.0 - label.size.x * 0.5, y)
	var linhas: int = maxi(label.get_line_count(), 1)
	return y + linhas * label.get_line_height()


static func _esconder_faixa(label: Label) -> void:
	label.self_modulate.a = 0.0 if label.text.is_empty() else 1.0
