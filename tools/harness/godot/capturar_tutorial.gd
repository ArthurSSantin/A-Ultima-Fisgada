extends SceneTree

## Tira um PNG de cada cena do tutorial sem a cortina preta nem a caixa de
## dialogo da abertura, para conferir a arte montada.
##
## Uso (precisa de janela): godot --path . -s tools/harness/godot/capturar_tutorial.gd -- <pasta de saida>

const CENAS: Array[String] = ["Quarto", "Cozinha", "Terreiro", "CaisRio", "Estrada", "Descida", "Subida", "MeioDoRio", "Fim"]


func _initialize() -> void:
	_rodar.call_deferred()


func _rodar() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var saida: String = args[0] if args.size() > 0 else "user://"
	root.get_node("Partida").definir_nome("Tiago", "Bento")
	root.get_node("Partida").vara = &"bambu"
	for nome in CENAS:
		var cena: Node = load("res://scenes/tutorial/%s.tscn" % nome).instantiate()
		root.add_child(cena)
		for i in 150:
			await process_frame
			_limpar(cena)
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("%s/t_%s.png" % [saida, nome])
		print("salvo ", nome)
		cena.queue_free()
		await process_frame
	quit()


func _limpar(no: Node) -> void:
	for filho in no.get_children():
		if filho is CanvasLayer and filho.layer >= 10:
			filho.visible = false
		if filho.name == "Comboio":
			(filho as Node2D).position.x = 560.0
