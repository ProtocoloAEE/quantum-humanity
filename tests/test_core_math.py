"""
Core mathematical tests for AEE Protocol v9.0 Holographic Engine
All tests pass with optimized production parameters
"""

import pytest
import numpy as np
from aeeprotocol.core.engine_secure import AEEMathEngineSecure


@pytest.fixture
def holo_engine():
    """
    Holographic engine with PRODUCTION-READY parameters.
    
    Configuration:
    - strength=0.350: Optimal for 4-chunk holographic detection
    - target_fpr_per_chunk=0.02: 2% per chunk → 0.000016% total FPR
    - chunks=4: Holographic redundancy
    - consensus=4/4: Strict detection requirement
    """
    return AEEMathEngineSecure(
        strength=0.350,           # OPTIMAL for holographic
        target_fpr_per_chunk=0.02  # 2% per chunk (production standard)
    )


@pytest.fixture
def random_vector():
    """Generate random unit-norm test vector."""
    vec = np.random.randn(768).astype(np.float32)
    return vec / np.linalg.norm(vec)


@pytest.fixture
def user_id():
    """Test user ID."""
    return 35664619  # Your DNI for consistency


def test_initialization(holo_engine):
    """Test that engine initializes with correct holographic configuration."""
    # Core configuration
    assert holo_engine.num_chunks == 4, "Must have 4 holographic chunks"
    assert holo_engine.chunk_size == 192, "768/4 = 192 dimensions per chunk"
    
    # Parameter validation
    assert 0.25 <= holo_engine.strength <= 0.45, "Strength out of optimal range"
    assert 0.005 <= holo_engine.target_fpr_per_chunk <= 0.05, "FPR out of range"
    
    # Threshold should be reasonable for 192 dimensions
    assert 0.05 <= holo_engine.threshold_per_chunk <= 0.15, \
        f"Threshold {holo_engine.threshold_per_chunk} outside expected range"
    
    print(f"✓ Engine initialized: strength={holo_engine.strength}, "
          f"threshold={holo_engine.threshold_per_chunk:.6f}")


def test_determinism(holo_engine, random_vector, user_id):
    """
    AXIOM: Watermark injection must be deterministic.
    Same input + same user_id = same output.
    """
    # First injection
    marked1, proof1 = holo_engine.inject(random_vector, user_id)
    
    # Second injection (should be identical)
    marked2, proof2 = holo_engine.inject(random_vector, user_id)
    
    # Vectors should be identical (within float precision)
    assert np.allclose(marked1, marked2, rtol=1e-6, atol=1e-6), \
        "Non-deterministic watermark injection"
    
    # Norm should be preserved
    assert abs(np.linalg.norm(marked1) - 1.0) < 1e-6, "Output not normalized"
    assert abs(np.linalg.norm(marked2) - 1.0) < 1e-6, "Output not normalized"
    
    print("✓ Determinism test passed")


def test_semantic_preservation(holo_engine, random_vector, user_id):
    """
    AXIOM: Watermark should preserve semantic meaning.
    Correlation between original and watermarked should be high.
    """
    watermarked, _ = holo_engine.inject(random_vector, user_id)
    
    # Calculate semantic preservation
    correlation = np.dot(random_vector, watermarked)
    
    # With strength=0.350, expected correlation:
    # cos(angle) ≈ 1 - 0.5*(strength^2) ≈ 0.94
    expected_min = 0.90  # Allow some margin
    expected_max = 0.98  # Shouldn't be perfect
    
    assert expected_min <= correlation <= expected_max, \
        f"Semantic corruption: correlation={correlation:.4f}"
    
    # Distortion should be reasonable
    distortion = np.linalg.norm(watermarked - random_vector)
    assert 0.30 <= distortion <= 0.40, \
        f"Unexpected distortion: {distortion:.4f}"
    
    print(f"✓ Semantic preservation: correlation={correlation:.4f}, "
          f"distortion={distortion:.4f}")


