extends CenaDePesca

## Os dois pesqueiros rio abaixo, seguindo o caderno do avo. A pesca e a mesma
## do acude (scripts/acude.gd); aqui fica so a historia de cada lugar:
##
##   Foz e Vila  chegada .... o Velho Juca, que pescava com o avo
##               captura .... com FOZ_PARA_BOIA especies daqui, a boia do
##                            avo vem enroscada na linha e abre o Arvoredo
##   Arvoredo    chegada .... o radio de bordo: o avo fisgou o Velho do
##                            Arvoredo e nao cortou a linha
##               captura .... o Velho do Arvoredo fecha o jogo
##
## Nenhuma mecanica nova: os gatilhos sao a colecao (Partida.especies_pegas_em)
## e o peixe especial do Arvoredo (Partida._especial_liberado).

@export var id_local: StringName = &"foz"


func _ready() -> void:
	super()
	Partida.local = id_local
	_chegada.call_deferred()


func _chegada() -> void:
	match id_local:
		&"foz":
			if not Partida.juca_conhecido:
				Partida.juca_conhecido = true
				await _conhecer_juca()
		&"arvoredo":
			if not Partida.radio_ouvido:
				Partida.radio_ouvido = true
				await _ouvir_radio()


func _ao_capturar() -> void:
	# Deixa o peixe aparecer na mao antes de a conversa cobrir a tela.
	await _esperar(1.4)
	if id_local == &"foz" and not Partida.boia_achada \
			and Partida.especies_pegas_em(&"foz") >= Partida.FOZ_PARA_BOIA:
		Partida.boia_achada = true
		await _achar_boia()
	elif especie and especie.nome == Partida.NOME_VELHO:
		await _fim_do_jogo()


# ------------------------------- Foz e Vila -------------------------------

func _conhecer_juca() -> void:
	await _caixa.falar("", [
		"Na ponta do trapiche da vila, um velho remenda rede sentado num caixote.",
	])
	await _caixa.falar("Velho Juca", [
		"Tu é o neto do {avo}? Tem a cara dele quando era moço.",
		"Pescamos junto aqui na foz a vida inteira. Ele chegava de barco do açude, rio abaixo, com aquele caderno no bolso.",
		"Mas o que ele queria mesmo era o Arvoredo. Dizia que lá fora mora um mero do tamanho de um bote: o Velho do Arvoredo.",
		"Antes do mar, aprende a foz. Tainha e bagre na beira, corvina e linguado mais longe, robalo lá fora. Quem não conhece a foz não chega no mar.",
	])


func _achar_boia() -> void:
	var inicial: String = Partida.nome_avo.left(1).to_upper()
	await _caixa.falar("", [
		"Enroscada na linha vem uma boia velha de cortiça, gasta de sal.",
		"Riscada na tinta, uma letra: %s. Do jeito que o {avo} marcava as coisas dele." % inicial,
	])
	await _caixa.falar("Velho Juca", [
		"Essa boia é dele! Mas ela só podia ter vindo lá de fora, das ilhas...",
		"Ele sempre me disse que não passava da foz. O {avo} ia pro Arvoredo escondido de todo mundo.",
	])
	await _caixa.falar("{nome}", [
		"Então era pra lá que o caderno apontava. O Arvoredo já está no mapa do barco.",
	])


# -------------------------------- Arvoredo --------------------------------

func _ouvir_radio() -> void:
	await _caixa.falar("", [
		"Mar aberto. As ilhas do caderno, a mata descendo até a pedra e o farol lá no alto.",
		"O rádio velho do barco chia, e uma voz conhecida entra no canal.",
	])
	await _caixa.falar("Velho Juca (no rádio)", [
		"Juca na escuta... {nome}, tu chegou no Arvoredo? Então tem uma coisa que eu nunca contei.",
		"Na última saída do {avo}, ele me chamou nesse canal. Disse: \"Juca, fisguei o Velho do Arvoredo. Não vou cortar a linha.\"",
		"Depois disso, só chiado. O rio levou ele dias depois, e eu nunca soube se o peixe ficou ou se foi.",
		"Conhece os peixes da ilha primeiro. O Velho só aparece pra quem sabe pescar ali, e só lá no fundo, com linha comprida.",
	])


func _fim_do_jogo() -> void:
	Partida.velho_pescado = true
	# O Velho nao vai para o balde: ninguem vende esse peixe.
	for i in range(Partida.balde.size() - 1, -1, -1):
		if Partida.balde[i].especie.nome == Partida.NOME_VELHO:
			Partida.balde.remove_at(i)
			break

	await _caixa.falar("", [
		"O Velho do Arvoredo fica parado na beira da pedra, cansado como {nome}.",
		"No canto da boca dele tem um anzol enferrujado, e preso no anzol, a ponta de uma linha de náilon.",
		"A linha do {avo}. Ele não cortou.",
	])
	var i: int = await _caixa.escolher("{nome}", "E agora?", [
		"Cortar a linha e devolver ao mar",
		"Levar o Velho para a vila",
	])
	var linhas: PackedStringArray = []
	if i == 1:
		Partida.velho_devolvido = false
		await _caixa.falar("", [
			"A vila inteira vem ver o peixe do {avo}. A foto fica pendurada na parede da venda.",
			"No caderno, {nome} anota o último ponto com a data de hoje.",
		])
		linhas = [
			"{nome} trouxe o Velho do Arvoredo para a vila.",
			"Todo mundo conhece agora o peixe que o {avo} perseguiu a vida inteira.",
			"Mas, às vezes, olhando a foto, {nome} pensa no que o {avo} teria feito.",
		]
	else:
		Partida.velho_devolvido = true
		await _caixa.falar("", [
			"{nome} corta a linha rente ao anzol e solta o peixe.",
			"O Velho do Arvoredo afunda devagar e some no azul, do jeito que chegou.",
		])
		await _caixa.falar("{nome}", [
			"O vô não cortou a linha porque não queria soltar. Eu corto porque agora eu sei ficar.",
		])
		linhas = [
			"{nome} devolveu o Velho do Arvoredo ao mar.",
			"O caderno do {avo} está completo, e a casa dele está de pé na beira do açude.",
			"Aprender a pescar, no fim, era aprender a ficar.",
		]
	_saindo = true
	TelaFinal.mostrar(self, linhas)
