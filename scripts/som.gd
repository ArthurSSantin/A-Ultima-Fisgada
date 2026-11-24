extends Node

## Todo o som do jogo passa por aqui (autoload "Som"): a musica, o ambiente de
## cada lugar e os efeitos.
##
##     Som.tocar("moeda")                     # efeito solto
##     Som.letra("Vô")                        # o tic do texto, na voz de quem fala
##     var trote := Som.laco("cavalo_trote", self)   # laco que morre com a cena
##     Som.abafar_musica(true)                # a musica baixa durante as falas
##
## O volume de cada efeito fica no CATALOGO, num lugar so, para o mix ficar
## coerente: os arquivos em assets/sons/ ja saem nivelados de
## tools/sons/gerar_sons.py, e aqui so se decide quem fica na frente.
##
## O ambiente troca sozinho com a cena (AMBIENTES), em fusao, e nao recomeca
## quando duas cenas seguidas usam o mesmo (o lago continua do cais ao acude).
## Enquanto houver um temporal na cena, o ambiente e a chuva.
##
## Barramentos: Musica, Ambiente, Efeitos e Interface, todos no Master.

const PASTA: String = "res://assets/sons/"

## "Gone Fishin'", Memoraphile @ You're Perfect Studio (OpenGameArt, CC0).
const MUSICA: String = "res://assets/musica/fundo.mp3"
const VOLUME_MUSICA_DB: float = -20.0
## Quanto a musica baixa enquanto uma caixa de dialogo esta aberta.
const ABAFADO_DB: float = -6.0

## nome: [volume em dB, variacao de tom (+-), barramento]
const CATALOGO: Dictionary = {
	# pescaria
	"lancamento": [0.0, 0.08, &"Efeitos"],
	"isca_agua": [-1.0, 0.08, &"Efeitos"],
	"mordida": [-13.0, 0.04, &"Efeitos"],
	"fisgada": [-5.0, 0.05, &"Efeitos"],
	"carretilha": [-16.0, 0.10, &"Efeitos"],
	"captura": [-14.0, 0.0, &"Efeitos"],
	"conquista": [-11.0, 0.0, &"Efeitos"],
	"escapou": [-15.0, 0.0, &"Efeitos"],
	# bichos e casa
	"latido": [-7.0, 0.03, &"Efeitos"],
	"ronrom": [-8.0, 0.0, &"Efeitos"],
	"cavalo_bufo": [-9.0, 0.04, &"Efeitos"],
	"cavalo_trote": [-7.0, 0.0, &"Efeitos"],
	"batida": [-4.0, 0.0, &"Efeitos"],
	"trovao": [-3.0, 0.06, &"Efeitos"],
	# interface
	"texto": [-24.0, 0.0, &"Interface"],
	"cursor": [-17.0, 0.0, &"Interface"],
	"confirmar": [-18.0, 0.0, &"Interface"],
	"moeda": [-16.0, 0.0, &"Interface"],
	# ambientes (lacos)
	"ambiente_lago": [-16.0, 0.0, &"Ambiente"],
	"mar": [-16.0, 0.0, &"Ambiente"],
	"chuva": [-12.0, 0.0, &"Ambiente"],
}

## Ambiente de cada cena; cena fora da lista fica so com a musica.
const AMBIENTES: Dictionary = {
	"res://scenes/Inicio.tscn": "mar",
	"res://scenes/Cais.tscn": "mar",
	"res://scenes/Acude.tscn": "ambiente_lago",
	"res://scenes/Foz.tscn": "mar",
	"res://scenes/Arvoredo.tscn": "mar",
	"res://scenes/tutorial/Descida.tscn": "ambiente_lago",
	"res://scenes/tutorial/CaisRio.tscn": "ambiente_lago",
	"res://scenes/tutorial/MeioDoRio.tscn": "ambiente_lago",
}

## A voz de cada um no tic do texto (pitch_scale). Quem nao esta aqui ganha
## um tom fixo tirado do nome.
const VOZES: Dictionary = {
	"Vô": 0.78, "Vó": 1.18, "Dona Marlene": 1.12, "Seu Valdir": 0.86,
	"Zeca": 0.96, "Dona Maria Ivone": 1.08, "Velho Juca": 0.72, "": 1.0,
}

## Quantos tocam ao mesmo tempo, por efeito; o resto corta o mais antigo.
const VOZES_POR_EFEITO: int = 3

