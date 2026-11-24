class_name Fontes
extends RefCounted

## A fonte do jogo: Jersey 10, pixelada e com os acentos do portugues
## (licenca SIL OFL 1.1, em assets/fontes/OFL.txt).
##
##     label.add_theme_font_override("font", Fontes.normal())
##
## O projeto tambem usa ela como fonte padrao (gui/theme/custom_font), entao
## um Label sem fonte propria ja sai pixelado.
##
## O arquivo em assets/fontes/ e a Jersey 10 ampliada em 4/3 (unitsPerEm de
## 1400 para 1050). Desenhada assim ela sai pequena; ampliada, ocupa o mesmo
## espaco da Arial que o jogo usava, e nenhum tamanho de fonte das cenas
## precisou mudar. As setas (← →) nao existem nela e saem da fonte do sistema.
##
## negrito() devolve a mesma fonte: a Jersey ja e encorpada, e o destaque fica
## por conta do tamanho, da cor e do contorno. Os chamadores continuam pedindo
## negrito() para o caso de trocar a fonte um dia.

const ARQUIVO: FontFile = preload("res://assets/fontes/Jersey10.ttf")


static func normal() -> Font:
	return ARQUIVO


static func negrito() -> Font:
	return ARQUIVO
