// Harness de simulacao da Fase 1 (docs/design-fase1.md).
//
// Replica a fisica do minijogo de scripts/cais_teste.gd e simula jogadores de
// tres niveis jogando a fase inteira: arremesso, fisgada, minijogo, venda,
// compras e reforma. Serve para medir taxa de captura, duracao e economia antes
// de implementar no Godot.
//
// Uso: node tools/harness/harness.mjs [rodadas]

const RODADAS = Number(process.argv[2] ?? 2000)
const DT = 1 / 60

// --- rng com semente, para resultados reproduziveis ---
let semente = 12345
function rand() {
	semente = (semente * 1664525 + 1013904223) >>> 0
	return semente / 4294967296
}
const entre = (a, b) => a + (b - a) * rand()
function gauss(media = 0, dp = 1) {
	const u = 1 - rand(), v = rand()
	return media + dp * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
}
const limitar = (x, a, b) => Math.min(b, Math.max(a, x))
const mover = (de, para, passo) => (Math.abs(para - de) <= passo ? para : de + Math.sign(para - de) * passo)

// --- constantes do minijogo, iguais as de cais_teste.gd ---
const BASE = {
	trilha: 240, zona: 56, empuxo: 1400, gravidade: 620, velMax: 400,
	inicial: 40, ganho: 24, perda: 18,
}

// --- jogadores simulados ---
// reacao: atraso de percepcao no minijogo (s); ruido: erro de leitura da posicao
// do peixe (px); decisao: intervalo entre decisoes (s); antecipa: quanto o
// jogador projeta o movimento da zona (s).
const JOGADORES = {
	iniciante: { reacao: 0.28, ruido: 22, decisao: 0.08, antecipa: 0.10, fisgada: [0.45, 0.12], afobado: 0.10, cai_falsa: 0.35, erro_forca: 7.2 },
	medio: { reacao: 0.20, ruido: 14, decisao: 0.05, antecipa: 0.15, fisgada: [0.35, 0.08], afobado: 0.05, cai_falsa: 0.20, erro_forca: 5.4 },
	bom: { reacao: 0.14, ruido: 8, decisao: 0.033, antecipa: 0.18, fisgada: [0.27, 0.05], afobado: 0.02, cai_falsa: 0.10, erro_forca: 3.6 },
}

// --- perfis de briga (scripts/minijogo.gd) ---
// PISO: nenhum perfil das especies desce abaixo da zona verde parada no fundo
// (0 a 64), senao o peixe e capturado sem apertar nada. "padrao" e o prototipo
// e fica so para regressao.
const PISO = 64
const PERFIS = {
	padrao: { tempo: [0.35, 1.5], vel: 1.0, alvo: (p) => entre(8, 232) },
	calmo: { tempo: [0.9, 2.0], vel: 0.8, alvo: (p) => limitar(p + entre(-60, 60), PISO, 232) },
	nervoso: { tempo: [0.2, 0.6], vel: 1.1, alvo: (p) => limitar(p + entre(-90, 90), PISO, 232) },
	pesado: { tempo: [0.8, 1.6], vel: 0.75, alvo: (p) => (rand() < 0.5 ? entre(PISO, 100) : entre(200, 232)) },
	saltador: { tempo: [0.5, 1.2], vel: 1.0, salto: { chance: 0.15, alvo: [215, 232], vel: 2.0, tempo: [0.3, 0.5] }, alvo: (p) => entre(PISO, 150) },
	mergulhador: { tempo: [0.6, 1.3], vel: 1.0, salto: { chance: 0.25, alvo: [150, 232], vel: 1.8, tempo: [0.3, 0.6] }, alvo: (p) => entre(PISO, 110) },
}

