extends Node2D

## Logica do jogo, originalmente traduzida da folha "Folha de eventos 1" do
## projeto Construct 3 PescaAlfa.
##
## Andar, carregar o arremesso, esperar a mordida, fisgar e o resultado seguem o
## original, inclusive na ordem dos eventos, porque a folha depende dela. Dois
## exemplos:
##
## - em "Lancamento", o evento que arremessa (Estado = 1) vem antes do que zera a
##   forca, e por isso a forca do arremesso sobrevive ao tick;
## - em "Movimento", pertoAgua e zerada todo tick e so volta a valer no evento
##   seguinte, quando o Player esta sobre a ZonaPesca.
##
## A fase de puxada NAO segue mais o original: no lugar da dupla tensao e
## resistencia entrou um minijogo no estilo Stardew Valley (ver _grupo_minijogo).
##
## Estados: 0 parado | 1 lancando | 2 esperando mordida | 3 fisgada
##          4 minijogo | 5 capturado | 6 falhou | 7 reset

const ESQUERDA: StringName = &"mover_esquerda"
const DIREITA: StringName = &"mover_direita"
const ESPACO: StringName = &"espaco"

# --- minijogo de captura ---
## Altura util da trilha e o Y da base dela na tela, iguais aos das barras.
const TRILHA_ALTURA: float = 240.0
const TRILHA_BASE_Y: float = 290.0
## Tamanho da zona verde que o jogador controla.
const ZONA_ALTURA: float = 64.0
## Segurando ESPACO a zona sobe; solta, a gravidade puxa de volta.
const ZONA_EMPUXO: float = 1400.0
const ZONA_GRAVIDADE: float = 620.0
const ZONA_VEL_MAX: float = 400.0
## Progresso comeca parcialmente cheio e some se o peixe ficar fora da zona.
const PROGRESSO_INICIAL: float = 40.0
const PROGRESSO_GANHO: float = 24.0
const PROGRESSO_PERDA: float = 18.0

# --- variaveis globais da folha de eventos ---
var estado: int = 0
var forca: float = 0.0
var direcao_forca: float = 1.0
var pos_lancamento: float = 0.0
var peso_peixe: float = 0.0
var peixes: int = 0
var total_kg: float = 0.0

# --- estado do minijogo, em coordenadas da trilha (0 = base, 240 = topo) ---
var progresso: float = 0.0
## Base da zona verde.
var zona_pos: float = 0.0
var zona_vel: float = 0.0
## Centro do peixe na trilha, e o ponto para onde ele esta indo.
var peixe_pos: float = 0.0
var peixe_alvo: float = 0.0
var peixe_tempo: float = 0.0

## Variavel de instancia "pertoAgua" da ZonaPesca. Vive aqui porque o layout tem
## uma unica instancia dela e o resto do codigo inteiro le esse valor.
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
@onready var _zona_captura: Sprite2D = $UI/ZonaCaptura
@onready var _peixe_marcador: Sprite2D = $UI/PeixeMarcador
@onready var _barra_progresso: Sprite2D = $UI/BarraFillProgresso
@onready var _placar: Label = $UI/Placar


func _ready() -> void:
	C3.set_altura(_zona_captura, ZONA_ALTURA)


func _process(delta: float) -> void:
	_quadro += 1
	_tempo += delta

	# No C3 os behaviors rodam antes dos eventos do tick.
	_mover.tick(delta)

	_grupo_movimento()
	_grupo_lancamento(delta)
	_grupo_espera_e_fisgada(delta)
	_grupo_minijogo(delta)
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
		_isca.position = Vector2(pos_lancamento, 478.0)
		_isca.visible = true
		_linha.visible = true
		_peixe.frame = 0
		_depois_do_lancamento()


func _depois_do_lancamento() -> void:
	await _esperar(0.5)
	if estado == 1:
		estado = 2


# --------------------------- Espera e fisgada ---------------------------

