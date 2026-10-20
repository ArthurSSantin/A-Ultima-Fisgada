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
## resistencia entrou um minijogo no estilo Stardew Valley (ver scripts/minijogo.gd).
## Tambem sao novos, para a Beta: a vara limita a forca, a especie e sorteada pela
## forca (scripts/partida.gd), a beliscada falsa, os bonus da loja e a energia:
## lancar e brigar com o peixe cansam, e sem energia o Tiago volta para o hub.
##
## Estados: 0 parado | 1 lancando | 2 esperando mordida | 3 fisgada
##          4 minijogo | 5 capturado | 6 falhou | 7 reset

const ESQUERDA: StringName = &"mover_esquerda"
const DIREITA: StringName = &"mover_direita"
const ESPACO: StringName = &"espaco"

const CENA_HUB: String = "res://scenes/Hub.tscn"

## Y da base da trilha do minijogo na tela, igual ao das barras. As constantes
## do minijogo ficam em scripts/minijogo.gd.
const TRILHA_BASE_Y: float = 290.0

## Encostou na borda esquerda do cais: volta para a Loja de Pesca.
const SAIDA_X: float = 40.0

## Na agua e no minijogo o peixe e sempre a sombra generica, para a especie ser
## surpresa; so na captura aparece o sprite da especie (ou o peixe generico).
const SOMBRA_PEIXE: Texture2D = preload("res://assets/sprites/peixe-animation 1-000.png")
const PEIXE_GENERICO: Texture2D = preload("res://assets/sprites/peixe-animation 1-001.png")

# --- variaveis globais da folha de eventos ---
var estado: int = 0
var forca: float = 0.0
var direcao_forca: float = 1.0
var pos_lancamento: float = 0.0
var peso_peixe: float = 0.0
var peixes: int = 0
var total_kg: float = 0.0

var minijogo: Minijogo = Minijogo.new()

## Variavel de instancia "pertoAgua" da ZonaPesca. Vive aqui porque o layout tem
## uma unica instancia dela e o resto do codigo inteiro le esse valor.
var perto_agua: bool = false

## Especie sorteada no lancamento atual e os bonus que valem para ele.
var especie: Especie = null
var _bonus: Dictionary = {}
## Este lancamento tem beliscada falsa antes da mordida, e ela esta acontecendo.
var _tem_falsa: bool = false
var _beliscando: bool = false
## Numero do lancamento, para uma espera antiga nao mexer no lancamento seguinte.
var _lance: int = 0
var _saindo: bool = false

## Equivale a expressao System.time do C3: segundos desde o inicio do layout.
var _tempo: float = 0.0

## Contador de ticks, usado por _gatilho_unico.
var _quadro: int = 0
var _gatilhos: Dictionary = {}

var _caixa: CaixaDialogo

@onready var _player: Sprite2D = $Jogo/Player
@onready var _visual: VisualTiago = $Jogo/Player/Visual
@onready var _mover: EightDir = $Jogo/Player/OitoDirecoes
@onready var _zona_pesca: Sprite2D = $Jogo/ZonaPesca
@onready var _isca: Sprite2D = $Jogo/Isca
@onready var _linha: Sprite2D = $Jogo/Linha
@onready var _peixe: Sprite2D = $Jogo/Peixe
@onready var _alerta: Label = $Jogo/Alerta
@onready var _barra_forca: Sprite2D = $UI/BarraFillForca
@onready var _zona_captura: Sprite2D = $UI/ZonaCaptura
@onready var _peixe_marcador: Sprite2D = $UI/PeixeMarcador
@onready var _barra_progresso: Sprite2D = $UI/BarraFillProgresso
@onready var _limite_forca: ColorRect = $UI/LimiteForca
@onready var _placar: Label = $UI/Placar
@onready var _dica: Label = $UI/Dica
@onready var _aviso: Label = $UI/Aviso


