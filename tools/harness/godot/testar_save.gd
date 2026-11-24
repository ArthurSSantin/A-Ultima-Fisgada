extends SceneTree

## Teste do save, do menu inicial, do mapa de lugares, da pausa e das
## configuracoes. Grava em arquivos proprios (user://save_teste.json e
## user://config_teste.cfg) e apaga no fim, entao nao mexe no save nem nas
## configuracoes de quem joga.
##
## Uso: godot --headless --fixed-fps 60 --path . -s tools/harness/godot/testar_save.gd
##
## Sai com codigo 1 se alguma verificacao falhar.

const SAVE_TESTE: String = "user://save_teste.json"
const CONFIG_TESTE: String = "user://config_teste.cfg"

var _falhas: int = 0


func _initialize() -> void:
	Engine.set_meta(&"texto_instantaneo", true)
	_rodar.call_deferred()


func _rodar() -> void:
	var partida: Node = root.get_node("Partida")
	var config: Node = root.get_node("Config")
	var pausa: Node = root.get_node("Pausa")
	partida.arquivo_save = SAVE_TESTE
	config.arquivo = CONFIG_TESTE
	partida.apagar_save()

	# --- A Fase 1 nao salva ---
	partida.comecar_tutorial()
	_conferir(not partida.salvar(), "a Fase 1 nao grava save")
	_conferir(not partida.tem_save(), "sem save depois da Fase 1")

	# --- Sem save, o menu comeca pelos nomes ---
	change_scene_to_file("res://scenes/Inicio.tscn")
	await _quadros(5)
	var menu: Node = current_scene
	_conferir(not menu._tem_save, "menu sem save")
	_conferir(menu._opcoes.size() == 4, "sem save: Começar, Coleção, Configurações, Sair")
	await _apertar(&"espaco")
	_conferir(menu._nomes.visible, "Começar sem save pede os nomes")
	await _apertar(&"ui_cancel")
	_conferir(not menu._nomes.visible and menu._menu.visible, "ESC volta dos nomes para o menu")

	# --- Monta uma partida da Fase 2 e salva ---
	partida.definir_nome("Ana", "Lauro")
	partida.iniciar_fase(2)
	partida.dia = 5
	partida.dinheiro = 345
	partida.ganhar_vara(&"vo")
	partida.varas_compradas.append(&"bambu")
	partida.estoque[&"camarao"] = 3
	partida.obras_pagas.append(&"casa")
	partida.jundia_entregue = true
	partida.relacao[&"zeca"] = 2
	partida.caderno_achado = true
	partida.juca_conhecido = true
	partida.boia_achada = true
	partida.teimoso_solto = true
	partida.diario.append("Primeiro peixe: o Teimoso.")
	var tainha: Resource = partida.especie(&"Tainha")
	_conferir(tainha != null, "a tainha existe na Fase 2")
	partida.registrar_captura(tainha, 1.2)
	partida.registrar_captura(partida.especie(&"Tilápia"), 0.8)
	partida.visitar(&"vila")
	partida.visitar(&"foz")
	_conferir(partida.salvar(), "a Fase 2 grava o save")
	_conferir(partida.tem_save(), "o arquivo do save existe")

	# --- Zera a memoria e le de volta ---
	partida.comecar_tutorial()
	partida.definir_nome("", "")
	_conferir(partida.carregar(), "le o save")
	_conferir(partida.nome == "Ana" and partida.nome_avo == "Lauro", "nomes voltam")
	_conferir(partida.fase == 2 and partida.dia == 5, "fase e dia voltam")
	_conferir(partida.dinheiro == 345, "dinheiro volta (tem %d)" % partida.dinheiro)
	_conferir(partida.vara == &"vo" and &"bambu" in partida.varas_compradas, "varas voltam")
	_conferir(partida.estoque[&"camarao"] == 3, "estoque volta")
	_conferir(partida.obra_paga(&"casa") and partida.jundia_entregue, "obra e jundia voltam")
	_conferir(partida.relacao[&"zeca"] == 2, "relacionamento volta")
	_conferir(partida.caderno_achado and partida.boia_achada and partida.juca_conhecido, "historia volta")
	_conferir(partida.teimoso_solto and partida.diario.size() == 1, "memorias da Fase 1 voltam")
	_conferir(partida.balde.size() == 2 and partida.balde[0].especie.nome == "Tainha", "balde volta com as especies")
	_conferir(partida.colecao.has("Tainha") and is_equal_approx(partida.colecao["Tainha"].recorde_kg, 1.2), "colecao volta")
	_conferir(partida.lugares_visitados == [&"vila", &"foz"], "lugares visitados voltam")
	_conferir(partida.local_liberado(&"arvoredo"), "o Arvoredo segue liberado pela boia")

	# --- Entrar numa cena da Fase 2 marca a visita e salva sozinho ---
	partida.dia = 6
	change_scene_to_file("res://scenes/Acude.tscn")
	await _quadros(5)
	_conferir(&"acude" in partida.lugares_visitados, "entrar no acude marca a visita")
	var lido: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SAVE_TESTE))
	_conferir(int(lido.dia) == 6 and "acude" in lido.lugares_visitados, "entrar numa cena salva")

	# --- Dormir salva ---
	partida.dormir()
	lido = JSON.parse_string(FileAccess.get_file_as_string(SAVE_TESTE))
	_conferir(int(lido.dia) == 7, "dormir salva o dia seguinte")

	# --- O ESPACO que fecha um dialogo nao lanca a vara ---
	var acude: Node = current_scene
	acude.get_node("Jogo/Player").position.x = acude.get_node("Jogo/ZonaPesca").position.x
	acude._caixa.falar("", ["Uma fala qualquer."])
	await _quadros(2)
	await _segurar(&"espaco", true)  # fecha a fala e continua segurando
	await _quadros(40)
	_conferir(acude.estado == 0 and acude.forca == 0.0, "segurar o ESPACO que fechou a fala nao carrega a forca")
	await _segurar(&"espaco", false)
	await _quadros(3)
	_conferir(acude.estado == 0, "soltar esse ESPACO nao lanca")
	await _segurar(&"espaco", true)
	await _quadros(30)
	_conferir(acude.forca > 5.0, "um toque novo carrega a forca")
	await _segurar(&"espaco", false)
	await _quadros(2)
	_conferir(acude.estado != 0, "soltar o toque novo lanca a vara")
	change_scene_to_file("res://scenes/Acude.tscn")
	await _quadros(5)

	# --- Pausa: ESC para o jogo e ESC de novo volta ---
	await _apertar(&"ui_cancel")
	_conferir(pausa.aberta() and paused, "ESC no acude abre a pausa e para o jogo")
	await _apertar(&"ui_cancel")
	_conferir(not pausa.aberta() and not paused, "ESC fecha a pausa")
	pausa.abrir()
	await _quadros(2)
	await _apertar(&"ui_down")
	await _apertar(&"ui_down")
	await _apertar(&"espaco")
	_conferir(_tem_filho(pausa, "TelaConfig"), "a pausa abre as configuracoes")
	await _apertar(&"ui_cancel")
	_conferir(not _tem_filho(pausa, "TelaConfig") and pausa.aberta(), "ESC volta das configuracoes para a pausa")
	await _apertar(&"ui_down")
	await _apertar(&"espaco")
	await _quadros(5)
	_conferir(current_scene.name == "Inicio" and not paused, "Voltar ao menu leva a tela inicial")

	# --- Com save, o menu continua pelo mapa de lugares ---
	menu = current_scene
	_conferir(menu._tem_save, "menu com save")
	_conferir(menu._opcoes.size() == 5, "com save aparece Novo jogo")
	await _apertar(&"espaco")
	var mapa: Node = _filho_da_classe(menu, "MapaLocais")
	_conferir(mapa != null, "Continuar abre o mapa")
	if mapa:
		_conferir(mapa._locais.size() == 3, "mapa com os 3 lugares visitados (tem %d)" % mapa._locais.size())
		_conferir(mapa._locais[0].id == &"vila", "a vila vem primeiro no mapa")
		await _apertar(&"ui_down")  # vila -> acude
		await _apertar(&"ui_down")  # acude -> foz
		await _apertar(&"espaco")
		await _quadros(5)
		_conferir(current_scene.name == "Foz", "escolher a Foz no mapa leva para a Foz")
		_conferir(partida.local == &"foz", "o pesqueiro de agora vira a Foz")

	# --- Novo jogo pede confirmacao e so apaga o save ao comecar ---
	change_scene_to_file("res://scenes/Inicio.tscn")
	await _quadros(5)
	menu = current_scene
	await _apertar(&"ui_down")
	await _apertar(&"espaco")
	_conferir(menu._caixa.aberta, "Novo jogo pede confirmacao")
	await _apertar(&"espaco")  # "Não, voltar"
	await _quadros(2)
	_conferir(partida.tem_save() and menu._menu.visible, "Não mantem o save")

	# --- Configuracoes ---
	config.volume_musica = 0.5
	config.volume_efeitos = 0.0
	config.aplicar_som()
	var musica: int = AudioServer.get_bus_index(&"Musica")
	var efeitos: int = AudioServer.get_bus_index(&"Efeitos")
	_conferir(absf(AudioServer.get_bus_volume_db(musica) - linear_to_db(0.5)) < 0.01, "volume da musica no barramento")
	_conferir(AudioServer.is_bus_mute(efeitos), "efeitos em 0% ficam mudos")
	_conferir(config.resolucoes_possiveis().has(0), "1280x720 sempre disponivel")
	var tela: Node = load("res://scripts/tela_config.gd").new()
	root.add_child(tela)
	await _quadros(2)
	var seta_menos: Label = tela._lista._itens[1].setas[0]
	var seta_mais: Label = tela._lista._itens[1].setas[1]
	var clique := InputEventMouseButton.new()
	clique.button_index = MOUSE_BUTTON_LEFT
	clique.pressed = true
	seta_menos.gui_input.emit(clique)
	_conferir(is_equal_approx(config.volume_musica, 0.4), "clicar no < baixa a musica (%.2f)" % config.volume_musica)
	seta_mais.gui_input.emit(clique)
	seta_mais.gui_input.emit(clique)
	_conferir(is_equal_approx(config.volume_musica, 0.6), "clicar no > sobe a musica (%.2f)" % config.volume_musica)
	tela.queue_free()
	_conferir(config.RESOLUCOES[-1] == Vector2i(1920, 1080), "vai ate 1920x1080")

	partida.apagar_save()
	_conferir(not partida.tem_save(), "apaga o save de teste")
	_conferir(FileAccess.file_exists(CONFIG_TESTE), "fechar as configuracoes grava o arquivo")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(CONFIG_TESTE))

	print("FALHAS ", _falhas)
	quit(1 if _falhas > 0 else 0)


func _tem_filho(no: Node, nome_classe: String) -> bool:
	return _filho_da_classe(no, nome_classe) != null


## Pelo nome, e nao pelo tipo: citar a classe aqui faria o script compilar
## antes dos autoloads existirem.
func _filho_da_classe(no: Node, nome_classe: String) -> Node:
	for filho in no.get_children():
		if filho.get_script() and filho.get_script().get_global_name() == nome_classe:
			return filho
	return null


func _apertar(acao: StringName) -> void:
	var evento := InputEventAction.new()
	evento.action = acao
	evento.pressed = true
	Input.parse_input_event(evento)
	await _quadros(2)
	var solta := InputEventAction.new()
	solta.action = acao
	solta.pressed = false
	Input.parse_input_event(solta)
	await _quadros(2)


func _segurar(acao: StringName, apertado: bool) -> void:
	var evento := InputEventAction.new()
	evento.action = acao
	evento.pressed = apertado
	Input.parse_input_event(evento)
	await _quadros(2)


func _quadros(n: int) -> void:
	for i in n:
		await process_frame


func _conferir(ok: bool, o_que: String) -> void:
	if ok:
		print("ok    ", o_que)
	else:
		_falhas += 1
		print("FALHA ", o_que)
