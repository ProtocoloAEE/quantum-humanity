from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aeeprotocol",
    version="0.3.0",
    author="Franco Luciano Carricondo",
    author_email="francocarricondo@gmail.com",
    description="AEE Protocol - Scientific Watermarking for Vector Embeddings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ProtocoloAEE/aee-protocol",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Legal Industry",
        "Topic :: Security :: Cryptography",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
        "pinecone": ["pinecone-client>=3.0.0"],
        "weaviate": ["weaviate-client>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "aee-validate=aeeprotocol.cli:validate",
            "aee-benchmark=aeeprotocol.cli:benchmark",
        ],
    },
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/ProtocoloAEE/aee-protocol/issues",
        "Source": "https://github.com/ProtocoloAEE/aee-protocol",
        "Documentation": "https://github.com/ProtocoloAEE/aee-protocol/blob/main/README.md",
        "Security": "https://github.com/ProtocoloAEE/aee-protocol/blob/main/SECURITY.md",
    },
)