# ============================================================================
# Archivo: test_client.py
# CLIENTE DE PRUEBA QUE USA LA API KEY CORRECTA
# ============================================================================

"""
Cliente de prueba para validar endpoints de AEE Protocol.
Ejecutar: python test_client.py

Este cliente:
1. Lee la API Key desde el mismo lugar que el servidor
2. Valida que la API Key sea correcta antes de enviar requests
3. Prueba todos los endpoints principales
"""

import requests
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))


class AEETestClient:
    """Cliente de prueba para AEE Protocol con validación de API Keys"""
    
    def __init__(self, base_url: str = "http://localhost:8000", use_dev_key: bool = True):
        """
        Inicializar cliente de prueba
        
        Args:
            base_url: URL base del servidor (default: localhost:8000)
            use_dev_key: Usar API Key de desarrollo (default: True)
        """
        self.base_url = base_url
        self.api_key = self._get_api_key(use_dev_key)
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        })
        
        print("=" * 80)
        print("🧪 AEE PROTOCOL - TEST CLIENT")
        print("=" * 80)
        print(f"\nServidor: {self.base_url}")
        print(f"API Key: {self.api_key}")
        print(f"Validación: {self._validate_key()}")
        print()
    
    def _get_api_key(self, use_dev: bool) -> str:
        """Obtener API Key del mismo lugar que el servidor"""
        
        # 1. Intentar leer desde .env
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('API_KEY_DEV'):
                        key = line.split('=', 1)[1].strip()
                        if use_dev:
                            return key
                    elif line.startswith('API_KEY_PROD'):
                        key = line.split('=', 1)[1].strip()
                        if not use_dev:
                            return key
        
        # 2. Intentar leer desde variables de entorno
        if use_dev:
            key = os.getenv('API_KEY_DEV')
        else:
            key = os.getenv('API_KEY_PROD')
        
        if key:
            return key
        
        # 3. Usar valores por defecto
        return 'aee-dev-key-2025' if use_dev else 'aee-prod-key-2025'
    
    def _validate_key(self) -> str:
        """Validar que la API Key sea reconocida por el servidor"""
        try:
            from aee.infrastructure.security import api_key_manager
            result = api_key_manager.validate(self.api_key)
            if result:
                return f"✓ VÁLIDA ({result.get('name', 'Unknown')})"
            else:
                return "✗ INVÁLIDA"
        except:
            return "? No se pudo validar localmente"
    
    def test_health(self) -> bool:
        """Probar endpoint /health"""
        print("\n[TEST 1] GET /health")
        print("-" * 80)
        
        try:
            resp = self.session.get(f"{self.base_url}/api/v1/health")
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"Status: {data.get('status')}")
                print(f"Version: {data.get('version')}")
                print(f"Components: {json.dumps(data.get('components'), indent=2)}")
                print("✓ ÉXITO")
                return True
            else:
                print(f"✗ FALLO: {resp.text}")
                return False
        except Exception as e:
            print(f"✗ ERROR: {e}")
            return False
    
    def test_certify(self) -> bool:
        """Probar endpoint POST /certify"""
        print("\n[TEST 2] POST /certify")
        print("-" * 80)
        
        payload = {
            "filename": "test_evidence.eml",
            "file_hash": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a",
            "file_size_bytes": 2048,
            "metadata": {
                "caso_numero": "2025-TEST-001",
                "perito_nombre": "Test User",
                "institucion": "Test Lab"
            }
        }
        
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            resp = self.session.post(
                f"{self.base_url}/api/v1/certify",
                json=payload
            )
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 201:
                data = resp.json()
                self.certificate_id = data.get('certificado_id')
                print(f"Certificate ID: {self.certificate_id}")
                print(f"Estado: {data.get('estado')}")
                print("✓ ÉXITO")
                return True
            else:
                print(f"✗ FALLO: {resp.text}")
                return False
        except Exception as e:
            print(f"✗ ERROR: {e}")
            return False
    
    def test_verify(self) -> bool:
        """Probar endpoint POST /verify"""
        print("\n[TEST 3] POST /verify")
        print("-" * 80)
        
        if not hasattr(self, 'certificate_id'):
            print("⊘ OMITIDO: No hay certificado de prueba (ejecuta /certify primero)")
            return None
        
        # Obtener certificado
        try:
            resp = self.session.get(f"{self.base_url}/api/v1/certificate/{self.certificate_id}")
            if resp.status_code != 200:
                print(f"✗ No se pudo obtener certificado: {resp.text}")
                return False
            
            certificado = resp.json()
        except Exception as e:
            print(f"✗ ERROR obteniendo certificado: {e}")
            return False
        
        # Verificar con mismo hash
        payload = {
            "file_hash": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a",
            "certificado": certificado
        }
        
        try:
            resp = self.session.post(
                f"{self.base_url}/api/v1/verify",
                json=payload
            )
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"Exitoso: {data.get('exitoso')}")
                print(f"Mensaje: {data.get('mensaje')}")
                print("✓ ÉXITO")
                return True
            else:
                print(f"✗ FALLO: {resp.text}")
                return False
        except Exception as e:
            print(f"✗ ERROR: {e}")
            return False
    
    def test_report(self) -> bool:
        """Probar endpoint GET /certificate/{id}/report"""
        print("\n[TEST 4] GET /certificate/{id}/report")
        print("-" * 80)
        
        if not hasattr(self, 'certificate_id'):
            print("⊘ OMITIDO: No hay certificado de prueba")
            return None
        
        try:
            resp = self.session.get(
                f"{self.base_url}/api/v1/certificate/{self.certificate_id}/report",
                params={"format": "json"}
            )
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"Generator: {data.get('metadata', {}).get('generator')}")
                print(f"Report Type: {data.get('metadata', {}).get('report_type')}")
                print("✓ ÉXITO")
                return True
            else:
                print(f"✗ FALLO: {resp.text}")
                return False
        except Exception as e:
            print(f"✗ ERROR: {e}")
            return False
    
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        results = {
            'health': self.test_health(),
            'certify': self.test_certify(),
            'verify': self.test_verify(),
            'report': self.test_report()
        }
        
        print("\n" + "=" * 80)
        print("📊 RESUMEN DE RESULTADOS")
        print("=" * 80)
        
        for test_name, result in results.items():
            status = "✓ ÉXITO" if result is True else ("✗ FALLO" if result is False else "⊘ OMITIDO")
            print(f"{test_name:20} -> {status}")
        
        passed = sum(1 for r in results.values() if r is True)
        total = sum(1 for r in results.values() if r is not None)
        
        print(f"\nTotal: {passed}/{total} tests pasaron")
        print("=" * 80)


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AEE Protocol Test Suite")
    parser.add_argument("--debug", action="store_true", help="Ejecutar solo debugger de API Keys")
    parser.add_argument("--url", default="http://localhost:8000", help="URL del servidor")
    parser.add_argument("--prod", action="store_true", help="Usar API Key de producción")
    
    args = parser.parse_args()
    
    if args.debug:
        debug_api_keys()
    else:
        client = AEETestClient(base_url=args.url, use_dev_key=not args.prod)
        client.run_all_tests()