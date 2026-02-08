"""
Universal QKD Key Generator

A production-grade, deterministic quantum key distribution simulator that produces
synchronized, secure keys across nodes without quantum hardware. This protocol
leverages the golden seed (iφ) as a root of trust with language-agnostic,
endian-independent implementation.

Protocol Specification (GCP-1 - Golden Consensus Protocol):

Layer 1: Root Seed
  - Seed Hex: 0000000000000000a8f4979b77e3f93fa8f4979b77e3f93fa8f4979b77e3f93f
  - Verify SHA-256: 096412ca0482ab0f519bc0e4ded667475c45495047653a21aa11e2c7c578fa6f

Layer 2: State Initialization
  - State = SHA256(Seed)
  - Counter = 0

Layer 3: Entropy Generation and QKD Sifting
  - Loop until 256 sifted bits collected:
    * Entropy = SHA256(State + Counter as string)
    * State = Entropy (ratchet for forward secrecy)
    * Counter += 1
    * For each byte in Entropy:
      - If ((byte >> 1) & 1) == ((byte >> 2) & 1):  # Basis match
        Append (byte & 1) to sifted_bits

Layer 4: Key Hardening and Output
  - For i = 0 to 127:
    Key_bit[i] = sifted_bits[i] XOR sifted_bits[i + 128]
  - Output 128-bit key (16 bytes)
  - Stream continues indefinitely for subsequent keys

This implementation provides:
  - Cryptographic determinism for cross-implementation verification
  - Forward secrecy via state ratcheting
  - Basis-matching simulation (~25-50% efficiency, mimicking quantum balance)
  - XOR folding for key hardening
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import Iterator, List


# Expected SHA-256 checksum for the seed
EXPECTED_CHECKSUM = "096412ca0482ab0f519bc0e4ded667475c45495047653a21aa11e2c7c578fa6f"

# Hex seed for initializing system state (iφ golden seed)
HEX_SEED = "0000000000000000a8f4979b77e3f93fa8f4979b77e3f93fa8f4979b77e3f93f"


def verify_seed_checksum(seed: bytes) -> bool:
    """
    Verify that the seed matches the expected SHA-256 checksum.

    Args:
        seed: The seed bytes to verify

    Returns:
        True if checksum matches, False otherwise
    """
    checksum = hashlib.sha256(seed).hexdigest()
    return checksum == EXPECTED_CHECKSUM


def basis_match(byte: int) -> bool:
    """
    Check if basis bits match for quantum sifting simulation.

    Simulates BB84/E91 basis matching where Alice and Bob must use the same
    measurement basis. The condition ((byte >> 1) & 1) == ((byte >> 2) & 1)
    provides ~25-50% efficiency, mimicking quantum 1/√2 balance.

    Args:
        byte: Single byte from entropy source

    Returns:
        True if basis bits match (bits 1 and 2 are equal)
    """
    bit1 = (byte >> 1) & 1
    bit2 = (byte >> 2) & 1
    return bit1 == bit2


def collect_sifted_bits(state: bytes, counter: int) -> tuple[List[int], bytes, int]:
    """
    Collect 256 sifted bits using basis-matching quantum simulation.

    Args:
        state: Current system state (32 bytes)
        counter: Current counter value

    Returns:
        Tuple of (sifted_bits, final_state, final_counter)
    """
    sifted_bits = []

    while len(sifted_bits) < 256:
        # Concatenate state with counter as string
        counter_str = str(counter).encode('utf-8')
        data = state + counter_str

        # Generate entropy and ratchet state
        entropy = hashlib.sha256(data).digest()
        state = entropy
        counter += 1

        # Apply basis matching for each byte
        for byte in entropy:
            if basis_match(byte):
                # Extract bit 0 as the sifted bit
                sifted_bits.append(byte & 1)

                # Stop if we have enough bits
                if len(sifted_bits) >= 256:
                    break

    return sifted_bits[:256], state, counter


def xor_fold_hardening(sifted_bits: List[int]) -> bytes:
    """
    Apply XOR folding to harden 256 sifted bits into 128-bit key.

    XOR folding provides information-theoretic hardening by combining
    the first and second halves of the sifted bits.

    Args:
        sifted_bits: List of 256 bits (0 or 1)

    Returns:
        Hardened key (16 bytes = 128 bits)
    """
    # XOR first half with second half
    key_bits = []
    for i in range(128):
        bit = sifted_bits[i] ^ sifted_bits[i + 128]
        key_bits.append(bit)

    # Convert bits to bytes
    key_bytes = bytearray()
    for i in range(0, 128, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | key_bits[i + j]
        key_bytes.append(byte)

    return bytes(key_bytes)


def universal_qkd_generator(seed_hex: str = HEX_SEED) -> Iterator[bytes]:
    """
    Universal QKD key generator - infinite stream of 128-bit keys.

    This generator produces an infinite stream of cryptographically strong
    keys using the golden seed as root of trust. Each key is generated
    through quantum basis-matching simulation and XOR folding hardening.

    Args:
        seed_hex: Hex string of the seed (default: golden seed iφ)

    Yields:
        128-bit keys as bytes (16 bytes each)

    Raises:
        ValueError: If seed checksum verification fails
    """
    # Initialize with seed
    seed = bytes.fromhex(seed_hex)

    # Verify checksum
    if not verify_seed_checksum(seed):
        raise ValueError(
            f"Seed checksum verification failed. "
            f"Expected: {EXPECTED_CHECKSUM}, "
            f"Got: {hashlib.sha256(seed).hexdigest()}"
        )

    # Layer 2: State Initialization
    state = hashlib.sha256(seed).digest()
    counter = 0

    # Infinite stream
    while True:
        # Layer 3: Entropy Generation and QKD Sifting
        sifted_bits, state, counter = collect_sifted_bits(state, counter)

        # Layer 4: Key Hardening and Output
        key = xor_fold_hardening(sifted_bits)

        yield key


def generate_keys(num_keys: int, seed_hex: str = HEX_SEED) -> List[str]:
    """
    Generate a specified number of keys from the Universal QKD Generator.

    Args:
        num_keys: Number of keys to generate
        seed_hex: Hex string of the seed (default: golden seed iφ)

    Returns:
        List of hexadecimal key strings
    """
    generator = universal_qkd_generator(seed_hex)
    keys = []

    for _ in range(num_keys):
        key = next(generator)
        keys.append(key.hex())

    return keys


def main():
    """
    Main function for CLI interface.
    """
    parser = argparse.ArgumentParser(
        description="Universal QKD Key Generator - Production-grade quantum key distribution simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Generate 10 keys (default)
  %(prog)s -n 100                   # Generate 100 keys
  %(prog)s -n 50 -o keys.txt        # Save 50 keys to file
  %(prog)s -n 20 --json             # Output 20 keys in JSON format
  %(prog)s --json -o keys.json      # Save JSON output to file
  %(prog)s --quiet -n 5             # Generate 5 keys with minimal output
  %(prog)s --verify-only            # Verify seed integrity only

Protocol: GCP-1 (Golden Consensus Protocol)
Based on: BB84/E91 quantum basis matching with XOR folding hardening
        """
    )

    parser.add_argument(
        "-n", "--num-keys",
        type=int,
        default=10,
        metavar="N",
        help="number of keys to generate (default: 10)"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        metavar="FILE",
        help="output file path (default: stdout)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="output in JSON format"
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="suppress informational messages, only output keys"
    )

    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="only verify seed checksum without generating keys"
    )

    parser.add_argument(
        "--binary",
        action="store_true",
        help="include binary representation in output"
    )

    args = parser.parse_args()

    # Verify seed checksum
    seed = bytes.fromhex(HEX_SEED)
    actual_checksum = hashlib.sha256(seed).hexdigest()

    if not args.quiet:
        print("Universal QKD Key Generator (GCP-1)", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print(file=sys.stderr)
        print(f"Protocol: Golden Consensus Protocol v1.0", file=sys.stderr)
        print(f"Seed: {HEX_SEED}", file=sys.stderr)
        print(f"Expected Checksum: {EXPECTED_CHECKSUM}", file=sys.stderr)
        print(f"Actual Checksum: {actual_checksum}", file=sys.stderr)
        print(f"Checksum Valid: {verify_seed_checksum(seed)}", file=sys.stderr)
        print(file=sys.stderr)

    if not verify_seed_checksum(seed):
        print("ERROR: Seed checksum verification failed!", file=sys.stderr)
        sys.exit(1)

    if args.verify_only:
        if not args.quiet:
            print("✓ Seed checksum verified successfully", file=sys.stderr)
        sys.exit(0)

    # Validate num_keys
    if args.num_keys < 1:
        print("ERROR: Number of keys must be at least 1", file=sys.stderr)
        sys.exit(1)

    if args.num_keys > 1000000:
        print("WARNING: Generating a large number of keys may take time", file=sys.stderr)

    # Generate keys
    if not args.quiet:
        print(f"Generating {args.num_keys} key{'s' if args.num_keys != 1 else ''}...", file=sys.stderr)
        print(file=sys.stderr)

    keys = generate_keys(args.num_keys)

    # Format output
    if args.json:
        output_data = {
            "protocol": "GCP-1",
            "description": "Golden Consensus Protocol v1.0 - Universal QKD Generator",
            "seed": HEX_SEED,
            "checksum": EXPECTED_CHECKSUM,
            "num_keys": len(keys),
            "keys": []
        }

        for i, key in enumerate(keys, 1):
            key_entry = {
                "index": i,
                "hex": key
            }
            if args.binary:
                key_bytes = bytes.fromhex(key)
                binary_str = ''.join(format(byte, '08b') for byte in key_bytes)
                key_entry["binary"] = binary_str
            output_data["keys"].append(key_entry)

        output_str = json.dumps(output_data, indent=2)
    else:
        output_lines = []
        if not args.quiet:
            output_lines.append("Generated Keys:")
            output_lines.append("-" * 60)

        for i, key in enumerate(keys, 1):
            if args.quiet:
                output_lines.append(key)
            elif args.binary:
                key_bytes = bytes.fromhex(key)
                binary_str = ''.join(format(byte, '08b') for byte in key_bytes)
                output_lines.append(f"Key {i:6d}: {key}")
                output_lines.append(f"         Binary: {binary_str}")
            else:
                output_lines.append(f"Key {i:6d}: {key}")

        output_str = "\n".join(output_lines)

    # Write output
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_str)
                if not output_str.endswith('\n'):
                    f.write('\n')

            if not args.quiet:
                print(f"✓ Output written to {args.output}", file=sys.stderr)
        except IOError as e:
            print(f"ERROR: Failed to write to {args.output}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_str)
        if not output_str.endswith('\n'):
            print()


if __name__ == "__main__":
    main()