// --- minijogo: retorna { capturou, duracao } ---
function minijogo(peso, perfil, jog, mods = {}) {
	const c = { ...BASE, ...mods }
	const p = PERFIS[perfil]
	let zona = (c.trilha - c.zona) / 2, zvel = 0
	let peixe = c.trilha / 2, alvo = peixe, tempo = 0, velMult = p.vel
	let prog = c.inicial, t = 0
	const hist = []
	let segurando = false, proxDecisao = 0, ruidoAtual = 0, proxRuido = 0
	const atraso = Math.round(jog.reacao / DT)

	while (t < 60) {
		hist.push(peixe)
		// decisao do jogador
		if (t >= proxRuido) { ruidoAtual = gauss(0, jog.ruido); proxRuido = t + 0.1 }
		if (t >= proxDecisao) {
			const visto = hist[Math.max(0, hist.length - 1 - atraso)] + ruidoAtual
			const centro = zona + c.zona / 2 + zvel * jog.antecipa
			segurando = !jog.parado && centro < visto
			proxDecisao = t + jog.decisao
		}
		// zona
		if (segurando) zvel += c.empuxo * DT
		zvel = limitar(zvel - c.gravidade * DT, -c.velMax, c.velMax)
		zona += zvel * DT
		const lim = c.trilha - c.zona
		if (zona <= 0) { zona = 0; zvel = 0 } else if (zona >= lim) { zona = lim; zvel = 0 }
		// peixe
		tempo -= DT
		if (tempo <= 0) {
			const fator = mods.fatorTempo ?? 1
			if (p.salto && rand() < p.salto.chance) {
				alvo = entre(...p.salto.alvo); velMult = p.vel * p.salto.vel; tempo = entre(...p.salto.tempo) * fator
			} else {
				alvo = p.alvo(peixe); velMult = p.vel; tempo = entre(...p.tempo) * fator
			}
		}
		peixe = mover(peixe, alvo, (cfg.vel[0] + peso * cfg.vel[1]) * velMult * DT)
		// progresso
		prog += (peixe >= zona && peixe <= zona + c.zona ? c.ganho : -c.perda) * DT
		t += DT
		if (prog >= 100) return { capturou: true, duracao: t }
		if (prog <= 0) return { capturou: false, duracao: t }
	}
	return { capturou: false, duracao: t }
}

// --- dados da Fase 1 (docs/design-fase1.md) ---
const ESPECIES = [
	{ nome: 'Tilápia', perfil: 'calmo', faixa: [0, 40], peso: [0.3, 1.2], rar: 'comum', valor: [12, 28], desvio: 0.22, trofeu: [0.05, 0.45] },
	{ nome: 'Cascudo', perfil: 'pesado', faixa: [25, 65], peso: [0.6, 2.2], rar: 'comum', valor: [22, 50], desvio: 0.20, trofeu: [0.05, 0.40] },
	{ nome: 'Carpa', perfil: 'saltador', faixa: [50, 85], peso: [2.0, 5.5], rar: 'incomum', valor: [60, 120], desvio: 0.18, trofeu: [0.04, 0.35] },
	{ nome: 'Jundiá', perfil: 'mergulhador', faixa: [68, 85], peso: [3.0, 6.0], rar: 'raro', valor: [95, 170], desvio: 0.16, trofeu: [0.04, 0.15] },
]
const ESPECIAL = { nome: 'Jundiá Gigante', perfil: 'mergulhador', faixa: [75, 85], peso: [7.0, 10.0], rar: 'especial', valor: [320, 430], desvio: 0.25, trofeu: [0, 0] }
const PESO_RAR = { comum: 1, incomum: 0.5, raro: 0.25 }
// Energia do dia (scripts/partida.gd): lancar gasta 6 + 3 x forca/100 e brigar
// com o peixe gasta 0.5/s. O cenario "proposta" usa 12 lancamentos fixos.
const LANCAMENTOS_DIA = 12
const ENERGIA = { max: 100, lancamento: 6, porForca: 3, lutaPorS: 0.5 }

