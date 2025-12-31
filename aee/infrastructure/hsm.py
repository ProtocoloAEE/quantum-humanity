# src/aee/infrastructure/hsm.py
# HSM MOCK INTEGRATION - Ready para Thales Luna / YubiHSM / AWS KMS

import os
import logging
from typing import Tuple, Optional
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger('AEE-HSM')


class HSMAdapter:
    """Adaptador abstracto para HSM"""
    
    def __init__(self):
        self.hsm_enabled = os.getenv('HSM_ENABLED', 'false').lower() == 'true'
        self.hsm_type = os.getenv('HSM_TYPE', 'mock')
        self.hsm_slot = int(os.getenv('HSM_SLOT', '0'))
        self.hsm_pin = os.getenv('HSM_PIN', '1234')
        self.hsm_label = os.getenv('HSM_LABEL', 'AEE-KEY-001')
        
        logger.info(f"HSM Adapter initialized: enabled={self.hsm_enabled}, type={self.hsm_type}")
    
    def sign_with_ed25519(self, message: bytes, key_id: str) -> bytes:
        """Sign usando Ed25519 desde HSM o memoria"""
        if self.hsm_enabled and self.hsm_type != 'mock':
            return self._sign_via_hsm(message, key_id)
        else:
            private_key = ed25519.Ed25519PrivateKey.generate()
            return private_key.sign(message)
    
    def _sign_via_hsm(self, message: bytes, key_id: str) -> bytes:
        """Placeholder para HSM real"""
        if self.hsm_type == 'thales':
            return self._sign_thales_luna(message, key_id)
        elif self.hsm_type == 'yubihsm':
            return self._sign_yubihsm(message, key_id)
        elif self.hsm_type == 'aws-kms':
            return self._sign_aws_kms(message, key_id)
        else:
            raise ValueError(f"Unsupported HSM type: {self.hsm_type}")
    
    def _sign_thales_luna(self, message: bytes, key_id: str) -> bytes:
        try:
            import PyKCS11
            lib = PyKCS11.PyKCS11Lib()
            lib.load(os.getenv('THALES_LUNA_SO', '/usr/lib/libcryptoki.so'))
            session = lib.openSession(self.hsm_slot)
            session.login(self.hsm_pin)
            
            private_keys = session.findObjects([
                (PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),
                (PyKCS11.CKA_LABEL, self.hsm_label)
            ])
            
            if not private_keys:
                raise RuntimeError(f"Key not found in HSM: {self.hsm_label}")
            
            signature = session.sign(private_keys[0], message, PyKCS11.Mechanism(PyKCS11.CKM_SHA256_RSA_PKCS))
            session.logout()
            session.closeSession()
            
            logger.info(f"✓ Signed with Thales Luna: {key_id}")
            return bytes(signature)
            
        except Exception as e:
            logger.error(f"Thales Luna error: {str(e)}")
            raise
    
    def _sign_yubihsm(self, message: bytes, key_id: str) -> bytes:
        try:
            from pyhsm.connector import Connector
            from pyhsm.hsm import YubiHsm
            
            with Connector() as connector:
                hsm = YubiHsm.create_session(
                    connector=connector,
                    authkey_id=1,
                    authkey=bytes.fromhex(os.getenv('YUBIHSM_AUTHKEY', '0'*32))
                )
                
                key_id_int = int(key_id, 16) if isinstance(key_id, str) else key_id
                signature = hsm.sign_ecdsa(key_id_int, message)
                
                logger.info(f"✓ Signed with YubiHSM: {key_id}")
                return signature
                
        except Exception as e:
            logger.error(f"YubiHSM error: {str(e)}")
            raise
    
    def _sign_aws_kms(self, message: bytes, key_id: str) -> bytes:
        try:
            import boto3
            
            kms = boto3.client('kms', region_name=os.getenv('AWS_REGION', 'us-east-1'))
            
            response = kms.sign(
                KeyId=key_id,
                Message=message,
                SigningAlgorithm='ECDSA_SHA_256'
            )
            
            logger.info(f"✓ Signed with AWS KMS: {key_id}")
            return response['Signature']
            
        except Exception as e:
            logger.error(f"AWS KMS error: {str(e)}")
            raise


hsm_adapter = HSMAdapter()
