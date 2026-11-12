# FSCT 8561 — Lab 8 / Lab 9: Cryptography Fundamentals
**Course**: FSCT 8561 - Security Applications  
**Instructor**: Dr. Maryam R. Aliabadi  
**Student Name**: Billy Zandan  
**Deliverable**: Lab Answers Document (`Lab9_Answers.md`)  
**Grading Rubric**: 100 Marks Total (Parts A–F)  

---

## Executive Summary & Scenario Context
As a Junior Security Engineer at CipherCorp, this audit evaluates the cryptographic primitives securing the company's legacy vault system. The following report documents experimental findings, code modifications, vulnerability assessments, and remediation strategies covering hashing, block ciphers, key derivation, and authenticated encryption.

---

## Part A: Hash Functions (One-Way Functions) [15 Marks Total]

### Task A1 — Basic Hashing (7 Marks)

#### 1. Observations
* **Re-running with identical password**:
  * Input: `Password123`
  * SHA-256 Digest 1: `008c70392e3abfbd0fa47bbc2ed96aa99bd49e159727fcba0f2e6abeb3a9d601`
  * SHA-256 Digest 2: `008c70392e3abfbd0fa47bbc2ed96aa99bd49e159727fcba0f2e6abeb3a9d601`
  * **Finding**: The hash is identical. Cryptographic hash functions are strictly deterministic.

* **Modifying a single character**:
  * Input 1: `Password123` -> `008c70392e3abfbd0fa47bbc2ed96aa99bd49e159727fcba0f2e6abeb3a9d601`
  * Input 2: `password123` (lowercase 'p') -> `ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f`
  * **Finding**: Changing one character completely changes the digest output (avalanche effect).

#### 2. Algorithm Comparisons (MD5, SHA-1, SHA-256)
Tested using input `Password123`:
* **MD5**: `42f749ade7f9e195bf475f37a44cafcb` (32 hex characters / 128 bits)
* **SHA-1**: `b2e98ad6f6eb8508dd6a14cfa704bad7f05f6fb1` (40 hex characters / 160 bits)
* **SHA-256**: `008c70392e3abfbd0fa47bbc2ed96aa99bd49e159727fcba0f2e6abeb3a9d601` (64 hex characters / 256 bits)

#### 3. Task A1 Rubric Questions
1. **What happens when you slightly change the input to a hash function?**  
   Changing even a single bit or character results in a completely different, uncorrelated digest. This property is called the **avalanche effect**.
2. **How does the length of MD5 compare to SHA-256?**  
   MD5 outputs a 128-bit digest (32 hexadecimal characters). SHA-256 outputs a 256-bit digest (64 hexadecimal characters), which is twice as long as MD5.
3. **Why is hashing considered a "one-way" function?**  
   Hashing uses non-reversible mathematical operations (such as modular arithmetic and bitwise rotations) that compress arbitrary data into a fixed-size digest. The original input data is intentionally discarded during compression, making it computationally impossible to invert the digest back into the original input (preimage resistance).

---

### Task A2 — Hashing with Salt (8 Marks)

#### 1. Implementation & Output
* **Password**: `Spring2026`
* **Generated Salt**: `uuid.uuid4().hex` (32 hexadecimal characters / 128 bits)
* **Stored Format**: `<sha256_hex>:<salt_hex>`
  * Example Output: `68a3fb70c291...6e70b2:5835b31a31d44fe193e62f026a31c510`
* **Verification Check**:
  * Correct password (`Spring2026`): `check_password(...) -> True`
  * Incorrect password (`WrongPass`): `check_password(...) -> False`

#### 2. Task A2 Rubric Questions
1. **What is the role of the salt in password hashing?**  
   A salt is a unique, random value added to a password before hashing. It guarantees that two identical passwords produce completely different stored hashes, defeating precomputed dictionary attacks and rainbow tables.
2. **Why does the hash change every time you run the code now?**  
   A new random salt (`uuid.uuid4().hex`) is generated on every run. Because the hash input consists of `salt + password`, the input bytes change on each execution, producing a unique SHA-256 digest every time.

---

## Part B: Symmetric Encryption with DES [10 Marks Total]

### 1. Base Execution & Output (4 Marks)
* **Secret Key**: `b"mycipher"` (8 bytes / 64 bits)
* **Plaintext Message**: `b"message "` (8 bytes)
* **Cipher Mode**: `DES.MODE_ECB`
* **Ciphertext (Hex)**: `7d93cb5c14de178b`
* **Decrypted Plaintext**: `message `

