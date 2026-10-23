extends CenaTutorial

## O cais do vo no rio, nas duas pontas da pescaria. Na ida os cavalos ficam
## amarrados no moirao e o bote espera no trapiche. Na volta
## (Partida.volta_do_rio) os dois desembarcam, desamarram os cavalos e pegam
## a estrada de volta montados.

const CENA_DESCIDA: String = "res://scenes/tutorial/Descida.tscn"
const CENA_ESTRADA: String = "res://scenes/tutorial/Estrada.tscn"


func _ready() -> void:
	if Partida.volta_do_rio:
		$Player.position.x = 760.0
		$Player.flip_h = true
		$Vo.position.x = 820.0
	super._ready()


func _ao_entrar() -> void:
	await escurecer(false, 0.8)
	if Partida.volta_do_rio:
		Partida.concluir(&"cais")
		await falar("Vô", ["Desamarra o Alexandre. Ele já tá com fome também."])
	else:
		await falar("Vô", ["Amarra o Alexandre ali no moirão. Nó bem dado, senão ele volta pra casa sozinho."])


func _dica_atual() -> String:
	if Partida.volta_do_rio:
		return "Monte no Alexandre pra voltar pra casa."
	return "O bote espera na ponta do trapiche."


func _acao(nome: StringName) -> String:
	match nome:
		&"Bote": return "Olhar o bote" if Partida.volta_do_rio else "Embarcar"
		&"Alexandre": return "Montar no Alexandre" if Partida.volta_do_rio else "Olhar o cavalo"
		&"Apollo": return "Olhar o cavalo"
	return "Olhar"


func _interagir(nome: StringName) -> void:
	match nome:
		&"Alexandre":
			if Partida.volta_do_rio:
				som("cavalo_bufo")
				await falar("{nome}", ["Bora pra casa, Alexandre."])
				await falar("Vô", ["Devagarinho, que a barriga dele tá cheia de capim."])
				ir_para(CENA_ESTRADA)
			else:
				await falar("", ["O Alexandre, amarrado no moirão, já arrancando um tufo de capim."])
		&"Apollo":
			som("cavalo_bufo")
			await falar("", ["O Apollo cochila em pé, com uma pata dobrada."])
		&"Bote":
			if Partida.volta_do_rio:
				await falar("", ["O bote de volta no trapiche, ainda pingando."])
			else:
				await falar("Vô", ["Senta no meio, que é pra não virar. Isso."])
				ir_para(CENA_DESCIDA)
