import aeeprotocol
import numpy as np

def run_full_flow_test():
    """
    Tests the full signing and verification flow of a quantum seal.
    """
    print("=== AEE Protocol: Full Flow Test (Sign & Verify) ===")

    try:
        # 1. Initialize the client for signing
        # This client will generate and hold the public key
        signing_client = aeeprotocol.AEEClient()
        print("[1/5] Signing AEEClient initialized successfully.")

        # 2. Generate a new post-quantum identity
        public_key, secret_key = signing_client.initialize_identity()
        print("[2/5] New Kyber-768 identity generated.")
        
        # 3. Create a client for verification, loaded with the secret key
        verifying_client = aeeprotocol.AEEClient(secret_key=secret_key)
        print("[3/5] Verification client created with the new secret key.")

        # 4. Create a sample embedding and seal it using the signing client
        embedding = np.random.randn(768).astype(np.float32)
        embedding_bytes = embedding.tobytes()
        print("[4/5] Sample embedding created and sealed with a quantum-safe signature.")
        
        sealed_data = signing_client.protect_vector(embedding_bytes)
        print(f"      Ciphertext: {sealed_data['ciphertext'][:32]}...")

        # 5. Verify the seal using the verification client
        # This simulates a scenario where a different entity, holding the secret key,
        # verifies the authenticity of the data.
        is_valid = verifying_client.verify_vector(sealed_data['ciphertext'])
        print("[5/5] Verification completed.")

        if is_valid:
            print("\n✅ SUCCESS: The quantum seal is valid. The full sign and verify flow works.")
        else:
            print("\n❌ FAILURE: The quantum seal is NOT valid.")

    except Exception as e:
        print(f"\n❌ An error occurred during the test: {e}")
        print("   Please ensure the 'aeeprotocol' package is installed correctly (`pip install -e .`)")
        print("   And that the project structure is correct as per the last report.")

if __name__ == "__main__":
    run_full_flow_test()