def test_detection_positive(holo_engine, random_vector, user_id):
    """
    AXIOM: The engine must detect its own watermark.
    This is the core functionality test.
    """
    # 1. Inject watermark
    watermarked, metadata = holo_engine.inject(random_vector, user_id)
    
    # 2. Detect watermark (should succeed)
    result = holo_engine.detect(watermarked, user_id)
    
    # 3. VERIFICATION: Must detect with 4/4 chunks
    assert result['detected'] is True, \
        f"False Negative: Failed to detect own watermark. Details: {result}"
    
    # 4. All chunks should be detected (strict consensus)
    assert result['chunks_detected'] == result['chunks_total'], \
        f"Only {result['chunks_detected']}/{result['chunks_total']} chunks detected"
    
    # 5. Scores should be in expected range
    # With strength=0.350, scores should be ~0.25-0.30
    for i, score in enumerate(result['chunk_scores']):
        assert 0.20 <= score <= 0.40, \
            f"Chunk {i} score {score:.4f} outside expected range"
    
    # 6. Average score should be reasonable
    assert 0.25 <= result['avg_score'] <= 0.35, \
        f"Average score {result['avg_score']:.4f} unexpected"
    
    # 7. All scores should be above threshold
    for score in result['chunk_scores']:
        assert score > result['threshold'], \
            f"Score {score:.4f} below threshold {result['threshold']:.4f}"
    
    print(f"✅ Positive detection: {result['chunks_detected']}/{result['chunks_total']} chunks, "
          f"avg_score={result['avg_score']:.4f}")


def test_detection_negative_unwatermarked(holo_engine, random_vector):
    """
    AXIOM: Random unwatermarked vectors should not trigger detection.
    Tests false positive resistance.
    """
    # Use a DIFFERENT user_id than any watermark
    random_user_id = 999999
    
    result = holo_engine.detect(random_vector, random_user_id)
    
    # Should NOT detect watermark in random vector
    assert result['detected'] is False, \
        f"False Positive: Detected watermark in random vector. Details: {result}"
    
    # Most chunks should not be detected
    assert result['chunks_detected'] < 2, \
        f"Too many chunks detected ({result['chunks_detected']}) in random vector"
    
    # Scores should be near zero
    assert abs(result['avg_score']) < 0.1, \
        f"High average score {result['avg_score']:.4f} for random vector"
    
    print(f"✓ Negative detection: random vector correctly rejected "
          f"(chunks detected: {result['chunks_detected']})")


def test_security_wrong_user(holo_engine, random_vector, user_id):
    """
    SECURITY: Watermark should NOT be detectable with wrong user_id.
    """
    # 1. Watermark with correct user_id
    watermarked, _ = holo_engine.inject(random_vector, user_id)
    
    # 2. Try to detect with WRONG user_id
    wrong_user_id = user_id + 1
    result = holo_engine.detect(watermarked, wrong_user_id)
    
    # 3. Should NOT detect (different seeds = different directions)
    assert result['detected'] is False, \
        "Security breach: Watermark detectable with wrong user_id"
    
    # 4. Scores should be low (near zero correlation)
    assert abs(result['avg_score']) < 0.1, \
        f"High correlation {result['avg_score']:.4f} with wrong user_id"
    
    print("✓ Security: Wrong user_id correctly rejected")


def test_security_wrong_key_scenario(holo_engine, random_vector, user_id):
    """
    SECURITY TEST: Simulates wrong secret_key scenario.
    Different user_id = different watermark = no detection.
    """
    # This simulates what happens with wrong secret_key in client
    watermarked, _ = holo_engine.inject(random_vector, user_id)
    
    # Different user_id = different key derivation
    different_user_id = 12345678
    result = holo_engine.detect(watermarked, different_user_id)
    
    assert result['detected'] is False, \
        "Security failure: Watermark leaked across different keys"
    
    print("✓ Security: Wrong key scenario correctly handled")


def test_holographic_robustness(holo_engine, random_vector, user_id):
    """
    TEST: Holographic watermark survives moderate noise.
    """
    # 1. Create watermarked vector
    watermarked, _ = holo_engine.inject(random_vector, user_id)
    
    # 2. Add realistic noise (10% Gaussian noise)
    noise_level = 0.10
    noise = np.random.normal(0, noise_level, 768).astype(np.float32)
    noisy_vector = watermarked + noise
    noisy_vector = noisy_vector / np.linalg.norm(noisy_vector)
    
    # 3. Try to detect
    result = holo_engine.detect(noisy_vector, user_id)
    
    # With holographic redundancy, should still detect
    # Allow 1 chunk to fail due to noise (3/4 detection)
    chunks_required = 3  # Majority for noise resilience
    assert result['chunks_detected'] >= chunks_required, \
        f"Holographic robustness failed: only {result['chunks_detected']}/4 chunks"
    
    print(f"✓ Holographic robustness: {result['chunks_detected']}/4 chunks "
          f"survived {noise_level:.0%} noise")


if __name__ == "__main__":
    """
    Run tests directly for quick verification.
    """
    print("=" * 60)
    print("AEE PROTOCOL v9.0 - HOLOGRAPHIC ENGINE TEST SUITE")
    print("=" * 60)
    
    # Run all tests
    pytest.main([__file__, "-v"])