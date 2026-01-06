# -*- coding: utf-8 -*-
"""
Cryptographic Hashing Utilities

Provides SHA-256 hashing with extension points for other algorithms.
"""

import hashlib
import json
from typing import Any, Dict


def compute_scenario_hash(data: Dict[str, Any], algorithm: str = 'sha256') -> str:
    """
    Compute cryptographic hash of scenario data.
    
    Uses canonical JSON serialization (sorted keys, deterministic).
    
    Args:
        data: Dictionary to hash
        algorithm: Hash algorithm (default: 'sha256', extension point for others)
    
    Returns:
        Hexadecimal hash string
    """
    if algorithm != 'sha256':
        raise ValueError(f"Only 'sha256' is currently supported, got: {algorithm}")
    
    # Canonical JSON serialization: sorted keys, no whitespace
    canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
    
    # Compute SHA-256 hash
    hash_obj = hashlib.sha256(canonical_json.encode('utf-8'))
    
    return hash_obj.hexdigest()


def compute_transaction_hash(transaction_dict: Dict[str, Any]) -> str:
    """
    Compute hash of a transaction dictionary.
    
    Args:
        transaction_dict: Transaction data dictionary
    
    Returns:
        Hexadecimal hash string
    """
    return compute_scenario_hash(transaction_dict)

