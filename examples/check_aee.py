# check_aee.py
import os
import sys

print("🔍 ANÁLISIS RÁPIDO AEE PROTOCOL")
print("=" * 50)

# Verificar estructura
essential = [
    'setup.py',
    'requirements.txt', 
    'README.md',
    'aeeprotocol/__init__.py',
    'aeeprotocol/core/engine.py',
    'aeeprotocol/sdk/client.py'
]

for file in essential:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} (FALTANTE)")

print("\n📊 RESUMEN:")
if os.path.exists("aeeprotocol/core/engine_secure.py"):
    print("✅ Versión segura detectada")
else:
    print("⚠️  ADVERTENCIA: No hay engine_secure.py")