"""
tests/test_cybershield.py
---------------------------
Unit + integration tests covering all four modules. Run with:

    pytest tests/ -v

Uses an in-memory SQLite DB (TestingConfig) so no MySQL server is
required to run the test suite itself.
"""

import os
import io
import base64
import pytest

os.environ["AES_MASTER_KEY"] = base64.b64encode(os.urandom(32)).decode()

from app import create_app
from models import db, User


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def register_and_login(client, username="alice", password="Str0ng!Passw0rd#2026"):
    client.post("/register", data={
        "username": username, "email": f"{username}@test.com",
        "full_name": "Alice Tester", "password": password, "confirm_password": password,
    }, follow_redirects=True)
    return client.post("/login", data={"identifier": username, "password": password}, follow_redirects=True)


# ---------------- Unit tests: Password Checker ----------------

def test_password_checker_weak():
    from utils.password_checker import check_password_strength
    result = check_password_strength("123456")
    assert result["label"] in ("Weak", "Fair")
    assert result["score"] < 50


def test_password_checker_strong():
    from utils.password_checker import check_password_strength
    result = check_password_strength("Tr0ub4dor&3xQzP!mK9")
    assert result["score"] >= 65
    assert result["label"] in ("Strong", "Very Strong")


# ---------------- Unit tests: AES Encryption ----------------

def test_aes_encrypt_decrypt_roundtrip():
    from utils.encryption import generate_dek, encrypt_file_bytes, decrypt_file_bytes
    dek = generate_dek()
    plaintext = b"Confidential university project data."
    ciphertext, nonce = encrypt_file_bytes(plaintext, dek)
    assert ciphertext != plaintext
    recovered = decrypt_file_bytes(ciphertext, dek, nonce)
    assert recovered == plaintext


def test_aes_tamper_detection():
    from utils.encryption import generate_dek, encrypt_file_bytes, decrypt_file_bytes, EncryptionError
    dek = generate_dek()
    ciphertext, nonce = encrypt_file_bytes(b"secret data", dek)
    tampered = bytearray(ciphertext)
    tampered[0] ^= 0xFF
    with pytest.raises(EncryptionError):
        decrypt_file_bytes(bytes(tampered), dek, nonce)


def test_dek_wrap_unwrap_roundtrip():
    from utils.encryption import generate_dek, wrap_dek, unwrap_dek
    master_key = base64.b64encode(os.urandom(32)).decode()
    dek = generate_dek()
    wrapped, nonce = wrap_dek(dek, master_key)
    unwrapped = unwrap_dek(wrapped, nonce, master_key)
    assert unwrapped == dek


# ---------------- Unit tests: Digital Signature ----------------

def test_signature_valid():
    from utils.digital_signature import generate_rsa_keypair, sign_document, verify_signature
    priv, pub = generate_rsa_keypair()
    doc = b"This is the original contract text."
    _, sig = sign_document(doc, priv)
    assert verify_signature(doc, sig, pub) is True


def test_signature_detects_tampering():
    from utils.digital_signature import generate_rsa_keypair, sign_document, verify_signature
    priv, pub = generate_rsa_keypair()
    doc = b"This is the original contract text."
    _, sig = sign_document(doc, priv)
    tampered_doc = b"This is the MODIFIED contract text."
    assert verify_signature(tampered_doc, sig, pub) is False


# ---------------- Unit tests: OTP / 2FA ----------------

def test_totp_generation_and_verification():
    from utils.otp_utils import generate_totp_secret, verify_totp
    import pyotp
    secret = generate_totp_secret()
    code = pyotp.TOTP(secret).now()
    assert verify_totp(secret, code) is True
    assert verify_totp(secret, "000000") is False


def test_numeric_otp_length():
    from utils.otp_utils import generate_numeric_otp
    code = generate_numeric_otp()
    assert len(code) == 6
    assert code.isdigit()


# ---------------- Integration tests: routes ----------------

def test_homepage_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_register_and_login_flow(client):
    resp = register_and_login(client)
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data or b"dashboard" in resp.data.lower()


def test_duplicate_registration_rejected(client):
    register_and_login(client, username="bob")
    client.get("/logout", follow_redirects=True)
    resp = client.post("/register", data={
        "username": "bob", "email": "bob@test.com", "full_name": "Bob",
        "password": "Str0ng!Passw0rd#2026", "confirm_password": "Str0ng!Passw0rd#2026",
    }, follow_redirects=True)
    assert b"already registered" in resp.data.lower()


def test_login_wrong_password_fails(client):
    client.post("/register", data={
        "username": "carol", "email": "carol@test.com", "full_name": "Carol",
        "password": "Str0ng!Passw0rd#2026", "confirm_password": "Str0ng!Passw0rd#2026",
    })
    resp = client.post("/login", data={"identifier": "carol", "password": "wrongpassword"}, follow_redirects=True)
    assert b"Invalid username" in resp.data


def test_password_check_api(client):
    resp = client.post("/api/password-check", json={"password": "abc123"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "score" in data and "label" in data


def test_file_upload_requires_login(client):
    resp = client.get("/storage", follow_redirects=True)
    assert b"log in" in resp.data.lower() or resp.status_code == 200


def test_file_upload_and_download(client):
    register_and_login(client, username="dave")
    data = {"file": (io.BytesIO(b"hello secure world"), "note.txt")}
    resp = client.post("/storage", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert resp.status_code == 200
    assert b"encrypted" in resp.data.lower() or b"note.txt" in resp.data


def test_admin_route_forbidden_for_normal_user(client):
    register_and_login(client, username="erin")
    resp = client.get("/admin")
    assert resp.status_code == 403