// Cenarios comparados. "proposta" e o docs/design-fase1.md como esta; "ajustada"
// e a correcao sugerida pelo harness.
const CENARIOS = {
	proposta: { varas: { bambu: 60, fibra: 85 }, telhado: 500, vel: [70, 18], zonaCafe: 96, janela: 0.9, janelaModao: 1.4 },
	ajustada: { varas: { bambu: 45, fibra: 85 }, telhado: 800, vel: [60, 28], zonaCafe: 72, janela: 0.6, janelaModao: 0.9, exigeJundia: true, energia: true },
}
let cfg = CENARIOS.proposta

function sortearEspecie(forca, dia, camarao, soTilapia) {
	if (soTilapia) return ESPECIES[0]
	if (dia >= 3 && forca >= ESPECIAL.faixa[0] && forca <= ESPECIAL.faixa[1] && rand() < (camarao ? 0.10 : 0.05)) return ESPECIAL
	const cand = ESPECIES.filter((e) => forca >= e.faixa[0] && forca <= e.faixa[1])
	const pesos = cand.map((e) => PESO_RAR[e.rar] * (camarao && e.rar !== 'comum' ? 2 : 1))
	let r = rand() * pesos.reduce((a, b) => a + b, 0)
	for (let i = 0; i < cand.length; i++) if ((r -= pesos[i]) <= 0) return cand[i]
	return cand[cand.length - 1]
}

// Mesma conta do scripts/partida.gd: a forca da a tendencia e o desvio da
// especie espalha o peso em volta dela. No alto da faixa pode sair um trofeu,
// acima do peso_max, e o valor acompanha porque a interpolacao nao e limitada.
const FRACAO_TROFEU = 0.6

function pesoEValor(esp, forca, camarao) {
	const centro = limitar((forca - esp.faixa[0]) / (esp.faixa[1] - esp.faixa[0]), 0, 1)
	const t = limitar(centro + gauss(0, esp.desvio), 0, 1)
	let peso = esp.peso[0] + (esp.peso[1] - esp.peso[0]) * t
	const [chance, bonus] = esp.trofeu
	if (centro >= FRACAO_TROFEU && rand() < chance * (camarao ? 2 : 1)) {
		peso = esp.peso[1] * (1 + 0.1 + rand() * Math.max(bonus - 0.1, 0))
	}
	const bruto = esp.valor[0] + (esp.valor[1] - esp.valor[0]) * t
	return { peso, valor: Math.round(bruto * melhorComprador(esp.nome)) }
}

// A vila tem dois compradores (scripts/partida.gd, COMPRADORES): o Zeca paga a
// tabela e a Dona Maria Ivone paga 25% acima, menos no cascudo. O jogador
// atento leva cada peixe a quem paga melhor, que e o que isto modela. O bonus
// de relacionamento fica de fora de proposito: assim o numero e o piso, nao o
// melhor caso.
const COMPRADORES = [
	{ base: 1.0, especialidade: {} },
	{ base: 1.25, especialidade: { Cascudo: 0.55 } },
]

function melhorComprador(nome) {
	return Math.max(...COMPRADORES.map((c) => c.base * (c.especialidade[nome] ?? 1)))
}

