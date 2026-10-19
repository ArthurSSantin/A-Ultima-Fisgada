class_name Minijogo
extends RefCounted

## Minijogo de captura no estilo Stardew Valley, na vertical: segure ESPACO para
## a zona verde subir e solte para ela cair. Enquanto o peixe estiver dentro da
## zona o progresso sobe; fora dela, desce. Chegou a 100 o peixe e seu, chegou a
## 0 ele escapa. Peixe mais pesado se move mais rapido.
##
## So tem a logica, sem nos nem desenho, para poder ser usado por qualquer cena
## de pesca e testado sem abrir o jogo (ver tools/harness). Coordenadas sao da
## trilha: 0 e a base, TRILHA_ALTURA e o topo.

enum Resultado { CONTINUA, CAPTUROU, ESCAPOU }

## Altura util da trilha, igual a das barras do HUD.
const TRILHA_ALTURA: float = 240.0
## Segurando ESPACO a zona sobe; solta, a gravidade puxa de volta.
const ZONA_EMPUXO: float = 1400.0
const ZONA_GRAVIDADE: float = 620.0
const ZONA_VEL_MAX: float = 400.0
## Progresso comeca parcialmente cheio e some se o peixe ficar fora da zona.
const PROGRESSO_INICIAL: float = 40.0
const PROGRESSO_GANHO: float = 24.0
const PROGRESSO_PERDA: float = 18.0
## Velocidade do peixe = VEL_BASE + peso x VEL_POR_KG, em px/s.
const VEL_BASE: float = 60.0
const VEL_POR_KG: float = 28.0

## Nenhum perfil das especies leva o peixe abaixo do PISO. A zona verde parada
## no fundo cobre de 0 ate a altura dela; se o peixe ficasse ali, saia sem o
## jogador apertar nada (o robalo saia assim 97% das vezes).
const PISO: float = 64.0

## Perfis de briga do GDD (secao 1.5). Cada especie usa um deles; "padrao" e o
## movimento do prototipo e so fica para os testes. Os numeros vem de
## tools/harness/harness.mjs.
##   tempo: de quanto em quanto tempo o peixe escolhe um destino novo (s)
##   vel: multiplicador da velocidade
##   alvo: faixa da trilha onde ele escolhe o destino; "perto" usa a distancia
##         maxima a partir da posicao atual em vez de uma faixa fixa
##   salto: chance de, ao trocar de destino, disparar para outra faixa
const PERFIS: Dictionary = {
	&"padrao": {"tempo": Vector2(0.35, 1.5), "vel": 1.0, "alvo": Vector2(8.0, 232.0)},
	&"calmo": {"tempo": Vector2(0.9, 2.0), "vel": 0.8, "perto": 60.0},
	&"nervoso": {"tempo": Vector2(0.2, 0.6), "vel": 1.1, "perto": 90.0},
	&"pesado": {"tempo": Vector2(0.8, 1.6), "vel": 0.75, "extremos": true},
	&"saltador": {
		"tempo": Vector2(0.5, 1.2), "vel": 1.0, "alvo": Vector2(PISO, 150.0),
		"salto": {"chance": 0.15, "alvo": Vector2(215.0, 232.0), "vel": 2.0, "tempo": Vector2(0.3, 0.5)},
	},
	&"mergulhador": {
		"tempo": Vector2(0.6, 1.3), "vel": 1.0, "alvo": Vector2(PISO, 110.0),
		"salto": {"chance": 0.25, "alvo": Vector2(150.0, 232.0), "vel": 1.8, "tempo": Vector2(0.3, 0.6)},
	},
}

## Tamanho da zona verde. Fica na instancia porque o Cafezinho aumenta; o cais
## usa Partida.ZONA_NORMAL.
var zona_altura: float = 64.0
var progresso: float = 0.0
## Base da zona verde e a velocidade dela.
var zona_pos: float = 0.0
var zona_vel: float = 0.0
## Centro do peixe na trilha, e o ponto para onde ele esta indo.
var peixe_pos: float = 0.0
var peixe_alvo: float = 0.0
var peixe_tempo: float = 0.0
var peso: float = 0.0

var _perfil: Dictionary = PERFIS[&"padrao"]
var _vel_mult: float = 1.0


func iniciar(peso_peixe: float, perfil: StringName = &"padrao") -> void:
	peso = peso_peixe
	_perfil = PERFIS[perfil]
	_vel_mult = _perfil.vel
	progresso = PROGRESSO_INICIAL
	zona_pos = (TRILHA_ALTURA - zona_altura) * 0.5
	zona_vel = 0.0
	peixe_pos = TRILHA_ALTURA * 0.5
	peixe_alvo = peixe_pos
	peixe_tempo = 0.0


## Avanca um tick. segurando = ESPACO pressionado neste tick.
func passo(delta: float, segurando: bool) -> Resultado:
	# Zona verde: empuxo enquanto segura, gravidade sempre.
	if segurando:
		zona_vel += ZONA_EMPUXO * delta
	zona_vel -= ZONA_GRAVIDADE * delta
	zona_vel = clampf(zona_vel, -ZONA_VEL_MAX, ZONA_VEL_MAX)
	zona_pos += zona_vel * delta

	var limite: float = TRILHA_ALTURA - zona_altura
	if zona_pos <= 0.0:
		zona_pos = 0.0
		zona_vel = 0.0
	elif zona_pos >= limite:
		zona_pos = limite
		zona_vel = 0.0

	# Peixe: escolhe um ponto novo de tempos em tempos e nada ate ele.
	peixe_tempo -= delta
	if peixe_tempo <= 0.0:
		_novo_destino()
	peixe_pos = move_toward(peixe_pos, peixe_alvo, (VEL_BASE + peso * VEL_POR_KG) * _vel_mult * delta)

	# Progresso
	if peixe_pos >= zona_pos and peixe_pos <= zona_pos + zona_altura:
		progresso += PROGRESSO_GANHO * delta
	else:
		progresso -= PROGRESSO_PERDA * delta
	progresso = clampf(progresso, 0.0, 100.0)

	if progresso >= 100.0:
		return Resultado.CAPTUROU
	if progresso <= 0.0:
		return Resultado.ESCAPOU
	return Resultado.CONTINUA


func _novo_destino() -> void:
	var p: Dictionary = _perfil
	if p.has("salto") and randf() < p.salto.chance:
		peixe_alvo = randf_range(p.salto.alvo.x, p.salto.alvo.y)
		peixe_tempo = randf_range(p.salto.tempo.x, p.salto.tempo.y)
		_vel_mult = p.vel * p.salto.vel
		return

	if p.has("perto"):
		peixe_alvo = clampf(peixe_pos + randf_range(-p.perto, p.perto), PISO, TRILHA_ALTURA - 8.0)
	elif p.has("extremos"):
		peixe_alvo = randf_range(PISO, 100.0) if randf() < 0.5 else randf_range(200.0, 232.0)
	else:
		peixe_alvo = randf_range(p.alvo.x, p.alvo.y)
	peixe_tempo = randf_range(p.tempo.x, p.tempo.y)
	_vel_mult = p.vel
