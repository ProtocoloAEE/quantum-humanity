"""
Script de Verificación para Certificados de Evidencia Digital AEE (Híbridos).
"""
import json
from pathlib import Path
import logging

# Importar la nueva función de verificación híbrida
from aee.pqc_hybrid import verificar_certificado_hibrido, NACL_AVAILABLE

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def imprimir_reporte_hibrido(resultados: dict):
    """Imprime un reporte de verificación formateado para certificados híbridos."""
    print("\n======================================================")
    print("      REPORTE DE VERIFICACIÓN DE EVIDENCIA HÍBRIDA      ")
    print("======================================================")
    
    hash_info = resultados.get('verificaciones', {}).get('hash', {})
    firmas_info = resultados.get('verificaciones', {}).get('firmas', {})

    # Resumen general
    if resultados.get('exitoso'):
        print("✅  VERIFICACIÓN GLOBAL EXITOSA")
    else:
        print("❌  VERIFICACIÓN GLOBAL FALLIDA")
    print(f"   Resumen: {resultados.get('mensaje', 'No se pudo completar la verificación.')}")
    print("------------------------------------------------------")

    # Detalle de Hash
    hash_estado = "✅ Éxito" if hash_info.get('exitoso') else "❌ Fallo"
    print(f"[{hash_estado}] Verificación de Hash de Archivo")
    print(f"   └── {hash_info.get('mensaje', 'Sin detalles.')}")

    # Detalle de Firmas
    if firmas_info:
        # Firma Clásica
        ed_estado = "✅ Éxito" if firmas_info.get('ed25519_valido') else "❌ Fallo"
        print(f"[{ed_estado}] Firma Clásica (Ed25519)")
        print(f"   └── {firmas_info.get('mensaje_ed25519', 'No verificado.')}")

        # Sello Post-Cuántico
        kyber_msg = firmas_info.get('mensaje_kyber', 'No presente.')
        kyber_estado = "ℹ️ Info"
        if "válido" in kyber_msg.lower(): # Para el caso de un auditor
            kyber_estado = "✅ Éxito"
        elif "inválido" in kyber_msg.lower():
             kyber_estado = "❌ Fallo"
        
        print(f"[{kyber_estado}] Sello Post-Cuántico (Kyber-768)")
        print(f"   └── {kyber_msg}")
    
    print("======================================================\n")


def main():
    """
    Función principal para demostrar la verificación de un certificado híbrido.
    """
    ARCHIVO_A_VERIFICAR = "prueba.txt"
    CERTIFICADO_PATH = "certificado_evidencia_hibrido.json"

    print(f"Iniciando verificación para '{ARCHIVO_A_VERIFICAR}' usando el certificado '{CERTIFICADO_PATH}'.\n")

    if not NACL_AVAILABLE:
        logging.error("La librería PyNaCl no está instalada (pip install PyNaCl). No se puede continuar.")
        return

    archivo_path = Path(ARCHIVO_A_VERIFICAR)
    certificado_path = Path(CERTIFICADO_PATH)

    if not archivo_path.exists() or not certificado_path.exists():
        logging.error(f"Faltan archivos: el archivo de evidencia '{archivo_path}' o el certificado '{certificado_path}' no existen.")
        return

    try:
        # 1. Cargar el certificado
        with open(certificado_path, 'r', encoding='utf-8') as f:
            certificado_data = json.load(f)

        # 2. Ejecutar la verificación híbrida completa
        # require_pqc=False por defecto para verificación pública
        resultados = verificar_certificado_hibrido(
            archivo_path=archivo_path,
            certificado=certificado_data
        )

        # 3. Imprimir el reporte
        imprimir_reporte_hibrido(resultados)

    except json.JSONDecodeError:
        logging.error(f"Error al leer el JSON del certificado: {certificado_path}", exc_info=True)
    except Exception as e:
        logging.error(f"Ocurrió un error inesperado durante la verificación: {e}", exc_info=True)

if __name__ == "__main__":
    main()
