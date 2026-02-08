#!/usr/bin/env python3
"""
Golden Ratio Coin Flip CLI

Command-line interface for generating and validating golden ratio coin flips.
"""

import argparse
import sys
from typing import List

from ..golden_ratio_coin_flip import (
    GoldenRatioCoinFlip,
    comprehensive_validation,
    PHI,
)


def format_flips(flips: List[int], format: str = 'binary') -> str:
    """Format coin flips for output."""
    if format == 'binary':
        return ''.join(str(f) for f in flips)
    elif format == 'text':
        return ''.join('H' if f == 0 else 'T' for f in flips)
    elif format == 'list':
        return ', '.join(str(f) for f in flips)
    else:
        return str(flips)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Golden Ratio Coin Flip - Generate perfect coin flips using {Z*phi}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -n 100                     # Generate 100 coin flips
  %(prog)s -n 1000 --format text      # Generate 1000 flips as H/T
  %(prog)s --validate                 # Run comprehensive validation
  %(prog)s -n 50 --show-fracs         # Show fractional values too
  %(prog)s -n 10000 -o flips.txt      # Save to file
        """
    )

    parser.add_argument(
        '-n', '--num-flips',
        type=int,
        default=100,
        metavar='N',
        help='number of coin flips to generate (default: 100)'
    )

    parser.add_argument(
        '--format',
        choices=['binary', 'text', 'list'],
        default='binary',
        help='output format: binary (01), text (HT), or list (default: binary)'
    )

    parser.add_argument(
        '--show-fracs',
        action='store_true',
        help='also show fractional values {Z*phi}'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='run comprehensive validation tests'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        metavar='FILE',
        help='output file path (default: stdout)'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='suppress informational messages'
    )

    args = parser.parse_args()

    if not args.quiet:
        print("Golden Ratio Coin Flip", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print(f"phi = {PHI:.15f}", file=sys.stderr)
        print(file=sys.stderr)

    if args.validate:
        if not args.quiet:
            print("Running comprehensive validation...", file=sys.stderr)
            print(file=sys.stderr)

        result = comprehensive_validation(10000)

        print("Validation Results:", file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        eq = result['equidistribution']
        print(f"Equidistribution (KS): {'✓' if eq['ks_test']['passed'] else '✗'} "
              f"(D={eq['ks_test']['ks_statistic']:.6f})", file=sys.stderr)
        print(f"Equidistribution (χ²): {'✓' if eq['chi_square']['passed'] else '✗'} "
              f"(χ²={eq['chi_square']['chi_square']:.2f})", file=sys.stderr)

        cf = result['coin_flip_fairness']
        print(f"Fair Coin Flip: {'✓' if cf['balance']['passed'] else '✗'} "
              f"(ratio={cf['balance']['heads_ratio']:.6f})", file=sys.stderr)

        qr = result['quasirandomness']
        print(f"Low Discrepancy: {'✓' if qr['discrepancy']['low_discrepancy'] else '✗'} "
              f"(D*={qr['discrepancy']['star_discrepancy']:.6f})", file=sys.stderr)

        print(file=sys.stderr)
        if result['overall_passed']:
            print("✓ All validations PASSED", file=sys.stderr)
        else:
            print("✗ Some validations failed (see details above)", file=sys.stderr)

        return 0

    # Generate coin flips
    if not args.quiet:
        print(f"Generating {args.num_flips} coin flips...", file=sys.stderr)
        print(file=sys.stderr)

    generator = GoldenRatioCoinFlip()
    flips = generator.generate_sequence(args.num_flips)

    output_lines = []

    if args.show_fracs:
        fracs = generator.generate_fractional_sequence(args.num_flips)
        output_lines.append("Z\tFractional\tCoin")
        output_lines.append("-" * 40)
        for z in range(1, min(args.num_flips + 1, 51)):  # Show first 50
            output_lines.append(f"{z}\t{fracs[z-1]:.6f}\t{flips[z-1]}")
        if args.num_flips > 50:
            output_lines.append("...")
        output_lines.append("")

    # Format flips
    formatted = format_flips(flips, args.format)

    if not args.quiet and not args.show_fracs:
        output_lines.append("Coin Flips:")
        output_lines.append("-" * 60)

    if args.format == 'binary':
        # Break into lines of 80 characters
        for i in range(0, len(formatted), 80):
            output_lines.append(formatted[i:i+80])
    else:
        output_lines.append(formatted)

    if not args.quiet:
        output_lines.append("")
        heads = sum(1 for f in flips if f == 0)
        tails = len(flips) - heads
        output_lines.append(f"Statistics:")
        output_lines.append(f"  Heads: {heads} ({heads/len(flips)*100:.2f}%)")
        output_lines.append(f"  Tails: {tails} ({tails/len(flips)*100:.2f}%)")

    output_str = "\n".join(output_lines)

    # Write output
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_str)
                if not output_str.endswith('\n'):
                    f.write('\n')

            if not args.quiet:
                print(f"\n✓ Output written to {args.output}", file=sys.stderr)
        except IOError as e:
            print(f"ERROR: Failed to write to {args.output}: {e}", file=sys.stderr)
            return 1
    else:
        print(output_str)

    return 0


if __name__ == '__main__':
    sys.exit(main())
