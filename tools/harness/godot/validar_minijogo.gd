extends SceneTree

## Roda o minijogo de verdade (cena Acude) com um bot e mede a taxa de
## captura por peso. Serve para validar a replica do minijogo em
## tools/harness/harness.mjs: os dois usam o mesmo modelo de jogador.
##
## Uso: godot --headless --fixed-fps 60 --path . -s tools/harness/godot/validar_minijogo.gd -- [tentativas] [perfil]
##
## Imprime uma linha JSON comecando com "RESULTADO ".

const PESOS: Array[float] = [0.5, 1.0, 2.0, 3.0, 4.5, 6.0, 7.0]

## Mesmos parametros de JOGADORES em harness.mjs.
const JOGADORES: Dictionary = {
	"iniciante": {"reacao": 0.28, "ruido": 22.0, "decisao": 0.08, "antecipa": 0.10},
	"medio": {"reacao": 0.20, "ruido": 14.0, "decisao": 0.05, "antecipa": 0.15},
	"bom": {"reacao": 0.14, "ruido": 8.0, "decisao": 0.033, "antecipa": 0.18},
}


class Bot:
	extends Node

	var jogo: Node
	var tentativas: int = 200
	var perfil: StringName = &"padrao"
	var resultado: Dictionary = {}
	var fila: Array = []

	var _atual: Array = []
	var _t: float = 0.0
	var _hist: Array[float] = []
	var _ruido: float = 0.0
	var _prox_ruido: float = 0.0
	var _prox_decisao: float = 0.0
	var _segurando: bool = false
	var _peixes_antes: int = 0
	var _ativo: bool = false

	func _ready() -> void:
		process_priority = -100
		for nome in JOGADORES:
			for peso in PESOS:
				for i in tentativas:
					fila.append([nome, peso])

	func _process(delta: float) -> void:
		if _ativo and jogo.estado != 4:
			var chave: String = "%s|%s" % [_atual[0], _atual[1]]
			if not resultado.has(chave):
				resultado[chave] = [0, 0, 0.0]
			resultado[chave][0] += 1 if jogo.peixes > _peixes_antes else 0
			resultado[chave][1] += 1
			resultado[chave][2] += _t
			_ativo = false

		if not _ativo:
			if fila.is_empty():
				Input.action_release(&"espaco")
				var saida: Dictionary = {}
				for chave in resultado:
					var r: Array = resultado[chave]
					saida[chave] = {"taxa": float(r[0]) / r[1], "duracao": r[2] / r[1], "n": r[1]}
				print("RESULTADO ", JSON.stringify(saida))
				get_tree().quit()
				return
			_iniciar(fila.pop_front())

		var j: Dictionary = JOGADORES[_atual[0]]
		var mj: Minijogo = jogo.minijogo
		_hist.append(mj.peixe_pos)
		if _t >= _prox_ruido:
			_ruido = randfn(0.0, j.ruido)
			_prox_ruido = _t + 0.1
		if _t >= _prox_decisao:
			var atraso: int = roundi(j.reacao / delta)
			var visto: float = _hist[maxi(0, _hist.size() - 1 - atraso)] + _ruido
			var centro: float = mj.zona_pos + mj.zona_altura / 2.0 + mj.zona_vel * j.antecipa
			_segurando = centro < visto
			_prox_decisao = _t + j.decisao
		if _segurando:
			Input.action_press(&"espaco")
		else:
			Input.action_release(&"espaco")
		_t += delta

	func _iniciar(caso: Array) -> void:
		_atual = caso
		_t = 0.0
		_hist.clear()
		_prox_ruido = 0.0
		_prox_decisao = 0.0
		_segurando = false
		_peixes_antes = jogo.peixes
		_ativo = true
		_entrar_no_minijogo(caso[1])

	## Coloca a cena no mesmo estado que a fisgada deixa.
	func _entrar_no_minijogo(peso: float) -> void:
		jogo.peso_peixe = peso
		jogo.estado = 4
		jogo.minijogo.iniciar(peso, perfil)


func _initialize() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var cena: Node = load("res://scenes/Acude.tscn").instantiate()
	root.add_child(cena)
	var bot := Bot.new()
	bot.jogo = cena
	if args.size() > 0:
		bot.tentativas = int(args[0])
	if args.size() > 1:
		bot.perfil = StringName(args[1])
	root.add_child(bot)
