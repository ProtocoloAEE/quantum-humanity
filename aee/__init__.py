"""
AEE Bot - Acta de Evidencia Electrónica
Certificación criptográfica post-cuántica para Telegram
Versión 3.0 - Sistema profesional de preservación digital
"""

__version__ = "3.0.0"
__author__ = "AEE Team - Ingeniería Forense Digital"
__license__ = "MIT"

from aee.database import DatabaseManager, PreservationRecord
from aee.certificate import CertificateGenerator

__all__ = [
    'DatabaseManager',
    'PreservationRecord',
    'CertificateGenerator'
]