"""
Fuzz Testing Script - AEE Protocol API v2.1
Pentesting tool para validar resistencia de la API a payloads maliciosos.

Modelo de Seguridad v2.1:
- Valida que el servidor maneja errores sin degradación silenciosa
- Verifica que no hay crashes del proceso Python
- Confirma que errores se manejan con códigos HTTP apropiados (4xx/5xx)
"""

import requests
import json
import random
import string
import sys
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configuración
BASE_URL = "http://127.0.0.1:8000"
API_KEY = "aee-dev-key-2025"  # API key de desarrollo
TOTAL_REQUESTS = 1000
TIMEOUT = 5  # segundos

# Estadísticas globales
stats = {
    'packets_sent': 0,
    'errors_controlled': 0,  # 4xx y 5xx que no crashean el servidor
    'crashes': 0,  # Cuando el servidor no responde o el proceso se cae
    'success_responses': 0,  # 2xx (no debería pasar con payloads corruptos)
    'connection_errors': 0,
    'timeout_errors': 0,
    'other_errors': 0
}


class Fuzzer:
    """Generador de payloads corruptos para fuzzing"""
    
    @staticmethod
    def generate_null_bytes(length: int = 100) -> str:
        """Genera string con caracteres nulos"""
        return '\x00' * length
    
    @staticmethod
    def generate_giant_string(size_mb: float = 10.0) -> str:
        """Genera string gigante (por defecto 10MB)"""
        size_bytes = int(size_mb * 1024 * 1024)
        return 'A' * size_bytes
    
    @staticmethod
    def generate_malformed_json() -> str:
        """Genera JSON malformado"""
        malformed_options = [
            '{"key": "value",}',  # Coma final
            '{"key": "value"',  # Sin cerrar
            '{key: "value"}',  # Sin comillas en key
            '{"key": value}',  # Sin comillas en value
            '{"key": "value" "key2": "value2"}',  # Sin coma
            '{"key": [1, 2, 3,]}',  # Coma final en array
            '{"key": {"nested": "value"}',  # Sin cerrar objeto anidado
            '{"key": null, "key2": undefined}',  # undefined no es válido en JSON
            '{"key": "value"}\n{"key2": "value2"}',  # Múltiples objetos
            '{"key": "value"}\x00{"key2": "value2"}',  # Null byte en medio
        ]
        return random.choice(malformed_options)
    
    @staticmethod
    def generate_wrong_types() -> Dict[str, Any]:
        """Genera payload con tipos de datos incorrectos"""
        return {
            'filename': 12345,  # Debería ser string
            'file_hash': ['a', 'b', 'c'],  # Debería ser string
            'file_size_bytes': "not_a_number",  # Debería ser int
            'metadata': "should_be_object",  # Debería ser objeto
            'file_hash': None,  # No debería ser None
            'file_size_bytes': -100,  # Debería ser > 0
            'file_size_bytes': 0,  # Debería ser > 0
        }
    
    @staticmethod
    def generate_corrupt_certify_payload() -> Dict[str, Any]:
        """Genera payload corrupto para /certify"""
        corruption_type = random.choice([
            'null_bytes',
            'giant_string',
            'malformed_json',
            'wrong_types',
            'missing_fields',
            'extra_fields',
            'sql_injection',
            'xss',
            'path_traversal'
        ])
        
        base_payload = {
            'filename': 'test.txt',
            'file_hash': 'a' * 64,  # Hash válido de 64 chars
            'file_size_bytes': 1024
        }
        
        if corruption_type == 'null_bytes':
            base_payload['filename'] = Fuzzer.generate_null_bytes(50)
            base_payload['file_hash'] = Fuzzer.generate_null_bytes(64)
        
        elif corruption_type == 'giant_string':
            base_payload['filename'] = Fuzzer.generate_giant_string(0.1)  # 100KB
            base_payload['file_hash'] = Fuzzer.generate_giant_string(0.01)  # 10KB
        
        elif corruption_type == 'wrong_types':
            wrong = Fuzzer.generate_wrong_types()
            base_payload.update(wrong)
        
        elif corruption_type == 'missing_fields':
            # Eliminar campos requeridos
            fields_to_remove = random.sample(list(base_payload.keys()), random.randint(1, len(base_payload)))
            for field in fields_to_remove:
                base_payload.pop(field, None)
        
        elif corruption_type == 'extra_fields':
            # Agregar campos extraños
            base_payload['__proto__'] = {'malicious': True}
            base_payload['constructor'] = {'prototype': {'polluted': True}}
            base_payload['$where'] = 'malicious_code'
        
        elif corruption_type == 'sql_injection':
            base_payload['filename'] = "test.txt'; DROP TABLE certificates; --"
            base_payload['file_hash'] = "1' OR '1'='1"
        
        elif corruption_type == 'xss':
            base_payload['filename'] = "<script>alert('XSS')</script>"
            base_payload['metadata'] = {'notas': "<img src=x onerror=alert(1)>"}
        
        elif corruption_type == 'path_traversal':
            base_payload['filename'] = "../../../etc/passwd"
            base_payload['file_hash'] = "....//....//etc/shadow"
        
        return base_payload
    
    @staticmethod
    def generate_corrupt_verify_payload() -> Dict[str, Any]:
        """Genera payload corrupto para /verify"""
        corruption_type = random.choice([
            'null_bytes',
            'giant_string',
            'wrong_types',
            'missing_fields',
            'corrupt_certificate',
            'invalid_signature_format'
        ])
        
        # Certificado base (válido estructuralmente pero corrupto)
        base_cert = {
            'certificado_id': 'test-id',
            'hash_sha256': 'a' * 64,
            'timestamp_ntp': {'timestamp_iso': '2026-01-01T00:00:00Z'},
            'archivo': {'nombre': 'test.txt', 'tamano_bytes': 1024},
            'claves_publicas': {
                'ed25519_public': 'b' * 64,
                'kyber_public': 'c' * 100
            },
            'firmas': {
                'signature_classic': 'd' * 128,
                'pqc_seal': 'e' * 100,
                'pqc_auth_tag': 'f' * 64,
                'timestamp': '2026-01-01T00:00:00Z'
            }
        }
        
        base_payload = {
            'file_hash': 'a' * 64,
            'certificado': base_cert
        }
        
        if corruption_type == 'null_bytes':
            base_payload['file_hash'] = Fuzzer.generate_null_bytes(64)
            base_payload['certificado']['hash_sha256'] = Fuzzer.generate_null_bytes(64)
        
        elif corruption_type == 'giant_string':
            base_payload['file_hash'] = Fuzzer.generate_giant_string(0.1)
            base_payload['certificado']['hash_sha256'] = Fuzzer.generate_giant_string(0.1)
        
        elif corruption_type == 'wrong_types':
            base_payload['file_hash'] = 12345
            base_payload['certificado'] = "not_an_object"
        
        elif corruption_type == 'missing_fields':
            base_payload.pop('certificado', None)
        
        elif corruption_type == 'corrupt_certificate':
            base_payload['certificado']['claves_publicas'] = None
            base_payload['certificado']['firmas'] = None
        
        elif corruption_type == 'invalid_signature_format':
            base_payload['certificado']['firmas']['signature_classic'] = "not_hex"
            base_payload['certificado']['claves_publicas']['ed25519_public'] = "not_hex"
        
        return base_payload


