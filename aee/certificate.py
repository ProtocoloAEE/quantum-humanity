"""
aee/certificate.py
Generador de certificados de preservación digital en formato PDF profesional.
Diseño de acta pericial técnica con garantías criptográficas.
"""

import logging
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, grey
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image
)
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import hashlib
from aee.database import DatabaseManager, PreservationRecord

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN DE ESTILOS
# ============================================================================

class CertificateStyles:
    """Estilos profesionales para el certificado PDF."""
    
    @staticmethod
    def get_styles():
        """Retorna estilos personalizados para el certificado."""
        styles = getSampleStyleSheet()
        
        # Encabezado principal
        styles.add(ParagraphStyle(
            name='CertTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=1,  # Centro
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        styles.add(ParagraphStyle(
            name='CertSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=HexColor('#333333'),
            spaceAfter=6,
            alignment=1,
            fontName='Helvetica'
        ))
        
        # Sección de metadatos
        styles.add(ParagraphStyle(
            name='MetadataLabel',
            parent=styles['Normal'],
            fontSize=9,
            textColor=HexColor('#666666'),
            spaceAfter=2,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='MetadataValue',
            parent=styles['Normal'],
            fontSize=9,
            textColor=HexColor('#333333'),
            spaceAfter=4,
            fontName='Courier'  # Monoespaciado para datos técnicos
        ))
        
        # Hash SHA-256 (monoespaciado, destacado)
        styles.add(ParagraphStyle(
            name='HashValue',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#000000'),
            backColor=HexColor('#f0f0f0'),
            spaceAfter=12,
            fontName='Courier-Bold',
            leftIndent=10,
            rightIndent=10
        ))
        
        # Disclaimer legal
        styles.add(ParagraphStyle(
            name='Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=HexColor('#666666'),
            spaceAfter=8,
            fontName='Helvetica-Oblique',
            leftIndent=10,
            rightIndent=10
        ))
        
        return styles


# ============================================================================
# GENERADOR DE CERTIFICADOS
# ============================================================================

class CertificateGenerator:
    """
    Generador de certificados de preservación digital.
    Produce PDFs profesionales con diseño de acta pericial.
    """
    
    @staticmethod
    def generate_certificate(preservation_id: int, output_path: str = None) -> bytes:
        """
        Genera un certificado PDF para una preservación registrada.
        
        Args:
            preservation_id: ID del registro de preservación en BD
            output_path: Ruta para guardar (opcional). Si es None, retorna bytes.
        
        Returns:
            bytes: Contenido del PDF, o None si hay error
        
        Raises:
            ValueError: Si el registro no existe
            Exception: Errores de generación de PDF
        """
        try:
            # Obtener registro de BD
            record = DatabaseManager.get_preservation_by_id(preservation_id)
            
            if not record:
                raise ValueError(f"Preservación no encontrada: ID={preservation_id}")
            
            logger.info(f"Generando certificado para preservación ID={preservation_id}")
            
            # Crear PDF en memoria
            pdf_buffer = BytesIO()
            
            # Documento A4
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm,
                title="Certificado de Preservación Digital"
            )
            
            # Construir contenido
            story = []
            styles = CertificateStyles.get_styles()
            
            # 1. ENCABEZADO
            story.append(Paragraph(
                "CERTIFICADO DE PRESERVACIÓN DIGITAL",
                styles['CertTitle']
            ))
            
            story.append(Paragraph(
                "Acta Electrónica de Evidencia - Sistema AEE",
                styles['CertSubtitle']
            ))
            
            story.append(Spacer(1, 0.3*cm))
            
            # Línea separadora
            story.append(Table(
                [['']], 
                colWidths=[17*cm],
                style=TableStyle([
                    ('LINEABOVE', (0, 0), (-1, -1), 2, HexColor('#1a1a1a')),
                ])
            ))
            
            story.append(Spacer(1, 0.3*cm))
            
            # 2. INFORMACIÓN GENERAL
            story.append(Paragraph(
                "📋 INFORMACIÓN DE LA PRESERVACIÓN",
                styles['Heading2']
            ))
            
            story.append(Spacer(1, 0.2*cm))
            
            # Tabla de metadatos
            metadata_data = [
                [
                    Paragraph("<b>Preservación ID:</b>", styles['MetadataLabel']),
                    Paragraph(f"<font face='Courier'>{record.id}</font>", styles['MetadataValue'])
                ],
                [
                    Paragraph("<b>Fecha y Hora UTC:</b>", styles['MetadataLabel']),
                    Paragraph(
                        f"<font face='Courier'>{record.timestamp_utc.isoformat()}Z</font>",
                        styles['MetadataValue']
                    )
                ],
                [
                    Paragraph("<b>Usuario (Telegram ID):</b>", styles['MetadataLabel']),
                    Paragraph(f"<font face='Courier'>{record.user_id}</font>", styles['MetadataValue'])
                ],
            ]
            
            metadata_table = Table(metadata_data, colWidths=[5*cm, 11*cm])
            metadata_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#dddddd')),
            ]))
            
            story.append(metadata_table)
            story.append(Spacer(1, 0.3*cm))
            
            # 3. BLOQUE DE INTEGRIDAD (El más importante)
            story.append(Paragraph(
                "🔒 INTEGRIDAD CRIPTOGRÁFICA",
                styles['Heading2']
            ))
            
            story.append(Spacer(1, 0.2*cm))
            
            story.append(Paragraph(
                "<b>Hash SHA-256:</b>",
                styles['MetadataLabel']
            ))
            
            story.append(Spacer(1, 0.1*cm))
            
            # Hash en bloque destacado
            story.append(Paragraph(
                f"<font face='Courier' size='11'><b>{record.file_hash}</b></font>",
                styles['HashValue']
            ))
            
            story.append(Spacer(1, 0.2*cm))
            
            # 4. INFORMACIÓN DEL ARCHIVO
            story.append(Paragraph(
                "📄 PROPIEDADES DEL ARCHIVO",
                styles['Heading2']
            ))
            
            story.append(Spacer(1, 0.2*cm))
            
            file_data = [
                [
                    Paragraph("<b>Nombre de Archivo:</b>", styles['MetadataLabel']),
                    Paragraph(f"<font face='Courier'>{record.file_name or 'N/A'}</font>", styles['MetadataValue'])
                ],
                [
                    Paragraph("<b>Tipo MIME:</b>", styles['MetadataLabel']),
                    Paragraph(f"<font face='Courier'>{record.mime_type or 'N/A'}</font>", styles['MetadataValue'])
                ],
                [
                    Paragraph("<b>Tamaño de Archivo:</b>", styles['MetadataLabel']),
                    Paragraph(
                        f"<font face='Courier'>{record.file_size:,} bytes ({record.file_size/1024/1024:.2f} MB)</font>",
                        styles['MetadataValue']
                    )
                ],
            ]
            
            file_table = Table(file_data, colWidths=[5*cm, 11*cm])
            file_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#dddddd')),
            ]))
            
            story.append(file_table)
            story.append(Spacer(1, 0.4*cm))
            
            # 5. DISCLAIMER LEGAL
            story.append(Paragraph(
                "⚠️ AVISO LEGAL",
                styles['Heading2']
            ))
            
            story.append(Spacer(1, 0.15*cm))
            
            disclaimer_text = (
                "<b>Alcance de la Certificación:</b> Este certificado valida exclusivamente "
                "la <u>integridad del binario</u> del archivo mediante el algoritmo SHA-256. "
                "NO certifica la <u>veracidad del contenido</u>, autoría, legalidad o contexto "
                "de la información contenida en el archivo. La integridad se verifica por comparación "
                "del hash SHA-256 proporcionado. Cualquier alteración del archivo producirá un hash diferente. "
                "<br/><br/>"
                "<b>Responsabilidad:</b> El usuario es responsable de mantener confidencial "
                "el certificado y de validar independientemente la autenticidad del contenido. "
                "El sistema AEE no es responsable del uso indebido de este certificado."
            )
            
            story.append(Paragraph(disclaimer_text, styles['Disclaimer']))
            
            story.append(Spacer(1, 0.4*cm))
            
            # 6. ESPECIFICACIONES TÉCNICAS
            story.append(Paragraph(
                "🔧 ESPECIFICACIONES TÉCNICAS",
                styles['Heading2']
            ))
            
            story.append(Spacer(1, 0.15*cm))
            
            specs_text = (
                "<b>Algoritmo de Hash:</b> SHA-256 (NIST FIPS 180-4)<br/>"
                "<b>Resistencia Criptográfica:</b> 256 bits<br/>"
                "<b>Colisiones Esperadas:</b> 2^256 (teóricamente irrealizables)<br/>"
                "<b>Estándar:</b> RFC 6234, NIST SP 800-14<br/>"
                "<b>Sistema de Preservación:</b> AEE v3.0 (Criptografía Estándar)"
            )
            
            story.append(Paragraph(specs_text, styles['Normal']))
            
            story.append(Spacer(1, 0.3*cm))
            
            # 7. FIRMA DIGITAL (placeholder para futuro)
            if record.cryptographic_signature:
                story.append(Paragraph(
                    "FIRMA CRIPTOGRÁFICA",
                    styles['Heading2']
                ))
                
                story.append(Spacer(1, 0.15*cm))
                
                sig_text = f"<font face='Courier' size='8'>{record.cryptographic_signature[:100]}...</font>"
                story.append(Paragraph(sig_text, styles['Normal']))
            else:
                story.append(Paragraph(
                    "Firma Criptográfica: (Reservada para implementación futura)",
                    styles['Disclaimer']
                ))
            
            story.append(Spacer(1, 0.4*cm))
            
            # 8. PIE DE PÁGINA
            timestamp_now = datetime.utcnow().isoformat()
            footer_text = (
                f"Certificado generado: {timestamp_now}Z<br/>"
                f"Sistema: Acta de Evidencia Electrónica (AEE) v3.0<br/>"
                f"Plataforma: Telegram Bot - python-telegram-bot v20.7"
            )
            
            story.append(Paragraph(footer_text, styles['Disclaimer']))
            
            # Construir PDF
            doc.build(story)
            
            # Obtener contenido del buffer
            pdf_content = pdf_buffer.getvalue()
            
            # Guardar a archivo si se proporciona ruta
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(pdf_content)
                logger.info(f"✅ Certificado guardado: {output_path}")
            
            logger.info(f"✅ Certificado generado exitosamente (tamaño: {len(pdf_content)} bytes)")
            
            return pdf_content
            
        except ValueError as e:
            logger.warning(f"Validación fallida: {e}")
            raise
            
        except Exception as e:
            logger.exception(f"❌ Error al generar certificado: {type(e).__name__}: {e}")
            raise
    
    @staticmethod
    def generate_certificate_by_hash(file_hash: str, output_path: str = None) -> bytes:
        """
        Genera certificado a partir de un hash SHA-256.
        
        Args:
            file_hash: Hash SHA-256
            output_path: Ruta para guardar (opcional)
        
        Returns:
            bytes: Contenido del PDF
        """
        try:
            record = DatabaseManager.get_preservation_by_hash(file_hash)
            
            if not record:
                raise ValueError(f"No se encontró preservación con hash: {file_hash}")
            
            return CertificateGenerator.generate_certificate(record.id, output_path)
            
        except Exception as e:
            logger.exception(f"Error en generate_certificate_by_hash: {type(e).__name__}: {e}")
            raise


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def create_certificate_file(preservation_id: int, output_dir: str = "./certificates/") -> str:
    """
    Crea un certificado PDF y lo guarda en el sistema de archivos.
    
    Args:
        preservation_id: ID de la preservación
        output_dir: Directorio de salida
    
    Returns:
        str: Ruta del archivo creado
    """
    import os
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"AEE_Certificado_{preservation_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(output_dir, filename)
        
        CertificateGenerator.generate_certificate(preservation_id, output_path)
        
        logger.info(f"Certificado guardado en: {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.exception(f"Error creando archivo de certificado: {type(e).__name__}: {e}")
        raise
