import jinja2
import qrcode
from xhtml2pdf import pisa
import os
import json
from PIL import Image

def generar_pdf_reporte(data_dict, output_filename="certificado_aee.pdf"):
    """
    Genera un reporte en PDF a partir de un diccionario de datos y una plantilla HTML.

    Args:
        data_dict (dict): Diccionario con los datos del certificado AEE.
        output_filename (str): Nombre del archivo PDF de salida.
    """
    try:
        # --- 1. Preparar datos para la plantilla ---
        template_data = {
            'id_sello': data_dict.get('id_sello', 'N/A'),
            'timestamp': data_dict.get('timestamp', 'N/A'),
            'version': data_dict.get('version', 'N/A'),
            'hash_evidencia': data_dict.get('hash_evidencia', 'N/A'),
            'firma_digital': data_dict.get('firma_digital', 'N/A'),
            'clave_publica_firmante': data_dict.get('clave_publica_firmante', 'N/A'),
            'firmante_details': json.dumps(data_dict.get('firmante', {}), indent=4),
            'nts_data': json.dumps(data_dict.get('nts_aee_record', {}), indent=4)
        }

        # --- 2. Generar QR code ---
        # Usamos una representación JSON de los datos para el QR
        qr_data = json.dumps(data_dict, sort_keys=True)
        qr_img = qrcode.make(qr_data)
        qr_code_path = "qrcode.png"
        qr_img.save(qr_code_path)

        # --- 3. Renderizar plantilla HTML ---
        template_loader = jinja2.FileSystemLoader(searchpath="./templates")
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template("report_template.html")
        source_html = template.render(template_data)

        # --- 4. Crear PDF ---
        with open(output_filename, "w+b") as result_file:
            pisa_status = pisa.CreatePDF(
                source_html,                # El HTML renderizado
                dest=result_file,           # El archivo de salida
                encoding='utf-8'
            )

        # --- 5. Limpieza ---
        if os.path.exists(qr_code_path):
            os.remove(qr_code_path)

        if pisa_status.err:
            print(f"Error al generar el PDF: {pisa_status.err}")
            return None
        else:
            print(f"Reporte PDF generado exitosamente: {output_filename}")
            return output_filename

    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        # Limpieza en caso de error
        if 'qr_code_path' in locals() and os.path.exists(qr_code_path):
            os.remove(qr_code_path)
        return None

if __name__ == '__main__':
    # Datos de ejemplo para una prueba rápida
    mock_data = {
        "id_sello": "AEE-20251228-ABCDEFG",
        "timestamp": "2025-12-28T12:00:00Z",
        "version": "1.0.0-pqc",
        "protocolo": "AEE-PQC-DILITHIUM-KYBER",
        "firmante": {
            "id_protocolo_qh": "urn:qh:identidad:test:luciano",
            "rol": "Notario PQC",
            "detalles_adicionales": "Entorno de prueba"
        },
        "hash_evidencia": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
        "clave_publica_firmante": "PUBLIC_KEY_HEX_EXAMPLE",
        "firma_digital": "SIGNATURE_HEX_EXAMPLE",
        "nts_aee_record": {
            "servidor_nts": "time.cloudflare.com:4460",
            "certificado_servidor": "SERVER_CERT_DATA_HERE",
            "cookie": "NTS_COOKIE_DATA",
            "timestamp_nts": "2025-12-28T12:00:01Z"
        }
    }
    
    print("Generando reporte PDF de prueba...")
    generar_pdf_reporte(mock_data, "reporte_de_prueba.pdf")

