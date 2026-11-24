extends SceneTree

## A partida da demonstracao do final (build "Windows Final", feature
## demo_final): confere o estado pronto para o Arvoredo, o radio, a mordida do
## Velho e a tela final.
##
##     godot --headless --fixed-fps 60 --path . -s tools/harness/godot/testar_demo.gd

var falhas: int = 0

func _initialize() -> void:
	Engine.set_meta(&"sem_save", true)
	_rodar.call_deferred()

func _q(n: int) -> void:
	for i in n:
		await process_frame

func _ok(c: bool, o: String) -> void:
	print(("ok    " if c else "FALHA ") + o)
	if not c: falhas += 1

## Evento de verdade, como o do teclado: a CaixaDialogo le pelo _input.
func _apertar(acao: StringName) -> void:
	for apertado in [true, false]:
		var ev := InputEventAction.new()
		ev.action = acao
		ev.pressed = apertado
		Input.parse_input_event(ev)
		await _q(2)

## Fecha as falas ate a cena ficar livre. Na escolha do Velho o ESPACO fica
## com a primeira opcao, devolver ao mar.
func _fechar(cena: Node) -> void:
	var livre: int = 0
	while livre < 4:
		await _q(2)
		if not is_instance_valid(cena) or not cena.is_inside_tree():
			return
		if cena._caixa.aberta:
			livre = 0
			await _apertar(&"espaco")
		else:
			livre += 1


## Pelo nome, e nao pelo tipo: citar a classe aqui faria o script compilar
## antes dos autoloads existirem.
func _tem_filho(no: Node, nome_classe: String) -> bool:
	for filho in no.get_children():
		if filho.get_script() and filho.get_script().get_global_name() == nome_classe:
			return true
	return false


func _rodar() -> void:
	var p: Node = root.get_node("Partida")
	p.preparar_demo_final()
	_ok(p.fase == 2 and p.vara == &"vo" and p.forca_maxima() == 100.0, "fase 2 com a vara do avo")
	_ok(p.local_liberado(&"foz") and p.local_liberado(&"arvoredo"), "Foz e Arvoredo liberados")
	_ok(p.especies_pegas_em(&"arvoredo") == 3 and p.especies_pegas_em(&"foz") == 5, "colecao: 5 da Foz e 3 do Arvoredo")
	_ok(p.lugares_abertos().size() == 4, "os 4 lugares no mapa do menu")
	_ok(not p.obra_paga(&"venda") and p.dinheiro >= p.OBRAS[&"venda"].preco, "venda por pagar, com dinheiro")
	_ok(p.colecao.size() == p.COLECAO_DEMO.size(), "todas as especies da demo existem")
	change_scene_to_file(p.entrar_em(&"arvoredo"))
	await _q(10)
	var cena: Node = current_scene
	_ok(cena.name == "Arvoredo", "entrou no Arvoredo")
	await _fechar(cena)
	_ok(p.radio_ouvido, "o radio tocou na chegada")
	var velhos: int = 0
	for i in 1000:
		if p.sortear_especie(90.0, false).nome == p.NOME_VELHO: velhos += 1
	print("Velho em 1000 lancamentos com forca 90: ", velhos)
	_ok(velhos > 200, "o Velho morde com forca alta")
	# captura do Velho, como no testar_fluxo
	cena.get_node("Jogo/Player").position.x = 572.0
	await _q(2)
	Input.action_press(&"espaco"); await _q(20); Input.action_release(&"espaco")
	for i in 600:
		if cena.estado == 3: break
		await process_frame
	cena.especie = p.especie(StringName(p.NOME_VELHO))
	cena.peso_peixe = 160.0
	await _apertar(&"espaco")
	cena.minijogo.progresso = 99.9
	cena.minijogo.peixe_pos = cena.minijogo.zona_pos + 10.0
	await _q(300)
	await _fechar(cena)
	var final: bool = _tem_filho(cena, "TelaFinal")
	_ok(p.velho_pescado and final, "pescou o Velho e a tela final apareceu")
	print("FALHAS ", falhas)
	quit()
