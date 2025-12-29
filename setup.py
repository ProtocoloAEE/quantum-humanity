"""
Setup de instalación para Protocolo AEE v2.0
"""

from setuptools import setup, find_packages
from pathlib import Path

# Leer README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="protocolo-aee",
    version="2.0.0-beta",
    
    # Metadata
    author="Protocolo AEE Team",
    author_email="protocolo.aee@proton.me",
    description="Certificación de Evidencia Digital - Argentina",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ProtocoloAEE/protocolo-aee-v2",
    
    # Licencia
    license="MIT",
    
    # Clasificación PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security :: Cryptography",
        "Topic :: Legal",
        "Operating System :: OS Independent",
    ],
    
    # Compatibilidad
    python_requires=">=3.8",
    
    # Paquetes
    packages=find_packages(),
    
    # Dependencias
    install_requires=[
        "cryptography>=41.0.0",
        "requests>=2.31.0",
        "ntplib>=0.4.0",
        "keyring>=24.0.0",
        "python-dateutil>=2.8.0",
    ],
    
    # Dependencias opcionales
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "pdf": [
            "reportlab>=4.0.0",
        ],
    },
    
    # Entry points (comandos CLI futuros)
    entry_points={
        "console_scripts": [
            "aee-certify=aee.cli:certify",  # Para v2.1
            "aee-verify=aee.cli:verify",    # Para v2.1
        ],
    },
    
    # Archivos adicionales
    include_package_data=True,
    package_data={
        "aee": ["py.typed"],
    },
    
    # Keywords para búsqueda
    keywords=[
        "evidence",
        "digital-evidence",
        "cryptography",
        "blockchain",
        "argentina",
        "legal-tech",
        "timestamp",
        "certification",
    ],
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/ProtocoloAEE/protocolo-aee-v2/issues",
        "Source": "https://github.com/ProtocoloAEE/protocolo-aee-v2",
        "Documentation": "https://github.com/ProtocoloAEE/protocolo-aee-v2/blob/main/README.md",
        "Reddit": "https://www.reddit.com/r/argentina",
    },
)