# Arte gerada por código

Os cenários do cais e do hub são desenhados em 1/4 da resolução e exportados em 4x.

    cd tools/arte
    python cais_arte.py ../../assets/sprites        # ceu, mar, grama e cais
    python hub_arte.py ../../assets/sprites/hub     # loja de pesca
    python tiago_arte.py ../../assets/sprites/tiago # Tiago: sem vara, vara nas costas e na mao

Para ver a cena sem abrir o editor:

    godot --path . -s tools/harness/godot/capturar_tela.gd -- res://scenes/Hub.tscn tela.png [telhado_pago 0|1]
