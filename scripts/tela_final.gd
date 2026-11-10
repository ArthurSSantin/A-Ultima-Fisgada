class_name TelaFinal
extends CanvasLayer

## Tela do fim do jogo, depois do Velho do Arvoredo: o epilogo e o resumo da
## partida. ESPACO volta para a tela inicial, e dali da para jogar de novo.
##
##     TelaFinal.mostrar(self, ["linha do epilogo", ...])

const CENA_INICIO: String = "res://scenes/Inicio.tscn"
## Tempo antes de aceitar o ESPACO, para ninguem pular o fim sem querer.
const ESPERA: float = 2.0

var epilogo: PackedStringArray = []
var _pronta: bool = false


static func mostrar(dono: Node, linhas: PackedStringArray) -> TelaFinal:
	var tela := TelaFinal.new()
	tela.epilogo = linhas
	dono.add_child(tela)
	return tela


func _ready() -> void:
	layer = 20
	var fundo := ColorRect.new()
	fundo.color = Color(0.05, 0.10, 0.20, 0.97)
	fundo.size = Vector2(1280, 720)
	add_child(fundo)

	var pegas: int = 0
	var todas: Array[Especie] = Partida.todas_especies()
	for e in todas:
		if Partida.colecao.has(e.nome):
			pegas += 1

	var linhas: PackedStringArray = ["FIM", ""]
	linhas.append_array(epilogo)
	linhas.append_array([
		"",
		"Dias de pesca: %d   |   Tempo de jogo: %d min" % [Partida.dia, roundi(Partida.minutos_jogados())],
		"Peixes pescados: %d   |   Total vendido: R$ %d" % [Partida.total_peixes, Partida.total_vendido],
		"Coleção: %d de %d espécies" % [pegas, todas.size()],
	])
	for id: StringName in Partida.COMPRADORES:
		linhas.append("%s: relação nível %d (+%d%% no preço)" % [
			Partida.COMPRADORES[id].nome, Partida.relacao[id], Partida.bonus_em_porcento(id),
		])
	linhas.append("Venda do %s: %s" % [
		Partida.nome_avo, "reaberta!" if Partida.obra_paga(&"venda") else "ainda de pé só na lembrança",
	])

	var texto := Label.new()
	texto.text = Partida.nome_em("\n".join(linhas))
	texto.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	texto.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	texto.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	texto.position = Vector2(140, 0)
	texto.size = Vector2(1000, 680)
	texto.add_theme_font_size_override("font_size", 20)
	texto.add_theme_color_override("font_color", Color(0.96, 0.94, 0.86))
	add_child(texto)

	var dica := Label.new()
	dica.text = "ESPAÇO volta para a tela inicial"
	dica.position = Vector2(0, 676)
	dica.size = Vector2(1280, 30)
	dica.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	dica.add_theme_font_size_override("font_size", 14)
	dica.add_theme_color_override("font_color", Color(0.62, 0.68, 0.74))
	dica.modulate.a = 0.0
	add_child(dica)

	await get_tree().create_timer(ESPERA).timeout
	_pronta = true
	create_tween().tween_property(dica, "modulate:a", 1.0, 0.6)


func _input(evento: InputEvent) -> void:
	if _pronta and evento.is_action_pressed(&"espaco"):
		get_viewport().set_input_as_handled()
		_pronta = false
		get_tree().change_scene_to_file.call_deferred(CENA_INICIO)
