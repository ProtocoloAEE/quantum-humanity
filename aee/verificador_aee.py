# verificador_aee.py
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

def verify_pqc_signature(engine, certificado, data_bytes):
    """
    Verifica la firma PQC de un registro.
    NOTA: Esta es una implementación conceptual. La versión actual del sellador
    usa un método de 'sellado' que no es verificable sin la clave privada.
    Una futura versión usará un esquema de firma digital estándar.
    """
    if not kyber_available or "sello_pqc_hex" not in certificado:
        return "NO_DISPONIBLE"

    # En un esquema de firma real, usaríamos la clave pública del reporte
    # y un método engine.verify(firma, datos, clave_publica).
    # Como el sellador actual usa claves efímeras, la verificación real no es posible.
    # Esta función sirve como marcador de posición para la arquitectura correcta.
    return "IMPOSIBLE_VERIFICAR_CON_SELLADO_ACTUAL"

def main():
    """Función principal del verificador AEE."""
    print("🛡️ Quantum Humanity - Verificador de Evidencia AEE v1.0")
    print("-" * 60)

    if len(sys.argv) > 1:
        aee_file_path = sys.argv[1]
    else:
        aee_file_path = input("Arrastrá el archivo .aee aquí y presioná Enter: ").strip().replace('"', '')

    # --- Validación del archivo AEE ---
    if not os.path.exists(aee_file_path):
        print(f"❌ ERROR: El archivo de evidencia '{aee_file_path}' no existe.")
        return

    try:
        with open(aee_file_path, 'r', encoding='utf-8-sig') as f:
            reporte = json.load(f)
        print(f"✅ Reporte AEE '{os.path.basename(aee_file_path)}' cargado correctamente.")
    except Exception as e:
        print(f"❌ ERROR: El archivo '{aee_file_path}' está corrupto o no es un JSON válido. Error: {e}")
        return

    # --- Validación del archivo HAR original ---
    har_file_path = reporte.get("archivo_origen")
    if not har_file_path or not os.path.exists(har_file_path):
        print("\n⚠️ ADVERTENCIA: No se encontró el archivo HAR original referenciado en el reporte.")
        print(f"   Se esperaba encontrar '{har_file_path}' en la misma carpeta.")
        print("   Solo se podrá mostrar la información del reporte, pero no verificar la integridad de los hashes.")
        har_data = None
    else:
        try:
            with open(har_file_path, 'r', encoding='utf-8-sig') as f:
                har_data = json.load(f)
            print(f"✅ Archivo HAR original '{har_file_path}' encontrado y cargado.")
        except Exception as e:
            print(f"\n❌ ERROR: El archivo HAR original '{har_file_path}' está corrupto. Error: {e}")
            print("   No se puede proceder con la verificación de integridad.")
            return

    # --- Proceso de Verificación ---
    print("\n🚀 INICIANDO PROCESO DE VERIFICACIÓN DE INTEGRIDAD...")
    
    registros_sellados = reporte.get("registros_sellados", [])
    total_registros = len(registros_sellados)
    verificados_sha = 0
    fallos_sha = 0
    
    kyber_engine = KyberEngine() if kyber_available else None

    if har_data:
        original_entries = har_data.get('log', {}).get('entries', [])
        if len(original_entries) != total_registros:
            print("\n❌ INCONSISTENCIA: El número de registros en el HAR y en el reporte AEE no coincide.")
            return

        for registro in registros_sellados:
            idx = registro['id_registro'] - 1
            original_entry = original_entries[idx]
            
            # Recrear el dato original exactamente como lo hizo el sellador
            registro_original_str = json.dumps(original_entry, ensure_ascii=False)
            registro_bytes = registro_original_str.encode('utf-8')
            
            # 1. Verificar Hash SHA-512
            hash_recalculado = hashlib.sha512(registro_bytes).hexdigest()
            hash_almacenado = registro['certificado_integridad']['hash_sha512']
            
            if hash_recalculado == hash_almacenado:
                verificados_sha += 1
                registro['verificacion_sha'] = "✅ VERIFICADO"
            else:
                fallos_sha += 1
                registro['verificacion_sha'] = "❌ FALLIDO"
            
            # 2. Verificar Sello PQC (conceptual)
            pqc_status = verify_pqc_signature(kyber_engine, registro['certificado_integridad'], registro_bytes)
            registro['verificacion_pqc'] = pqc_status
    else:
        print("   Saltando verificación de hashes por ausencia de archivo HAR.")

    print("✅ Verificación de integridad completada.")

    # --- Presentación de Resultados ---
    print("\n" + "="*60)
    print("📊 RESULTADOS DE LA VERIFICACIÓN")
    print("="*60)
    print(f"Fecha de Verificación: {datetime.now().isoformat()}")
    print(f"Archivo Analizado: {os.path.basename(aee_file_path)}")
    print(f"Protocolo del Reporte: {reporte.get('protocolo_reporte', 'N/A')}")
    
    if har_data:
        print(f"\n🔗 Verificación de Integridad (SHA-512):")
        print(f"   - Registros Totales: {total_registros}")
        print(f"   - Registros Verificados: {verificados_sha}")
        print(f"   - Registros Fallidos: {fallos_sha}")
        if fallos_sha == 0 and total_registros > 0:
            print("   - Conclusión: ¡LA EVIDENCIA ES ÍNTEGRA Y NO HA SIDO ALTERADA!")
        else:
            print("   - Conclusión: ¡ADVERTENCIA! LA EVIDENCIA PUEDE HABER SIDO ALTERADA.")

    print("\n🚨 Resumen de Anomalías Originales:")
    anomalias = reporte.get("anomalias", [])
    if not anomalias:
        print("   - No se detectaron anomalías en el reporte original.")
    else:
        print(f"   - Se encontraron {len(anomalias)} anomalía(s) documentada(s):")
        for anomalia in anomalias:
            print(f"     - Registro #{anomalia['id_registro']}: {anomalia['alertas']} en URL: {anomalia['url']}")

    # --- Generación de Certificado de Verificación ---
    output_filename = f"certificado_verificacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("CERTIFICADO DE VERIFICACIÓN - QUANTUM HUMANITY\n")
        f.write("="*60 + "\n")
        f.write(f"Fecha: {datetime.now().isoformat()}\n")
        f.write(f"Archivo de Evidencia: {aee_file_path}\n")
        f.write(f"Archivo HAR Original: {har_file_path or 'No encontrado'}\n\n")
        if har_data:
            f.write(f"Resultado de Integridad SHA-512: {verificados_sha}/{total_registros} verificados.\n")
            f.write(f"Conclusión: {'ÍNTEGRO' if fallos_sha == 0 else 'ALTERADO'}\n\n")
        f.write("Anomalías Reportadas:\n")
        if not anomalias:
            f.write("  - Ninguna.\n")
        else:
            for anomalia in anomalias:
                 f.write(f"  - Reg #{anomalia['id_registro']}: {anomalia['alertas']} en {anomalia['url']}\n")
        f.write("\nEste documento certifica el resultado del análisis de integridad sobre el archivo de evidencia digital referenciado.")

    print("\n" + "="*60)
    print(f"📄 Certificado de verificación guardado en: {output_filename}")
    print("="*60)

if __name__ == "__main__":
    main()