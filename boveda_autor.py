import os
import sys
import hashlib
import getpass
from pathlib import Path

# Forzar ruta al core
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

try:
    import aeeprotocol
    engine = aeeprotocol.engine
except ImportError as e:
    print(f"âŒ Error importando protocolo: {e}")
    sys.exit(1)

BOVEDA_FILE = "identidad_franco.key"
MANIFESTO_FILE = "manifiesto_qh.txt"

def generar_boveda():
    print("\nðŸ” GENERANDO BÃ“VEDA DE IDENTIDAD CUÃNTICA")
    print("   Autor: Franco Luciano Carricondo\n")

    pk, sk = engine.generate_keypair()

    print(f"ðŸ†” Tu Clave PÃºblica (Tu ID mundial):")
    print(f"    {pk.hex()}\n")

    password = getpass.getpass("ðŸ”’ IngresÃ¡ una contraseÃ±a para proteger tu llave privada: ")
    password2 = getpass.getpass("   RepetÃ­ la contraseÃ±a: ")

    if password != password2:
        print("âŒ Las contraseÃ±as no coinciden")
        return

    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha512', password.encode(), salt, 100000, dklen=32)
    
    # EncriptaciÃ³n simple XOR para la llave privada
    mask = hashlib.sha256(key + salt).digest() * (len(sk) // 32 + 1)
    encrypted_sk = bytes(a ^ b for a, b in zip(sk, mask))

    with open(BOVEDA_FILE, "w") as f:
        f.write(f"OWNER: Franco Luciano Carricondo\n")
        f.write(f"PUBLIC_KEY: {pk.hex()}\n")
        f.write(f"ENCRYPTED_SK: {encrypted_sk.hex()}\n")
        f.write(f"SALT: {salt.hex()}\n")

    print(f"\nâœ… BÃ“VEDA GENERADA: {BOVEDA_FILE}")

def firmar_manifiesto():
    if not os.path.exists(BOVEDA_FILE):
        print("âŒ No existe la bÃ³veda. ElegÃ­ opciÃ³n 1 primero.")
        return

    with open(BOVEDA_FILE, "r") as f:
        data = {l.split(": ")[0]: l.split(": ")[1].strip() for l in f}

    password = getpass.getpass("ðŸ”’ ContraseÃ±a para desbloquear identidad: ")
    salt = bytes.fromhex(data['SALT'])
    key = hashlib.pbkdf2_hmac('sha512', password.encode(), salt, 100000, dklen=32)
    
    # Desencriptar SK
    enc_sk = bytes.fromhex(data['ENCRYPTED_SK'])
    mask = hashlib.sha256(key + salt).digest() * (len(enc_sk) // 32 + 1)
    sk = bytes(a ^ b for a, b in zip(enc_sk, mask))
    pk = bytes.fromhex(data['PUBLIC_KEY'])

    if not os.path.exists(MANIFESTO_FILE):
        with open(MANIFESTO_FILE, "w") as f: f.write("MANIFIESTO QUANTUM HUMANITY\nAUTOR: FRANCO CARRICONDO")

    with open(MANIFESTO_FILE, "r", encoding="utf-8") as f: contenido = f.read()

    print("ðŸ“œ Firmando con tu Identidad Permanente...")
    sello = engine.seal_embedding(contenido.encode('utf-8'), pk)

    with open("manifiesto_firmado_OFICIAL.aee", "w") as f:
        f.write(f"--- CERTIFICADO OFICIAL AEE ---\n")
        f.write(f"AUTOR: {data['OWNER']}\n")
        f.write(f"FIRMA_PQC: {sello['ciphertext'].hex()}\n")
        f.write(f"PUB_KEY: {data['PUBLIC_KEY']}\n")

    print(f"\nðŸŽ‰ Â¡OBRA SELLADA PARA LA ETERNIDAD!")
    print(f"Firma: {sello['ciphertext'].hex()[:32]}...")

if __name__ == "__main__":
    print("ðŸ›¡ï¸ SISTEMA DE IDENTIDAD AEE")
    print("1. Crear mi BÃ³veda Maestra")
    print("2. Firmar Manifiesto con mi Identidad")
    op = input("SelecciÃ³n: ")
    if op == "1": generar_boveda()
    elif op == "2": firmar_manifiesto()