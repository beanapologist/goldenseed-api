"""
GQS-1 (Golden Quantum Standard) - Test Vector Generation

Wrapper module providing class-based interface for GQS-1 protocol.
"""

from .gqs1_core import (
    HEX_SEED,
    EXPECTED_CHECKSUM,
    verify_seed_checksum,
    hash_drbg_ratchet,
    simulate_quantum_sifting,
    xor_fold_hardening,
    generate_key,
    generate_test_vectors,
)


class GQS1:
    """
    GQS-1 Protocol Implementation

    Provides test vector generation for quantum key distribution compliance testing.
    """

    SEED = HEX_SEED
    CHECKSUM = EXPECTED_CHECKSUM

    @staticmethod
    def generate_test_vectors(num_vectors: int = 10):
        """Generate GQS-1 compliant test vectors."""
        return generate_test_vectors(num_vectors)

    @staticmethod
    def verify_seed():
        """Verify seed checksum."""
        import hashlib
        seed = bytes.fromhex(HEX_SEED)
        return verify_seed_checksum(seed)


__all__ = [
    "GQS1",
    "generate_test_vectors",
    "HEX_SEED",
    "EXPECTED_CHECKSUM",
]
