# Arte gerada por código

Os cenários do cais e do hub são desenhados em 1/4 da resolução e exportados em 4x.

    cd tools/arte
    python cais_arte.py   ../../assets/sprites/cais    # ceu, mar, costao, cais e barco
    python acude_arte.py  ../../assets/sprites/acude   # ceu, agua, barranco e estrutura
    python peixes_arte.py ../../assets/sprites/peixes  # as 5 especies da Fase 1
    python mapa_arte.py   ../../assets/sprites/ui      # o mapa de escolher o pesqueiro
    python hub_arte.py ../../assets/sprites/hub     # loja de pesca
    python tiago_arte.py ../../assets/sprites/tiago # Tiago: sem vara, vara nas costas e na mao

Para ver a cena sem abrir o editor:

    godot --path . -s tools/harness/godot/capturar_tela.gd -- res://scenes/Vila.tscn tela.png [casa_pronta 0|1]
