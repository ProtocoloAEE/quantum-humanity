"""
Ejemplo de uso del Motor Híbrido AEE para certificar un archivo.
Crea un certificado con doble firma: Ed25519 (clásica) y Kyber-768 (post-cuántica).
"""
import logging
from pathlib import Path
import json

# Importar el nuevo motor híbrido y las funciones de ayuda
from aee.pqc_hybrid import (
    HybridCryptoEngine,
    generar_certificado_hibrido,
    cargar_keypair,
    guardar_keypair_seguro,
    KYBER_AVAILABLE,
    NACL_AVAILABLE
)

# Configurar logging para ver el proceso en consola
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Función principal para demostrar la certificación HÍBRIDA de un archivo.
    """
    # --- Definición de Archivos ---
    KEYPAIR_FILE = Path("auditor_keypair.json")
    ARCHIVO_A_CERTIFICAR = "prueba.txt"
    CERTIFICADO_SALIDA = "certificado_evidencia_hibrido.json"
    
    # --- Preparación ---
    archivo_path = Path(ARCHIVO_A_CERTIFICAR)
    if not archivo_path.exists():
        print(f"Creando archivo de prueba: {archivo_path}")
        archivo_path.write_text("Este es el contenido para la certificación híbrida.", encoding='utf-8')

    print("======================================================")
    print("      INICIANDO PROCESO DE CERTIFICACIÓN HÍBRIDA      ")
    print("======================================================")
    
    if not NACL_AVAILABLE:
        logging.error("La librería PyNaCl no está instalada (pip install PyNaCl). No se puede continuar.")
        return
        
    if not KYBER_AVAILABLE:
        logging.warning("La librería Kyber no está instalada. El certificado se generará SIN la capa post-cuántica.")
    else:
        logging.info("Librería Kyber detectada. Se generará certificado con doble firma.")

    print(f"Archivo a certificar: {ARCHIVO_A_CERTIFICAR}")
    print(f"Keypair de auditor:   {KEYPAIR_FILE}")
    print(f"Certificado de salida:  {CERTIFICADO_SALIDA}")
    print("------------------------------------------------------\n")

    try:
        # 1. Gestión del par de claves del auditor
        if KEYPAIR_FILE.exists():
            logging.info(f"Cargando par de claves existente desde {KEYPAIR_FILE}...")
            keypair = cargar_keypair(KEYPAIR_FILE)
        else:
            logging.info("No se encontró par de claves. Generando uno nuevo...")
            engine = HybridCryptoEngine()
            keypair = engine.generar_par_claves_hibrido()
            guardar_keypair_seguro(keypair, KEYPAIR_FILE)
            logging.info(f"Nuevo par de claves guardado en {KEYPAIR_FILE}. ¡Guárdelo en un lugar seguro!")

        # 2. Llamar al proceso de generación de certificado híbrido
        certificado_hibrido = generar_certificado_hibrido(
            archivo_path=archivo_path,
            keypair=keypair,
            metadata={'caso_id': 'HYB-2025-001', 'descripcion': 'Prueba de concepto híbrida'}
        )

        # 3. Guardar el certificado en un archivo
        with open(CERTIFICADO_SALIDA, 'w', encoding='utf-8') as f:
            json.dump(certificado_hibrido, f, indent=4, ensure_ascii=False)

        print("\n------------------------------------------------------")
        print("✅  CERTIFICACIÓN HÍBRIDA COMPLETADA EXITOSAMENTE")
        print(f"   El certificado ha sido guardado en: {CERTIFICADO_SALIDA}")
        print("======================================================\n")

    except Exception as e:
        logging.error(f"El proceso de certificación falló: {e}", exc_info=True)
        print("\n------------------------------------------------------")
        print("❌  ERROR: La certificación no pudo completarse.")
        print("    Revise el archivo 'aee_forensic.log' para más detalles.")
        print("======================================================\n")

if __name__ == "__main__":
    main()