func _ready() -> void:
	_caixa = CaixaDialogo.new()
	add_child(_caixa)
	$UI.add_child(BarraEnergia.new())
	minijogo.zona_altura = Partida.ZONA_NORMAL
	C3.set_altura(_zona_captura, minijogo.zona_altura)
	# Marca na barra ate onde a vara deixa a forca chegar.
	_limite_forca.position.y = TRILHA_BASE_Y - Partida.forca_maxima() / 100.0 * 240.0
	_aviso.text = ""
	Partida.cais_visitado = true


func _process(delta: float) -> void:
	if _caixa.ocupada() or _saindo:
		return

	_quadro += 1
	_tempo += delta

	# No C3 os behaviors rodam antes dos eventos do tick.
	_mover.tick(delta)

	_grupo_movimento()
	_grupo_lancamento(delta)
	_grupo_espera_e_fisgada(delta)
	_grupo_minijogo(delta)
	_grupo_resultado(delta)
	_grupo_fim_do_dia()
	_grupo_interface()


# ------------------------------- Movimento -------------------------------

func _grupo_movimento() -> void:
	# Todo tick
	perto_agua = false
	_player.position.x = clampf(_player.position.x, SAIDA_X, 590.0)

	# Player esta sobrepondo ZonaPesca
	if C3.sobrepondo(_player, _zona_pesca):
		perto_agua = true

	# Na beira (ou pescando) a vara sai das costas e vai para a mao
	_visual.na_mao = perto_agua or estado != 0

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

	# Andou ate a borda esquerda: volta para a Loja de Pesca
	if estado == 0 and _player.position.x <= SAIDA_X and Input.is_action_pressed(ESQUERDA):
		_voltar_ao_hub()


# ------------------------------ Lancamento ------------------------------

func _grupo_lancamento(delta: float) -> void:
	# A vara limita ate onde a barra de forca sobe.
	var maxima: float = Partida.forca_maxima()
	var pode_lancar: bool = not Partida.cansado()

	# Forca vai e volta enquanto segura ESPACO
	if Input.is_action_pressed(ESPACO) and estado == 0 and perto_agua and pode_lancar:
		forca = clampf(forca + 90.0 * delta * direcao_forca, 0.0, maxima)

		if forca >= maxima:
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
		_lance += 1
		_player.flip_h = false
		pos_lancamento = 660.0 + (forca / 100.0) * 520.0
		_bonus = Partida.usar_lancamento(forca)
		especie = Partida.sortear_especie(forca, _bonus.camarao)
		peso_peixe = Partida.sortear_peso(especie, forca)
		_tem_falsa = not Partida.tutorial() and randf() < Partida.CHANCE_FALSA
		_beliscando = false
		minijogo.zona_altura = Partida.ZONA_CAFEZINHO if _bonus.cafezinho else Partida.ZONA_NORMAL
		C3.set_altura(_zona_captura, minijogo.zona_altura)
		_isca.position = Vector2(pos_lancamento, 478.0)
		_isca.visible = true
		_linha.visible = true
		_peixe.texture = SOMBRA_PEIXE
		_aviso.text = ""
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

	# Isca balancando de leve e peixe rondando. Na beliscada falsa a isca treme,
	# mas bem menos que na mordida de verdade.
	if estado == 2:
		if _beliscando:
			_isca.position.y = 480.0 + 3.0 * C3.sin_g(_tempo * 900.0)
		else:
			_isca.position.y = 478.0 + 2.0 * C3.sin_g(_tempo * 150.0)
		_peixe.position = Vector2(_isca.position.x + 90.0 * C3.cos_g(_tempo * 70.0), 545.0)
		_peixe.flip_h = C3.sin_g(_tempo * 70.0) > 0.0  # indo para a esquerda, vira
		C3.set_opacidade(_peixe, minf(C3.opacidade(_peixe) + 30.0 * delta, 45.0))

	# Apertou ESPACO antes da mordida
	if Input.is_action_just_pressed(ESPACO) and estado == 2:
		_aviso.text = "Era só uma beliscada!" if _beliscando else "Puxou cedo demais!"
		estado = 6

	# Entrou no Estado 3
	if estado == 3 and _gatilho_unico(&"fisgada"):
		_depois_da_fisgada()

	# Janela da fisgada: a isca chacoalha forte, que e o aviso de que mordeu
	if estado == 3:
		_isca.position.y = 486.0 + 8.0 * C3.sin_g(_tempo * 1400.0)
		_peixe.position = Vector2(_isca.position.x + 36.0, 520.0)
		_peixe.flip_h = true  # boca virada para a isca
		C3.set_opacidade(_peixe, 70.0)

	# O Modao destaca a mordida verdadeira; no tutorial ela tambem e marcada.
	_alerta.visible = estado == 3 and (_bonus.get(&"modao", false) or Partida.tutorial())
	_alerta.position = Vector2(_isca.position.x - 12.0, _isca.position.y - 70.0)

	# Fisgou dentro da janela: comeca o minijogo
	if Input.is_action_just_pressed(ESPACO) and estado == 3:
		estado = 4
		_peixe.flip_h = false  # foge para o mar
		minijogo.iniciar(peso_peixe, especie.perfil if especie else &"padrao")


