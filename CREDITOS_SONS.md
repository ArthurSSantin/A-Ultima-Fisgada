# Créditos dos sons

A música de fundo é da OpenGameArt e pode ser usada com ou sem crédito. Os efeitos do Pixabay estão sob a [Pixabay Content License](https://pixabay.com/service/license-summary/): uso livre, comercial ou não, sem obrigação de crédito. O que a licença não permite é revender ou redistribuir o som sozinho, fora do jogo. Mesmo sem obrigação, os autores ficam registrados aqui.

As gravações originais ficam em `tools/sons/originais/`. O jogo usa só o trecho de cada uma que aparece na tabela, cortado, com entrada e saída suaves e o volume nivelado por `tools/sons/gerar_sons.py`, que grava os `.ogg` de `assets/sons/`.

| Arquivo no jogo | Uso | Fonte | Autor |
|---|---|---|---|
| assets/musica/fundo.mp3 | música de fundo | [Gone Fishin' (OpenGameArt)](https://opengameart.org/content/gone-fishin), CC0 / CC-BY 4.0 / OGA-BY 3.0 | Memoraphile @ You're Perfect Studio |
| assets/sons/lancamento.ogg | lançar a vara | [Fishing Rod Whoosh](https://pixabay.com/sound-effects/film-special-effects-fishing-rod-whoosh-411640/) | spinopel |
| assets/sons/isca_agua.ogg | isca caindo na água (primeiros 0,6 s) | [Water Splash 46402](https://pixabay.com/sound-effects/film-special-effects-water-splash-46402/) | freesound_community |
| assets/sons/fisgada.ogg | fisgar o peixe (primeiros 0,55 s) | [Water Splash 80537](https://pixabay.com/sound-effects/nature-water-splash-80537/) | freesound_community |
| assets/sons/ambiente_lago.ogg | ambiente do rio e do açude (40 s em laço) | [Fishing on the Lake](https://pixabay.com/sound-effects/nature-fishing-on-the-lake-310740/) | mindmist |
| assets/sons/cavalo_trote.ogg | cavalo andando na estrada (12 s em laço) | [Horse Clip Clopping Downhill](https://pixabay.com/sound-effects/film-special-effects-horse-clip-clopping-downhill-stereo-33768/) | freesound_community |
| assets/sons/cavalo_bufo.ogg | cavalo bufando (uma bufada) | [horse snort](https://pixabay.com/sound-effects/nature-horse-snort-95874/) | freesound_community |
| assets/sons/ronrom.ogg | ronronar do MauMau (2,5 s) | [Mozza the cat, purring close mic](https://pixabay.com/sound-effects/nature-mozza-the-cat-purring-close-mic-33756/) | freesound_community |
| assets/sons/latido.ogg | latido da Paçoca (dois latidos) | [Dog Barking](https://pixabay.com/sound-effects/nature-dog-barking-70772/) | freesound_community |

Os demais sons são sintetizados em `tools/sons/gerar_sons.py`, sem arquivo de terceiros: `batida` (porta), `texto`, `cursor`, `confirmar` e `moeda` (interface), `mordida`, `carretilha`, `captura`, `conquista` e `escapou` (pescaria), e `chuva`, `trovao` e `mar` (ambiente).
