"""
Golden Quantum Standard (GQS-1) Implementation

This module implements the GQS-1 protocol for generating deterministic
test vectors using hash-based key derivation.

Protocol Overview:
1. Initialize system state S_0 with hex seed
2. Verify SHA-256 checksum
3. Use Hash-DRBG ratchet: S_{n+1} = SHA-256(S_n || Counter)
   (where || denotes concatenation)
4. Apply XOR folding for key hardening (256 bits -> 128 bits)
5. Output keys as hexadecimal strings

Mathematical Operations:
- Hash ratchet: Applies SHA-256 to concatenation of state and counter
- XOR folding: Splits output into two halves and XORs them together
  Result[i] = FirstHalf[i] XOR SecondHalf[i] for i = 0 to 127
  This provides information-theoretic security by combining entropy
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import List


# Expected SHA-256 checksum for the seed
EXPECTED_CHECKSUM = "096412ca0482ab0f519bc0e4ded667475c45495047653a21aa11e2c7c578fa6f"

# Hex seed for initializing system state S_0
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


def hash_drbg_ratchet(state: bytes, counter: int) -> bytes:
    """
    Hash-DRBG ratchet function: S_{n+1} = SHA-256(S_n || Counter)
    
    This function implements a forward-secure state progression using
    cryptographic hashing. The state is updated by hashing the concatenation
    of the current state and a counter value.
    
    Args:
        state: Current state S_n (32 bytes)
        counter: Counter value (encoded as 4-byte big-endian)
        
    Returns:
        Next state S_{n+1} (32 bytes)
    """
    counter_bytes = counter.to_bytes(4, byteorder='big')
    combined = state + counter_bytes  # Concatenate state and counter
    return hashlib.sha256(combined).digest()


def simulate_quantum_sifting(raw_bits: bytes) -> bytes:
    """
    Pass through the hash output for deterministic key generation.
    
    In a real quantum key distribution system, Alice and Bob would randomly
    choose measurement bases and discard bits where their bases don't match.
    This creates the "sifted key" from raw quantum measurements.
    
    For deterministic test vectors in GQS-1, we skip this probabilistic
    step and use the full hash output directly. The XOR folding step
    provides the necessary key hardening.
    
    Args:
        raw_bits: Raw bits from DRBG (32 bytes = 256 bits)
        
    Returns:
        Output bits (32 bytes) - passed through unchanged for deterministic behavior
    """
    # For deterministic test vectors, we use all bits from the DRBG output
    # The XOR folding step provides information-theoretic hardening
    return raw_bits


def xor_fold_hardening(bits: bytes) -> bytes:
    """
    Apply XOR folding to compress 256 bits into 128 bits with hardening.
    
    XOR folding provides information-theoretic security by combining
    two halves of the input:
    - Split 256 bits into two 128-bit halves: A and B
    - Compute C = A XOR B
    - Output C as the hardened 128-bit key
    
    This operation ensures that an attacker needs to compromise both
    halves to reconstruct information, providing key hardening.
    
    Mathematical formula:
    For i = 0 to 15 (bytes):
        result[i] = first_half[i] XOR second_half[i]
    
    Args:
        bits: Input bits (32 bytes = 256 bits)
        
    Returns:
        Hardened key (16 bytes = 128 bits)
    """
    half_len = len(bits) // 2
    first_half = bits[:half_len]   # First 128 bits
    second_half = bits[half_len:]  # Second 128 bits
    
    # XOR the two halves byte by byte
    hardened = bytes(a ^ b for a, b in zip(first_half, second_half))
    return hardened


def generate_key(state: bytes, counter: int) -> tuple[bytes, bytes]:
    """
    Generate a single hardened 128-bit key from the current state.
    
    Process:
    1. Apply Hash-DRBG ratchet to advance state: S_{n+1} = SHA-256(S_n || Counter)
    2. Use the new state as 256-bit intermediate material
    3. Apply XOR folding to compress to 128 bits: key = first_half XOR second_half
    
    Args:
        state: Current system state (32 bytes)
        counter: Counter for this key generation
        
    Returns:
        Tuple of (hardened_key, next_state)
    """
    # Apply Hash-DRBG ratchet to get next state
    next_state = hash_drbg_ratchet(state, counter)
    
    # Pass through for deterministic behavior (no probabilistic sifting)
    output_bits = simulate_quantum_sifting(next_state)
    
    # Apply XOR folding to compress 256 bits to 128 bits
    hardened_key = xor_fold_hardening(output_bits)
    
    return hardened_key, next_state


def generate_test_vectors(num_keys: int = 10) -> List[str]:
    """
    Generate the first N test vectors for GQS-1 compliance testing.
    
    Args:
        num_keys: Number of keys to generate (default: 10)
        
    Returns:
        List of hexadecimal key strings
    """
    # Initialize system state S_0 with the hex seed
    seed = bytes.fromhex(HEX_SEED)
    
    # Verify checksum
    if not verify_seed_checksum(seed):
        raise ValueError(
            f"Seed checksum verification failed. "
            f"Expected: {EXPECTED_CHECKSUM}, "
            f"Got: {hashlib.sha256(seed).hexdigest()}"
        )
    
    # Initialize state
    state = seed
    test_vectors = []
    
    # Generate keys
    for counter in range(1, num_keys + 1):
        key, state = generate_key(state, counter)
        test_vectors.append(key.hex())
    
    return test_vectors


def main():
    """
    Main function to generate and display test vectors.
    """
    parser = argparse.ArgumentParser(
        description="Generate GQS-1 compliant test vectors for quantum key distribution testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Generate 10 test vectors (default)
  %(prog)s -n 100                   # Generate 100 test vectors
  %(prog)s -n 50 -o vectors.txt     # Save 50 vectors to file
  %(prog)s -n 20 --json             # Output 20 vectors in JSON format
  %(prog)s --json -o vectors.json   # Save JSON output to file
  %(prog)s --quiet -n 5             # Generate 5 vectors with minimal output
        """
    )

    parser.add_argument(
        "-n", "--num-keys",
        type=int,
        default=10,
        metavar="N",
        help="number of test vectors to generate (default: 10)"
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
        help="suppress informational messages, only output vectors"
    )

    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="only verify seed checksum without generating vectors"
    )

    args = parser.parse_args()

    # Verify seed checksum
    seed = bytes.fromhex(HEX_SEED)
    actual_checksum = hashlib.sha256(seed).hexdigest()

    if not args.quiet:
        print("Golden Quantum Standard (GQS-1) Test Vector Generation", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print(file=sys.stderr)
        print(f"Hex Seed: {HEX_SEED}", file=sys.stderr)
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

    # Generate test vectors
    if not args.quiet:
        print(f"Generating {args.num_keys} test vector{'s' if args.num_keys != 1 else ''}...", file=sys.stderr)
        print(file=sys.stderr)

    test_vectors = generate_test_vectors(args.num_keys)

    # Format output
    if args.json:
        output_data = {
            "protocol": "GQS-1",
            "seed": HEX_SEED,
            "checksum": EXPECTED_CHECKSUM,
            "num_vectors": len(test_vectors),
            "vectors": test_vectors
        }
        output_str = json.dumps(output_data, indent=2)
    else:
        output_lines = []
        if not args.quiet:
            output_lines.append("Test Vectors:")
            output_lines.append("-" * 60)

        for i, key in enumerate(test_vectors, 1):
            if args.quiet:
                output_lines.append(key)
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
