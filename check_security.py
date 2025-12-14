"""
Verificación completa de implementación de seguridad
"""

import os
import sys
import re

def check_file_exists(filename, description):
    """Verifica que un archivo existe."""
    exists = os.path.exists(filename)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filename}")
    return exists

def check_file_content(filename, patterns):
    """Verifica contenido de archivo."""
    if not os.path.exists(filename):
        print(f"  ❌ Archivo no existe: {filename}")
        return False
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n📄 Verificando {filename}:")
    all_ok = True
    
    for pattern_name, pattern in patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            print(f"  ✅ {pattern_name}")
        else:
            print(f"  ❌ {pattern_name} - NO ENCONTRADO")
            all_ok = False
    
    return all_ok

def main():
    print("="*70)
    print("VERIFICACIÓN DE IMPLEMENTACIÓN DE SEGURIDAD")
    print("="*70)
    
    # 1. Verificar archivos creados
    print("\n📁 ARCHIVOS DE SEGURIDAD:")
    
    files_to_check = [
        ("aeeprotocol/core/engine_secure.py", "Engine seguro (HMAC)"),
        ("aeeprotocol/sdk/client_secure.py", "Cliente seguro"),
        (".env.example", "Plantilla de variables de entorno"),
        (".gitignore", "Gitignore (debe incluir .env)"),
    ]
    
    all_files_exist = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ Faltan archivos de seguridad. No continúes.")
        return False
    
    # 2. Verificar contenido de engine_secure.py
    print("\n" + "="*70)
    print("🔐 VERIFICACIÓN DE ENGINE SEGURO")
    
    engine_patterns = {
        "HMAC implementation": r"hmac\.new",
        "Secret key parameter": r"secret_key.*bytes",
        "Key generation": r"secrets\.token_bytes",
        "Key fingerprint": r"key_fingerprint",
        "Security warning": r"SECURITY WARNING",
    }
    
    engine_ok = check_file_content(
        "aeeprotocol/core/engine_secure.py", 
        engine_patterns
    )
    
    # 3. Verificar contenido de client_secure.py
    print("\n" + "="*70)
    print("🔐 VERIFICACIÓN DE CLIENTE SEGURO")
    
    client_patterns = {
        "Environment variable": r"AEE_SECRET_KEY|os\.getenv",
        "Base64 encoding": r"base64\.b64decode|base64\.b64encode",
        "Key generation method": r"generate_key",
        "Secure initialization": r"AEEClientSecure",
    }
    
    client_ok = check_file_content(
        "aeeprotocol/sdk/client_secure.py", 
        client_patterns
    )
    
    # 4. Verificar .env.example
    print("\n" + "="*70)
    print("🔐 VERIFICACIÓN DE .env.example")
    
    if os.path.exists(".env.example"):
        with open(".env.example", 'r') as f:
            env_content = f.read()
        
        if "AEE_SECRET_KEY" in env_content:
            print("  ✅ Contiene AEE_SECRET_KEY")
        else:
            print("  ❌ NO contiene AEE_SECRET_KEY")
            client_ok = False
        
        if "# Generate with:" in env_content:
            print("  ✅ Tiene instrucciones de generación")
        else:
            print("  ⚠️  Sin instrucciones de generación")
    else:
        print("  ❌ .env.example no existe")
        client_ok = False
    
    # 5. Verificar .gitignore
    print("\n" + "="*70)
    print("🔐 VERIFICACIÓN DE .gitignore")
    
    if os.path.exists(".gitignore"):
        with open(".gitignore", 'r') as f:
            gitignore = f.read()
        
        if ".env" in gitignore or "*.env" in gitignore:
            print("  ✅ .env está en .gitignore")
        else:
            print("  ❌ .env NO está en .gitignore - ¡AGREGALO!")
            print("  Añade esta línea a .gitignore:")
            print("  .env")
            print("  *.env")
    else:
        print("  ⚠️  .gitignore no existe")
    
    # 6. Verificar git status
    print("\n" + "="*70)
    print("🔐 VERIFICACIÓN DE GIT STATUS")
    
    try:
        import subprocess
        result = subprocess.run(
            "git status --short", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        if result.stdout.strip():
            print("  ⚠️  Cambios pendientes por commit:")
            print("  " + result.stdout.replace("\n", "\n  "))
        else:
            print("  ✅ Todo commiteado")
    except:
        print("  ⚠️  No se pudo verificar git status")
    
    # 7. Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE SEGURIDAD")
    print("="*70)
    
    if engine_ok and client_ok and all_files_exist:
        print("✅ IMPLEMENTACIÓN DE SEGURIDAD COMPLETA")
        print("\n🎯 Próximos pasos:")
        print("1. git add . && git commit -m 'SECURITY: Complete implementation'")
        print("2. git push origin main")
        print("3. Crear Release v0.2.4")
        print("4. Actualizar README.md con instrucciones de seguridad")
    else:
        print("❌ IMPLEMENTACIÓN DE SEGURIDAD INCOMPLETA")
        print("\n⚠️  Corrige los problemas antes de continuar.")
    
    print("="*70)
    
    return engine_ok and client_ok and all_files_exist

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)