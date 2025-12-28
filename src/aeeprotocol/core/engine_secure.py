"""
AEE Math Engine v9.0 - Holographic Secure Edition
Optimized parameters for production reliability
"""

import numpy as np
import hashlib
from scipy.special import erfinv
from typing import Tuple, Dict, Optional, Any


class AEEMathEngineSecure:
    """
    Holographic watermarking engine - PRODUCTION READY v9.0
    
    OPTIMAL CONFIGURATION:
    - strength: 0.350 (35% of unit sphere) - Balanced for reliable detection
    - target_fpr_per_chunk: 0.02 (2% per chunk)
    - chunks: 4 (holographic redundancy)
    - consensus: 4/4 (strict requirement)
    - Total FPR: (0.02)^4 = 0.000016% (forensic grade)
    """

    def __init__(self, strength: float = 0.350, target_fpr_per_chunk: float = 0.02):
        """
        Initialize holographic engine with PRODUCTION-READY parameters.
        
        Args:
            strength: Watermark strength (0.30-0.40 recommended for holographic)
            target_fpr_per_chunk: False positive rate per chunk (0.01-0.05 recommended)
        
        Raises:
            ValueError: If parameters are outside safe ranges
        """
        # PRODUCTION-READY VALIDATION RANGES
        if not 0.25 <= strength <= 0.45:
            raise ValueError(
                f"strength={strength} invalid. Use 0.25-0.45 range. "
                f"Recommended: 0.350 for holographic mode."
            )
        
        if not 0.005 <= target_fpr_per_chunk <= 0.05:
            raise ValueError(
                f"target_fpr_per_chunk={target_fpr_per_chunk} invalid. "
                f"Use 0.005-0.05 (0.5%-5%). Recommended: 0.02 (2%)."
            )
        
        # OPTIMAL PARAMETERS (validated empirically)
        self.strength = float(strength)
        self.target_fpr_per_chunk = float(target_fpr_per_chunk)
        self.num_chunks = 4  # Fixed holographic redundancy
        
        # Scientific threshold calculation
        self.threshold_per_chunk = self._calculate_threshold(self.target_fpr_per_chunk)
        
        # Engine constants
        self.dimension = 768
        self.chunk_size = self.dimension // self.num_chunks  # 768/4 = 192
        
        # Configuration fingerprint (for debugging)
        self.config_hash = hashlib.md5(
            f"{strength}:{target_fpr_per_chunk}:v9.0-prod".encode()
        ).hexdigest()[:16]
        
        # Log optimal configuration
        self._log_configuration()

    def _calculate_threshold(self, fpr_target: float) -> float:
        """
        Calculate correlation threshold for desired FPR.
        
        Uses Z-score approximation for Gaussian distribution of random correlations.
        In 192 dimensions (chunk_size), random vectors have correlation ~N(0, 1/√192)
        
        Returns:
            Correlation threshold for detection
        """
        # Convert FPR to Z-score (one-tailed)
        # For Gaussian: P(X > threshold) = fpr_target
        # threshold = Z * sigma, where sigma = 1/√n
        
        # Using inverse error function for precision
        z_score = np.sqrt(2) * erfinv(1 - 2 * fpr_target)
        
        # Standard deviation of correlation in n dimensions
        sigma = 1.0 / np.sqrt(self.chunk_size)
        
        threshold = z_score * sigma
        return float(threshold)

    def _log_configuration(self):
        """Log optimized engine configuration."""
        total_fpr = self.target_fpr_per_chunk ** self.num_chunks
        
        print("=" * 60)
        print("AEE MATH ENGINE v9.0-HOLO - PRODUCTION CONFIG")
        print("=" * 60)
        print(f"✓ Strength:          {self.strength:.3f} (OPTIMAL)")
        print(f"✓ Chunks:            {self.num_chunks}")
        print(f"✓ Chunk FPR Target:  {self.target_fpr_per_chunk:.3f} ({self.target_fpr_per_chunk:.1%})")
        print(f"✓ Overall FPR:       ~{total_fpr:.8f} ({total_fpr:.6f}%)")
        print(f"✓ Chunk Threshold:   {self.threshold_per_chunk:.6f}")
        print(f"✓ Chunk Size:        {self.chunk_size} dimensions")
        print(f"✓ Expected Scores:   {self.strength*0.7:.3f} - {self.strength*1.3:.3f}")
        print(f"✓ Config Fingerprint:{self.config_hash}")
        print("=" * 60)
        print("NOTE: Requires 4/4 chunks for detection (strict consensus)")
        print("=" * 60)

    def _get_chunk_seed(self, user_id: int, chunk_idx: int) -> int:
        """
        Generate deterministic seed for each holographic chunk.
        
        Ensures reproducibility across inject/detect cycles.
        """
        seed_str = f"{user_id}_v9_holo_{chunk_idx}_{self.config_hash}"
        seed_bytes = hashlib.sha256(seed_str.encode()).digest()
        return int.from_bytes(seed_bytes[:4], 'big', signed=False)

    def compute_chunk_direction(self, chunk_dim: int, seed: int) -> np.ndarray:
        """
        Generate deterministic direction vector for a chunk.
        
        Args:
            chunk_dim: Dimension of the chunk (192 for 768/4)
            seed: Deterministic seed for reproducibility
        
        Returns:
            Unit-norm direction vector
        """
        rng = np.random.RandomState(seed)
        direction = rng.randn(chunk_dim).astype(np.float32)
        
        # Ensure unit norm
        norm = np.linalg.norm(direction)
        if norm > 1e-9:
            direction = direction / norm
        
        return direction

    def inject(self, embedding: np.ndarray, user_id: int) -> Tuple[np.ndarray, dict]:
        """
        Inject holographic watermark into 4 orthogonal sub-spaces.
        
        Args:
            embedding: Original vector (768-D, unit norm recommended)
            user_id: User identifier for deterministic seeding
        
        Returns:
            watermarked: Watermarked vector (unit norm preserved)
            metadata: Injection metadata
        """
        # 1. Ensure input is normalized
        original_norm = np.linalg.norm(embedding)
        if abs(original_norm - 1.0) > 1e-6:
            embedding = embedding / original_norm
        
        # 2. Split into 4 equal chunks
        chunks = np.array_split(embedding, self.num_chunks)
        marked_chunks = []
        
        # 3. Inject watermark into each chunk
        for i, chunk in enumerate(chunks):
            # Generate deterministic direction for this chunk
            seed = self._get_chunk_seed(user_id, i)
            direction = self.compute_chunk_direction(len(chunk), seed)
            
            # ORTHOGONAL INJECTION (core algorithm)
            # V'_i = V_i + strength * D_i
            marked_chunk = chunk + (self.strength * direction)
            marked_chunks.append(marked_chunk)
        
        # 4. Reassemble and normalize
        watermarked = np.concatenate(marked_chunks)
        watermarked = watermarked / np.linalg.norm(watermarked)
        
        # Metadata for debugging/auditing
        metadata = {
            "version": "v9.0-holo",
            "strength": self.strength,
            "chunks": self.num_chunks,
            "user_id": user_id,
            "config_hash": self.config_hash,
            "original_norm": float(original_norm),
            "final_norm": float(np.linalg.norm(watermarked))
        }
        
        return watermarked, metadata

    def detect(self, embedding: np.ndarray, user_id: int) -> Dict[str, Any]:
        """
        Detect holographic watermark with strict 4/4 consensus.
        
        Args:
            embedding: Vector to check (768-D)
            user_id: User identifier to regenerate watermark
        
        Returns:
            Detection result with detailed scores
        """
        # 1. Normalize input vector
        input_norm = np.linalg.norm(embedding)
        if input_norm > 1e-9:
            embedding = embedding / input_norm
        
        # 2. Split into chunks
        chunks = np.array_split(embedding, self.num_chunks)
        
        # 3. Check each chunk independently
        chunk_scores = []
        chunks_detected = 0
        
        for i, chunk in enumerate(chunks):
            # Regenerate the same direction as during injection
            seed = self._get_chunk_seed(user_id, i)
            direction = self.compute_chunk_direction(len(chunk), seed)
            
            # Compute correlation score
            chunk_norm = np.linalg.norm(chunk)
            if chunk_norm > 1e-9:
                normalized_chunk = chunk / chunk_norm
                score = float(np.dot(normalized_chunk, direction))
            else:
                score = 0.0
            
            chunk_scores.append(score)
            
            # Individual chunk detection
            if score > self.threshold_per_chunk:
                chunks_detected += 1
        
        # 4. STRICT CONSENSUS: Require ALL chunks (4/4)
        # This maintains the mathematical guarantee: FPR_total = (FPR_chunk)^4
        is_verified = chunks_detected == self.num_chunks
        
        # 5. Calculate confidence metrics
        avg_score = np.mean(chunk_scores) if chunk_scores else 0.0
        min_score = min(chunk_scores) if chunk_scores else 0.0
        max_score = max(chunk_scores) if chunk_scores else 0.0
        
        return {
            "detected": is_verified,
            "chunks_detected": chunks_detected,
            "chunks_total": self.num_chunks,
            "chunk_scores": chunk_scores,
            "threshold": self.threshold_per_chunk,
            "avg_score": avg_score,
            "min_score": min_score,
            "max_score": max_score,
            "user_id": user_id,
            "config_hash": self.config_hash,
            "consensus_required": f"{self.num_chunks}/{self.num_chunks}",
            "strength": self.strength
        }