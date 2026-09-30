extends Node2D

## Traducao da folha "Folha de eventos 1" do projeto Construct 3 PescaAlfa.
##
## Os grupos e a ordem dos eventos dentro de cada grupo seguem exatamente o
## original, porque a folha depende dessa ordem. Dois exemplos:
##
## - em "Lancamento", o evento que arremessa (Estado = 1) vem antes do que zera a
##   forca, e por isso a forca do arremesso sobrevive ao tick;
## - em "Movimento", pertoAgua e zerada todo tick e so volta a valer no evento
##   seguinte, quando o Player esta sobre a ZonaPesca.
##
## Estados: 0 parado | 1 lancando | 2 esperando mordida | 3 fisgada
##          4 puxando | 5 capturado | 6 falhou | 7 reset

const ESQUERDA: StringName = &"mover_esquerda"
const DIREITA: StringName = &"mover_direita"
const ESPACO: StringName = &"espaco"

# --- variaveis globais da folha de eventos ---
var estado: int = 0
var forca: float = 0.0
var resistencia: float = 0.0
var tensao: float = 0.0
var direcao_forca: float = 1.0
var pos_lancamento: float = 0.0
var peso_peixe: float = 0.0
var peixes: int = 0
var total_kg: float = 0.0

## Variavel de instancia "pertoAgua" da ZonaPesca. Vive aqui porque o layout tem
## uma unica instancia dela e a folha de eventos inteira le esse valor.
var perto_agua: bool = false

## Equivale a expressao System.time do C3: segundos desde o inicio do layout.
var _tempo: float = 0.0

## Contador de ticks, usado por _gatilho_unico.
var _quadro: int = 0
var _gatilhos: Dictionary = {}

@onready var _player: Sprite2D = $Jogo/Player
@onready var _mover: EightDir = $Jogo/Player/OitoDirecoes
@onready var _zona_pesca: Sprite2D = $Jogo/ZonaPesca
@onready var _isca: Sprite2D = $Jogo/Isca
@onready var _linha: Sprite2D = $Jogo/Linha
@onready var _peixe: AnimatedSprite2D = $Jogo/Peixe
@onready var _barra_forca: Sprite2D = $UI/BarraFillForca
@onready var _barra_tensao: Sprite2D = $UI/BarraFillTensao
@onready var _barra_puxada: Sprite2D = $UI/BarraFill
@onready var _status: Label = $UI/StatusLabel
@onready var _placar: Label = $UI/Placar


func _process(delta: float) -> void:
	_quadro += 1
	_tempo += delta

	# No C3 os behaviors rodam antes dos eventos do tick.
	_mover.tick(delta)

	_grupo_movimento()
	_grupo_lancamento(delta)
	_grupo_espera_e_fisgada(delta)
	_grupo_puxada(delta)
	_grupo_resultado(delta)
	_grupo_interface()


# ------------------------------- Movimento -------------------------------

func _grupo_movimento() -> void:
	# Todo tick
	perto_agua = false
	_player.position.x = clampf(_player.position.x, 40.0, 590.0)

	# Player esta sobrepondo ZonaPesca
	if C3.sobrepondo(_player, _zona_pesca):
		perto_agua = true

	# Estado = 0
	if estado == 0:
		_mover.enabled = true

	# Estado <> 0
	if estado != 0:
		_mover.enabled = false

	# Carregando o arremesso na beira: trava o Player no lugar
	if Input.is_action_pressed(ESPACO) and estado == 0 and perto_agua:
		_mover.enabled = false

	# Seta esquerda pressionada
	if Input.is_action_just_pressed(ESQUERDA) and estado == 0:
		_player.flip_h = true

	# Seta direita pressionada
	if Input.is_action_just_pressed(DIREITA) and estado == 0:
		_player.flip_h = false


# ------------------------------ Lancamento ------------------------------

