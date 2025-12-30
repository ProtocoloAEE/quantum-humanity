import json
import hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519

def verificar_evidencia(archivo_path, certificado_path):
    try:
        # 1. Cargar el certificado
        with open(certificado_path, 'r') as f: cert = json.load(f)
        
        # 2. Re-calcular el hash del archivo actual
        with open(archivo_path, 'rb') as f: 
            hash_actual = hashlib.sha256(f.read()).hexdigest()
        
        # 3. Verificar integridad del contenido
        if hash_actual != cert['evidence']['file_hash']:
            return '❌ ALERTA: El archivo ha sido ALTERADO. El hash no coincide.'
        
        # 4. Validar Firma Digital Ed25519
        pub_key_hex = cert['auditor']['public_key']
        signature_hex = cert['signature']['value']
        data_signed = json.dumps(cert['signature']['data_signed'], sort_keys=True).encode()
        
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_key_hex))
        public_key.verify(bytes.fromhex(signature_hex), data_signed)
        
        return '✅ ÉXITO: Firma válida. Evidencia íntegra y auténtica.'
    except Exception as e:
        return f'❌ ERROR: Verificación fallida. Detalle: {str(e)}'

print('--- PROBANDO INTEGRIDAD DEL PROTOCOLO AEE ---')
print(verificar_evidencia('prueba.txt', 'certificado_evidencia.json'))
