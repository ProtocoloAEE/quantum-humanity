import sys
import os
import hashlib
sys.path.insert(0, os.getcwd() + '/src')
import aeeprotocol

def certificar_mensaje(mensaje_texto):
    engine = aeeprotocol.engine
    
    # 1. Tu Identidad
    pk, sk = engine.generate_keypair()
    
    # 2. Convertir texto en "Esencia Digital" (Hash del contenido)
    print(f"📄 Certificando: '{mensaje_texto}'")
    contenido_bytes = mensaje_texto.encode('utf-8')
    
    # 3. Aplicar Sello Cuántico
    sello = engine.seal_embedding(contenido_bytes, pk)
    
    # 4. Guardar Certificado
    with open("certificado_autoria.aee", "w") as f:
        f.write(f"ID_SELLADO: {sello['ciphertext'].hex()}\n")
        f.write(f"ALGORITMO: {sello['algorithm']}\n")
        f.write(f"PROPIETARIO_PK: {pk.hex()}\n")
    
    print("-" * 40)
    print("✅ CERTIFICADO GENERADO: certificado_autoria.aee")
    print(f"🆔 FIRMA: {sello['ciphertext'][:20].hex()}...")
    print("-" * 40)

if __name__ == "__main__":
    test_msg = input("Ingresá el mensaje o nombre de obra a certificar: ")
    certificar_mensaje(test_msg)
