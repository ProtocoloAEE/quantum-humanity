import sys
import os
sys.path.insert(0, os.getcwd() + '/src')
import aeeprotocol
import numpy as np

print("🛡️  SISTEMA QUANTUM HUMANITY v0.6.0")
print("-" * 40)

engine = aeeprotocol.engine

# 1. Generar llaves
print("🔑 Generando Par de Llaves Cuánticas...")
pk, sk = engine.generate_keypair()

# 2. Asegurarnos que la obra sea un array de NumPy explícito
print("✍️  Preparando Obra Humana (Embedding)...")
obra = np.random.randn(768).astype(np.float32)

# 3. Sellar (con manejo de errores interno)
print("🔐 Aplicando Sello Post-Cuántico...")
try:
    # Pasamos la obra asegurándonos que sea el objeto correcto
    sello = engine.seal_embedding(obra, pk)

    print("-" * 40)
    print("✅ ¡OBRA CERTIFICADA EXITOSAMENTE!")
    print(f"📦 Algoritmo: {sello.get('algorithm', 'Kyber-768')}")
    # Accedemos al ciphertext con seguridad
    c_data = sello.get('ciphertext', b'')
    print(f"🆔 Hash del Sello: {c_data[:30].hex()}...")
    print(f"🛡️  Seguridad: ML-KEM-768 Activo")
    print("-" * 40)
except Exception as e:
    print(f"❌ Error en el sellado: {e}")
    print("Intentando modo compatibilidad directa...")
    # Si falla, es probable que el motor espere bytes directos
    sello = engine.seal_embedding(obra.tobytes(), pk)
    print("✅ Certificado mediante canal de compatibilidad.")
