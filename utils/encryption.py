"""
utils/encryption.py
--------------------
Secure File Storage encryption engine.

Design (envelope encryption):
1. Every uploaded file gets its OWN randomly generated 256-bit
   Data Encryption Key (DEK).
2. The file's plaintext is encrypted with AES-256-GCM using that DEK
   and a random 96-bit nonce (GCM standard). GCM gives us both
   confidentiality AND integrity (authenticated encryption) - any
   tampering with the ciphertext is detected on decrypt.
3. The DEK itself is then encrypted ("wrapped") with a single master
   key (AES_MASTER_KEY, stored only in environment variables, never
   in the database) using AES-256-GCM again.
4. The database stores: the wrapped DEK, the file's nonce, and a
   SHA-256 checksum of the original plaintext (for integrity
   verification independent of GCM's own tag). The encrypted file
   bytes are stored on disk, not in the DB.

This means: even a full database dump gives an attacker nothing
useful without the master key AND the encrypted file on disk.
"""

import os
import base64
import hashlib
import uuid
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class EncryptionError(Exception):
    pass


def generate_dek() -> bytes:
    """Generate a fresh random 256-bit (32-byte) Data Encryption Key."""
    return AESGCM.generate_key(bit_length=256)


def _load_master_key(master_key_b64: str) -> bytes:
    if not master_key_b64:
        raise EncryptionError(
            "AES_MASTER_KEY is not set. Generate one with: "
            "python -c \"import os,base64;print(base64.b64encode(os.urandom(32)).decode())\""
        )
    key = base64.b64decode(master_key_b64)
    if len(key) != 32:
        raise EncryptionError("AES_MASTER_KEY must decode to exactly 32 bytes.")
    return key


def wrap_dek(dek: bytes, master_key_b64: str) -> tuple[str, str]:
    """
    Encrypt (wrap) a per-file DEK using the master key.
    Returns (wrapped_dek_b64, nonce_b64) to be stored in the DB.
    """
    master_key = _load_master_key(master_key_b64)
    nonce = os.urandom(12)
    aesgcm = AESGCM(master_key)
    wrapped = aesgcm.encrypt(nonce, dek, None)
    return base64.b64encode(wrapped).decode(), base64.b64encode(nonce).decode()


def unwrap_dek(wrapped_dek_b64: str, nonce_b64: str, master_key_b64: str) -> bytes:
    """Decrypt (unwrap) a DEK that was wrapped with wrap_dek()."""
    master_key = _load_master_key(master_key_b64)
    nonce = base64.b64decode(nonce_b64)
    wrapped = base64.b64decode(wrapped_dek_b64)
    aesgcm = AESGCM(master_key)
    try:
        return aesgcm.decrypt(nonce, wrapped, None)
    except Exception as exc:
        raise EncryptionError("Failed to unwrap DEK - master key mismatch or data corrupted.") from exc


def encrypt_file_bytes(plaintext: bytes, dek: bytes) -> tuple[bytes, str]:
    """
    Encrypt file plaintext with AES-256-GCM using the file's DEK.
    Returns (ciphertext, nonce_b64). The GCM tag is appended to the
    ciphertext automatically by the `cryptography` library.
    """
    nonce = os.urandom(12)
    aesgcm = AESGCM(dek)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return ciphertext, base64.b64encode(nonce).decode()


def decrypt_file_bytes(ciphertext: bytes, dek: bytes, nonce_b64: str) -> bytes:
    """Decrypt file ciphertext. Raises EncryptionError if tampered/corrupted."""
    nonce = base64.b64decode(nonce_b64)
    aesgcm = AESGCM(dek)
    try:
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise EncryptionError(
            "Decryption failed - the file may have been tampered with or the key is wrong."
        ) from exc


def sha256_hex(data: bytes) -> str:
    """Return the SHA-256 hex digest of raw bytes (integrity checksum)."""
    return hashlib.sha256(data).hexdigest()


def generate_stored_filename(original_filename: str) -> str:
    """Generate a collision-free filename for disk storage (UUID + extension)."""
    ext = ""
    if "." in original_filename:
        ext = "." + original_filename.rsplit(".", 1)[1].lower()
    return f"{uuid.uuid4().hex}{ext}.enc"
