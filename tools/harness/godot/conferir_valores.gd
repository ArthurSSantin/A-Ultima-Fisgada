extends SceneTree

## Sorteia 500 pesos de cada especie (das duas fases) e confere que peso e
## valor saem sempre positivos e com texto legivel, sem "0 kg" nem R$ negativo.
##
## Uso: godot --headless --path . -s tools/harness/godot/conferir_valores.gd

func _initialize() -> void:
	var partida: Node = root.get_node("Partida")
	var falhas: int = 0
	for fase in [1, 2]:
		partida.fase = fase
		partida.carregar_especies()
		for e: Especie in partida.especies:
			var menor: int = 1 << 30
			var maior: int = -1
			var exemplo: String = ""
			for i in 500:
				var forca: float = randf_range(e.forca_min, e.forca_max)
				var peso: float = partida.sortear_peso(e, forca)
				var valor: int = e.valor_para(peso)
				if peso <= 0.0 or valor <= 0 or valor > 100000:
					falhas += 1
					print("FALHA %s: peso %s valor %d" % [e.nome, peso, valor])
					break
				menor = mini(menor, valor)
				maior = maxi(maior, valor)
				exemplo = partida.texto_peso(peso)
			print("fase %d  %-16s R$ %d a %d   ex.: %s" % [fase, e.nome, menor, maior, exemplo])
	print("FALHAS ", falhas)
	quit(1 if falhas > 0 else 0)
