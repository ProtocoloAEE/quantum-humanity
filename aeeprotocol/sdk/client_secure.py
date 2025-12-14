"""
AEE Client Secure - With proper key management
"""

import numpy as np
import os
import base64
from typing import Dict, Tuple, Optional
from ..core.engine import AEEMathEngineSecure


class AEEClientSecure:
    """
    Secure client with cryptographic key management.
    
    Best practices:
    1. Key stored in environment variable
    2. Key never logged or exposed
    3. Key rotation support
    4. Separate key from user_id
    """
    
    def __init__(self, user_id: int, strength: float = 0.5, 
                 target_fpr: float = 0.02, secret_key: Optional[bytes] = None):
        """
        Initialize secure client.
        
        Args:
            user_id: Public user identifier (can be public)
            strength: Watermark strength
            target_fpr: Target false positive rate
            secret_key: Cryptographic key (or use AEE_SECRET_KEY env var)
        """
        self.user_id = int(user_id)
        
        # Get secret key from parameter or environment
        if secret_key is not None:
            final_key = secret_key
        else:
            # Try environment variable (RECOMENDADO para producción)
            key_b64 = os.getenv('AEE_SECRET_KEY')
            if key_b64:
                try:
                    final_key = base64.b64decode(key_b64)
                except:
                    raise ValueError(
                        "Invalid AEE_SECRET_KEY in environment. "
                        "Use base64 encoding."
                    )
            else:
                # Generate new key (with warning)
                import secrets
                final_key = secrets.token_bytes(32)
                print("\n" + "="*60)
                print("⚠️  SECURITY WARNING: No secret key provided")
                print("="*60)
                print("Generated new key. For production:")
                print("1. Save this key securely:")
                print(f"   export AEE_SECRET_KEY='{base64.b64encode(final_key).decode()}'")
                print("2. Never commit key to version control")
                print("3. Rotate key periodically")
                print("="*60)
        
        # Initialize secure engine
        self.engine = AEEMathEngineSecure(
            strength=strength,
            target_fpr=target_fpr,
            secret_key=final_key
        )
        
        print(f"🔐 AEE Client Secure initialized:")
        print(f"   User ID: {self.user_id} (public)")
        print(f"   Key fingerprint: {self.engine.key_fingerprint}")
        print(f"   Strength: {strength}")
        print(f"   Target FPR: {target_fpr:.2%}")
    
    def watermark(self, embedding: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """Secure watermarking."""
        if embedding.ndim != 1:
            raise ValueError(f"Embedding must be 1D, got shape {embedding.shape}")
        
        if len(embedding) != 768:
            embedding = self._adjust_dimension(embedding)
        
        watermarked, metadata = self.engine.inject(embedding, self.user_id)
        
        # Remove sensitive info from public metadata
        safe_metadata = {
            k: v for k, v in metadata.items()
            if k not in ['secret_key', 'key_fingerprint']
        }
        
        return watermarked, safe_metadata
    
    def verify(self, embedding: np.ndarray) -> Dict:
        """Secure verification."""
        if len(embedding) != 768:
            embedding = self._adjust_dimension(embedding)
        
        result = self.engine.detect(embedding, self.user_id)
        
        return {
            'verified': result['detected'],
            'confidence_score': result['correlation_score'],
            'confidence_level': result.get('confidence', 0.0),
            'threshold': result['threshold'],
            'strength': result['strength'],
            'target_fpr': result['target_fpr'],
            'user_id': result['user_id'],
            'key_fingerprint': result['key_fingerprint'],
        }
    
    def _adjust_dimension(self, embedding: np.ndarray, target_dim: int = 768):
        """Adjust dimension."""
        current_dim = len(embedding)
        
        if current_dim == target_dim:
            return embedding
        
        if current_dim > target_dim:
            return embedding[:target_dim].copy()
        else:
            padded = np.zeros(target_dim, dtype=embedding.dtype)
            padded[:current_dim] = embedding
            return padded
    
    @staticmethod
    def generate_key() -> str:
        """Generate and return base64-encoded key."""
        import secrets
        key = secrets.token_bytes(32)
        return base64.b64encode(key).decode()
    
    @staticmethod
    def save_key_to_env_file(key_b64: str, env_file: str = ".env"):
        """Save key to .env file (for development)."""
        with open(env_file, 'w') as f:
            f.write(f"AEE_SECRET_KEY='{key_b64}'\n")
        print(f"✅ Key saved to {env_file}")
        print(f"   Add {env_file} to .gitignore!")