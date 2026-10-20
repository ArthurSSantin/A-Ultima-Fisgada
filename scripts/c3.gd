class_name C3
extends RefCounted

## Funcoes que reproduzem a semantica do runtime do Construct 3 onde ela difere
## da do Godot:
##
## - trigonometria: o C3 trabalha em graus, o Godot em radianos;
## - opacidade: 0 a 100 no C3, modulate.a de 0 a 1 no Godot;
## - largura/altura: pixels no C3, escala da textura no Godot;
## - texto: o operador "&" do C3 imprime numeros sem zeros sobrando ("4", nao "4.0");
## - colisao: sprites sem rotacao no C3 colidem pela caixa da imagem.


static func sin_g(graus: float) -> float:
	return sin(deg_to_rad(graus))


static func cos_g(graus: float) -> float:
	return cos(deg_to_rad(graus))


static func set_opacidade(no: CanvasItem, valor: float) -> void:
	no.modulate.a = clampf(valor, 0.0, 100.0) / 100.0


static func opacidade(no: CanvasItem) -> float:
	return no.modulate.a * 100.0


## Equivale a acao "Definir largura" do C3: a imagem passa a ocupar px pixels,
## respeitando o ponto de origem configurado no sprite.
static func set_largura(sp: Sprite2D, px: float) -> void:
	sp.scale.x = px / float(sp.texture.get_width())


## Equivale a acao "Definir altura" do C3.
static func set_altura(sp: Sprite2D, px: float) -> void:
	sp.scale.y = px / float(sp.texture.get_height())


## Caixa da imagem em coordenadas globais, que e o que o C3 usa para testar
## sobreposicao de sprites sem rotacao.
## get_rect() ja considera offset, centered e um quadro so de hframes/vframes.
static func caixa(sp: Sprite2D) -> Rect2:
	var local: Rect2 = sp.get_rect()
	return Rect2(sp.global_position + local.position * sp.scale, local.size * sp.scale.abs())


## Equivale a condicao "Esta sobrepondo outro objeto" do C3.
static func sobrepondo(a: Sprite2D, b: Sprite2D) -> bool:
	return caixa(a).intersects(caixa(b))


## Converte numero em texto como o C3 faz ao concatenar com "&":
## 4.0 -> "4", 1.5 -> "1.5", 2.7999999 -> "2.8".
static func num(valor: float) -> String:
	var texto: String = "%.10f" % valor
	if texto.contains("."):
		texto = texto.rstrip("0").rstrip(".")
	return texto
