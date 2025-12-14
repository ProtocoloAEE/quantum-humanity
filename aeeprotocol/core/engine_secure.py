"""
AEE Protocol v8.3-SECURE - Engine with cryptographic key protection
"""

import numpy as np
import hashlib
import hmac
import secrets
from typing import Tuple, Dict, Optional
import base64
import json

try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


class AEEMathEngineSecure:
    """
    SECURE version with proper key management.
    
    Critical fixes:
    1. Uses HMAC for direction generation (not just user_id)
    2. Key is separate from user_id
    3. Supports key rotation
    4. No private information in metadata
    """
    
    DEFAULT_DIM = 768
    
    def __init__(self, strength: float = 0.5, target_fpr: float = 0.02, 
                 secret_key: Optional[bytes] = None):
        """
        Initialize with cryptographic security.
        
        Args:
            strength: Watermark strength (0.3-0.7)
            target_fpr: Target false positive rate
            secret_key: Cryptographic key (generate if None)
                      KEEP THIS SECRET! Never commit to git.
        """
        if not 0.1 <= strength <= 1.0:
            raise ValueError(f"strength must be between 0.1 and 1.0, got {strength}")
        
        if not 1e-6 <= target_fpr <= 0.5:
            raise ValueError(f"target_fpr must be between 1e-6 and 0.5, got {target_fpr}")
        
        self.strength = float(strength)
        self.target_fpr = float(target_fpr)
        
        # Generate or use provided secret key
        if secret_key is None:
            self.secret_key = secrets.token_bytes(32)  # 256-bit key
            print("⚠️  GENERATED NEW SECRET KEY - SAVE THIS FOR FUTURE USE!")
            print(f"   Key (hex): {self.secret_key.hex()}")
            print(f"   Key (b64): {base64.b64encode(self.secret_key).decode()}")
        else:
            self.secret_key = secret_key
        
        # Calculate threshold scientifically
        self.threshold = self._calculate_threshold(target_fpr)
        
        # Cache for directions (key: (user_id, key_fingerprint))
        self._direction_cache = {}
        
        # Key fingerprint for verification
        self.key_fingerprint = hashlib.sha256(self.secret_key).hexdigest()[:16]
        
        self._print_secure_config()
    
    def _print_secure_config(self):
        """Print secure configuration."""
        print("\n" + "="*60)
        print("AEE MATH ENGINE v8.3-SECURE - CRYPTOGRAPHIC CONFIG")
        print("="*60)
        print(f"✓ Strength:          {self.strength:.3f}")
        print(f"✓ Target FPR:        {self.target_fpr:.3%}")
        print(f"✓ Threshold:         {self.threshold:.6f}")
        print(f"✓ Key fingerprint:   {self.key_fingerprint}")
        print(f"✓ Key length:        {len(self.secret_key)} bytes")
        print("="*60)
        print("⚠️  SECURITY WARNING:")
        print("   - Keep secret_key secure (never commit to git)")
        print("   - Rotate key if compromised")
        print("   - Store key in environment variable or key manager")
        print("="*60)
    
    def _calculate_threshold(self, target_fpr: float) -> float:
        """Calculate threshold scientifically."""
        n = self.DEFAULT_DIM
        
        if HAS_SCIPY:
            z_score = stats.norm.ppf(1 - target_fpr / 2)
        else:
            import math
            z_score = math.sqrt(2) * math.erfcinv(target_fpr)
        
        threshold = z_score / np.sqrt(n - 3)
        return float(np.clip(threshold, 0.01, 0.5))
    
    def _compute_direction_secure(self, user_id: int) -> np.ndarray:
        """
        Generate direction using HMAC for cryptographic security.
        
        HMAC ensures:
        1. Key secrecy: Cannot derive key from output
        2. Determinism: Same input = same output
        3. One-way: Cannot derive inputs from output
        """
        cache_key = (user_id, self.key_fingerprint)
        
        if cache_key in self._direction_cache:
            return self._direction_cache[cache_key]
        
        # Use HMAC for cryptographic security
        message = f"user:{user_id}:dim:{self.DEFAULT_DIM}".encode('utf-8')
        hmac_result = hmac.new(self.secret_key, message, hashlib.sha256).digest()
        
        # Convert to deterministic seed
        seed_int = int.from_bytes(hmac_result[:8], byteorder='big')
        
        # Generate direction
        rng = np.random.RandomState(seed_int % (2**32))
        direction = rng.randn(self.DEFAULT_DIM).astype(np.float32)
        
        # Normalize
        norm = np.linalg.norm(direction)
        if norm < 1e-10:
            direction = np.ones(self.DEFAULT_DIM, dtype=np.float32)
            norm = np.linalg.norm(direction)
        
        direction = direction / norm
        
        # Cache
        self._direction_cache[cache_key] = direction
        
        return direction
    
    def inject(self, embedding: np.ndarray, user_id: int) -> Tuple[np.ndarray, Dict]:
        """Secure watermark injection."""
        embedding = embedding.astype(np.float32)
        
        # Normalize input
        input_norm = np.linalg.norm(embedding)
        if abs(input_norm - 1.0) > 1e-6:
            embedding = embedding / input_norm
        
        # Get secure direction
        direction = self._compute_direction_secure(user_id)
        
        # Inject
        watermarked = embedding + self.strength * direction
        watermarked = watermarked / np.linalg.norm(watermarked)
        
        # METADATA SEGURO (sin información sensible)
        metadata = {
            'user_id': user_id,
            'strength': self.strength,
            'target_fpr': self.target_fpr,
            'threshold': self.threshold,
            'key_fingerprint': self.key_fingerprint,  # Solo fingerprint, no key
            'watermarked_hash': hashlib.sha256(watermarked.tobytes()).hexdigest()[:12],
            'algorithm': 'AEEv8.3-SECURE',
            'timestamp': np.datetime64('now').astype(str),
            'security_level': 'HMAC-SHA256',
        }
        
        return watermarked.astype(np.float32), metadata
    
    def detect(self, embedding: np.ndarray, user_id: int) -> Dict:
        """Secure detection."""
        test_vector = embedding.astype(np.float32).copy()
        test_norm = np.linalg.norm(test_vector)
        
        if abs(test_norm - 1.0) > 1e-6:
            test_vector = test_vector / test_norm
        
        # Use SAME secure direction generation
        direction = self._compute_direction_secure(user_id)
        
        correlation = np.abs(np.dot(test_vector, direction))
        detected = correlation > self.threshold
        
        result = {
            'detected': bool(detected),
            'correlation_score': float(correlation),
            'threshold': float(self.threshold),
            'strength': float(self.strength),
            'target_fpr': float(self.target_fpr),
            'user_id': user_id,
            'key_fingerprint': self.key_fingerprint,
        }
        
        if detected:
            confidence = (correlation - self.threshold) / (1.0 - self.threshold)
            result['confidence'] = float(np.clip(confidence, 0.0, 1.0))
        else:
            result['confidence'] = 0.0
        
        return result
    
    @classmethod
    def generate_key(cls) -> bytes:
        """Generate a secure random key."""
        return secrets.token_bytes(32)
    
    @classmethod
    def load_from_env(cls, strength=0.5, target_fpr=0.02):
        """Load key from environment variable (RECOMENDADO)."""
        import os
        key_b64 = os.getenv('AEE_SECRET_KEY')
        
        if not key_b64:
            raise ValueError(
                "AEE_SECRET_KEY environment variable not set. "
                "Set it with: export AEE_SECRET_KEY='your-base64-key'"
            )
        
        try:
            secret_key = base64.b64decode(key_b64)
            return cls(strength=strength, target_fpr=target_fpr, 
                      secret_key=secret_key)
        except:
            raise ValueError("Invalid AEE_SECRET_KEY format. Use base64.")