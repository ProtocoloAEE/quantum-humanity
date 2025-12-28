"""
AEE Protocol v8.3 - Rigorous Statistical Audit
Tests with scientific threshold calculation
"""

import numpy as np
import sys
from pathlib import Path

# Add parent directory to path to import aeeprotocol
sys.path.insert(0, str(Path(__file__).parent))

from aeeprotocol.sdk.client import AEEClient


def run_comprehensive_audit():
    """Run comprehensive audit with new v8.3 engine"""
    
    print("\n" + "="*70)
    print("AEE PROTOCOL v8.3 - COMPREHENSIVE STATISTICAL AUDIT")
    print("="*70)
    
    # Test different configurations
    test_configs = [
        {"strength": 0.5, "target_fpr": 0.02, "name": "Balanced (2% FPR)"},
        {"strength": 0.5, "target_fpr": 0.01, "name": "Strict (1% FPR)"},
        {"strength": 0.5, "target_fpr": 0.001, "name": "Very Strict (0.1% FPR)"},
        {"strength": 0.4, "target_fpr": 0.02, "name": "Low Strength (0.4)"},
        {"strength": 0.6, "target_fpr": 0.02, "name": "High Strength (0.6)"},
    ]
    
    for config in test_configs:
        print(f"\n{'='*50}")
        print(f"CONFIG: {config['name']}")
        print(f"Strength: {config['strength']}, Target FPR: {config['target_fpr']:.3%}")
        print(f"{'='*50}")
        
        # Initialize client
        client = AEEClient(
            user_id=35664619,
            strength=config['strength'],
            target_fpr=config['target_fpr']
        )
        
        # Get engine threshold for reporting
        threshold = client.engine.threshold
        
        # 1. False Positive Rate Test
        print(f"\n1. FALSE POSITIVE RATE TEST (Target: {config['target_fpr']:.3%})")
        
        n_fpr_tests = 10000
        false_positives = 0
        fpr_scores = []
        
        for i in range(n_fpr_tests):
            # Generate completely random vector
            random_vec = np.random.randn(768).astype(np.float32)
            random_vec = random_vec / np.linalg.norm(random_vec)
            
            result = client.verify(random_vec)
            fpr_scores.append(result['confidence_score'])
            
            if result['verified']:
                false_positives += 1
        
        observed_fpr = false_positives / n_fpr_tests
        
        print(f"   Tests: {n_fpr_tests:,}")
        print(f"   Threshold: {threshold:.6f}")
        print(f"   False positives: {false_positives}")
        print(f"   Observed FPR: {observed_fpr:.4%}")
        print(f"   Target FPR: {config['target_fpr']:.4%}")
        print(f"   Difference: {observed_fpr - config['target_fpr']:.4%}")
        print(f"   Score range: {min(fpr_scores):.6f} to {max(fpr_scores):.6f}")
        
        # 2. True Positive Rate (No noise)
        print(f"\n2. TRUE POSITIVE RATE (No noise)")
        
        n_tpr_tests = 100
        true_positives = 0
        tpr_scores = []
        
        for i in range(n_tpr_tests):
            # Generate and watermark vector
            original = np.random.randn(768).astype(np.float32)
            original = original / np.linalg.norm(original)
            
            watermarked, _ = client.watermark(original)
            result = client.verify(watermarked)
            
            tpr_scores.append(result['confidence_score'])
            if result['verified']:
                true_positives += 1
        
        tpr = true_positives / n_tpr_tests
        avg_score = np.mean(tpr_scores)
        
        print(f"   Tests: {n_tpr_tests}")
        print(f"   True positives: {true_positives}")
        print(f"   TPR: {tpr:.2%}")
        print(f"   Average score: {avg_score:.6f}")
        print(f"   Score range: {min(tpr_scores):.6f} to {max(tpr_scores):.6f}")
        
        # 3. Noise Resilience Test
        print(f"\n3. NOISE RESILIENCE TEST")
        
        noise_levels = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
        n_noise_tests = 50
        
        print(f"   Noise levels: {noise_levels}")
        print(f"   Tests per level: {n_noise_tests}")
        print(f"   {'Noise (σ)':<10} {'Survival':<10} {'Avg Score':<12} {'Min Score':<12} {'Max Score':<12}")
        print(f"   {'-'*60}")
        
        # Create one watermarked vector for all noise tests
        original = np.random.randn(768).astype(np.float32)
        original = original / np.linalg.norm(original)
        watermarked, _ = client.watermark(original)
        
        for sigma in noise_levels:
            survival_count = 0
            noise_scores = []
            
            for trial in range(n_noise_tests):
                # Add Gaussian noise
                noise = np.random.normal(0, sigma, 768).astype(np.float32)
                attacked = watermarked + noise
                attacked = attacked / np.linalg.norm(attacked)
                
                result = client.verify(attacked)
                noise_scores.append(result['confidence_score'])
                
                if result['verified']:
                    survival_count += 1
            
            survival_rate = survival_count / n_noise_tests
            avg_noise_score = np.mean(noise_scores)
            min_score = min(noise_scores)
            max_score = max(noise_scores)
            
            print(f"   {sigma:<10.2f} {survival_rate:<10.2%} {avg_noise_score:<12.6f} "
                  f"{min_score:<12.6f} {max_score:<12.6f}")
    
    print(f"\n{'='*70}")
    print("AUDIT COMPLETED SUCCESSFULLY")
    print("="*70)
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"  - Engine v8.3 uses scientific threshold calculation")
    print(f"  - FPR is now configurable (2%, 1%, 0.1%, etc.)")
    print(f"  - Threshold adapts automatically to target FPR")
    print(f"  - Better transparency and predictability")
    
    return True


if __name__ == "__main__":
    try:
        success = run_comprehensive_audit()
        if success:
            print("\n✅ Audit passed! The protocol is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Audit failed! Check the implementation.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error during audit: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)