var _efeitos: Dictionary = {}
var _musica: AudioStreamPlayer
var _ambiente: AudioStreamPlayer
var _ambiente_nome: String = ""
var _cena: Node = null
var _temporais: int = 0
var _letras: int = 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for nome in [&"Musica", &"Ambiente", &"Efeitos", &"Interface"]:
		if AudioServer.get_bus_index(nome) == -1:
			AudioServer.add_bus()
			AudioServer.set_bus_name(AudioServer.bus_count - 1, nome)
			AudioServer.set_bus_send(AudioServer.bus_count - 1, &"Master")

	var faixa: AudioStreamMP3 = load(MUSICA)
	faixa.loop = true
	_musica = AudioStreamPlayer.new()
	_musica.stream = faixa
	_musica.bus = &"Musica"
	_musica.volume_db = -60.0
	add_child(_musica)
	_musica.play()
	create_tween().tween_property(_musica, "volume_db", VOLUME_MUSICA_DB, 2.0)


func _process(_delta: float) -> void:
	var cena: Node = get_tree().current_scene
	if cena != _cena:
		_cena = cena
		_ambiente_da_cena()


## Toca um efeito do CATALOGO. `tom` multiplica a altura (o tom de cada voz,
## a beliscada mais aguda que a mordida).
func tocar(nome: String, tom: float = 1.0, volume_extra_db: float = 0.0) -> void:
	var dados: Array = CATALOGO[nome]
	var p: AudioStreamPlayer = _efeitos.get(nome)
	if p == null:
		p = AudioStreamPlayer.new()
		p.stream = load(PASTA + nome + ".ogg")
		p.bus = dados[2]
		p.max_polyphony = VOZES_POR_EFEITO
		add_child(p)
		_efeitos[nome] = p
	p.volume_db = dados[0] + volume_extra_db
	p.pitch_scale = tom * (1.0 + randf_range(-dados[1], dados[1]))
	p.play()


## O tic de uma letra, na voz de quem fala. Toca uma letra sim, outra nao,
## para o texto nao virar metralhadora.
func letra(quem: String) -> void:
	_letras += 1
	if _letras % 2 == 0:
		return
	var tom: float = VOZES.get(quem, 0.9 + float(absi(hash(quem)) % 30) / 100.0)
	tocar("texto", tom * randf_range(0.97, 1.03))


## Um laco (trote, carretilha) que pertence a `dono` e some junto com ele.
## Comeca no volume do CATALOGO; quem chama pode mexer em volume_db.
func laco(nome: String, dono: Node) -> AudioStreamPlayer:
	var stream: AudioStream = load(PASTA + nome + ".ogg").duplicate()
	stream.set(&"loop", true)
	var p := AudioStreamPlayer.new()
	p.stream = stream
	p.bus = CATALOGO[nome][2]
	p.volume_db = volume(nome)
	dono.add_child(p)
	p.play()
	return p


## O volume de um som no CATALOGO, para quem controla o proprio laco.
func volume(nome: String) -> float:
	return CATALOGO[nome][0]


## Some com um laco em `segundos` e libera o no.
func soltar(p: AudioStreamPlayer, segundos: float = 0.4) -> void:
	if not is_instance_valid(p):
		return
	var t := p.create_tween()
	t.tween_property(p, "volume_db", -60.0, segundos)
	t.tween_callback(p.queue_free)


func abafar_musica(sim: bool) -> void:
	var alvo: float = VOLUME_MUSICA_DB + (ABAFADO_DB if sim else 0.0)
	create_tween().tween_property(_musica, "volume_db", alvo, 0.35 if sim else 0.8)


## Troca o ambiente em fusao. "" deixa so a musica.
func ambiente(nome: String, segundos: float = 1.5) -> void:
	if nome == _ambiente_nome:
		return
	_ambiente_nome = nome
	if _ambiente:
		soltar(_ambiente, segundos)
		_ambiente = null
	if nome.is_empty():
		return
	_ambiente = laco(nome, self)
	_ambiente.volume_db = -60.0
	# comeca num ponto sorteado, para a repeticao nao se notar
	_ambiente.play(randf_range(0.0, _ambiente.stream.get_length()))
	create_tween().tween_property(_ambiente, "volume_db", volume(nome), segundos)


## O Temporal avisa quando entra e sai da cena: enquanto houver um, chove.
func temporal_entrou() -> void:
	_temporais += 1
	ambiente("chuva", 0.8)


func temporal_saiu() -> void:
	_temporais = maxi(_temporais - 1, 0)
	_ambiente_da_cena.call_deferred()


func _ambiente_da_cena() -> void:
	if _temporais > 0:
		ambiente("chuva", 0.8)
		return
	var cena: Node = get_tree().current_scene
	ambiente(AMBIENTES.get(cena.scene_file_path, "") if cena else "")