def send_fuzz_request(endpoint: str, payload: Any, is_json: bool = True) -> Optional[requests.Response]:
    """
    Envía una petición de fuzzing al endpoint.
    
    Returns:
        Response object si la petición se completó, None si hubo crash/error crítico
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        if is_json:
            # Intentar serializar como JSON
            try:
                json_payload = json.dumps(payload)
            except (TypeError, ValueError):
                # Si no se puede serializar, enviar como string raw
                json_payload = str(payload)
                headers['Content-Type'] = 'text/plain'
            
            response = requests.post(
                url,
                data=json_payload,
                headers=headers,
                timeout=TIMEOUT
            )
        else:
            # Enviar como string raw (JSON malformado)
            response = requests.post(
                url,
                data=payload,
                headers=headers,
                timeout=TIMEOUT
            )
        
        return response
        
    except requests.exceptions.ConnectionError:
        stats['connection_errors'] += 1
        stats['crashes'] += 1
        return None
    
    except requests.exceptions.Timeout:
        stats['timeout_errors'] += 1
        stats['crashes'] += 1
        return None
    
    except Exception as e:
        stats['other_errors'] += 1
        stats['crashes'] += 1
        print(f"  [ERROR] Excepción inesperada: {type(e).__name__}: {e}")
        return None


def check_server_health() -> bool:
    """Verifica que el servidor esté respondiendo"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def run_fuzz_test():
    """Ejecuta el test de fuzzing completo"""
    print("=" * 70)
    print("FUZZ TESTING - AEE Protocol API v2.1")
    print("=" * 70)
    print(f"Target: {BASE_URL}")
    print(f"Total requests: {TOTAL_REQUESTS}")
    print(f"Timeout: {TIMEOUT}s")
    print()
    
    # Verificar que el servidor esté corriendo
    print("[1/3] Verificando disponibilidad del servidor...")
    if not check_server_health():
        print("  [ERROR] El servidor no está respondiendo en", BASE_URL)
        print("  Inicia el servidor con: uvicorn aee.api.fastapi_server:app --host 127.0.0.1 --port 8000")
        sys.exit(1)
    print("  [OK] Servidor disponible")
    print()
    
    # Fuzzing de /certify
    print("[2/3] Fuzzing endpoint /api/v1/certify...")
    certify_endpoint = "/api/v1/certify"
    
    for i in range(TOTAL_REQUESTS // 2):
        if (i + 1) % 100 == 0:
            print(f"  Progreso: {i + 1}/{TOTAL_REQUESTS // 2} requests")
        
        # Generar payload corrupto
        payload = Fuzzer.generate_corrupt_certify_payload()
        
        # Enviar petición
        response = send_fuzz_request(certify_endpoint, payload)
        stats['packets_sent'] += 1
        
        if response is None:
            continue  # Ya contado como crash
        
        # Analizar respuesta
        status_code = response.status_code
        
        if 200 <= status_code < 300:
            stats['success_responses'] += 1
            print(f"  [WARNING] Respuesta exitosa inesperada: {status_code}")
        
        elif 400 <= status_code < 500:
            stats['errors_controlled'] += 1  # Error controlado (4xx)
        
        elif 500 <= status_code < 600:
            stats['errors_controlled'] += 1  # Error controlado (5xx)
        
        else:
            stats['other_errors'] += 1
    
    print(f"  [OK] {TOTAL_REQUESTS // 2} requests enviadas a /certify")
    print()
    
    # Fuzzing de /verify
    print("[3/3] Fuzzing endpoint /api/v1/verify...")
    verify_endpoint = "/api/v1/verify"
    
    for i in range(TOTAL_REQUESTS // 2):
        if (i + 1) % 100 == 0:
            print(f"  Progreso: {i + 1}/{TOTAL_REQUESTS // 2} requests")
        
        # Generar payload corrupto
        payload = Fuzzer.generate_corrupt_verify_payload()
        
        # Enviar petición
        response = send_fuzz_request(verify_endpoint, payload)
        stats['packets_sent'] += 1
        
        if response is None:
            continue  # Ya contado como crash
        
        # Analizar respuesta
        status_code = response.status_code
        
        if 200 <= status_code < 300:
            stats['success_responses'] += 1
            print(f"  [WARNING] Respuesta exitosa inesperada: {status_code}")
        
        elif 400 <= status_code < 500:
            stats['errors_controlled'] += 1  # Error controlado (4xx)
        
        elif 500 <= status_code < 600:
            stats['errors_controlled'] += 1  # Error controlado (5xx)
        
        else:
            stats['other_errors'] += 1
    
    print(f"  [OK] {TOTAL_REQUESTS // 2} requests enviadas a /verify")
    print()
    
    # Verificación final del servidor
    print("[VERIFICACION] Comprobando que el servidor sigue funcionando...")
    if check_server_health():
        print("  [OK] Servidor sigue respondiendo correctamente")
    else:
        print("  [CRITICAL] El servidor dejó de responder - posible crash")
        stats['crashes'] += 1
    print()


def print_summary():
    """Imprime resumen final del fuzzing"""
    print("=" * 70)
    print("RESUMEN DE FUZZ TESTING")
    print("=" * 70)
    print(f"Paquetes enviados:        {stats['packets_sent']}")
    print(f"Errores controlados:      {stats['errors_controlled']} (4xx/5xx)")
    print(f"Crashes del sistema:      {stats['crashes']}")
    print()
    print("Desglose adicional:")
    print(f"  - Respuestas exitosas (2xx):     {stats['success_responses']}")
    print(f"  - Errores de conexión:           {stats['connection_errors']}")
    print(f"  - Timeouts:                      {stats['timeout_errors']}")
    print(f"  - Otros errores:                 {stats['other_errors']}")
    print()
    
    # Evaluación de seguridad
    if stats['crashes'] == 0:
        print("[RESULTADO] ✅ El servidor manejó todos los payloads sin crashes")
    else:
        print(f"[RESULTADO] ⚠️  Se detectaron {stats['crashes']} posibles crashes")
    
    if stats['success_responses'] > 0:
        print(f"[ADVERTENCIA] ⚠️  {stats['success_responses']} payloads corruptos fueron aceptados")
    
    print("=" * 70)


if __name__ == "__main__":
    try:
        run_fuzz_test()
        print_summary()
        
        # Exit code basado en resultados
        if stats['crashes'] > 0:
            sys.exit(1)  # Hay crashes
        elif stats['success_responses'] > 0:
            sys.exit(2)  # Payloads corruptos aceptados
        else:
            sys.exit(0)  # Todo OK
    
    except KeyboardInterrupt:
        print("\n[INTERRUPCION] Fuzzing interrumpido por el usuario")
        print_summary()
        sys.exit(130)
    
    except Exception as e:
        print(f"\n[ERROR CRITICO] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        print_summary()
        sys.exit(1)