// --- um lancamento completo; retorna { tempo, peixe?, valor } ---
function lancamento(jog, alvoForca, cap, dia, b) {
	const forca = limitar(alvoForca + gauss(0, jog.erro_forca), 6, cap)
	let tempo = forca / 90 + 0.5 // carregar a barra + espera do estado 1
	const espera = entre(1.5, 4.0)
	// apertou antes da mordida
	if (rand() < jog.afobado) return { tempo: tempo + espera * rand() + 1.6, motivo: 'afobado' }
	// beliscada falsa (a partir do dia 2, metade dos lancamentos)
	if (dia >= 2 && !b.tutorial && rand() < 0.5 && rand() < jog.cai_falsa * (b.modao ? 0.25 : 1))
		return { tempo: tempo + espera * 0.6 + 1.6, motivo: 'falsa' }
	tempo += espera
	const janela = b.modao ? cfg.janelaModao : cfg.janela
	const reacao = Math.max(0.12, gauss(...jog.fisgada))
	if (reacao > janela) return { tempo: tempo + janela + 1.6, motivo: 'fisgada' }
	tempo += reacao
	const esp = sortearEspecie(forca, dia, b.camarao, b.tutorial)
	const { peso, valor } = pesoEValor(esp, forca, b.camarao)
	const mods = {}
	if (b.cafezinho) mods.zona = cfg.zonaCafe
	const r = minijogo(peso, esp.perfil, jog, mods)
	tempo += r.duracao + (r.capturou ? 2.2 : 1.6)
	return r.capturou ? { tempo, peixe: esp.nome, valor, forca, luta: r.duracao } : { tempo, motivo: 'minijogo', peixe: esp.nome, forca, luta: r.duracao }
}

// --- fase inteira ---
// politica: 'economico' nao compra bebidas; 'gastador' compra Cafezinho e
// Modao quando abrem e ha dinheiro.
function fase(jog, politica) {
	let dinheiro = 80 - 50, vara = 'bambu', tempo = 60 // prologo
	// No jogo a fase fecha com o telhado e um jundia entregue a Dona Marlene;
	// o primeiro jundia fica guardado em vez de vendido.
	let jundia = !cfg.exigeJundia
	const log = { capturas: {}, perdas: {}, comprouFibraNoDia: null, dias: 0 }
	for (let dia = 1; dia <= 10; dia++) {
		log.dias = dia
		tempo += 15 + 3 // dialogo do dia + andar ate a zona
		if (dia === 1) tempo += 60 // instrucoes do tutorial
		const b = { tutorial: dia === 1, modao: 0, cafezinho: 0, camarao: false }
		if (politica === 'gastador' && dia >= 3) {
			if (dinheiro >= 70 + 50) { dinheiro -= 70; b.cafezinho = 5 }
			if (dinheiro >= 80 + 50) { dinheiro -= 80; b.modao = 5 }
		}
		let renda = 0
		let energia = ENERGIA.max
		for (let i = 0; cfg.energia ? energia > 0 : i < LANCAMENTOS_DIA; i++) {
			const cap = cfg.varas[vara]
			const alvo = dia === 1 ? 20 : cap - 4
			const r = lancamento(jog, alvo, cap, dia, b)
			tempo += r.tempo
			const forca = r.forca ?? alvo
			energia -= ENERGIA.lancamento + ENERGIA.porForca * forca / 100 + ENERGIA.lutaPorS * (r.luta ?? 0)
			if (r.peixe && r.valor) {
				log.capturas[r.peixe] = (log.capturas[r.peixe] ?? 0) + 1
				if (r.peixe.startsWith('Jundiá') && !jundia) jundia = true
				else renda += r.valor
			}
			else log.perdas[r.motivo] = (log.perdas[r.motivo] ?? 0) + 1
			if (b.cafezinho) b.cafezinho--
			if (b.modao) b.modao--
		}
		dinheiro += renda
		if (dia === 1) log.dinheiroDia1 = dinheiro
		tempo += 30 // hub
		if (dinheiro >= cfg.telhado && jundia) { tempo += 60; return { ...log, tempo, dinheiro: dinheiro - cfg.telhado } }
		if (dia >= 2 && vara === 'bambu' && dinheiro >= 300) { dinheiro -= 300; vara = 'fibra'; log.comprouFibraNoDia = dia }
	}
	return { ...log, tempo, dinheiro, naoFechou: true }
}

// ------------------------------- relatorios -------------------------------

const pct = (x) => (100 * x).toFixed(0) + '%'
const q = (arr, p) => arr.slice().sort((a, b) => a - b)[Math.floor(p * (arr.length - 1))]

