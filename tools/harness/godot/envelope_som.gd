extends SceneTree

## Toca um som e imprime o volume (RMS) a cada 100 ms, para achar onde estao
## os latidos, a bufada etc. dentro de uma gravacao longa.
##
## Uso (precisa de janela, para o audio rodar): godot --path . -s tools/harness/godot/envelope_som.gd -- res://assets/sons/latido.mp3

func _initialize() -> void:
	_rodar.call_deferred()


func _rodar() -> void:
	var caminho: String = OS.get_cmdline_user_args()[0]
	var bus: int = AudioServer.bus_count
	AudioServer.add_bus(bus)
	AudioServer.set_bus_name(bus, "Analise")
	AudioServer.set_bus_mute(bus, false)
	var cap := AudioEffectCapture.new()
	cap.buffer_length = 1.0
	AudioServer.add_bus_effect(bus, cap)
	var p := AudioStreamPlayer.new()
	p.stream = load(caminho)
	p.bus = "Analise"
	root.add_child(p)
	p.play()
	var taxa: float = AudioServer.get_mix_rate()
	var bloco: int = int(taxa * 0.1)
	var acumulado := PackedVector2Array()
	var t: float = 0.0
	var linha: String = ""
	while p.playing:
		await process_frame
		acumulado.append_array(cap.get_buffer(cap.get_frames_available()))
		while acumulado.size() >= bloco:
			var soma: float = 0.0
			for i in bloco:
				var s: Vector2 = acumulado[i]
				soma += (s.x * s.x + s.y * s.y) * 0.5
			acumulado = acumulado.slice(bloco)
			var rms: float = sqrt(soma / bloco)
			linha += "%.1f:%d " % [t, int(rms * 1000)]
			t += 0.1
	print(caminho, " ", "%.1f s" % t)
	print(linha)
	quit()
