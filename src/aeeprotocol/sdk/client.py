from ..core.kyber_engine import KyberEngine

class AEEClient:
    def __init__(self):
        self.engine = KyberEngine()
        self.identity = None

    def create_identity(self):
        pub, sec = self.engine.generate_keypair()
        self.identity = {'public': pub, 'secret': sec}
        return "OK: Identidad Cuantica Generada."

    def sign_data(self, data):
        if not self.identity: 
            raise ValueError("Error: Falta Identidad")
        return self.engine.seal_embedding(self.identity['public'], data)
