from fpdf import FPDF

class AEEReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'ACTA DE CERTIFICACIÓN DE EVIDENCIA DIGITAL', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, 'Protocolo AEE v2.0 - Soberanía Digital', 0, 1, 'C')
        self.ln(10)

    def create_report(self, data):
        self.add_page()
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, '1. DATOS DEL AUDITOR', 0, 1)
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 10, f"Nombre: {data['nombre']}\nDNI: {data['dni']}\nID de Auditor: {data['user_id']}")
        
        self.ln(5)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, '2. EVIDENCIA TÉCNICA', 0, 1)
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 10, f"Hash SHA-256: {data['hash']}\nFecha Cierta (NTP UTC): {data['fecha']}\nOrigen: {data['url']}")
        
        self.ln(5)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, '3. SELLO CRIPTOGRÁFICO (Ed25519)', 0, 1)
        self.set_font('Courier', '', 8)
        self.multi_cell(0, 5, f"Firma Digital:\n{data['firma']}")
        
        self.ln(10)
        self.set_font('Arial', 'I', 9)
        self.multi_cell(0, 10, "Este documento es una certificación técnica preliminar bajo la Ley 25.506 de Firma Digital. La integridad del archivo original puede verificarse comparando el hash mencionado.")
        
        self.output(f"Certificado_AEE_{data['hash'][:10]}.pdf")

print("📄 Generador de reportes listo.")