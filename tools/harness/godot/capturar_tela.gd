extends SceneTree

## Salva um PNG de uma cena, para conferir a arte sem abrir o editor.
##
## Uso (precisa de janela; em servidor use xvfb-run):
##   godot --path . -s tools/harness/godot/capturar_tela.gd -- <cena.tscn> <saida.png> [casa_pronta 0|1] [vara] [x do jogador]
##
## Ex.: ... -- res://scenes/Acude.tscn acude.png 0 fibra 555


func _initialize() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var cena: String = args[0] if args.size() > 0 else "res://scenes/Acude.tscn"
	var saida: String = args[1] if args.size() > 1 else "user://tela.png"
	var partida: Node = root.get_node("Partida")
	partida.set("prologo_visto", true)
	if args.size() > 2 and args[2] == "1":
		partida.obras_pagas.append(&"casa")
	if args.size() > 3 and args[3] != "":
		partida.set("vara", StringName(args[3]))
	var no: Node = load(cena).instantiate()
	root.add_child(no)
	if args.size() > 4:
		await process_frame
		(no.find_child("Player", true, false) as Node2D).position.x = float(args[4])
	for i in 8:
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png(saida)
	print("salvo: ", saida)
	quit()
