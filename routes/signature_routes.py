"""
routes/signature_routes.py
------------------------------
Digital Signature Verification module: generate an RSA-2048 key
pair, sign an uploaded document, and verify a document + signature
+ public key combination (detecting tampering).
"""

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, send_file
)
from flask_login import login_required, current_user
import io

from models import db, DigitalSignature
from utils.digital_signature import (
    generate_rsa_keypair, private_key_to_pem, public_key_to_pem,
    load_public_key_from_pem, sign_document, verify_signature, compute_sha256,
)

signature_bp = Blueprint("signature", __name__)


@signature_bp.route("/digital-signature", methods=["GET"])
@login_required
def signature_home():
    signatures = (
        DigitalSignature.query.filter_by(user_id=current_user.id)
        .order_by(DigitalSignature.created_at.desc())
        .all()
    )
    return render_template("digital_signature.html", signatures=signatures)


@signature_bp.route("/digital-signature/sign", methods=["POST"])
@login_required
def sign():
    upload = request.files.get("document")
    if not upload or upload.filename == "":
        flash("Please choose a document to sign.", "danger")
        return redirect(url_for("signature.signature_home"))

    document_bytes = upload.read()

    # 1. Generate a fresh RSA-2048 key pair for this signing operation
    private_key, public_key = generate_rsa_keypair()

    # 2. Hash (SHA-256) + Sign (RSA-PSS) the document
    document_hash, signature_value = sign_document(document_bytes, private_key)

    record = DigitalSignature(
        user_id=current_user.id,
        document_name=upload.filename,
        document_hash=document_hash,
        signature_value=signature_value,
        public_key=public_key_to_pem(public_key),
        private_key_encrypted=private_key_to_pem(private_key),  # demo only - see README security notes
        status="signed",
    )
    db.session.add(record)
    db.session.commit()

    flash(f"'{upload.filename}' signed successfully with RSA-2048 + SHA-256.", "success")
    return redirect(url_for("signature.signature_home"))


@signature_bp.route("/digital-signature/verify", methods=["POST"])
@login_required
def verify():
    upload = request.files.get("document")
    signature_value = request.form.get("signature_value", "").strip()
    public_key_pem = request.form.get("public_key", "").strip()

    if not upload or not signature_value or not public_key_pem:
        flash("Document, signature, and public key are all required to verify.", "danger")
        return redirect(url_for("signature.signature_home"))

    try:
        document_bytes = upload.read()
        
        # Try to load the public key
        try:
            public_key = load_public_key_from_pem(public_key_pem)
        except Exception as e:
            flash(f"❌ Invalid public key format. Please ensure you're using a valid PEM-formatted RSA public key. Error: {str(e)}", "danger")
            return redirect(url_for("signature.signature_home"))
        
        # Try to decode the signature
        try:
            import base64
            base64.b64decode(signature_value)
        except Exception as e:
            flash(f"❌ Invalid signature format. Signature must be base64-encoded. Error: {str(e)}", "danger")
            return redirect(url_for("signature.signature_home"))

        is_valid = verify_signature(document_bytes, signature_value, public_key)
        current_hash = compute_sha256(document_bytes)

        if is_valid:
            flash(f"✅ Signature VALID. Document integrity confirmed (SHA-256: {current_hash[:16]}...).", "success")
        else:
            flash("❌ Signature INVALID. The document may have been modified or the signature/key do not match.", "danger")
    
    except Exception as e:
        flash(f"❌ Verification error: {str(e)}", "danger")

    return redirect(url_for("signature.signature_home"))


@signature_bp.route("/digital-signature/download/<int:sig_id>")
@login_required
def download_signature(sig_id):
    record = DigitalSignature.query.get_or_404(sig_id)
    if record.user_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("signature.signature_home"))

    content = (
        f"Document: {record.document_name}\n"
        f"SHA-256 Hash: {record.document_hash}\n"
        f"Signature (base64, RSA-2048/PSS):\n{record.signature_value}\n\n"
        f"Public Key (PEM):\n{record.public_key}\n"
    )
    return send_file(
        io.BytesIO(content.encode()),
        download_name=f"{record.document_name}.signature.txt",
        as_attachment=True,
    )
