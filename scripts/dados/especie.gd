class_name Especie
extends Resource

## Uma especie de peixe. Os arquivos ficam em dados/especies/ e os valores vem
## de docs/design-fase1.md.
##
## A forca do arremesso define a distancia, e cada especie vive numa faixa de
## forca. Dentro da faixa, quanto mais forca, mais pesado e mais valioso. A
## forca e so a tendencia: o peso sai sorteado em volta dela (ver desvio_peso),
## e de vez em quando vem um exemplar trofeu, acima do peso_max da especie.

enum Raridade { COMUM, INCOMUM, RARO, ESPECIAL }

@export var nome: String = ""
## Perfil de briga, uma das chaves de Minijogo.PERFIS.
@export var perfil: StringName = &"padrao"
@export var fase: int = 1
@export var raridade: Raridade = Raridade.COMUM
@export_range(0, 100) var forca_min: float = 0.0
@export_range(0, 100) var forca_max: float = 100.0
@export var peso_min: float = 0.5
@export var peso_max: float = 1.0
@export var valor_min: int = 10
@export var valor_max: int = 20

## Espalhamento do peso em volta do que a forca sugere, como fracao da faixa da
## especie (desvio padrao de uma normal). Em 0 o peso vira funcao direta da
## forca; quanto maior, menos o arremesso garante o tamanho do peixe.
@export_range(0.0, 0.6) var desvio_peso: float = 0.18
## Chance, por captura, de sair um exemplar trofeu: um peixe acima do peso_max.
## So vale para arremessos na parte de cima da faixa (ver FRACAO_TROFEU).
@export_range(0.0, 1.0) var chance_trofeu: float = 0.04
## Quanto um trofeu passa do peso_max, no maximo, como fracao dele.
@export_range(0.0, 1.0) var bonus_trofeu: float = 0.35

## Peixe revelado na captura (arte 4x, virado para a direita).
@export var sprite: Texture2D
## Sombra que aparece na agua antes da captura.
@export var sombra: Texture2D
## Coloracoes alternativas do peixe capturado. Com alguma aqui, cada captura
## sorteia entre o sprite e elas (a joaninha do rio tem quatro).
@export var variantes: Array[Texture2D] = []

## Um trofeu so pode sair se a forca ja estiver nesta altura da faixa. Sem isso
## um arremesso curto na beira poderia render o maior peixe da especie.
const FRACAO_TROFEU: float = 0.6
## Limites de quanto o peixe capturado encolhe ou cresce na tela, do peso_min ao
## peso_max. Trofeus passam do teto, ate ESCALA_MAXIMA.
const ESCALA_MINIMA: float = 0.8
const ESCALA_NO_MAXIMO: float = 1.15
const ESCALA_MAXIMA: float = 1.45


## O sprite que aparece nesta captura, ja com a coloracao sorteada.
func sprite_da_captura() -> Texture2D:
	if variantes.is_empty():
		return sprite
	var todas: Array[Texture2D] = []
	if sprite:
		todas.append(sprite)
	todas.append_array(variantes)
	return todas.pick_random()


func alcancavel(forca: float) -> bool:
	return forca >= forca_min and forca <= forca_max


## Posicao (0 a 1) da forca dentro da faixa da especie.
func fracao(forca: float) -> float:
	return clampf(inverse_lerp(forca_min, forca_max, forca), 0.0, 1.0)


func peso_para(forca: float) -> float:
	return lerpf(peso_min, peso_max, fracao(forca))


## Fora da faixa normal da especie: o peixe de parede.
func e_trofeu(peso: float) -> bool:
	return peso > peso_max


## O valor acompanha o peso e continua subindo acima do peso_max, que e o que
## faz um trofeu valer a pena.
## Peixe de peso fixo (o Teimoso) vale sempre o valor_min, e nenhum peixe vale
## menos de R$ 1.
func valor_para(peso: float) -> int:
	return maxi(roundi(lerpf(valor_min, valor_max, _posicao(peso))), maxi(valor_min, 1))


## Onde o peso cai na faixa da especie (0 no peso_min, 1 no peso_max; passa de
## 1 no trofeu). Faixa de um peso so da 0, em vez de dividir por zero.
func _posicao(peso: float) -> float:
	if is_equal_approx(peso_min, peso_max):
		return 0.0
	return maxf(inverse_lerp(peso_min, peso_max, peso), 0.0)


## Tamanho na tela do peixe capturado: o mesmo sprite encolhe nos exemplares
## pequenos e cresce nos grandes, para o peso dar para ver.
func escala_para(peso: float) -> float:
	var t: float = _posicao(peso)
	return clampf(lerpf(ESCALA_MINIMA, ESCALA_NO_MAXIMO, t), ESCALA_MINIMA, ESCALA_MAXIMA)