### 2. Observations & Modifications (3 Marks)
* **Re-running with same key and message**: Produces identical ciphertext (`7d93cb5c14de178b`). ECB mode is purely deterministic.
* **Changing message to `b"secret12"`**: Ciphertext changes to `45fbe5b84c8d5045`.
* **Unpadded message test (`"hello"` / 5 bytes)**:  
  * **Observed Error**: `ValueError: Data must be aligned to block boundary in ECB mode`
  * **Fix**: Apply padding to 8 bytes using `.ljust(8)`:
    ```python
    message = "hello".ljust(8).encode()
    ```
    Padded message `b'hello   '` encrypts successfully to hex `0db6b7dc4c7ab05b` and decrypts to `hello`.
* **Key change test (`b"newkey12"`)**:  
  * New ciphertext generated: `ccd6c513162d20c2`.
  * Decrypting with old key (`b"mycipher"`) yields garbled bytes (`b'\xbf\x95\x99\xf6\xae^\xc4\x0e'`), proving decryption requires the exact matching key.

### 3. Part B Rubric Questions (3 Marks)
1. **Why does DES require the input to be a multiple of 8 bytes?**  
   DES is a 64-bit block cipher. Its internal 16-round Feistel structure operates strictly on fixed 8-byte blocks. In ECB mode without automated padding, inputs must align exactly to the 8-byte block size.
2. **What happens if you use the same key and message again?**  
   It produces the exact same ciphertext every time because ECB mode encrypts each block independently without any randomness or feedback.
3. **Why is using ECB mode considered a security issue?**  
   ECB preserves plaintext data patterns because identical plaintext blocks always encrypt into identical ciphertext blocks. Attackers can analyze message patterns, detect data repetitions, and reorder or replay blocks without cracking the encryption key.

---

## Part C: AES Encryption [20 Marks Total]

### 1. Base Execution & Output (6 Marks)
* **Key**: `b"secret-key-12345"` (16 bytes = 128 bits)
* **IV**: `b"This is an IV456"` (16 bytes = 128 bits)
* **Plaintext**: `b"This is a secret message for lab"` (32 bytes = 2 AES blocks)
* **Cipher Mode**: `AES.MODE_CBC`
* **Ciphertext (Hex)**: `2b79e8faeb99a72d4fe658e38083789c80e7aceec1cb1824a1876e0f24863ee4`
* **Decrypted Text**: `This is a secret message for lab`

### 2. Observations & Modifications (7 Marks)
* **Re-running with identical key, IV, and message**: Produces identical ciphertext. CBC mode is deterministic when the IV is fixed.
* **Modifying the IV to `b"DifferentIV12345"`**:  
  * Ciphertext changes completely to `d13e13f1dc88087f3547caeff3b6958fe683782d1c24d5d75cd99b393f8bc4e8`.
* **Supplying invalid key length (`b"secret"` / 6 bytes)**:  
  * **Observed Error**: `ValueError: Incorrect AES key length (6 bytes)`
  * **Reason**: AES accepts only 16, 24, or 32-byte keys.
* **Supplying unpadded message (`"Short msg"` / 9 bytes)**:  
  * **Observed Error**: `ValueError: Data must be padded to 16 byte boundary in CBC mode`
  * **Fix**: Apply padding to 16 bytes:
    ```python
    message = "Short msg".ljust(16).encode()
    ```
    Padded message `b'Short msg       '` encrypts and decrypts cleanly.

### 3. Part C Rubric Questions (7 Marks)
1. **Why does AES require a specific key size?**  
   The AES standard strictly defines key sizes of 128, 192, or 256 bits (16, 24, or 32 bytes). Its mathematical key schedule expands these exact bit lengths into 10, 12, or 14 transformation rounds. Other key lengths cannot configure the internal state schedule.
2. **What is the purpose of the Initialization Vector (IV)?**  
   The IV provides randomness for CBC mode. It XORs with the first plaintext block before encryption, ensuring that encrypting the same message multiple times generates completely distinct ciphertexts, preventing pattern disclosure.
