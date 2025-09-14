#!/usr/bin/env python3
"""
Generate SemID from text and output it in a format usable by Solidity scripts
"""

import sys
import os

# Add the meanhash module to the path
sys.path.append('/Users/tanbajintaro/sentence_match/meanhash')

from gold import SemID

def generate_semid(text: str) -> str:
    """Generate SemID from text and return it as hex string"""
    semid_instance = SemID()
    semid_value = semid_instance.id24(text)
    semid_hex = semid_instance.id_hex(text)

    print(f"Text: '{text}'")
    print(f"SemID (decimal): {semid_value}")
    print(f"SemID (hex): {semid_hex}")

    # Convert to 32-byte format for Solidity
    semid_bytes32 = semid_value.to_bytes(32, 'big').hex()
    print(f"SemID (bytes32): 0x{semid_bytes32}")

    return semid_bytes32

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_semid.py 'your text here'")
        sys.exit(1)

    text = sys.argv[1]
    semid_bytes32 = generate_semid(text)

    # Output in a format that can be used in Solidity scripts
    print(f"\n// Solidity usage:")
    print(f"bytes32 salt = hex\"{semid_bytes32}\";")
    print(f"// or")
    print(f"bytes32 salt = 0x{semid_bytes32};")
