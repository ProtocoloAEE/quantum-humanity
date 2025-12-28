"""
AEE Protocol - Quantum Humanity v0.6.0
=======================================
Protocolo de Autenticación de Embeddings Existenciales
Sellado post-cuántico para certificación de autoría humana
"""
from .core.kyber_engine import KyberEngine
# Instanciamos un motor por defecto para uso rápido
engine = KyberEngine()

def get_info():
    return {
        "version": "0.6.0",
        "protocol": "AEE (Authentic Embedding Existential)",
        "status": "ACTIVE",
        "quantum_safe": True,
        "total_lines": 9552
    }

__all__ = ['KyberEngine', 'engine', 'get_info']
__version__ = "0.6.0"
