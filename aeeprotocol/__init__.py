"""
AEE Protocol - Cryptographic Watermarking for Vector Embeddings
"""

__version__ = "0.2.3"
__author__ = "Franco Luciano Carricondo"
__email__ = "francocarricondo@gmail.com"
__license__ = "MIT"

from aeeprotocol.core.engine import AEEMathEngine
from aeeprotocol.sdk.client import AEEClient

__all__ = [
    "AEEMathEngine",
    "AEEClient",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]