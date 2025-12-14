from setuptools import setup, find_packages

setup(
    name="aeeprotocol",
    version="0.2.3",
    author="Franco Luciano Carricondo",
    author_email="francocarricondo@gmail.com",
    description="Cryptographic watermarking for vector embeddings",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ProtocoloAEE/aee-protocol",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)