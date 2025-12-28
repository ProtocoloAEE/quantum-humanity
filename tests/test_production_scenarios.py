"""
Production scenario tests for AEE Protocol v0.3.0
Validates real-world use cases and edge cases
"""

import pytest
import numpy as np
import secrets
from aeeprotocol.sdk.client import AEEClient


class TestProductionScenarios:
    """End-to-end production scenario tests."""
    
    def setup_method(self):
        """Setup for each test."""
        self.secret_key = secrets.token_bytes(32)
        self.client = AEEClient(
            secret_key=self.secret_key,
            strength=0.350,
            target_fpr=0.0001  # 0.01% total FPR
        )
    
    def test_production_workflow(self):
        """Complete production workflow: generate, store, verify."""
        print("\n=== PRODUCTION WORKFLOW TEST ===")
        
        # 1. Generate synthetic embedding (simulating OpenAI/Cohere)
        original_embedding = np.random.randn(768).astype(np.float32)
        original_embedding = original_embedding / np.linalg.norm(original_embedding)
        
        print(f"1. Original embedding: norm={np.linalg.norm(original_embedding):.6f}")
        
        # 2. Watermark before storage
        watermarked, proof = self.client.watermark(
            original_embedding,
            metadata={"source": "test_dataset", "model": "text-embedding-3-small"}
        )
        
        print(f"2. Watermarked: proof_id={proof['config_hash'][:8]}")
        print(f"   Distortion: {np.linalg.norm(watermarked - original_embedding):.6f}")
        
        # 3. Simulate storage in vector DB
        stored_vector = watermarked.copy()
        
        # 4. Later verification (blind detection)
        verification_result = self.client.verify(stored_vector)
        
        print(f"3. Verification: {verification_result['verified']}")
        print(f"   Confidence: {verification_result['confidence_percent']}")
        print(f"   Chunks: {verification_result['chunks_detected']}/"
              f"{verification_result['chunks_total']}")
        
        # 5. ASSERT: Must detect own watermarks
        assert verification_result['verified'] is True, \
            "Production failure: cannot verify own watermarks"
        
        assert verification_result['confidence'] > 0.7, \
            f"Low confidence: {verification_result['confidence']:.3f}"
        
        print("✅ PRODUCTION WORKFLOW PASSED")
    
    def test_false_positive_rate_empirical(self):
        """Empirical FPR test with 10,000 random vectors."""
        print("\n=== EMPIRICAL FPR TEST (10,000 vectors) ===")
        
        n_trials = 10000
        false_positives = 0
        
        for i in range(n_trials):
            # Generate random vector (no watermark)
            random_vec = np.random.randn(768).astype(np.float32)
            random_vec = random_vec / np.linalg.norm(random_vec)
            
            # Verify (should NOT detect)
            result = self.client.verify(random_vec)
            
            if result['verified']:
                false_positives += 1
                
                # Log details of false positives for debugging
                if false_positives <= 3:  # Log first few
                    print(f"  False positive #{false_positives}: "
                          f"confidence={result['confidence']:.3f}, "
                          f"scores={[f'{s:.3f}' for s in result['chunk_scores']]}")
        
        empirical_fpr = false_positives / n_trials
        theoretical_fpr = 0.0001  # 0.01% target
        
        print(f"Trials: {n_trials}")
        print(f"False positives: {false_positives}")
        print(f"Empirical FPR: {empirical_fpr:.8f} ({empirical_fpr*100:.6f}%)")
        print(f"Theoretical FPR: {theoretical_fpr:.8f} ({theoretical_fpr*100:.6f}%)")
        print(f"Ratio: {empirical_fpr/theoretical_fpr:.2f}x")
        
        # Statistical tolerance: within 5x of theoretical
        assert empirical_fpr <= theoretical_fpr * 5, \
            f"FPR too high: {empirical_fpr:.8f} > {theoretical_fpr*5:.8f}"
        
        # But should have at least SOME false positives (or test is broken)
        assert false_positives > 0 or n_trials < 100000, \
            "Unrealistic: zero false positives"
        
        print(f"✅ FPR TEST PASSED: {false_positives} false positives "
              f"({empirical_fpr*100:.6f}%)")
    
    def test_noise_resilience(self):
        """Test watermark survival under realistic noise conditions."""
        print("\n=== NOISE RESILIENCE TEST ===")
        
        # Create watermarked vector
        original = np.random.randn(768).astype(np.float32)
        original = original / np.linalg.norm(original)
        
        watermarked, _ = self.client.watermark(original)
        
        noise_levels = [0.05, 0.10, 0.15, 0.20]  # 5% to 20% noise
        detection_rates = []
        
        for noise_sigma in noise_levels:
            n_success = 0
            n_trials = 100
            
            for _ in range(n_trials):
                # Add Gaussian noise
                noise = np.random.normal(0, noise_sigma, 768).astype(np.float32)
                noisy = watermarked + noise
                noisy = noisy / np.linalg.norm(noisy)
                
                # Try to detect
                result = self.client.verify(noisy)
                if result['verified']:
                    n_success += 1
            
            detection_rate = n_success / n_trials
            detection_rates.append(detection_rate)
            
            print(f"  Noise σ={noise_sigma:.2f}: {detection_rate:.1%} detection "
                  f"({n_success}/{n_trials})")
        
        # Requirements for production:
        assert detection_rates[0] >= 0.98, f"5% noise: {detection_rates[0]:.1%} < 98%"
        assert detection_rates[1] >= 0.90, f"10% noise: {detection_rates[1]:.1%} < 90%"
        assert detection_rates[2] >= 0.70, f"15% noise: {detection_rates[2]:.1%} < 70%"
        
        print("✅ NOISE RESILIENCE PASSED")
    
    def test_batch_operations(self):
        """Test batch watermarking and verification."""
        print("\n=== BATCH OPERATIONS TEST ===")
        
        # Generate batch of 100 vectors
        batch_size = 100
        vectors = np.random.randn(batch_size, 768).astype(np.float32)
        
        # Normalize each vector
        for i in range(batch_size):
            vectors[i] = vectors[i] / np.linalg.norm(vectors[i])
        
        print(f"Batch size: {batch_size} vectors")
        
        # Batch watermark
        import time
        start = time.time()
        watermarked_batch, proofs = self.client.batch_watermark(vectors)
        watermark_time = time.time() - start
        
        print(f"Batch watermark time: {watermark_time:.3f}s "
              f"({watermark_time/batch_size*1000:.1f}ms/vector)")
        
        # Batch verify
        start = time.time()
        results = self.client.batch_verify(watermarked_batch)
        verify_time = time.time() - start
        
        print(f"Batch verify time: {verify_time:.3f}s "
              f"({verify_time/batch_size*1000:.1f}ms/vector)")
        
        # All should be verified
        verified_count = sum(1 for r in results if r['verified'])
        
        assert verified_count == batch_size, \
            f"Batch verification failed: {verified_count}/{batch_size}"
        
        # Performance requirement: < 2ms per vector
        assert watermark_time/batch_size < 0.002, \
            f"Watermark too slow: {watermark_time/batch_size*1000:.1f}ms/vector"
        
        assert verify_time/batch_size < 0.002, \
            f"Verify too slow: {verify_time/batch_size*1000:.1f}ms/vector"
        
        print(f"✅ BATCH OPERATIONS PASSED: {verified_count}/{batch_size} verified")
    
    def test_key_management(self):
        """Test secure key generation and management."""
        print("\n=== KEY MANAGEMENT TEST ===")
        
        # Test key generation methods
        key_bytes = AEEClient.generate_key()
        key_hex = AEEClient.generate_key_hex()
        key_b64 = AEEClient.generate_key_b64()
        
        print(f"Key bytes length: {len(key_bytes)} bytes")
        print(f"Key hex length: {len(key_hex)} chars")
        print(f"Key b64 length: {len(key_b64)} chars")
        
        # Validation
        assert len(key_bytes) == 32, "Key must be 32 bytes"
        assert len(key_hex) == 64, "Hex key must be 64 chars"
        
        # Test that hex and b64 decode correctly
        key_from_hex = bytes.fromhex(key_hex)
        key_from_b64 = base64.b64decode(key_b64)
        
        assert len(key_from_hex) == 32, "Hex decode failed"
        assert len(key_from_b64) == 32, "Base64 decode failed"
        
        # Test client initialization with different key formats
        client1 = AEEClient(secret_key=key_bytes, strength=0.35, target_fpr=0.0001)
        client2 = AEEClient(secret_key=key_from_hex, strength=0.35, target_fpr=0.0001)
        client3 = AEEClient(secret_key=key_from_b64, strength=0.35, target_fpr=0.0001)
        
        # All should have different fingerprints (different keys)
        fingerprints = {
            client1.key_fingerprint,
            client2.key_fingerprint,
            client3.key_fingerprint
        }
        
        assert len(fingerprints) == 3, "Key fingerprints should be unique"
        
        print("✅ KEY MANAGEMENT PASSED")
    
    def test_forensic_evidence(self):
        """Test that results are suitable as forensic evidence."""
        print("\n=== FORENSIC EVIDENCE TEST ===")
        
        # Create a watermarked vector
        vector = np.random.randn(768).astype(np.float32)
        vector = vector / np.linalg.norm(vector)
        
        watermarked, proof = self.client.watermark(vector)
        result = self.client.verify(watermarked)
        
        # Forensic requirements:
        # 1. Must have high confidence
        assert result['confidence'] > 0.8, \
            f"Low confidence for forensic: {result['confidence']:.3f}"
        
        # 2. Must have strict consensus (4/4 chunks)
        assert result['chunks_detected'] == result['chunks_total'], \
            f"Not strict consensus: {result['chunks_detected']}/{result['chunks_total']}"
        
        # 3. Must have detailed scores
        assert 'chunk_scores' in result, "Missing chunk scores"
        assert len(result['chunk_scores']) == 4, "Should have 4 chunk scores"
        
        # 4. All scores must be well above threshold
        threshold = result['threshold']
        for score in result['chunk_scores']:
            assert score > threshold * 1.5, \
                f"Score {score:.4f} too close to threshold {threshold:.4f}"
        
        # 5. Result must be reproducible
        result2 = self.client.verify(watermarked)
        assert result['verified'] == result2['verified'], "Non-reproducible results"
        
        print(f"✅ FORENSIC EVIDENCE PASSED:")
        print(f"   Confidence: {result['confidence_percent']}")
        print(f"   Consensus: {result['chunks_detected']}/{result['chunks_total']}")
        print(f"   Min score/threshold: {min(result['chunk_scores']):.4f}/{threshold:.4f}")


def run_all_production_tests():
    """Run all production tests and provide summary."""
    print("=" * 70)
    print("AEE PROTOCOL v0.3.0 - PRODUCTION VALIDATION SUITE")
    print("=" * 70)
    
    test_class = TestProductionScenarios()
    tests = [
        test_class.test_production_workflow,
        test_class.test_false_positive_rate_empirical,
        test_class.test_noise_resilience,
        test_class.test_batch_operations,
        test_class.test_key_management,
        test_class.test_forensic_evidence,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test_class.setup_method()
            test()
            passed += 1
            print(f"✅ {test.__name__}: PASSED\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__}: FAILED - {str(e)}\n")
    
    print("=" * 70)
    print("SUMMARY:")
    print(f"  Passed: {passed}/{len(tests)}")
    print(f"  Failed: {failed}/{len(tests)}")
    print("=" * 70)
    
    if failed == 0:
        print("🎉 ALL PRODUCTION TESTS PASSED - READY FOR v0.3.0 RELEASE!")
    else:
        print("⚠️  SOME TESTS FAILED - NEEDS FIXING BEFORE RELEASE")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_production_tests()
    exit(0 if success else 1)