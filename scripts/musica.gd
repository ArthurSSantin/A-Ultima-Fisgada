extends AudioStreamPlayer

## Musica de fundo do jogo inteiro (autoload "Musica"): toca em loop, baixinho,
## por baixo dos sons das cenas, e nao recomeca quando a cena troca.

## "Gone Fishin'", Memoraphile @ You're Perfect Studio (OpenGameArt, CC0).
const FAIXA: String = "res://assets/musica/fundo.mp3"
## Volume baixo, para nao brigar com as falas e os sons do rio.
const VOLUME_DB: float = -20.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var faixa: AudioStreamMP3 = load(FAIXA)
	faixa.loop = true
	stream = faixa
	volume_db = VOLUME_DB
	play()
