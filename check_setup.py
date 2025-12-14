#!/usr/bin/env python3
"""
check_setup.py - Verifica que el setup.py está correctamente configurado
"""

import os
import sys
import subprocess
import pkg_resources

def run_command(cmd):
    """Ejecuta un comando y retorna salida"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_file_exists(filename):
    """Verifica que un archivo existe"""
    exists = os.path.exists(filename)
    status = "✅" if exists else "❌"
    print(f"{status} {filename}")
    return exists

def check_package_import():
    """Verifica que el paquete se puede importar"""
    try:
        import aeeprotocol
        print(f"✅ aeeprotocol importado: v{aeeprotocol.__version__}")
        return True
    except ImportError as e:
        print(f"❌ No se puede importar aeeprotocol: {e}")
        return False
    except AttributeError as e:
        print(f"⚠️  aeeprotocol importado pero falta __version__: {e}")
        return True

def check_dependencies():
    """Verifica dependencias instaladas"""
    required = ["numpy", "scipy"]
    print("\n📦 Verificando dependencias:")
    
    all_ok = True
    for dep in required:
        try:
            version = pkg_resources.get_distribution(dep).version
            print(f"  ✅ {dep}: {version}")
        except pkg_resources.DistributionNotFound:
            print(f"  ❌ {dep}: NO INSTALADO")
            all_ok = False
    
    return all_ok

def main():
    print("="*60)
    print("VERIFICACIÓN DE CONFIGURACIÓN DEL PAQUETE")
    print("="*60)
    
    # Cambiar al directorio del script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Verificar archivos esenciales
    print("\n📁 Archivos esenciales:")
    essential_files = [
        "setup.py",
        "requirements.txt", 
        "aeeprotocol/__init__.py",
        "README.md",
        "LICENSE",
    ]
    
    all_files_exist = all(check_file_exists(f) for f in essential_files)
    
    # 2. Verificar dependencias
    deps_ok = check_dependencies()
    
    # 3. Verificar importación
    print("\n🐍 Verificando importación del paquete:")
    import_ok = check_package_import()
    
    # 4. Resumen
    print("\n" + "="*60)
    print("RESUMEN:")
    
    if all_files_exist and deps_ok and import_ok:
        print("✅ CONFIGURACIÓN COMPLETA - Todo listo!")
        print("\n📋 Siguientes pasos:")
        print("1. python -c \"from aeeprotocol.sdk.client import AEEClient; print('Cliente funciona')\"")
        print("2. python auditor_test.py (para validar)")
        print("3. git add . && git commit -m 'build: Professional setup.py'")
        print("4. git push origin main")
    else:
        print("⚠️  Hay problemas que resolver:")
        if not all_files_exist:
            print("  - Faltan archivos esenciales")
        if not deps_ok:
            print("  - Faltan dependencias: pip install numpy scipy")
        if not import_ok:
            print("  - Error al importar paquete")
    
    print("="*60)
    return all_files_exist and deps_ok and import_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)