func _depois_da_espera(segundos: float) -> void:
	var lance: int = _lance
	if _tem_falsa:
		# Belisca no meio da espera, para e so depois morde.
		await _esperar(segundos * randf_range(0.3, 0.6))
		if estado != 2 or lance != _lance:
			return
		_beliscando = true
		await _esperar(0.6)
		_beliscando = false
		if estado != 2 or lance != _lance:
			return
		await _esperar(randf_range(0.8, 1.6))
	else:
		await _esperar(segundos)
	if estado == 2 and lance == _lance:
		estado = 3


func _depois_da_fisgada() -> void:
	var lance: int = _lance
	var janela: float = Partida.JANELA_MODAO if _bonus.get(&"modao", false) else Partida.JANELA_FISGADA
	await _esperar(janela)
	if estado == 3 and lance == _lance:
		_aviso.text = "Demorou para fisgar."
		estado = 6


# ------------------------------- Minijogo -------------------------------

## A logica do minijogo fica em scripts/minijogo.gd; aqui so o tick e o desenho
## da isca e do peixe na agua.
func _grupo_minijogo(delta: float) -> void:
	if estado != 4:
		return

	var resultado: Minijogo.Resultado = minijogo.passo(delta, Input.is_action_pressed(ESPACO))
	Partida.gastar_energia(Partida.ENERGIA_LUTA_POR_S * delta)

	# A isca e o peixe na agua vem chegando conforme o progresso sobe.
	_isca.position = Vector2(
		lerpf(pos_lancamento, 640.0, minijogo.progresso / 100.0),
		484.0 + 3.0 * C3.sin_g(_tempo * 900.0),
	)
	_peixe.position = Vector2(
		_isca.position.x + 34.0 + 8.0 * C3.sin_g(_tempo * 500.0),
		_isca.position.y + 36.0,
	)

	if resultado == Minijogo.Resultado.CAPTUROU:
		estado = 5
	elif resultado == Minijogo.Resultado.ESCAPOU:
		_aviso.text = "O peixe escapou..."
		estado = 6


# ------------------------------- Resultado -------------------------------

func _grupo_resultado(delta: float) -> void:
	# Entrou no Estado 5
	if estado == 5 and _gatilho_unico(&"capturado"):
		peixes += 1
		total_kg = roundf((total_kg + peso_peixe) * 10.0) / 10.0
		if especie:
			_anunciar_captura()
		_isca.visible = false
		_linha.visible = false
		_peixe.texture = especie.sprite if especie and especie.sprite else PEIXE_GENERICO
		C3.set_opacidade(_peixe, 100.0)
		# A borda do peixe fica no mesmo lugar para qualquer tamanho (96 px -> +70).
		_peixe.position = Vector2(_player.position.x + 22.0 + _peixe.texture.get_width() * 0.5, 420.0)
		_peixe.flip_h = false
		_depois_da_captura()

	# Entrou no Estado 6
	if estado == 6 and _gatilho_unico(&"falhou"):
		_peixe.flip_h = false
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
		minijogo.progresso = 0.0
		_isca.visible = false
		_linha.visible = false
		_peixe.visible = false
		_peixe.texture = SOMBRA_PEIXE


