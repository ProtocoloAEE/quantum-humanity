# analizar_aee.py
import os
import sys
import re
import subprocess
from pathlib import Path

print('='*70)
print('🔍 ANÁLISIS COMPLETO DEL PROYECTO AEE PROTOCOL')
print('='*70)

# 1. VERIFICAR ESTRUCTURA DE ARCHIVOS
print('\n📁 ESTRUCTURA DE ARCHIVOS:')
print('='*40)

essential_files = {
    'setup.py': 'Configuración del paquete',
    'requirements.txt': 'Dependencias',
    'README.md': 'Documentación principal',
    'aeeprotocol/__init__.py': 'Paquete principal',
    'aeeprotocol/core/engine.py': 'Motor original (v8.3)',
    'aeeprotocol/sdk/client.py': 'Cliente original',
    'aeeprotocol/core/engine_secure.py': 'Motor seguro (¿EXISTE?)',
    'aeeprotocol/sdk/client_secure.py': 'Cliente seguro (¿EXISTE?)',
    '.env.example': 'Plantilla de variables (¿EXISTE?)',
    'auditor_test_v8.3.py': 'Auditoría principal',
    'VALIDATION.md': 'Resultados de validación',
}

all_files_ok = True
for filepath, description in essential_files.items():
    exists = os.path.exists(filepath)
    status = '✅' if exists else '❌'
    print(f'{status} {description:40} {filepath}')
    if not exists:
        all_files_ok = False

# 2. VERIFICAR VULNERABILIDADES DE SEGURIDAD
print('\n🔐 ANÁLISIS DE SEGURIDAD:')
print('='*40)

security_issues = []

# Verificar si engine.py tiene la vulnerabilidad
engine_path = 'aeeprotocol/core/engine.py'
if os.path.exists(engine_path):
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Vulnerabilidad: user_id usado como única semilla
    if 'def _compute_direction' in content and 'user_id' in content:
        if 'secret_key' not in content and 'hmac' not in content:
            print('❌ engine.py: VULNERABLE - user_id como única semilla')
            security_issues.append('engine.py usa user_id como clave secreta')
        else:
            print('✅ engine.py: Parece seguro (tiene HMAC/secret_key)')
    else:
        print('⚠️  engine.py: No se pudo analizar completamente')

# Verificar si existe engine_secure.py
secure_engine_path = 'aeeprotocol/core/engine_secure.py'
if os.path.exists(secure_engine_path):
    with open(secure_engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'hmac.new' in content and 'secret_key' in content:
        print('✅ engine_secure.py: Implementación HMAC correcta')
    else:
        print('❌ engine_secure.py: FALTA implementación HMAC')
        security_issues.append('engine_secure.py no tiene HMAC')
else:
    print('❌ engine_secure.py: NO EXISTE - Vulnerabilidad CRÍTICA')
    security_issues.append('Falta engine_secure.py')

# 3. VERIFICAR VERSIONES
print('\n📦 INFORMACIÓN DE VERSIÓN:')
print('='*40)

# Leer versión de __init__.py
init_path = 'aeeprotocol/__init__.py'
if os.path.exists(init_path):
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
        version_match = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content)
        if version_match:
            version = version_match.group(1)
            print(f'Versión del paquete: {version}')
            
            # Verificar si es vulnerable
            if version == '0.2.3':
                print('⚠️  ADVERTENCIA: v0.2.3 tiene vulnerabilidades de seguridad conocidas')
                print('   Recomendado: Actualizar a v0.2.4 o usar engine_secure.py')
            elif version == '0.2.4':
                print('✅ v0.2.4 debería tener fixes de seguridad')
        else:
            print('❌ No se encontró __version__ en __init__.py')

# 4. VERIFICAR GIT STATUS
print('\n📊 ESTADO DE GIT:')
print('='*40)

try:
    # Commits locales no pusheados
    result = subprocess.run(['git', 'log', 'origin/main..HEAD', '--oneline'], 
                          capture_output=True, text=True, shell=True)
    if result.stdout.strip():
        print('Commits locales no pusheados:')
        for line in result.stdout.strip().split('\n'):
            print(f'  • {line}')
    else:
        print('✅ Todo sincronizado con origin/main')
    
    # Archivos modificados/no trackeados
    result = subprocess.run(['git', 'status', '--short'], 
                          capture_output=True, text=True, shell=True)
    if result.stdout.strip():
        print('\nArchivos modificados/no trackeados:')
        print(result.stdout)
    else:
        print('✅ Todo commiteado')
        
except Exception as e:
    print(f'⚠️  Error al verificar git: {e}')

# 5. VERIFICAR DEPENDENCIAS
print('\n📦 DEPENDENCIAS INSTALADAS:')
print('='*40)

try:
    import numpy as np
    print(f'✅ numpy {np.__version__}')
except ImportError:
    print('❌ numpy NO instalado')

try:
    import scipy
    print(f'✅ scipy {scipy.__version__}')
except ImportError:
    print('❌ scipy NO instalado')

# 6. RESUMEN Y RECOMENDACIONES
print('\n' + '='*70)
print('📊 RESUMEN DEL ANÁLISIS')
print('='*70)

if not security_issues and all_files_ok:
    print('✅ PROYECTO EN BUEN ESTADO')
    print('\n🎯 Próximos pasos recomendados:')
    print('1. git push origin main (si hay commits pendientes)')
    print('2. Crear Release v0.2.4 en GitHub')
    print('3. Actualizar PyPI si es necesario')
    print('4. Publicar en redes')
    
else:
    print('⚠️  PROBLEMAS DETECTADOS:')
    
    if security_issues:
        print('\n🔴 VULNERABILIDADES DE SEGURIDAD:')
        for issue in security_issues:
            print(f'  • {issue}')
        print('\n🚨 ACCIÓN INMEDIATA REQUERIDA:')
        print('  - Crear engine_secure.py y client_secure.py')
        print('  - Crear .env.example')
        print('  - NO promocionar v0.2.3 públicamente')
    
    if not all_files_ok:
        print('\n📁 ARCHIVOS FALTANTES:')
        for filepath, desc in essential_files.items():
            if not os.path.exists(filepath):
                print(f'  • {filepath} ({desc})')
    
    print('\n🔧 PASOS PARA CORREGIR:')
    print('1. Crear los archivos de seguridad faltantes')
    print('2. Actualizar a versión 0.2.4')
    print('3. Commit y push de los fixes')
    print('4. Solo entonces crear Release')

print('='*70)

# 7. COMANDOS SUGERIDOS
print('\n💻 COMANDOS SUGERIDOS BASADOS EN EL ANÁLISIS:')

try:
    if 'aeeprotocol' in os.listdir('.') and 'core' in os.listdir('aeeprotocol'):
        if 'engine_secure.py' not in os.listdir('aeeprotocol/core'):
            print('\nPara crear engine_secure.py:')
            print('  notepad aeeprotocol\\core\\engine_secure.py')
            print('  (Copia el código seguro que te envié)')
except:
    pass

if security_issues:
    print('\nPara corregir seguridad rápidamente:')
    print('  1. notepad .env.example')
    print('  2. notepad aeeprotocol\\core\\engine_secure.py')
    print('  3. notepad aeeprotocol\\sdk\\client_secure.py')
    print('  4. git add . && git commit -m "SECURITY: Fix critical vulnerabilities"')
    print('  5. git push origin main')

print('='*70)