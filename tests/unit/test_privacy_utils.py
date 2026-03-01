"""
Unit tests for privacy utilities
"""
from app.utils import hash_address, hash_ip, hash_transaction


def test_hash_address():
    """Test address hashing"""
    address = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
    hashed = hash_address(address)

    assert len(hashed) == 8
    assert isinstance(hashed, str)
    assert hashed != address  # Should be different


def test_hash_address_consistency():
    """Test that same address produces same hash"""
    address = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
    hash1 = hash_address(address)
    hash2 = hash_address(address)

    assert hash1 == hash2


def test_hash_address_different():
    """Test that different addresses produce different hashes"""
    addr1 = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
    addr2 = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"

    hash1 = hash_address(addr1)
    hash2 = hash_address(addr2)

    assert hash1 != hash2


def test_hash_ip():
    """Test IP hashing"""
    ip = "192.168.1.1"
    hashed = hash_ip(ip)

    assert len(hashed) == 64  # Full SHA-256 hash for IP
    assert hashed != ip


def test_hash_transaction():
    """Test transaction hash truncation"""
    tx_hash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    hashed = hash_transaction(tx_hash)

    assert len(hashed) == 8  # Truncated to 8 characters
    assert hashed != tx_hash
