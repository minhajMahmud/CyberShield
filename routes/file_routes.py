"""
routes/file_routes.py
------------------------
Secure File Storage module: upload (encrypt), list/history,
download (decrypt), and delete.
"""

import os
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    send_file, current_app, abort
)
from flask_login import login_required, current_user
from datetime import datetime
import io

from models import db, FileRecord, ActivityLog
from utils.decorators import allowed_file, validate_file_size
from utils.encryption import (
    generate_dek, wrap_dek, unwrap_dek, encrypt_file_bytes,
    decrypt_file_bytes, sha256_hex, generate_stored_filename,
)

file_bp = Blueprint("files", __name__)


@file_bp.route("/storage", methods=["GET", "POST"])
@login_required
def storage():
    if request.method == "POST":
        upload = request.files.get("file")
        if not upload or upload.filename == "":
            flash("Please choose a file to upload.", "danger")
            return redirect(url_for("files.storage"))

        allowed_ext = current_app.config["ALLOWED_EXTENSIONS"]
        if not allowed_file(upload.filename, allowed_ext):
            flash(f"File type not allowed. Allowed: {', '.join(sorted(allowed_ext))}", "danger")
            return redirect(url_for("files.storage"))

        if not validate_file_size(upload.stream, current_app.config["MAX_CONTENT_LENGTH"]):
            flash("File exceeds the maximum allowed size.", "danger")
            return redirect(url_for("files.storage"))

        plaintext = upload.read()
        checksum = sha256_hex(plaintext)

        # --- Envelope encryption ---
        dek = generate_dek()
        ciphertext, file_nonce_b64 = encrypt_file_bytes(plaintext, dek)
        wrapped_dek_b64, master_nonce_b64 = wrap_dek(dek, current_app.config["AES_MASTER_KEY"])
        # Combine master nonce + wrapped dek into a single stored field
        encrypted_dek_field = f"{master_nonce_b64}:{wrapped_dek_b64}"

        stored_filename = generate_stored_filename(upload.filename)
        disk_path = os.path.join(current_app.config["ENCRYPTED_FOLDER"], stored_filename)
        with open(disk_path, "wb") as f:
            f.write(ciphertext)

        record = FileRecord(
            user_id=current_user.id,
            original_filename=upload.filename,
            stored_filename=stored_filename,
            file_size=len(plaintext),
            file_type=upload.filename.rsplit(".", 1)[-1].lower(),
            encryption_iv=file_nonce_b64,
            encrypted_dek=encrypted_dek_field,
            checksum_sha256=checksum,
        )
        db.session.add(record)
        db.session.commit()

        ActivityLog.record(
            current_user.id, "FILE_UPLOAD", f"Uploaded {upload.filename}",
            request.remote_addr, request.headers.get("User-Agent", "")[:255],
        )
        flash(f"'{upload.filename}' encrypted with AES-256-GCM and stored securely.", "success")
        return redirect(url_for("files.storage"))

    files = (
        FileRecord.query.filter_by(user_id=current_user.id, is_deleted=False)
        .order_by(FileRecord.uploaded_at.desc())
        .all()
    )
    return render_template("file_storage.html", files=files)


@file_bp.route("/storage/download/<int:file_id>")
@login_required
def download(file_id):
    record = FileRecord.query.get_or_404(file_id)
    if record.user_id != current_user.id:
        abort(403)

    disk_path = os.path.join(current_app.config["ENCRYPTED_FOLDER"], record.stored_filename)
    if not os.path.exists(disk_path):
        flash("Encrypted file missing from disk.", "danger")
        return redirect(url_for("files.storage"))

    with open(disk_path, "rb") as f:
        ciphertext = f.read()

    master_nonce_b64, wrapped_dek_b64 = record.encrypted_dek.split(":", 1)
    dek = unwrap_dek(wrapped_dek_b64, master_nonce_b64, current_app.config["AES_MASTER_KEY"])
    plaintext = decrypt_file_bytes(ciphertext, dek, record.encryption_iv)

    # Integrity re-check against the checksum captured at upload time
    if sha256_hex(plaintext) != record.checksum_sha256:
        flash("Integrity check failed - file may be corrupted.", "danger")
        return redirect(url_for("files.storage"))

    ActivityLog.record(
        current_user.id, "FILE_DOWNLOAD", f"Downloaded {record.original_filename}",
        request.remote_addr, request.headers.get("User-Agent", "")[:255],
    )

    return send_file(
        io.BytesIO(plaintext),
        download_name=record.original_filename,
        as_attachment=True,
    )


@file_bp.route("/storage/delete/<int:file_id>", methods=["POST"])
@login_required
def delete(file_id):
    record = FileRecord.query.get_or_404(file_id)
    if record.user_id != current_user.id:
        abort(403)

    disk_path = os.path.join(current_app.config["ENCRYPTED_FOLDER"], record.stored_filename)
    if os.path.exists(disk_path):
        os.remove(disk_path)

    record.is_deleted = True
    record.deleted_at = datetime.utcnow()
    db.session.commit()

    ActivityLog.record(
        current_user.id, "FILE_DELETE", f"Deleted {record.original_filename}",
        request.remote_addr, request.headers.get("User-Agent", "")[:255],
    )
    flash("File deleted.", "info")
    return redirect(url_for("files.storage"))
