"""
Script de prueba para verificar generación de PDFs
"""
import sys
from pathlib import Path

# Agregar directorio al path
sys.path.insert(0, str(Path(__file__).parent))

from aee.certificate import generate_test_certificate

def main():
    print("=" * 60)
    print("TEST: Generación de Certificado PDF")
    print("=" * 60)
    
    try:
        pdf_path = generate_test_certificate()
        
        # Verificaciones
        assert pdf_path.exists(), f"PDF no existe: {pdf_path}"
        assert pdf_path.stat().st_size > 0, "PDF está vacío"
        
        print(f"\n✅ ÉXITO TOTAL")
        print(f"📄 PDF generado: {pdf_path}")
        print(f"📊 Tamaño: {pdf_path.stat().st_size} bytes")
        print(f"📁 Ubicación: {pdf_path.parent}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()