3. **How is AES stronger than DES?**  
   * **Key Size**: AES uses 128, 192, or 256-bit keys versus DES's 56-bit key. DES can be brute-forced in hours, while AES-128 is practically uncrackable.
   * **Block Size**: AES uses 128-bit blocks versus DES's 64-bit blocks, preventing birthday-bound collision attacks.
   * **Algorithm Architecture**: AES is built on a modern Substitution-Permutation Network resistant to linear and differential cryptanalysis.

---

## Part D: Key Derivation — PBKDF2 [15 Marks Total]

### 1. Base Execution & Output (5 Marks)
* **Password**: `"mypassword"`
* **Salt**: 16 cryptographically random bytes (`Random.new().read(16)`)
* **Iterations**: `count=10000`
* **Derived Key Length**: `dkLen=16` bytes (128 bits)
* **Output**: Derived 16-byte key (32 hex characters).
* **Finding on multiple runs**: Each run produces a completely different derived key because each run uses a brand-new random salt.

### 2. Experiments: Salt & Iteration Work Factor (5 Marks)
* **Fixed Salt Experiment (`salt = b'fixedsalt123456'`)**:
  * Run 1 Derived Key: `333c1b85e3662c4788d8efa46a716d9a`
  * Run 2 Derived Key: `333c1b85e3662c4788d8efa46a716d9a`
  * **Finding**: A fixed salt makes key derivation repeatable and deterministic.
* **Iteration Benchmark (`count=100` vs `count=100000`)**:
  * `count=100`: Execution took ~0.05 milliseconds. Derived key: `6a28ff0f8fe641c73a87ec3444458316`
  * `count=100000`: Execution took ~10.1 milliseconds. Derived key: `3245a55ae58679c61bfce3bb5bc23a23`
  * **Finding**: 100,000 iterations increases the computational workload by ~200x, proving effective defense against high-speed guessing attacks.

### 3. Part D Rubric Questions (5 Marks)
1. **Why does changing the salt change the derived key?**  
   The salt is a direct input to the underlying pseudorandom function (HMAC). Because cryptographic hash functions exhibit the avalanche effect, any change in salt alters the initial digest and all subsequent iterative hash rounds, producing an entirely different key.
2. **What is the role of iterations in PBKDF2?**  
   Iterations add deliberate computational delay (work factor). Repeating the hash tens or hundreds of thousands of times slows down offline brute-force and dictionary attacks, making them cost-prohibitive for attackers while remaining negligible for legitimate users.

---

## Part E: Fernet (Simplified Secure Encryption) [25 Marks Total]

### 1. Base Execution & Output (8 Marks)
* **Generated Key**: URL-safe base64-encoded 32-byte key (e.g., `JSMtG8EufaQfxn67HXvKG5CvtrSBRvwOl2L8dpcan-w=`)
* **Plaintext Message**: `b"Secret message"`
* **Encrypted Token**: Base64 token starting with `gAAAAA...`
* **Decrypted Output**: `b"Secret message"`

### 2. Observations & Key Experiments (7 Marks)
* **Encrypting the same message twice with the same key**:
  * Token 1: `gAAAAABq9WmX8a_...`
  * Token 2: `gAAAAABq9Wma9b_...`
  * **Finding**: Tokens are completely different because Fernet automatically injects a fresh random 16-byte IV and current timestamp into each token.
* **Decryption with saved key**: Successfully restores the original plaintext.
* **Decryption with incorrect key or tampered token**:
  * **Observed Exception**: `cryptography.fernet.InvalidToken`
  * **Finding**: Fernet verifies the HMAC signature before decrypting; invalid signatures trigger an immediate exception.

### 3. Part E Rubric Questions (10 Marks)
1. **Why is Fernet safer to use than manually configuring AES?**  
   Fernet is an authenticated encryption standard that bundles AES-128-CBC, PKCS7 padding, a cryptographically secure random IV per message, and HMAC-SHA256 data authentication. It protects against common developer mistakes such as IV reuse, padding oracle vulnerabilities, and undetected ciphertext tampering.
2. **What happens if the decryption key is incorrect?**  
   Fernet checks the HMAC-SHA256 signature prior to decryption. If the key is wrong or ciphertext is modified, the signature check fails and Fernet raises `cryptography.fernet.InvalidToken`, aborting decryption and refusing to return corrupted plaintext.

---

## Part F: Broken Vault Challenge [15 Marks Total]

### Task F1: Brute-Forcing the Admin PIN (5 Marks)

