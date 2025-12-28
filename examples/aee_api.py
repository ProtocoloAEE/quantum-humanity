#!/usr/bin/env python3
"""
AEE Protocol - Flask API Backend
REST API para sellado criptográfico de embeddings

Instalación:
    pip install flask flask-cors numpy cryptography

Ejecución:
    python aee_api.py

API disponible en: http://localhost:5000
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import json
import time
import secrets
from typing import Dict, Tuple
import numpy as np

# Cryptography imports
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

app = Flask(__name__)
CORS(app)  # Permitir requests desde React

# ============================================================================
# SIMULADOR KEM (igual que la demo CLI que funciona)
# ============================================================================
class KEMSimulator:
    """Key Encapsulation Mechanism - Simulador educativo"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        
    def generate_keypair(self) -> Tuple[bytes, float]:
        """Genera par de claves"""
        start = time.time()
        
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        elapsed = time.time() - start
        return public_bytes, elapsed
    
    def encapsulate(self, public_key_bytes: bytes) -> Tuple[bytes, bytes, float]:
        """Encapsular secreto"""
        start = time.time()
        
        shared_secret = secrets.token_bytes(32)
        ciphertext = self.public_key.encrypt(
            shared_secret,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        elapsed = time.time() - start
        return ciphertext, shared_secret, elapsed
    
    def decapsulate(self, ciphertext: bytes) -> Tuple[bytes, float]:
        """Desencapsular secreto"""
        start = time.time()
        
        shared_secret = self.private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        elapsed = time.time() - start
        return shared_secret, elapsed


# ============================================================================
# CLASE AEE PROTOCOL
# ============================================================================
class AEEProtocol:
    """Sellado criptográfico para embeddings"""
    
    def __init__(self):
        self.kem = KEMSimulator()
        self.public_key = None
        
    def generate_keypair(self) -> Dict:
        """Genera par de claves y retorna info"""
        public_key, gen_time = self.kem.generate_keypair()
        self.public_key = public_key
        
        return {
            "public_key": public_key.hex(),
            "key_size": len(public_key),
            "generation_time_ms": gen_time * 1000,
            "algorithm": "AEE-KEM-SHA3"
        }
    
    def create_seal(self, embedding: list, metadata: Dict = None) -> Dict:
        """Crea sello criptográfico"""
        if self.public_key is None:
            raise ValueError("Genera claves primero")
        
        # Convertir a numpy array
        embedding_array = np.array(embedding, dtype=np.float32)
        vector_bytes = embedding_array.tobytes()
        
        # Hash SHA3-256
        content_hash = hashlib.sha3_256(vector_bytes).digest()
        
        # Encapsular
        start = time.time()
        ciphertext, shared_secret, _ = self.kem.encapsulate(self.public_key)
        
        # Combinar para sello
        if metadata:
            metadata_json = json.dumps(metadata, sort_keys=True).encode()
            combined = content_hash + shared_secret + metadata_json
        else:
            combined = content_hash + shared_secret
        
        seal = hashlib.sha3_256(combined).hexdigest()
        seal_time = (time.time() - start) * 1000
        
        # Certificado
        certificate = {
            "seal": seal,
            "content_hash": content_hash.hex(),
            "algorithm": "AEE-KEM-SHA3",
            "timestamp": time.time(),
            "vector_shape": embedding_array.shape,
            "seal_time_ms": seal_time,
            "metadata": metadata
        }
        
        return {
            "certificate": certificate,
            "ciphertext": ciphertext.hex()
        }
    
    def verify_seal(
        self,
        embedding: list,
        certificate: Dict,
        ciphertext_hex: str,
        metadata: Dict = None
    ) -> Dict:
        """Verifica integridad"""
        start = time.time()
        
        # Convertir
        embedding_array = np.array(embedding, dtype=np.float32)
        vector_bytes = embedding_array.tobytes()
        
        # Hash actual
        current_hash = hashlib.sha3_256(vector_bytes).digest()
        original_hash = bytes.fromhex(certificate["content_hash"])
        
        # Verificar hash
        hash_valid = current_hash == original_hash
        
        if not hash_valid:
            return {
                "valid": False,
                "reason": "Content hash mismatch",
                "verification_time_ms": (time.time() - start) * 1000
            }
        
        # Desencapsular
        try:
            ciphertext = bytes.fromhex(ciphertext_hex)
            shared_secret, _ = self.kem.decapsulate(ciphertext)
        except Exception as e:
            return {
                "valid": False,
                "reason": f"Decapsulation failed: {str(e)}",
                "verification_time_ms": (time.time() - start) * 1000
            }
        
        # Reconstruir sello
        if metadata:
            metadata_json = json.dumps(metadata, sort_keys=True).encode()
            combined = current_hash + shared_secret + metadata_json
        else:
            combined = current_hash + shared_secret
        
        expected_seal = hashlib.sha3_256(combined).hexdigest()
        seal_valid = expected_seal == certificate["seal"]
        
        verify_time = (time.time() - start) * 1000
        
        return {
            "valid": seal_valid,
            "hash_valid": hash_valid,
            "seal_valid": seal_valid,
            "verification_time_ms": verify_time
        }


# Instancia global (en producción usarías gestión de sesiones)
aee = None


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "service": "AEE Protocol API",
        "version": "0.1.0",
        "timestamp": time.time()
    })


