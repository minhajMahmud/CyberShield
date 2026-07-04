"""
utils/digital_signature.py
----------------------------
Digital Signature Verification module.

Cryptographic design:
1. Key generation: RSA-2048 key pair (public/private) is generated
   per signing operation using `cryptography`'s RSA implementation.
   2048-bit RSA is the current minimum recommended strength for
   RSA in production systems (NIST SP 800-57).
2. Hashing: the uploaded document's bytes are hashed with SHA-256
   to produce a fixed-length 256-bit digest. Hashing first means we
   sign a small fixed-size value instead of the whole file, which is
   both faster and how virtually every real signing scheme (X.509,
   PGP, code-signing) works.
3. Signing: the SHA-256 digest is signed with the RSA private key
   using PSS padding (probabilistic, recommended over legacy PKCS#1
   v1.5) - this produces the signature_value.
4. Verification: given the original document + signature + public
   key, we recompute the document's SHA-256 hash and verify the RSA
   signature against it. If verification succeeds, both integrity
   (file unmodified) and authenticity (signed by holder of the
   private key) are proven. Any single byte changed in the document
   will make verification fail - this is how we "detect document
   modification."
"""

import base64
import hashlib

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature


class SignatureError(Exception):
    pass


def generate_rsa_keypair(key_size: int = 2048):
    """Generate a fresh RSA key pair. Returns (private_key_obj, public_key_obj)."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    public_key = private_key.public_key()
    return private_key, public_key


def private_key_to_pem(private_key, password: bytes = None) -> str:
    encryption = (
        serialization.BestAvailableEncryption(password)
        if password
        else serialization.NoEncryption()
    )
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )
    return pem.decode()


def public_key_to_pem(public_key) -> str:
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem.decode()


def load_private_key_from_pem(pem_str: str, password: bytes = None):
    return serialization.load_pem_private_key(pem_str.encode(), password=password)


def load_public_key_from_pem(pem_str: str):
    """Load a public key from PEM format string."""
    try:
        # Clean up the PEM string (remove extra whitespace, ensure proper format)
        pem_str = pem_str.strip()
        
        # Check if it looks like a valid PEM format
        if not pem_str.startswith('-----BEGIN'):
            raise ValueError("PEM string must start with '-----BEGIN' header")
        
        return serialization.load_pem_public_key(pem_str.encode())
    except Exception as e:
        raise ValueError(f"Unable to load PEM file. Ensure the public key is in valid PEM format. Details: {str(e)}")


def compute_sha256(document_bytes: bytes) -> str:
    """Return the hex-encoded SHA-256 digest of a document's bytes."""
    return hashlib.sha256(document_bytes).hexdigest()


def sign_document(document_bytes: bytes, private_key) -> tuple[str, str]:
    """
    Sign a document. Returns (document_hash_hex, signature_b64).
    """
    digest_hex = compute_sha256(document_bytes)
    signature = private_key.sign(
        document_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return digest_hex, base64.b64encode(signature).decode()


def verify_signature(document_bytes: bytes, signature_b64: str, public_key) -> bool:
    """
    Verify a document against a base64 signature and a public key.
    Returns True if valid, False if the signature does not match
    (i.e. the document was modified or the wrong key/signature was used).
    """
    signature = base64.b64decode(signature_b64)
    try:
        public_key.verify(
            signature,
            document_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False