#### 1. Target Hash & Solution
* **Target MD5 Hash**: `81dc9bdb52d04dc20036dbd8313ed055`
* **Recovered PIN**: **`1234`**

#### 2. Brute-Force Code Snippet
```python
import hashlib

target_hash = "81dc9bdb52d04dc20036dbd8313ed055"

print("Starting Brute Force Attack...")
for i in range(10000):
    pin = str(i).zfill(4)
    if hashlib.md5(pin.encode()).hexdigest() == target_hash:
        print(f"PIN Found: {pin}")
        break
```

#### 3. Security Reasoning
A 4-digit PIN has only 10,000 combinations (`0000`–`9999`). MD5 is an unsalted, computationally lightweight algorithm. A modern CPU tests all 10,000 hashes in under 10 milliseconds, making unsalted PIN verification completely trivial to crack.

---

### Task F2: Analyzing the ECB Leak (5 Marks)

#### 1. Code Execution & Observed Output
* **Key**: `b"security"`
* **Packet 1**: `b"DATA_REQ"` -> Ciphertext (hex): `6e9501ebbf08ec18`
* **Packet 2**: `b"DATA_REQ"` -> Ciphertext (hex): `6e9501ebbf08ec18`

#### 2. Analysis & Interpretation
1. **Information gained by attacker without the secret key**:  
   The attacker discovers that Packet 1 and Packet 2 contain identical plaintext data because their ciphertexts are identical.
2. **Database vulnerability (Male/Female, Yes/No fields)**:  
   In columns with low cardinality (such as Yes/No or Male/Female), identical plaintexts yield identical ciphertext blocks. An attacker can perform **frequency analysis** to infer sensitive records without cracking the encryption key (e.g., matching the more common ciphertext block to the majority demographic).

---

### Task F3: Security Engineer's Recommendation & Mini Challenge (5 Marks)

#### 1. Security Remediation Table

| Legacy Design | Security Weakness | Recommended Replacement | Why? |
|---|---|---|---|
| **Four-digit PIN** | Extremely small keyspace (10,000 combinations); cracked in milliseconds via brute force. | Long alphanumeric passphrase (12+ characters) or Multi-Factor Authentication (MFA). | Increases entropy exponentially ($>2^{70}$ combinations), rendering online and offline brute force impossible. |
| **Unsalted MD5 password verifier** | Cryptographically broken algorithm; lacks salt and work factor; vulnerable to rainbow tables. | Salted Argon2id or PBKDF2-HMAC-SHA256 (600,000+ iterations) with unique 128-bit salt. | Salt neutralizes rainbow tables; memory/computational hardness makes password cracking cost-prohibitive. |
| **DES-ECB for sensitive data** | 56-bit key broken in hours; ECB mode leaks structural patterns and data equality. | AES-256 in Galois/Counter Mode (AES-256-GCM) or Fernet with fresh random IV/nonce. | AES-256 provides uncrackable confidentiality; GCM/Fernet provides Authenticated Encryption (AEAD) to prevent tampering. |
| **Hard-coded encryption key in source code** | Key is exposed to source repositories, developers, build logs, and binary reverse engineering. | Dedicated Key Management Service (AWS KMS, Azure Key Vault, HashiCorp Vault) or protected environment variables. | Separates secrets from codebase, enforces least-privilege IAM access, provides audit logging, and enables automated rotation. |

#### 2. Mini Challenge: Analysis of Developer's Proposed Fix
*Proposed Fix: Replace MD5 with `SHA256(PIN)` and use AES-CBC with a fixed IV.*

**Two Remaining Security Flaws**:
1. **Unsalted Fast Hash on Low Entropy (`SHA256(PIN)`)**:  
   The search space is still only 10,000 4-digit PINs. SHA-256 is an unsalted, fast cryptographic hash designed for high throughput. An attacker can precompute or brute-force all 10,000 SHA-256 hashes in less than a millisecond, rendering the change ineffective.
2. **Fixed IV Destroys Semantic Security in AES-CBC**:  
   Reusing a fixed IV in CBC mode means identical plaintext messages (or identical first blocks) always produce identical initial ciphertext blocks across sessions. This leaks data patterns and makes the system vulnerable to replay attacks and chosen-plaintext analysis. Additionally, unauthenticated AES-CBC remains susceptible to padding oracle attacks.
