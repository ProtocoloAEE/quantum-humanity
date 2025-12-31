# src/aee/infrastructure/security.py
# VALIDACIÓN DE API KEY

from fastapi import HTTPException, status, Header
from typing import Optional, Dict, Any
import os

class APIKeyManager:
    """Gestión de API Keys"""
    
    def __init__(self):
        self.api_keys = {
            os.getenv('API_KEY_DEV', 'aee-dev-key-2025'): {
                'name': 'Development',
                'operations': ['CERTIFY', 'VERIFY', 'BATCH_CERTIFY', 'REPORT'],
                'rate_limit': 1000
            },
            os.getenv('API_KEY_PROD', 'aee-prod-key-2025'): {
                'name': 'Production',
                'operations': ['CERTIFY', 'VERIFY', 'BATCH_CERTIFY', 'REPORT', 'REVOKE', 'AUDIT'],
                'rate_limit': 10000
            }
        }
    
    def validate(self, api_key: str) -> Optional[Dict[str, Any]]:
        return self.api_keys.get(api_key)


api_key_manager = APIKeyManager()


async def verify_api_key(
    x_api_key: str = Header(..., description="API Key")
) -> Dict[str, Any]:
    """Dependency: Verificar API Key"""
    client_info = api_key_manager.validate(x_api_key)
    if not client_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return client_info