func _grupo_lancamento(delta: float) -> void:
	# Forca vai e volta enquanto segura ESPACO
	if Input.is_action_pressed(ESPACO) and estado == 0 and perto_agua:
		forca = clampf(forca + 90.0 * delta * direcao_forca, 0.0, 100.0)

		if forca >= 100.0:
			direcao_forca = -1.0

		if forca <= 0.0:
			direcao_forca = 1.0

	# Soltou ESPACO com forca suficiente: arremessa
	if Input.is_action_just_released(ESPACO) and estado == 0 and perto_agua and forca > 5.0:
		estado = 1

	# Soltou ESPACO sem arremessar: zera a barra de forca. O evento acima ja
	# mudou o Estado para 1 quando o arremesso valeu, e por isso a forca do
	# arremesso continua valendo aqui.
	if Input.is_action_just_released(ESPACO) and estado == 0:
		forca = 0.0
		direcao_forca = 1.0

	# Entrou no Estado 1
	if estado == 1 and _gatilho_unico(&"lancamento"):
		_player.flip_h = false
		pos_lancamento = 660.0 + (forca / 100.0) * 520.0
		peso_peixe = roundf((randf_range(0.5, 2.5) + (forca / 100.0) * 4.5) * 10.0) / 10.0
		resistencia = 0.0
		tensao = 0.0
		_isca.position = Vector2(pos_lancamento, 478.0)
		_isca.visible = true
		_linha.visible = true
		_peixe.frame = 0
		_status.text = "Lançando..."
		_depois_do_lancamento()


func _depois_do_lancamento() -> void:
	await _esperar(0.5)
	if estado == 1:
		estado = 2


# --------------------------- Espera e fisgada ---------------------------

func _grupo_espera_e_fisgada(delta: float) -> void:
	# Entrou no Estado 2
	if estado == 2 and _gatilho_unico(&"espera"):
		_status.text = "Esperando a mordida... (não aperte ainda!)"
		C3.set_opacidade(_peixe, 0.0)
		_peixe.visible = true
		_depois_da_espera(randf_range(1.5, 4.0))

	# Isca balancando e peixe rondando
	if estado == 2:
		_isca.position.y = 478.0 + 2.0 * C3.sin_g(_tempo * 150.0)
		_peixe.position = Vector2(_isca.position.x + 90.0 * C3.cos_g(_tempo * 70.0), 545.0)
		C3.set_opacidade(_peixe, minf(C3.opacidade(_peixe) + 30.0 * delta, 45.0))

	# Apertou ESPACO antes da mordida
	if Input.is_action_just_pressed(ESPACO) and estado == 2:
		_status.text = "Muito cedo! O peixe se assustou."
		estado = 6

	# Entrou no Estado 3
	if estado == 3 and _gatilho_unico(&"fisgada"):
		_status.text = "FISGOU! Aperte ESPAÇO agora!"
		_depois_da_fisgada()

	# Janela da fisgada
	if estado == 3:
		_isca.position.y = 486.0 + 3.0 * C3.sin_g(_tempo * 1400.0)
		_peixe.position = Vector2(_isca.position.x + 36.0, 520.0)
		C3.set_opacidade(_peixe, 70.0)

	# Fisgou dentro da janela
	if Input.is_action_just_pressed(ESPACO) and estado == 3:
		estado = 4
		_status.text = "Segure ESPAÇO para puxar. Solte se a tensão subir!"


func _depois_da_espera(segundos: float) -> void:
	await _esperar(segundos)
	if estado == 2:
		estado = 3


func _depois_da_fisgada() -> void:
	await _esperar(0.9)
	if estado == 3:
		_status.text = "Muito lento... o peixe escapou."
		estado = 6


# -------------------------------- Puxada --------------------------------

func _grupo_puxada(delta: float) -> void:
	# Segurando ESPACO: puxa e a tensao sobe pulsando conforme o peso do peixe
	if estado == 4 and Input.is_action_pressed(ESPACO):
		resistencia += 16.0 * delta
		tensao += (12.0 + peso_peixe * 9.0 * (0.5 + 0.5 * C3.sin_g(_tempo * 170.0))) * delta

	# Sem ESPACO: perde puxada devagar e alivia a tensao rapido
	if estado == 4 and not Input.is_action_pressed(ESPACO):
		resistencia -= 5.0 * delta
		tensao -= 40.0 * delta

	# Todo tick
	resistencia = clampf(resistencia, 0.0, 100.0)
	tensao = clampf(tensao, 0.0, 100.0)

	# Isca e peixe se aproximando do cais
	if estado == 4:
		_isca.position = Vector2(
			lerpf(pos_lancamento, 640.0, resistencia / 100.0),
			484.0 + 3.0 * C3.sin_g(_tempo * 900.0),
		)
		_peixe.position = Vector2(
			_isca.position.x + 34.0 + 8.0 * C3.sin_g(_tempo * 500.0),
			_isca.position.y + 36.0,
		)

	# Tensao no limite: a linha arrebenta
	if estado == 4 and tensao >= 100.0:
		_status.text = "A linha arrebentou!"
		estado = 6

	# Puxada completa: peixe capturado
	if estado == 4 and resistencia >= 100.0:
		estado = 5


