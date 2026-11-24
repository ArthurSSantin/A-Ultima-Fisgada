extends Node

## As configuracoes do jogador (autoload "Config"): volume e tela. Ficam em
## user://config.cfg, separadas do save, porque valem para qualquer partida.
##
##   volume geral ...... o barramento Master
##   musica ............ o barramento Musica
##   efeitos ........... Efeitos, Ambiente e Interface juntos
##   resolucao ......... tamanho da janela, ate 1920x1080
##   tela cheia ........ ou modo janela
##
## O jogo e desenhado em 1280x720 e a janela so escala (stretch canvas_items),
## entao trocar a resolucao nao muda nada do layout.
##
## Os testes ligam Engine.set_meta(&"sem_save", true) ou trocam `arquivo`, para
## nao mexer nas configuracoes de quem joga.

const ARQUIVO: String = "user://config.cfg"

const RESOLUCOES: Array[Vector2i] = [
	Vector2i(1280, 720),
	Vector2i(1366, 768),
	Vector2i(1600, 900),
	Vector2i(1920, 1080),
]
## De quanto em quanto as setas mexem no volume.
const PASSO_VOLUME: float = 0.1

var volume_geral: float = 1.0
var volume_musica: float = 0.8
var volume_efeitos: float = 1.0
var resolucao: int = 0
var tela_cheia: bool = false
## Onde as configuracoes ficam. Os testes trocam por outro arquivo.
var arquivo: String = ARQUIVO


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	carregar()
	# Depois do _ready do Som, que e quem cria os barramentos.
	aplicar.call_deferred()


func carregar() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(arquivo) != OK:
		return
	volume_geral = clampf(cfg.get_value("som", "geral", volume_geral), 0.0, 1.0)
	volume_musica = clampf(cfg.get_value("som", "musica", volume_musica), 0.0, 1.0)
	volume_efeitos = clampf(cfg.get_value("som", "efeitos", volume_efeitos), 0.0, 1.0)
	resolucao = clampi(cfg.get_value("tela", "resolucao", resolucao), 0, RESOLUCOES.size() - 1)
	tela_cheia = cfg.get_value("tela", "tela_cheia", tela_cheia)


func salvar() -> void:
	if Engine.get_meta(&"sem_save", false):
		return
	var cfg := ConfigFile.new()
	cfg.set_value("som", "geral", volume_geral)
	cfg.set_value("som", "musica", volume_musica)
	cfg.set_value("som", "efeitos", volume_efeitos)
	cfg.set_value("tela", "resolucao", resolucao)
	cfg.set_value("tela", "tela_cheia", tela_cheia)
	cfg.save(arquivo)


func aplicar() -> void:
	aplicar_som()
	aplicar_tela()


func aplicar_som() -> void:
	_volume_do_barramento(&"Master", volume_geral)
	_volume_do_barramento(&"Musica", volume_musica)
	for barramento in [&"Efeitos", &"Ambiente", &"Interface"]:
		_volume_do_barramento(barramento, volume_efeitos)


func aplicar_tela() -> void:
	if DisplayServer.get_name() == "headless":
		return
	if tela_cheia:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
		return
	if DisplayServer.window_get_mode() != DisplayServer.WINDOW_MODE_WINDOWED:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	var tela: int = DisplayServer.window_get_current_screen()
	var area: Rect2i = DisplayServer.screen_get_usable_rect(tela)
	var tamanho: Vector2i = RESOLUCOES[resolucao]
	DisplayServer.window_set_size(tamanho)
	DisplayServer.window_set_position(area.position + (area.size - tamanho) / 2)


## Resolucoes que cabem na tela deste computador (a primeira sempre entra).
func resolucoes_possiveis() -> Array[int]:
	var cabem: Array[int] = [0]
	var area: Vector2i = Vector2i(1920, 1080)
	if DisplayServer.get_name() != "headless":
		area = DisplayServer.screen_get_size(DisplayServer.window_get_current_screen())
	for i in range(1, RESOLUCOES.size()):
		if RESOLUCOES[i].x <= area.x and RESOLUCOES[i].y <= area.y:
			cabem.append(i)
	return cabem


static func texto_resolucao(i: int) -> String:
	return "%d x %d" % [RESOLUCOES[i].x, RESOLUCOES[i].y]


static func texto_volume(v: float) -> String:
	return "%d%%" % roundi(v * 100.0)


func _volume_do_barramento(nome: StringName, volume: float) -> void:
	var i: int = AudioServer.get_bus_index(nome)
	if i == -1:
		return
	AudioServer.set_bus_mute(i, volume <= 0.001)
	AudioServer.set_bus_volume_db(i, linear_to_db(maxf(volume, 0.001)))