func _grupo_espera_e_fisgada(delta: float) -> void:
	# Entrou no Estado 2
	if estado == 2 and _gatilho_unico(&"espera"):
		C3.set_opacidade(_peixe, 0.0)
		_peixe.visible = true
		_depois_da_espera(randf_range(1.5, 4.0))

	# Isca balancando de leve e peixe rondando
	if estado == 2:
		_isca.position.y = 478.0 + 2.0 * C3.sin_g(_tempo * 150.0)
		_peixe.position = Vector2(_isca.position.x + 90.0 * C3.cos_g(_tempo * 70.0), 545.0)
		C3.set_opacidade(_peixe, minf(C3.opacidade(_peixe) + 30.0 * delta, 45.0))

	# Apertou ESPACO antes da mordida
	if Input.is_action_just_pressed(ESPACO) and estado == 2:
		estado = 6

	# Entrou no Estado 3
	if estado == 3 and _gatilho_unico(&"fisgada"):
		_depois_da_fisgada()

	# Janela da fisgada: a isca chacoalha forte, que e o aviso de que mordeu
	if estado == 3:
		_isca.position.y = 486.0 + 8.0 * C3.sin_g(_tempo * 1400.0)
		_peixe.position = Vector2(_isca.position.x + 36.0, 520.0)
		C3.set_opacidade(_peixe, 70.0)

	# Fisgou dentro da janela: comeca o minijogo
	if Input.is_action_just_pressed(ESPACO) and estado == 3:
		estado = 4
		progresso = PROGRESSO_INICIAL
		zona_pos = (TRILHA_ALTURA - ZONA_ALTURA) * 0.5
		zona_vel = 0.0
		peixe_pos = TRILHA_ALTURA * 0.5
		peixe_alvo = peixe_pos
		peixe_tempo = 0.0


func _depois_da_espera(segundos: float) -> void:
	await _esperar(segundos)
	if estado == 2:
		estado = 3


func _depois_da_fisgada() -> void:
	await _esperar(0.9)
	if estado == 3:
		estado = 6


# ------------------------------- Minijogo -------------------------------

## Minijogo no estilo Stardew Valley, na vertical: segure ESPACO para a zona
## verde subir e solte para ela cair. Enquanto o peixe estiver dentro da zona o
## progresso sobe; fora dela, desce. Chegou a 100 o peixe e seu, chegou a 0 ele
## escapa. Peixe mais pesado se move mais rapido.
func _grupo_minijogo(delta: float) -> void:
	if estado != 4:
		return

	# Zona verde: empuxo enquanto segura, gravidade sempre.
	if Input.is_action_pressed(ESPACO):
		zona_vel += ZONA_EMPUXO * delta
	zona_vel -= ZONA_GRAVIDADE * delta
	zona_vel = clampf(zona_vel, -ZONA_VEL_MAX, ZONA_VEL_MAX)
	zona_pos += zona_vel * delta

	var limite: float = TRILHA_ALTURA - ZONA_ALTURA
	if zona_pos <= 0.0:
		zona_pos = 0.0
		zona_vel = 0.0
	elif zona_pos >= limite:
		zona_pos = limite
		zona_vel = 0.0

	# Peixe: escolhe um ponto novo de tempos em tempos e nada ate ele.
	peixe_tempo -= delta
	if peixe_tempo <= 0.0:
		peixe_alvo = randf_range(8.0, TRILHA_ALTURA - 8.0)
		peixe_tempo = randf_range(0.35, 1.5)
	peixe_pos = move_toward(peixe_pos, peixe_alvo, (70.0 + peso_peixe * 18.0) * delta)

	# Progresso
	if peixe_pos >= zona_pos and peixe_pos <= zona_pos + ZONA_ALTURA:
		progresso += PROGRESSO_GANHO * delta
	else:
		progresso -= PROGRESSO_PERDA * delta
	progresso = clampf(progresso, 0.0, 100.0)

	# A isca e o peixe na agua vem chegando conforme o progresso sobe.
	_isca.position = Vector2(
		lerpf(pos_lancamento, 640.0, progresso / 100.0),
		484.0 + 3.0 * C3.sin_g(_tempo * 900.0),
	)
	_peixe.position = Vector2(
		_isca.position.x + 34.0 + 8.0 * C3.sin_g(_tempo * 500.0),
		_isca.position.y + 36.0,
	)

	if progresso >= 100.0:
		estado = 5
	elif progresso <= 0.0:
		estado = 6


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
		direcao_forca = 1.0
		progresso = 0.0
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
	C3.set_altura(_barra_progresso, (progresso / 100.0) * 240.0)

	# A trilha do minijogo so aparece durante o minijogo.
	_zona_captura.visible = estado == 4
	_peixe_marcador.visible = estado == 4
	if estado == 4:
		_zona_captura.position.y = TRILHA_BASE_Y - zona_pos
		_peixe_marcador.position.y = TRILHA_BASE_Y - peixe_pos

	_placar.text = "Peixes: " + C3.num(peixes) + "   |   Total: " + C3.num(total_kg) + " kg"


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
