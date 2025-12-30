import sys
sys.path.insert(0, '.')

print('🚀 PRUEBA DEL PROTOCOLO AEE v2.0')
print('=' * 40)

try:
    # 1. Importar
    print('1. Importando...')
    from aee import EvidenceProtocol
    print('   ✅ EvidenceProtocol importado')
    
    # 2. Crear instancia
    print('2. Creando instancia...')
    p = EvidenceProtocol('franco@test.com')
    print('   ✅ Instancia creada')
    
    # 3. Inicializar
    print('3. Inicializando...')
    result = p.initialize()
    print(f'   ✅ Inicializado: {result}')
    
    # 4. Ver métodos
    print('4. Métodos disponibles:')
    methods = [m for m in dir(p) if not m.startswith('_') and callable(getattr(p, m))]
    for m in methods:
        print(f'   - {m}()')
    
    # 5. Crear archivo de prueba
    print('5. Creando archivo de prueba...')
    with open('test_aee.txt', 'w', encoding='utf-8') as f:
        f.write('Contenido de prueba AEE v2.0\n')
    print('   ✅ Archivo creado')
    
    # 6. Certificar
    print('6. Certificando archivo...')
    cert = p.certify_file('test_aee.txt', 
                         evidence_type='documento', 
                         description='Prueba del sistema')
    print('   ✅ Certificado generado')
    
    # 7. Mostrar resultados
    print('7. Resultados:')
    import json
    print(json.dumps(cert, indent=2, ensure_ascii=False)[:500] + '...' if len(json.dumps(cert)) > 500 else '')
    
    print('\n🎉 ¡PRUEBA EXITOSA!')
    
except Exception as e:
    print(f'❌ ERROR: {e}')
    import traceback
    traceback.print_exc()

print('=' * 40)
