import hashlib
import json
import os
import time
import ntplib
import platform
import statistics
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

class EvidenceProtocol:
    def __init__(self, user_id):
        self.user_id = user_id
        self.version = "2.1-HARDENED"
        self.private_key = None
        self.public_key = None
        self._initialized = False

    def initialize(self):
        """Genera claves asimétricas reales Ed25519 (No decorativas)"""
        print(f"🔧 Protocolo AEE {self.version} inicializando...")
        # En producción, esto debería interactuar con el keyring/TPM
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        
        pub_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        self.pub_hex = pub_bytes.hex()
        self._initialized = True
        print(f"✅ Claves Ed25519 generadas. Pub: {self.pub_hex[:16]}...")

    def _get_ntp_consensus(self):
        """Implementa consenso estadístico para evitar manipulación de tiempo local"""
        servers = ['time.google.com', 'pool.ntp.org', 'time.windows.com', 'time.cloudflare.com']
        responses = []
        client = ntplib.NTPClient()
        
        for server in servers:
            try:
                response = client.request(server, timeout=2)
                responses.append(response.tx_time)
            except:
                continue

        if len(responses) < 3:
            raise Exception("❌ ERROR FORENSE: Quórum NTP insuficiente para garantizar fecha cierta.")

        # Análisis de desviación
        stdev = statistics.stdev(responses)
        if stdev > 0.5: # Máximo 500ms de diferencia entre servidores
            raise Exception(f"❌ ERROR FORENSE: Desviación de tiempo excesiva ({stdev}s). Posible ataque de red.")

        return datetime.fromtimestamp(statistics.median(responses)).isoformat()

    def certify_file(self, file_path):
        if not self._initialized:
            raise Exception("Protocolo no inicializado. Ejecute initialize() primero.")

        # 1. Integridad del archivo
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            file_hash = hashlib.sha256(file_bytes).hexdigest()

        # 2. Metadatos de bajo nivel (Cadena de Custodia)
        stats = os.stat(file_path)
        forensic_meta = {
            "inode": stats.st_ino,
            "device": stats.st_dev,
            "size_bytes": stats.st_size,
            "os_mtime": datetime.fromtimestamp(stats.st_mtime).isoformat()
        }

        # 3. Tiempo Certificado (Consenso)
        certified_time = self._get_ntp_consensus()

        # 4. Payload Canónico para Firma
        payload = {
            "file_hash": file_hash,
            "timestamp": certified_time,
            "user_id": self.user_id,
            "version": self.version
        }
        payload_bytes = json.dumps(payload, sort_keys=True).encode()

        # 5. Firma Digital Real (Ed25519)
        signature = self.private_key.sign(payload_bytes).hex()

        # 6. Construcción del Certificado Final
        certificate = {
            "metadata": {"version": self.version, "id": f"AEE-{int(time.time())}"},
            "auditor": {"user_id": self.user_id, "public_key": self.pub_hex},
            "evidence": {"file_hash": file_hash, "forensic_metadata": forensic_meta},
            "timestamp": {"value": certified_time, "source": "ntp_consensus_stdev_verified"},
            "signature": {"value": signature, "data_signed": payload}
        }

        return certificate