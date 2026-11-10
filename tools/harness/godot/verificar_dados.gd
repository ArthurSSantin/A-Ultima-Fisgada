extends SceneTree

## Confere os dados de dados/especies/ contra as regras de design e aponta
## inconsistencias. Sai com codigo 1 se achar algum erro.
##
## Uso: godot --headless --path . -s tools/harness/godot/verificar_dados.gd -- [forca_bambu] [forca_fibra]
##
## As forcas maximas das varas ainda nao sao dados do jogo; por isso vem por
## argumento (padrao: os valores de docs/design-fase1.md, 60 e 85).

const PASTA: String = "res://dados/especies/"

var _erros: int = 0
var _avisos: int = 0


func _initialize() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var bambu: float = float(args[0]) if args.size() > 0 else 45.0
	var fibra: float = float(args[1]) if args.size() > 1 else 85.0

	var todas: Array[Especie] = []
	for arquivo in DirAccess.get_files_at(PASTA):
		if arquivo.ends_with(".tres"):
			todas.append(load(PASTA + arquivo))
	# A fase 1 (tutorial do rio) so tem a vara de bambu; o acude vai ate a
	# fibra. A Foz e o Arvoredo so abrem depois da casa, quando o neto ja tem
	# a vara do avo (forca 100), e ali o bambu nao conta mais.
	var grupos: Array = [
		["Fase 1 (rio)", 1, &"", bambu, bambu],
		["Acude", 2, &"acude", fibra, bambu],
		["Foz e Vila", 2, &"foz", 100.0, -1.0],
		["Arvoredo", 2, &"arvoredo", 100.0, -1.0],
	]
	for g in grupos:
		var especies: Array[Especie] = []
		for e in todas:
			if e.fase == g[1] and e.local == g[2]:
				especies.append(e)
		print("%s: %d especies" % [g[0], especies.size()])
		_conferir_fase(especies, g[3], g[4])

	print("Resultado: %d erro(s), %d aviso(s)" % [_erros, _avisos])
	quit(1 if _erros > 0 else 0)


func _conferir_fase(especies: Array[Especie], fibra: float, bambu: float) -> void:

	for e in especies:
		if not Minijogo.PERFIS.has(e.perfil):
			_erro("%s: perfil '%s' nao existe em Minijogo.PERFIS" % [e.nome, e.perfil])
		if e.forca_min >= e.forca_max or e.forca_min < 0.0 or e.forca_max > 100.0:
			_erro("%s: faixa de forca invalida (%s a %s)" % [e.nome, e.forca_min, e.forca_max])
		if e.peso_min > e.peso_max or e.valor_min > e.valor_max:
			_erro("%s: peso ou valor com minimo acima do maximo" % e.nome)
		if e.forca_min > fibra:
			_erro("%s: so aparece com forca %s, acima da melhor vara da fase (%s)" % [e.nome, e.forca_min, fibra])
		elif e.forca_max > fibra:
			var perdido: float = e.peso_max - e.peso_para(fibra)
			_aviso("%s: com a melhor vara o peso maximo fica em %.1f kg (%.1f kg da faixa fora de alcance)" % [e.nome, e.peso_para(fibra), perdido])
		if e.raridade != Especie.Raridade.COMUM and e.forca_min <= bambu:
			_aviso("%s (%s) ja aparece com o Bambu (forca %s a %s)" % [e.nome, Especie.Raridade.keys()[e.raridade], e.forca_min, minf(bambu, e.forca_max)])

	# Toda forca de arremesso valida (acima de 5) precisa ter algum peixe.
	var forca: float = 6.0
	while forca <= fibra:
		var tem: bool = false
		for e in especies:
			tem = tem or (e.raridade != Especie.Raridade.ESPECIAL and e.alcancavel(forca))
		if not tem:
			_erro("nenhuma especie comum alcanca a forca %s" % forca)
		forca += 1.0



func _erro(texto: String) -> void:
	_erros += 1
	print("ERRO  ", texto)


func _aviso(texto: String) -> void:
	_avisos += 1
	print("AVISO ", texto)