func _anunciar_captura() -> void:
	var nova: bool = not Partida.colecao.has(especie.nome)
	var recorde: bool = Partida.registrar_captura(especie, peso_peixe)
	var texto: String = "%s, %s kg  (R$ %d)" % [especie.nome, C3.num(peso_peixe), especie.valor_para(peso_peixe)]
	if especie.raridade == Especie.Raridade.ESPECIAL:
		texto += "\nPEIXE ESPECIAL!"
	elif nova:
		texto += "\nEspécie nova na coleção!"
	elif recorde:
		texto += "\nNovo recorde!"
	_aviso.text = texto


func _depois_da_captura() -> void:
	await _esperar(2.2)
	if estado == 5:
		estado = 7


func _depois_da_falha() -> void:
	await _esperar(1.6)
	if estado == 6:
		estado = 7


# ------------------------------ Fim do dia ------------------------------

func _grupo_fim_do_dia() -> void:
	if estado == 0 and Partida.cansado() and _gatilho_unico(&"fim_do_dia"):
		_fim_do_dia()


func _fim_do_dia() -> void:
	await _caixa.falar("", ["Tiago está exausto. Hora de voltar para a Loja de Pesca, vender o balde e descansar."])
	_voltar_ao_hub()


func _voltar_ao_hub() -> void:
	if _saindo:
		return
	_saindo = true
	Partida.hub_x = 1100.0
	get_tree().change_scene_to_file.call_deferred(CENA_HUB)


# ------------------------------- Interface -------------------------------

func _grupo_interface() -> void:
	# Todo tick: linha ligando a vara na isca, barras e placar
	var mao: Vector2 = Vector2(_player.position.x + 30.0, _player.position.y - 46.0)
	var ponta: Vector2 = Vector2(_isca.position.x, _isca.position.y - 10.0)

	_linha.position = mao
	_linha.rotation = (ponta - mao).angle()
	C3.set_largura(_linha, mao.distance_to(ponta))

	C3.set_altura(_barra_forca, (forca / 100.0) * 240.0)
	C3.set_altura(_barra_progresso, (minijogo.progresso / 100.0) * 240.0)

	# A trilha do minijogo so aparece durante o minijogo.
	_zona_captura.visible = estado == 4
	_peixe_marcador.visible = estado == 4
	if estado == 4:
		_zona_captura.position.y = TRILHA_BASE_Y - minijogo.zona_pos
		_peixe_marcador.position.y = TRILHA_BASE_Y - minijogo.peixe_pos

	_placar.text = "Dia %d   |   R$ %d   |   Balde: %d peixes" % [
		Partida.dia, Partida.dinheiro, Partida.balde.size(),
	]
	var bonus: PackedStringArray = []
	for item in Partida.estoque:
		if Partida.estoque[item] > 0:
			bonus.append("%s: %d" % [Partida.ITENS[item].nome.get_slice(" (", 0), Partida.estoque[item]])
	if not bonus.is_empty():
		_placar.text += "\n" + "   ".join(bonus)

	_dica.text = _texto_da_dica()


## Tutorial pratico: no dia 1 cada passo tem uma dica; no dia 2 so a da
## beliscada, que e a novidade do dia.
func _texto_da_dica() -> String:
	if Partida.cansado() and estado == 0:
		return ""
	if Partida.dia == 2 and estado == 2:
		return "Cuidado: se a isca só tremer de leve, é beliscada. Espere a mordida forte."
	if Partida.dia == 2 and estado == 0:
		return "Quanto mais longe o lançamento, maiores os peixes."
	if not Partida.tutorial():
		return ""
	match estado:
		0:
			if not perto_agua:
				return "Use as setas para andar até a ponta do cais."
			return "Segure ESPAÇO para carregar a força e solte para lançar.\nHoje só tem parati na beira. Amanhã, lance mais longe para peixes maiores."
		1, 2:
			return "Agora espere... não aperte nada antes de o peixe morder."
		3:
			return "MORDEU! Aperte ESPAÇO!"
		4:
			return "Segure ESPAÇO para subir a barra verde e solte para descer.\nMantenha o peixe dentro dela até a barra de captura encher."
	return ""


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