function tabelaMinijogo() {
	console.log('\n## 1. Minijogo: taxa de captura (duracao media) por peso, perfil atual "padrao"\n')
	const pesos = [0.5, 1, 2, 3, 4.5, 6, 8, 10]
	console.log('| Jogador | ' + pesos.map((p) => p + ' kg').join(' | ') + ' |')
	console.log('|---|' + pesos.map(() => '---').join('|') + '|')
	for (const [n, j] of Object.entries(JOGADORES)) {
		const cel = pesos.map((p) => {
			let ok = 0, d = 0
			for (let i = 0; i < RODADAS; i++) { const r = minijogo(p, 'padrao', j); ok += r.capturou; d += r.duracao }
			return `${pct(ok / RODADAS)} (${(d / RODADAS).toFixed(1)}s)`
		})
		console.log(`| ${n} | ${cel.join(' | ')} |`)
	}
}

function tabelaEspecies() {
	console.log('\n## 2. Minijogo por especie da Fase 1 (peso medio da faixa, perfil proposto)\n')
	const todas = [...ESPECIES, ESPECIAL]
	const cols = ['sem bonus', 'Cafezinho']
	console.log('| Especie | Perfil | Peso | sem apertar nada | ' + Object.keys(JOGADORES).flatMap((j) => cols.map((c) => `${j} ${c}`)).join(' | ') + ' |')
	console.log('|---|---|---|---|' + Object.keys(JOGADORES).flatMap(() => cols.map(() => '---')).join('|') + '|')
	for (const e of todas) {
		const peso = (e.peso[0] + e.peso[1]) / 2
		const cel = Object.values(JOGADORES).flatMap((j) => [{}, { zona: cfg.zonaCafe }].map((m) => {
			let ok = 0
			for (let i = 0; i < RODADAS; i++) ok += minijogo(peso, e.perfil, j, m).capturou
			return pct(ok / RODADAS)
		}))
		// Jogador que nunca aperta: mede se o peixe sai de graca.
		let parado = 0
		for (let i = 0; i < RODADAS; i++) parado += minijogo(peso, e.perfil, { ...JOGADORES.medio, parado: true }).capturou
		console.log(`| ${e.nome} | ${e.perfil} | ${peso.toFixed(1)} kg | ${pct(parado / RODADAS)} | ${cel.join(' | ')} |`)
	}
}

function tabelaFisgada() {
	console.log('\n## 3. Fisgada: chance de acertar a janela\n')
	console.log(`| Jogador | Janela ${cfg.janela} s | Modao ${cfg.janelaModao} s |`)
	console.log('|---|---|---|')
	for (const [n, j] of Object.entries(JOGADORES)) {
		let a = 0, b = 0
		for (let i = 0; i < RODADAS * 5; i++) { const r = Math.max(0.12, gauss(...j.fisgada)); a += r <= cfg.janela; b += r <= cfg.janelaModao }
		console.log(`| ${n} | ${pct(a / (RODADAS * 5))} | ${pct(b / (RODADAS * 5))} |`)
	}
}

function tabelaRiscoRetorno() {
	console.log('\n## 4. Risco e retorno do arremesso: R$ por minuto pescando (dia 3, jogador medio)\n')
	console.log('| Mira de forca | Vara | Captura | R$/lancamento | R$/min |')
	console.log('|---|---|---|---|---|')
	const j = JOGADORES.medio
	for (const [alvo, vara] of [[20, 'bambu'], [cfg.varas.bambu - 4, 'bambu'], [60, 'fibra'], [70, 'fibra'], [81, 'fibra']]) {
		let ok = 0, val = 0, t = 0
		for (let i = 0; i < RODADAS; i++) {
			const r = lancamento(j, alvo, cfg.varas[vara], 3, { tutorial: false })
			t += r.tempo; if (r.valor) { ok++; val += r.valor }
		}
		console.log(`| ${alvo} | ${vara} | ${pct(ok / RODADAS)} | R$ ${(val / RODADAS).toFixed(0)} | R$ ${(val / (t / 60)).toFixed(0)} |`)
	}
}

