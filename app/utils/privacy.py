"""
Privacy utility functions for hashing sensitive data
"""
import hashlib


def hash_address(address: str) -> str:
    """
    Hash wallet address and truncate to 8 characters.

    Args:
        address: Wallet address (e.g., Ethereum address)

    Returns:
        Truncated hash of the address (8 characters)
    """
    full_hash = hashlib.sha256(address.encode()).hexdigest()
    return full_hash[:8]


def hash_ip(ip: str) -> str:
    """
    Hash IP address for anonymization.

    Args:
        ip: IP address string

    Returns:
        Hashed IP address
    """
    return hashlib.sha256(ip.encode()).hexdigest()


def hash_transaction(tx_hash: str) -> str:
    """
    Hash transaction hash and truncate.

    Args:
        tx_hash: Transaction hash

    Returns:
        Truncated hash (8 characters)
    """
    full_hash = hashlib.sha256(tx_hash.encode()).hexdigest()
    return full_hash[:8]
