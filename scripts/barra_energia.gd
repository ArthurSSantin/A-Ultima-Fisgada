class_name BarraEnergia
extends Control

## Barra de energia do pescador, no canto inferior esquerdo do cais e do hub. Le
## Partida.energia todo quadro. Desenhada em codigo ate a arte chegar.

const TAMANHO: Vector2 = Vector2(36, 180)
const MARGEM: float = 24.0
const BORDA: float = 4.0

const COR_MOLDURA: Color = Color(0.36, 0.22, 0.12)
const COR_FUNDO: Color = Color(0.16, 0.1, 0.07)
const COR_CHEIA: Color = Color(0.36, 0.8, 0.3)
const COR_MEIO: Color = Color(0.95, 0.78, 0.25)
const COR_VAZIA: Color = Color(0.88, 0.27, 0.2)

var _mostrada: float = Partida.ENERGIA_MAX
var _tempo: float = 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size = TAMANHO + Vector2(0, 22)
	position = Vector2(MARGEM, 720.0 - MARGEM - size.y)


func _process(delta: float) -> void:
	_tempo += delta
	# A barra desce suave em vez de pular.
	_mostrada = move_toward(_mostrada, Partida.energia, 60.0 * delta)
	queue_redraw()


func _draw() -> void:
	var fonte: Font = ThemeDB.fallback_font
	draw_string_outline(fonte, Vector2(TAMANHO.x / 2.0 - 40.0, 14), "ENERGIA", HORIZONTAL_ALIGNMENT_CENTER, 80, 13, 4, COR_FUNDO)
	draw_string(fonte, Vector2(TAMANHO.x / 2.0 - 40.0, 14), "ENERGIA", HORIZONTAL_ALIGNMENT_CENTER, 80, 13, Color(1, 0.96, 0.86))

	var caixa := Rect2(Vector2(0, 22), TAMANHO)
	draw_rect(caixa, COR_MOLDURA)
	var dentro := caixa.grow(-BORDA)
	draw_rect(dentro, COR_FUNDO)

	var fracao: float = clampf(_mostrada / Partida.ENERGIA_MAX, 0.0, 1.0)
	var cor: Color = COR_MEIO.lerp(COR_CHEIA, (fracao - 0.5) * 2.0) if fracao > 0.5 else COR_VAZIA.lerp(COR_MEIO, fracao * 2.0)
	# Pisca quando esta quase no fim.
	if fracao < 0.2 and fmod(_tempo, 0.6) < 0.3:
		cor = cor.lightened(0.35)
	var altura: float = dentro.size.y * fracao
	draw_rect(Rect2(dentro.position.x, dentro.end.y - altura, dentro.size.x, altura), cor)