function tabelaFase() {
	console.log('\n## 5. Fase 1 completa (' + RODADAS + ' partidas por linha)\n')
	console.log('| Jogador | Politica | Dias (med) | Tempo p10 / mediana / p90 | Dentro de 10-15 min | Nao fechou em 10 dias | Fibra no dia | Sobra media | R$ fim do dia 1 (p90) |')
	console.log('|---|---|---|---|---|---|---|---|')
	const detalhes = {}
	for (const [n, j] of Object.entries(JOGADORES)) {
		for (const pol of ['economico', 'gastador']) {
			const rs = Array.from({ length: RODADAS }, () => fase(j, pol))
			const min = rs.map((r) => r.tempo / 60)
			const dias = rs.map((r) => r.dias)
			const dentro = min.filter((m) => m >= 10 && m <= 15).length / RODADAS
			const nf = rs.filter((r) => r.naoFechou).length / RODADAS
			const fib = rs.map((r) => r.comprouFibraNoDia).filter(Boolean)
			const sobra = rs.reduce((a, r) => a + r.dinheiro, 0) / RODADAS
			console.log(`| ${n} | ${pol} | ${q(dias, 0.5)} | ${q(min, 0.1).toFixed(1)} / ${q(min, 0.5).toFixed(1)} / ${q(min, 0.9).toFixed(1)} min | ${pct(dentro)} | ${pct(nf)} | ${fib.length ? q(fib, 0.5) : '-'} | R$ ${sobra.toFixed(0)} | R$ ${q(rs.map((r) => r.dinheiroDia1), 0.9).toFixed(0)} |`)
			if (pol === 'economico') detalhes[n] = rs
		}
	}
	console.log('\n### Capturas e perdas medias por partida (politica economica)\n')
	for (const [n, rs] of Object.entries(detalhes)) {
		const soma = (campo) => {
			const o = {}
			for (const r of rs) for (const [k, v] of Object.entries(r[campo])) o[k] = (o[k] ?? 0) + v
			return Object.entries(o).map(([k, v]) => `${k} ${(v / rs.length).toFixed(1)}`).join(', ')
		}
		console.log(`- **${n}**: capturas: ${soma('capturas')} | perdas: ${soma('perdas')}`)
	}
}

// Modo de validacao: imprime em JSON a mesma tabela que
// tools/harness/godot/validar_minijogo.gd mede no jogo real. Usa o cenario
// "ajustada", que e o que o jogo usa desde a aprovacao; o 5o argumento troca.
if (process.argv[3] === '--validar') {
	cfg = CENARIOS[process.argv[5] ?? 'ajustada']
	const saida = {}
	for (const [n, j] of Object.entries(JOGADORES)) {
		for (const p of [0.5, 1, 2, 3, 4.5, 6, 7]) {
			let ok = 0, d = 0
			for (let i = 0; i < RODADAS; i++) { const r = minijogo(p, process.argv[4] ?? 'padrao', j); ok += r.capturou; d += r.duracao }
			saida[`${n}|${p.toFixed(1)}`] = { taxa: ok / RODADAS, duracao: d / RODADAS, n: RODADAS }
		}
	}
	console.log('RESULTADO ' + JSON.stringify(saida))
	process.exit(0)
}

console.log('# Harness da Fase 1, ' + RODADAS + ' rodadas por celula')
for (const [nome, c] of Object.entries(CENARIOS)) {
	cfg = c
	semente = 12345
	console.log('\n\n# Cenario: ' + nome + ' ' + JSON.stringify(c))
	tabelaMinijogo()
	tabelaEspecies()
	tabelaFisgada()
	tabelaRiscoRetorno()
	tabelaFase()
}
