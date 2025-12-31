# ============================================================================
# Archivo: debug_api_keys.py
# VERIFICAR EXACTAMENTE QUÉ API KEYS ESPERA EL SERVIDOR
# ============================================================================

"""
Script para debuggear y verificar las API Keys configuradas en el servidor.
Ejecutar: python debug_api_keys.py
"""

import os
import sys
from pathlib import Path

# Agregar src al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent / "src"))

def debug_api_keys():
    """Mostrar todas las API Keys disponibles y su configuración"""
    
    print("=" * 80)
    print("🔑 AEE PROTOCOL - API KEY DEBUGGER")
    print("=" * 80)
    
    # 1. Verificar variables de entorno
    print("\n[1] VARIABLES DE ENTORNO DETECTADAS:")
    print("-" * 80)
    
    api_key_dev = os.getenv('API_KEY_DEV', 'aee-dev-key-2025')
    api_key_prod = os.getenv('API_KEY_PROD', 'aee-prod-key-2025')
    
    print(f"API_KEY_DEV:  {api_key_dev}")
    print(f"API_KEY_PROD: {api_key_prod}")
    
    # 2. Verificar archivo .env
    print("\n[2] VERIFICANDO ARCHIVO .env:")
    print("-" * 80)
    
    env_path = Path(".env")
    if env_path.exists():
        print("✓ Archivo .env ENCONTRADO")
        with open(env_path, 'r') as f:
            content = f.read()
            if 'API_KEY_DEV' in content:
                print("  ✓ API_KEY_DEV está en .env")
            if 'API_KEY_PROD' in content:
                print("  ✓ API_KEY_PROD está en .env")
    else:
        print("✗ Archivo .env NO ENCONTRADO (usando valores por defecto)")
    
    # 3. Cargar APIKeyManager desde security.py
    print("\n[3] CARGANDO APIKEY MANAGER:")
    print("-" * 80)
    
    try:
        from aee.infrastructure.security import api_key_manager
        
        print("✓ APIKeyManager cargado correctamente")
        
        # 4. Mostrar claves registradas
        print("\n[4] CLAVES REGISTRADAS EN EL SISTEMA:")
        print("-" * 80)
        
        api_keys = api_key_manager.api_keys
        
        if not api_keys:
            print("✗ No hay claves registradas (problema crítico)")
        else:
            for idx, (key, info) in enumerate(api_keys.items(), 1):
                print(f"\n  Clave #{idx}:")
                print(f"    Valor: {key}")
                print(f"    Nombre: {info.get('name', 'N/A')}")
                print(f"    Operaciones: {', '.join(info.get('operations', []))}")
                print(f"    Rate Limit: {info.get('rate_limit', 'N/A')} req/hr")
        
        # 5. Validar una clave
        print("\n[5] PRUEBA DE VALIDACIÓN:")
        print("-" * 80)
        
        test_keys = [
            'aee-dev-key-2025',
            'aee-prod-key-2025',
            'invalid-key',
            api_key_dev,
            api_key_prod
        ]
        
        print("Validando claves de prueba:")
        for test_key in test_keys:
            result = api_key_manager.validate(test_key)
            status = "✓ VÁLIDA" if result else "✗ INVÁLIDA"
            print(f"  {test_key:30} -> {status}")
            if result:
                print(f"     ├─ Nombre: {result.get('name')}")
                print(f"     └─ Ops: {', '.join(result.get('operations', []))}")
    
    except ImportError as e:
        print(f"✗ Error importando APIKeyManager: {e}")
        print("  Verifica que security.py existe en aee/infrastructure/")
    
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 80)
    print("FIN DEL DEBUGGER")
    print("=" * 80)