# ------------------------------- Resultado -------------------------------

func _grupo_resultado(delta: float) -> void:
	# Entrou no Estado 5
	if estado == 5 and _gatilho_unico(&"capturado"):
		peixes += 1
		total_kg = roundf((total_kg + peso_peixe) * 10.0) / 10.0
		_isca.visible = false
		_linha.visible = false
		_peixe.frame = 1
		C3.set_opacidade(_peixe, 100.0)
		_peixe.position = Vector2(_player.position.x + 70.0, 420.0)
		_status.text = "Capturado! Peixe de " + C3.num(peso_peixe) + " kg"
		_depois_da_captura()

	# Entrou no Estado 6
	if estado == 6 and _gatilho_unico(&"falhou"):
		_depois_da_falha()

	# Peixe fugindo
	if estado == 6:
		C3.set_opacidade(_peixe, maxf(C3.opacidade(_peixe) - 80.0 * delta, 0.0))
		_peixe.position.x += 150.0 * delta

	# Estado 7: volta tudo ao inicio
	if estado == 7:
		estado = 0
		forca = 0.0
		resistencia = 0.0
		tensao = 0.0
		direcao_forca = 1.0
		_isca.visible = false
		_linha.visible = false
		_peixe.visible = false
		_peixe.frame = 0


func _depois_da_captura() -> void:
	await _esperar(2.2)
	if estado == 5:
		estado = 7


func _depois_da_falha() -> void:
	await _esperar(1.6)
	if estado == 6:
		estado = 7


# ------------------------------- Interface -------------------------------

func _grupo_interface() -> void:
	# Todo tick: linha ligando a vara na isca, barras e placar
	var mao: Vector2 = Vector2(_player.position.x + 30.0, _player.position.y - 46.0)
	var ponta: Vector2 = Vector2(_isca.position.x, _isca.position.y - 10.0)

	_linha.position = mao
	_linha.rotation = (ponta - mao).angle()
	C3.set_largura(_linha, mao.distance_to(ponta))

	C3.set_altura(_barra_forca, (forca / 100.0) * 240.0)
	C3.set_altura(_barra_tensao, (tensao / 100.0) * 240.0)
	C3.set_altura(_barra_puxada, (resistencia / 100.0) * 240.0)

	# Perto de arrebentar, a barra de tensao pisca
	C3.set_opacidade(
		_barra_tensao,
		(55.0 + 45.0 * absf(C3.sin_g(_tempo * 900.0))) if tensao > 75.0 else 100.0,
	)

	_placar.text = "Peixes: " + C3.num(peixes) + "   |   Total: " + C3.num(total_kg) + " kg"

	# Estado 0 e perto da agua
	if estado == 0 and perto_agua:
		_status.text = "Segure ESPAÇO para carregar e solte para lançar"

	# Estado 0 e longe da agua
	if estado == 0 and not perto_agua:
		_status.text = "Vá até a ponta do cais  (← →)"


# --------------------------- Apoio do runtime ---------------------------

## Equivale a acao "Aguardar" do C3: o resto do evento roda depois do tempo,
## seguindo o time scale do jogo.
func _esperar(segundos: float) -> void:
	await get_tree().create_timer(segundos, true, false, false).timeout


## Equivale a condicao "Disparar uma vez enquanto verdadeiro" do C3: so passa no
## primeiro tick em que as condicoes anteriores do evento ficaram verdadeiras.
func _gatilho_unico(chave: StringName) -> bool:
	var anterior: int = _gatilhos.get(chave, -1)
	_gatilhos[chave] = _quadro
	return anterior != _quadro - 1
