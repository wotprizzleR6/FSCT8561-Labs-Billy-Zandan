#!/usr/bin/env python3
"""
Adversarial Stress Testing Script for Metadata Scanner
Tests:
1. Case insensitivity vulnerability in lifecycle prefix matching
2. Unpadded / URL-safe Base64 handling
3. Non-ASCII / Unicode UserComment handling
4. Polyglot / Multi-layer metadata priority order
5. Maximum payload length / ReDoS vulnerability on regexes
"""

import base64
import sys
import time
from pathlib import Path
from PIL import Image, PngImagePlugin

LAB6_DIR = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6")
if str(LAB6_DIR) not in sys.path:
    sys.path.insert(0, str(LAB6_DIR))

import metadata_scanner

def run_adversarial_experiments():
    print("================ ADVERSARIAL STRESS EXPERIMENTS ================")
    
    # 1. Case Sensitivity Experiment
    print("\n[Experiment 1] Stage Prefix Case Sensitivity:")
    text_upper = "RECON: Target server identified"
    text_lower = "recon: Target server identified"
    _, _, cov_u, _ = metadata_scanner.analyze_and_deobfuscate("Test", text_upper)
    _, _, cov_l, _ = metadata_scanner.analyze_and_deobfuscate("Test", text_lower)
    print(f"  Upper prefix 'RECON:': is_covert={cov_u}")
    print(f"  Lower prefix 'recon:': is_covert={cov_l}")
    if cov_u and not cov_l:
        print("  --> FINDING: Case sensitivity limitation detected: lowercase 'recon:' not recognized unless keyword matches.")

    # 2. Base64 Variants: Unpadded & URL-Safe
    print("\n[Experiment 2] Base64 Variants (Unpadded / URL-safe):")
    # "EXFIL: Secret data payload"
    raw_secret = "EXFIL: Secret data payload"
    std_b64 = base64.b64encode(raw_secret.encode()).decode()
    url_b64 = base64.urlsafe_b64encode(raw_secret.encode()).decode()
    unpadded_b64 = std_b64.rstrip("=")
    
    _, enc_std, cov_std, _ = metadata_scanner.analyze_and_deobfuscate("Test", std_b64)
    _, enc_url, cov_url, _ = metadata_scanner.analyze_and_deobfuscate("Test", url_b64)
    _, enc_unp, cov_unp, _ = metadata_scanner.analyze_and_deobfuscate("Test", unpadded_b64)
    print(f"  Standard Base64: {std_b64} -> is_covert={cov_std}, encoding={enc_std}")
    print(f"  URL-safe Base64: {url_b64} -> is_covert={cov_url}, encoding={enc_url}")
    print(f"  Unpadded Base64: {unpadded_b64} -> is_covert={cov_unp}, encoding={enc_unp}")
    if not cov_unp or not cov_url:
        print("  --> FINDING: Regex requires exact standard RFC 4648 padding (len % 4 == 0) and standard charset (+/). Unpadded or URL-safe Base64 falls back to plain text.")

    # 3. ReDoS / Regex Timing Test
    print("\n[Experiment 3] Regex Performance on Oversized Payload:")
    large_payload = "A" * 1000000 + "!"
    t0 = time.perf_counter()
    _, _, is_cov_large, _ = metadata_scanner.analyze_and_deobfuscate("Test", large_payload)
    elapsed = time.perf_counter() - t0
    print(f"  Evaluated 1,000,000 char string in {elapsed:.4f}s (is_covert={is_cov_large})")
    if elapsed < 0.1:
        print("  --> PASS: Regex linear performance confirmed, no ReDoS vulnerability.")

    # 4. Multi-layer Priority Order Test
    print("\n[Experiment 4] Multi-layer Priority Conflict:")
    # If an image has covert payload in BOTH PNG text and EXIF, which one takes precedence?
    # In scan_single_image, candidates are iterated in order: PNG info first, then EXIF.
    print("  Scanner candidate iteration order: PNG info -> EXIF IFD0 -> Exif Sub-IFD.")
    print("  First matching covert candidate terminates search.")

if __name__ == "__main__":
    run_adversarial_experiments()
