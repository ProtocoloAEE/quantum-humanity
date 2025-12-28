# har_sealer_real.py
import json
import os
import hashlib
from datetime import datetime
import sys

# --- Intento de importar Kyber ---
try:
    from aeeprotocol.core.kyber_engine import KyberEngine
    kyber_available = True
except ImportError:
    kyber_available = False
# ---------------------------------

def certificar_registro(registro_bytes, engine=None):
    """
    Certifica un registro de evidencia. Usa Kyber si está disponible,
    si no, recurre a un hash SHA-512.
    """
    timestamp = datetime.now().isoformat()
    h = hashlib.sha512(registro_bytes).hexdigest()
    
    certificado = {
        "protocolo": "AEE-QH v1.1",
        "fecha_sellado": timestamp,
        "hash_sha512": h,
        "integridad": "VERIFICADA (SHA-512)"
    }

    if engine:
        try:
            # En una futura versión, esto debería usar una clave de firma del reporte.
            pk, _ = engine.generate_keypair()
            sello_pqc = engine.seal_data(registro_bytes, pk)
            certificado["algoritmo_pqc"] = "Kyber-768"
            certificado["clave_publica_pqc_hex"] = pk.hex()
            certificado["sello_pqc_hex"] = sello_pqc.hex()
            certificado["integridad"] = "VERIFICADA (PQC + SHA-512)"
        except Exception as e:
            certificado["error_pqc"] = f"Fallo en el sellado PQC: {e}"

    return certificado

def procesar_har(archivo_har_path):
    """
    Función principal que procesa un archivo HAR y genera el reporte AEE.
    """
    # --- PASO 1: Validaciones ---
    if not os.path.exists(archivo_har_path):
        print(f"❌ ERROR CRÍTICO: El archivo no existe en la ruta: {archivo_har_path}")
        return False

    if os.path.getsize(archivo_har_path) < 100:
        print(f"❌ ERROR CRÍTICO: El archivo '{os.path.basename(archivo_har_path)}' está vacío o corrupto.")
        return False

    print(f"✅ Archivo '{os.path.basename(archivo_har_path)}' encontrado ({os.path.getsize(archivo_har_path) / 1024:.2f} KB). Procediendo a analizar...")

    # --- PASO 2: Lectura y análisis ---
    try:
        with open(archivo_har_path, 'r', encoding='utf-8-sig') as f:
            har_data = json.load(f)
    except Exception as e:
        print(f"❌ ERROR DE FORMATO o LECTURA: {e}")
        return False

    # --- PASO 3: Procesamiento y sellado ---
    print("🚀 Procesando registros de red...")
    kyber_engine = KyberEngine() if kyber_available else None
    
    # El nombre del archivo AEE se basará en el nombre del HAR
    base_name = os.path.splitext(os.path.basename(archivo_har_path))[0]
    output_filename = f"{base_name}.aee"
    
    reporte_forense = {
        "protocolo_reporte": "AEE-QH Forensic Report v1.3",
        "fecha_generacion": datetime.now().isoformat(),
        "archivo_origen": os.path.basename(archivo_har_path),
        "motor_pqc_disponible": kyber_available,
        "estadisticas": {"total_registros": 0, "anomalias_detectadas": 0},
        "anomalias": [],
        "registros_sellados": []
    }
    
    entries = har_data.get('log', {}).get('entries', [])
    reporte_forense["estadisticas"]["total_registros"] = len(entries)

    for i, entry in enumerate(entries):
        request = entry.get('request', {})
        response = entry.get('response', {})
        status = response.get('status', 0)
        url = request.get('url', 'N/A')
        anomalias_registro = []
        if 400 <= status < 600:
            anomalias_registro.append(f"Status de error HTTP: {status}")
        
        if response.get('content', {}).get('mimeType', '').startswith('application/json'):
            try:
                content_text = response.get('content', {}).get('text', '')
                if content_text:
                    content_data = json.loads(content_text)
                    if isinstance(content_data, dict) and content_data.get('success') is False:
                        anomalias_registro.append("Respuesta JSON con 'success: false'")
            except Exception:
                pass
        
        if anomalias_registro:
            reporte_forense["estadisticas"]["anomalias_detectadas"] += 1
            detalle_anomalia = {"id_registro": i + 1, "url": url, "status": status, "alertas": anomalias_registro}
            reporte_forense["anomalias"].append(detalle_anomalia)
            print(f"   🚨 Anomalía encontrada en registro #{i+1} ({url})")

        registro_original_str = json.dumps(entry, ensure_ascii=False)
        registro_bytes = registro_original_str.encode('utf-8')
        certificado = certificar_registro(registro_bytes, kyber_engine)
        
        registro_sellado = {
            "id_registro": i + 1,
            "timestamp_original": entry.get("startedDateTime"),
            "url": url,
            "status": status,
            "certificado_integridad": certificado
        }
        reporte_forense["registros_sellados"].append(registro_sellado)
        
    # --- PASO 4: Generar reporte ---
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(reporte_forense, f, indent=4, ensure_ascii=False)
        
        print("\n" + "="*50)
        print(f"✅ ¡ÉXITO! Reporte forense sellado y guardado en: {output_filename}")
        print(f"   - Total de registros analizados: {reporte_forense['estadisticas']['total_registros']}")
        print(f"   - Total de anomalías detectadas: {reporte_forense['estadisticas']['anomalias_detectadas']}")
        print("="*50)
        return True
    except Exception as e:
        print(f"❌ ERROR CRÍTICO AL GUARDAR EL REPORTE: {e}")
        return False

if __name__ == "__main__":
    # Si se pasa un argumento por línea de comandos, se usa el modo automático.
    # Si no, se usa el modo interactivo.
    if len(sys.argv) > 1:
        har_path = sys.argv[1].strip().replace('"', '')
        procesar_har(har_path)
    else:
        print("🛡️ Quantum Humanity - Real HAR Sealer v1.3 (Modo Interactivo)")
        if kyber_available:
            print("✅ Motor Kyber-768 detectado y listo.")
        else:
            print("⚠️ ADVERTENCIA: Motor Kyber no encontrado.")
        print("-" * 50)
        
        har_path = input("Arrastrá el archivo .har aquí y presioná Enter: ").strip().replace('"', '')
        procesar_har(har_path)
        
        print("\nProceso finalizado. Presioná Enter para salir.")
        input()