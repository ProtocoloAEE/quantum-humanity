import json
import hashlib
from datetime import datetime
from pathlib import Path
import sys
import requests  # Para BFA si hay API futura

# Ruta a tu motor Kyber (ajusta)
from src.aeeprotocol.core.kyber_engine import KyberEngine

def generar_hash(cuerpo: bytes) -> str:
    return hashlib.sha3_512(cuerpo).hexdigest()

def certificar_evidencia(ruta_json: str):
    with open(ruta_json, 'r', encoding='utf-8') as f:
        evidencia = json.load(f)
    
    cuerpo = json.dumps(evidencia, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    hash_integridad = generar_hash(cuerpo.encode('utf-8'))
    
    motor = KyberEngine()
    pk, sk = motor.generate_keypair()  # O usa vault para clave fija
    sello = motor.seal_embedding(cuerpo.encode('utf-8'), pk)
    
    certificado = {
        "protocolo": "AEE v1.5",
        "autor": "Franco Carricondo",
        "dni": "35664619",
        "fecha": datetime.utcnow().isoformat() + "Z",
        "evidencia_original": evidencia,
        "hash_sha3_512": hash_integridad,
        "sello_post_cuantico": {
            "algoritmo": "ML-KEM-768",
            "ciphertext": sello['ciphertext'].hex(),
            "public_key": pk.hex()
        },
        "nota_bfa": "Para timestamp oficial, subí el hash_sha3_512 a https://bfa.ar/sello2"
    }
    
    salida = Path(ruta_json).stem + "_certificado.aee"
    with open(salida, 'w', encoding='utf-8') as f:
        json.dump(certificado, f, indent=4, ensure_ascii=False)
    
    print(f"Certificado generado: {salida}")
    print(f"Hash: {hash_integridad}")
    print("Subí este hash a BFA.ar para timestamp oficial gratuito.")

def verificar_certificado(ruta_aee: str):
    with open(ruta_aee, 'r', encoding='utf-8') as f:
        cert = json.load(f)
    
    cuerpo = json.dumps(cert["evidencia_original"], sort_keys=True, separators=(',', ':'))
    hash_verif = generar_hash(cuerpo.encode('utf-8'))
    
    if hash_verif == cert["hash_sha3_512"]:
        print("Integridad OK")
    else:
        print("Alterado")
    
    # Verificación sello (ajusta con tu Kyber)
    motor = KyberEngine()
    # if motor.verify(...): print("Sello OK")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python notario_pqc.py <evidencia.json>")
        sys.exit(1)
    
    if sys.argv[1] == "--verify":
        verificar_certificado(sys.argv[2])
    else:
        certificar_evidencia(sys.argv[1])