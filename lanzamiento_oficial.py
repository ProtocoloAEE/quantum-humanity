import sys, os, hashlib
# Forzar la ruta del core
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
try:
    import aeeprotocol
    engine = aeeprotocol.engine
    
    manifiesto = "MANIFIESTO QUANTUM HUMANITY v1.0\nAUTOR: FRANCO CARRICONDO\n1. SOBERANIA\n2. INTEGRIDAD\n3. RESISTENCIA"
    
    print("\n🚀 INICIANDO SELLADO CUANTICO...")
    pk, sk = engine.generate_keypair()
    
    # Sellado del manifiesto
    sello = engine.seal_embedding(manifiesto.encode('utf-8'), pk)
    
    # Guardar el resultado
    with open("certificado_manifiesto.aee", "w") as f:
        f.write(f"ID: {sello['ciphertext'].hex()}\n")
        f.write(f"PK: {pk.hex()}\n")
        f.write(f"ALGO: {sello['algorithm']}\n")
    
    print("-" * 40)
    print("✅ SELLADO EXITOSO EN DISCO")
    print(f"🆔 FIRMA: {sello['ciphertext'][:15].hex()}...")
    print("-" * 40)
except Exception as e:
    print(f"❌ ERROR CRITICO: {e}")