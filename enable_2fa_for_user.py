"""
Manually enable 2FA for a user (for testing)
Usage: python enable_2fa_for_user.py <username>
"""
import sys
from app import create_app
from models import db, User
from utils.otp_utils import generate_totp_secret, get_totp_uri, generate_qr_code_base64

def enable_2fa(username):
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ User '{username}' not found!")
            return
        
        # Generate new secret if doesn't exist
        if not user.twofa_secret:
            user.twofa_secret = generate_totp_secret()
        
        # Enable 2FA
        user.is_2fa_enabled = True
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ 2FA ENABLED SUCCESSFULLY")
        print("="*60)
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"is_2fa_enabled: {user.is_2fa_enabled}")
        print(f"twofa_secret: {user.twofa_secret}")
        print("\n" + "="*60)
        print("📱 SCAN THIS QR CODE WITH GOOGLE AUTHENTICATOR:")
        print("="*60)
        
        # Generate QR code
        totp_uri = get_totp_uri(user.twofa_secret, user.email)
        print(f"\nOr manually enter this secret: {user.twofa_secret}")
        print(f"Account: {user.email}")
        print(f"Issuer: CyberShield\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enable_2fa_for_user.py <username>")
        sys.exit(1)
    
    enable_2fa(sys.argv[1])
