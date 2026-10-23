# Harness

Ferramentas para testar balanceamento e regressão sem jogar à mão. Precisam de
Node, Godot 4.7 e Python 3.

| Arquivo                        | O que faz                                                                  |
|--------------------------------|----------------------------------------------------------------------------|
| `harness.mjs`                  | Réplica do minijogo e simulação da Fase 1 inteira com 3 níveis de jogador, comparando o cenário "proposta" com o "ajustada" |
| `godot/validar_minijogo.gd`    | Roda um bot no minijogo de verdade (cena Acude) e mede a taxa de captura |
| `godot/verificar_dados.gd`     | Confere `dados/especies/` contra as regras de design                       |
| `godot/testar_fluxo.gd`        | Joga a Fase 1 de ponta a ponta com o teclado simulado (hub, loja, cais, venda, sono, fechamento) |
| `comparar.py`                  | Teste estatístico entre dois resultados (Godot × Node, ou antes × depois)  |

## Comandos

    # simulação da fase (rápida, 1000 partidas por linha)
    node tools/harness/harness.mjs 1000

    # o harness bate com o jogo real?
    godot --headless --fixed-fps 60 --path . -s tools/harness/godot/validar_minijogo.gd -- 400 > godot.txt
    node tools/harness/harness.mjs 4000 --validar > node.txt
    python tools/harness/comparar.py godot.txt node.txt

    # um perfil de briga específico
    godot ... validar_minijogo.gd -- 300 saltador
    node tools/harness/harness.mjs 3000 --validar saltador

    # dados das espécies, com a força máxima do bambu e da fibra
    godot --headless --path . -s tools/harness/godot/verificar_dados.gd -- 45 85

    # fluxo da fase inteira; sai com código 1 se algo quebrar
    godot --headless --fixed-fps 60 --path . -s tools/harness/godot/testar_fluxo.gd

O `--validar` do harness usa o cenário "ajustada", que é o que o jogo usa. Para
comparar com o antigo: `node tools/harness/harness.mjs 3000 --validar padrao proposta`.

Para usar como teste de regressão: rode `validar_minijogo.gd` antes e depois de
mexer no minijogo e compare os dois com `comparar.py`. Com 21 células a 99% de
confiança, uma divergência isolada perto de 100% é ruído; várias indicam
mudança de comportamento.

O jogador simulado é um modelo e não foi calibrado com pessoas. Os números
servem para comparar cenários; antes de fechar o balanceamento, ajuste
`JOGADORES` (nos dois arquivos) com dados de playtest.
