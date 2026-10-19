class_name Especie
extends Resource

## Uma especie de peixe. Os arquivos ficam em dados/especies/ e os valores vem
## de docs/design-fase1.md.
##
## A forca do arremesso define a distancia, e cada especie vive numa faixa de
## forca. Dentro da faixa, quanto mais forca, mais pesado e mais valioso.

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


func alcancavel(forca: float) -> bool:
	return forca >= forca_min and forca <= forca_max


## Posicao (0 a 1) da forca dentro da faixa da especie.
func fracao(forca: float) -> float:
	return clampf(inverse_lerp(forca_min, forca_max, forca), 0.0, 1.0)


func peso_para(forca: float) -> float:
	return lerpf(peso_min, peso_max, fracao(forca))


func valor_para(peso: float) -> int:
	return roundi(lerpf(valor_min, valor_max, inverse_lerp(peso_min, peso_max, peso)))
