"""
AEE Protocol Core - Deterministic Integrity Anchor
Handles generation and verification of integrity anchors
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path


class AEEProtocol:
    """
    AEE Protocol: Deterministic Integrity Anchor for Critical Data & AI Pipelines
    
    Purpose:
    - Generate cryptographic anchors for files and datasets
    - Verify file integrity without exposing data to external systems
    - Maintain deterministic, reproducible results across platforms
    """
    
    def __init__(self):
        self.algorithm = "sha256"
        self.version = "1.2.1"
    
    def generate(self, filepath: str, user: str = "system", metadata: dict = None) -> dict:
        """
        Generate an integrity anchor for a file.
        
        Args:
            filepath: Path to the file to hash
            user: User identifier (for audit trail)
            metadata: Additional metadata to include in anchor
            
        Returns:
            dict: Contains anchor hash, status, timestamp, metadata
        """
        
        # Validate file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Read file and compute hash
        file_hash = self._compute_hash(filepath)
        
        # Get file metadata
        filesize = os.path.getsize(filepath)
        filename = os.path.basename(filepath)
        
        # Construct anchor metadata
        anchor_metadata = {
            "filename": filename,
            "filesize": filesize,
            "user": user,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        if metadata:
            anchor_metadata.update(metadata)
        
        # Return structured anchor
        return {
            "anchor": file_hash,
            "status": "GENERATED",
            "metadata": anchor_metadata,
            "algorithm": self.algorithm,
            "version": self.version
        }
    
    def verify(self, filepath: str, anchor: str) -> dict:
        """
        Verify file integrity against a previously generated anchor.
        
        Args:
            filepath: Path to the file to verify
            anchor: Previously generated anchor hash
            
        Returns:
            dict: Verification result with status and details
        """
        
        # Validate file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Compute current hash
        current_hash = self._compute_hash(filepath)
        
        # Compare hashes
        is_valid = current_hash == anchor
        
        return {
            "verified": is_valid,
            "current_anchor": current_hash,
            "expected_anchor": anchor,
            "status": "VERIFIED" if is_valid else "MISMATCH",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def _compute_hash(self, filepath: str) -> str:
        """
        Compute SHA-256 hash of file with deterministic serialization.
        
        Uses binary concatenation (0x00 separator) for cross-platform consistency.
        """
        hasher = hashlib.sha256()
        
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def batch_generate(self, filepath_list: list, user: str = "system") -> list:
        """
        Generate anchors for multiple files.
        
        Args:
            filepath_list: List of file paths
            user: User identifier for audit trail
            
        Returns:
            list: List of anchor dictionaries
        """
        results = []
        for filepath in filepath_list:
            try:
                result = self.generate(filepath, user=user)
                results.append(result)
            except FileNotFoundError as e:
                results.append({
                    "error": str(e),
                    "filepath": filepath,
                    "status": "FAILED"
                })
        return results