"""
Módulo de generación de certificados PDF de preservación digital
"""
import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
import logging

logger = logging.getLogger(__name__)

# Configuración de rutas ABSOLUTAS
BASE_DIR = Path(__file__).parent.parent.resolve()
OUTPUT_DIR = BASE_DIR / "certificates"

# Crear directorio si no existe
OUTPUT_DIR.mkdir(exist_ok=True)

logger.info(f"📁 Directorio de certificados: {OUTPUT_DIR}")
logger.info(f"📁 CWD actual: {os.getcwd()}")


class CertificateGenerator:
    """Generador de certificados PDF de preservación digital"""

    def __init__(self, preservation_record):
        """
        Inicializa el generador con un registro de preservación

        Args:
            preservation_record: Objeto PreservationRecord de SQLAlchemy
        """
        self.record = preservation_record
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

        # Debug log
        logger.info(f"🔍 Generando certificado para hash: {self.record.file_hash[:16]}...")

    def _setup_custom_styles(self):
        """Configura estilos personalizados para el documento"""
        # Estilo para título
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495e'),
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))

    def _create_header(self):
        """Crea el encabezado del certificado"""
        elements = []

        # Título principal
        title = Paragraph(
            "CERTIFICADO DE PRESERVACIÓN DIGITAL",
            self.styles['CustomTitle']
        )
        elements.append(title)

        # Subtítulo con protocolo
        subtitle = Paragraph(
            "Protocolo AEE - Autenticidad, Evidencia y Existencia",
            self.styles['CustomBody']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3*inch))

        return elements

    def _format_file_size(self, size_bytes):
        """Formatea el tamaño del archivo de forma legible"""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def _create_record_info(self):
        """Crea la sección de información del registro"""
        elements = []

        # Título de sección
        section_title = Paragraph(
            "INFORMACIÓN DEL REGISTRO",
            self.styles['CustomHeading']
        )
        elements.append(section_title)

        # Formatear timestamp
        timestamp_str = self.record.timestamp_utc.strftime('%Y-%m-%d %H:%M:%S UTC')

        # Formatear tamaño de archivo
        file_size_str = self._format_file_size(self.record.file_size)

        # Datos en tabla
        data = [
            ['Hash SHA-256:', self.record.file_hash],
            ['ID de Registro:', str(self.record.id)],
            ['Fecha de Preservación:', timestamp_str],
            ['Nombre del Archivo:', self.record.file_name or 'Sin nombre'],
            ['Tipo MIME:', self.record.mime_type or 'Desconocido'],
            ['Tamaño del Archivo:', file_size_str],
            ['Usuario ID:', self.record.user_id],
            ['Estado:', 'Preservado y Verificado'],
        ]

        # Agregar firma criptográfica si existe
        if self.record.cryptographic_signature:
            sig_preview = self.record.cryptographic_signature[:50] + "..." if len(self.record.cryptographic_signature) > 50 else self.record.cryptographic_signature
            data.append(['Firma Criptográfica:', sig_preview])

        table = Table(data, colWidths=[2*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Courier'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

        return elements

    def _create_verification_section(self):
        """Crea la sección de verificación del certificado"""
        elements = []

        section_title = Paragraph(
            "VERIFICACIÓN DE AUTENTICIDAD",
            self.styles['CustomHeading']
        )
        elements.append(section_title)

        verification_text = f"""
        <para align=left>
        Este certificado verifica que el archivo fue preservado digitalmente mediante el
        <b>Protocolo AEE</b> (Autenticidad, Evidencia y Existencia) en la fecha y hora indicadas.
        <br/><br/>
        <b>Hash SHA-256:</b> {self.record.file_hash}
        <br/><br/>
        El hash SHA-256 es una huella digital criptográfica única del archivo.
        Cualquier modificación del archivo original resultará en un hash completamente diferente,
        garantizando la integridad de la evidencia digital.
        </para>
        """

        verification_para = Paragraph(verification_text, self.styles['CustomBody'])
        elements.append(verification_para)
        elements.append(Spacer(1, 0.3*inch))

        return elements

    def _create_footer(self):
        """Crea el pie del certificado"""
        elements = []

        elements.append(Spacer(1, 0.4*inch))

        footer_text = f"""
        <para align=center>
        <font size=8 color="#7f8c8d">
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br/>
        <b>PROTOCOLO AEE - CERTIFICADO DE PRESERVACIÓN DIGITAL</b><br/>
        Hash de Verificación: {self.record.file_hash[:32]}...<br/>
        Certificado generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}<br/>
        ID del Registro: {self.record.id} | Versión del Protocolo: 1.0.0<br/>
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        </font>
        </para>
        """

        footer = Paragraph(footer_text, self.styles['Normal'])
        elements.append(footer)

        return elements

    def generate(self):
        """
        Genera el certificado PDF

        Returns:
            Path: Ruta absoluta al archivo PDF generado

        Raises:
            FileNotFoundError: Si el PDF no se generó correctamente
            Exception: Si hubo error en la generación
        """
        try:
            # Nombre del archivo basado en hash
            filename = f"cert_{self.record.file_hash[:16]}.pdf"
            output_path = OUTPUT_DIR / filename

            logger.info(f"🔧 Generando PDF: {output_path}")

            # Crear documento
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )

            # Construir contenido
            story = []
            story.extend(self._create_header())
            story.extend(self._create_record_info())
            story.extend(self._create_verification_section())
            story.extend(self._create_footer())

            # Generar PDF
            doc.build(story)

            # VERIFICACIÓN CRÍTICA
            if not output_path.exists():
                logger.error(f"❌ PDF NO EXISTE después de build(): {output_path}")
                raise FileNotFoundError(f"PDF no generado en {output_path}")

            file_size = output_path.stat().st_size

            if file_size == 0:
                logger.error(f"❌ PDF generado pero está vacío: {output_path}")
                raise ValueError(f"PDF vacío en {output_path}")

            logger.info(f"✅ PDF generado exitosamente: {output_path} ({file_size} bytes)")

            return output_path

        except Exception as e:
            logger.error(f"❌ Error al generar PDF: {e}", exc_info=True)
            raise


def generate_certificate(preservation_record):
    """
    Función de conveniencia para generar un certificado

    Args:
        preservation_record: Registro de preservación (PreservationRecord)

    Returns:
        Path: Ruta al archivo PDF generado
    """
    generator = CertificateGenerator(preservation_record)
    return generator.generate()


def generate_test_certificate():
    """Genera un certificado de prueba para testing"""
    from datetime import datetime
    from types import SimpleNamespace

    # Crear registro de prueba que simula PreservationRecord
    test_record = SimpleNamespace(
        id=9999,
        file_hash="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
        file_name="documento_prueba.pdf",
        mime_type="application/pdf",
        file_size=1024000,
        user_id="123456789",
        timestamp_utc=datetime.now(),
        cryptographic_signature="sig_test_abc123xyz789"
    )

    output_path = generate_certificate(test_record)
    print(f"✅ Certificado de prueba generado: {output_path}")
    return output_path
