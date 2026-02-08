"""
GoldenSeed - Deterministic High-Entropy Byte Streams

⚠️ NOT FOR CRYPTOGRAPHY: This library generates deterministic pseudo-random
streams and must NOT be used for cryptographic purposes.

This package provides deterministic stream generation for:
- Procedural content generation (games, simulations)
- Reproducible test data and fixtures
- Deterministic noise functions
- Consensus randomness in distributed systems
- Space-efficient storage of procedural content

Core Implementations:
- Universal stream generator with deterministic output
- Test vector generation for cross-platform validation
- Golden ratio-based deterministic sequences
- Commercial licensing watermarking system

Example Usage:
    >>> from gq import UniversalQKD, GQS1
    >>>
    >>> # Generate deterministic byte streams
    >>> generator = UniversalQKD()
    >>> stream = next(generator)
    >>> print(stream.hex())
    '3c732e0d04dac163a5cc2b15c7caf42c'
    >>>
    >>> # Generate test vectors
    >>> vectors = GQS1.generate_test_vectors(10)
    >>> print(vectors[0])
    'a01611f01e8207a27c1529c3650c4838'
"""

from .universal_qkd import (
    universal_qkd_generator as UniversalQKD,
    generate_keys as generate_universal_keys,
    HEX_SEED,
    EXPECTED_CHECKSUM,
    GOLDEN_RATIO,
    PI,
    E,
    SQRT2,
    GOLDEN_RATIO_HEX,
    PI_HEX,
    E_HEX,
    SQRT2_HEX,
)

from .gqs1 import (
    generate_test_vectors as generate_gqs1_vectors,
    GQS1,
)

from .golden_ratio_coin_flip import (
    GoldenRatioCoinFlip,
    EquidistributionValidator,
    CoinFlipValidator,
    QuasirandomnessValidator,
    PerformanceMetricsValidator,
    fractional_part,
    comprehensive_validation,
    PHI,
)

from .watermark import (
    WatermarkData,
    WatermarkError,
    encode_watermark,
    decode_watermark,
    embed_watermark_in_binary,
    extract_watermark_from_binary,
    check_watermark_present,
)

__all__ = [
    "UniversalQKD",
    "generate_universal_keys",
    "GQS1",
    "generate_gqs1_vectors",
    "HEX_SEED",
    "EXPECTED_CHECKSUM",
    # Mathematical constants
    "GOLDEN_RATIO",
    "PI",
    "E",
    "SQRT2",
    "GOLDEN_RATIO_HEX",
    "PI_HEX",
    "E_HEX",
    "SQRT2_HEX",
    # Golden Ratio sequences
    "GoldenRatioCoinFlip",
    "EquidistributionValidator",
    "CoinFlipValidator",
    "QuasirandomnessValidator",
    "PerformanceMetricsValidator",
    "fractional_part",
    "comprehensive_validation",
    "PHI",
    # Watermarking for commercial licensing
    "WatermarkData",
    "WatermarkError",
    "encode_watermark",
    "decode_watermark",
    "embed_watermark_in_binary",
    "extract_watermark_from_binary",
    "check_watermark_present",
]

__version__ = "3.0.0"
__author__ = "beanapologist"
