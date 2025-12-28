try:
    from aeeprotocol import AEEWatermark
    print('--- PROBANDO PROTOCOLO AEE v0.5.0 ---')
    wm = AEEWatermark()
    print('? Sistema cargado.')
    res = wm.inject(texto='Soberanía Digital', author_id='franco')
    print(f'? Prueba Exitosa. Autor: {res.get("author_id")}')
    print('?? PROYECTO 100% OPERATIVO')
except Exception as e:
    print(f'? Error: {e}')