@app.route('/api/keypair/generate', methods=['POST'])
def generate_keypair():
    """
    Genera par de claves
    
    POST /api/keypair/generate
    Response: {
        "public_key": "hex_string",
        "key_size": 294,
        "generation_time_ms": 45.2,
        "algorithm": "AEE-KEM-SHA3"
    }
    """
    global aee
    
    try:
        aee = AEEProtocol()
        result = aee.generate_keypair()
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/seal/create', methods=['POST'])
def create_seal():
    """
    Crea sello criptográfico
    
    POST /api/seal/create
    Body: {
        "embedding": [0.1, 0.2, ...],
        "metadata": {
            "model": "text-embedding-ada-002",
            "organization": "org_xyz"
        }
    }
    """
    global aee
    
    if aee is None:
        return jsonify({
            "success": False,
            "error": "Genera claves primero con /api/keypair/generate"
        }), 400
    
    try:
        data = request.get_json()
        
        if not data or 'embedding' not in data:
            return jsonify({
                "success": False,
                "error": "Campo 'embedding' requerido"
            }), 400
        
        embedding = data['embedding']
        metadata = data.get('metadata', None)
        
        # Validar embedding
        if not isinstance(embedding, list):
            return jsonify({
                "success": False,
                "error": "Embedding debe ser una lista de números"
            }), 400
        
        result = aee.create_seal(embedding, metadata)
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/seal/verify', methods=['POST'])
def verify_seal():
    """
    Verifica integridad
    
    POST /api/seal/verify
    Body: {
        "embedding": [0.1, 0.2, ...],
        "certificate": { ... },
        "ciphertext": "hex_string",
        "metadata": { ... }
    }
    """
    global aee
    
    if aee is None:
        return jsonify({
            "success": False,
            "error": "Genera claves primero"
        }), 400
    
    try:
        data = request.get_json()
        
        required = ['embedding', 'certificate', 'ciphertext']
        for field in required:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Campo '{field}' requerido"
                }), 400
        
        result = aee.verify_seal(
            data['embedding'],
            data['certificate'],
            data['ciphertext'],
            data.get('metadata')
        )
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/demo/full', methods=['POST'])
def demo_full():
    """
    Demo completa: genera claves, crea sello, verifica
    
    POST /api/demo/full
    Body: {
        "dimensions": 1536
    }
    """
    try:
        data = request.get_json() or {}
        dimensions = data.get('dimensions', 1536)
        
        # 1. Generar claves
        demo_aee = AEEProtocol()
        keypair = demo_aee.generate_keypair()
        
        # 2. Crear embedding de ejemplo
        embedding = np.random.randn(dimensions).astype(np.float32).tolist()
        
        metadata = {
            "model": "demo-embedding",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dimensions": dimensions
        }
        
        # 3. Crear sello
        seal_result = demo_aee.create_seal(embedding, metadata)
        
        # 4. Verificar original
        verify_original = demo_aee.verify_seal(
            embedding,
            seal_result['certificate'],
            seal_result['ciphertext'],
            metadata
        )
        
        # 5. Verificar alterado
        embedding_tampered = embedding.copy()
        embedding_tampered[0] += 0.001
        
        verify_tampered = demo_aee.verify_seal(
            embedding_tampered,
            seal_result['certificate'],
            seal_result['ciphertext'],
            metadata
        )
        
        return jsonify({
            "success": True,
            "data": {
                "keypair": keypair,
                "embedding_shape": [dimensions],
                "seal": seal_result['certificate']['seal'][:48] + "...",
                "verification_original": verify_original,
                "verification_tampered": verify_tampered,
                "summary": {
                    "original_valid": verify_original['valid'],
                    "tampered_valid": verify_tampered['valid'],
                    "attack_detected": not verify_tampered['valid']
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    print("=" * 70)
    print("🔐 AEE PROTOCOL - API BACKEND")
    print("=" * 70)
    print()
    print("API disponible en: http://localhost:5000")
    print()
    print("Endpoints:")
    print("  GET  /api/health           - Health check")
    print("  POST /api/keypair/generate - Generar claves")
    print("  POST /api/seal/create      - Crear sello")
    print("  POST /api/seal/verify      - Verificar sello")
    print("  POST /api/demo/full        - Demo completa")
    print()
    print("Ejemplo con curl:")
    print('  curl http://localhost:5000/api/health')
    print('  curl -X POST http://localhost:5000/api/demo/full')
    print()
    print("=" * 70)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)