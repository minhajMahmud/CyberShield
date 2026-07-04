"""
Check user dashboard statistics
"""
import sys
from app import create_app, db
from models import User, FileRecord, DigitalSignature

def check_stats(username=None):
    app = create_app()
    
    with app.app_context():
        if username:
            user = User.query.filter_by(username=username).first()
            if not user:
                print(f"❌ User '{username}' not found!")
                return
            users = [user]
        else:
            users = User.query.all()
        
        print("\n" + "="*80)
        print("USER DASHBOARD STATISTICS")
        print("="*80)
        
        for user in users:
            file_count = FileRecord.query.filter_by(user_id=user.id, is_deleted=False).count()
            signature_count = DigitalSignature.query.filter_by(user_id=user.id).count()
            
            print(f"\n👤 Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"   📁 Encrypted Files: {file_count}")
            print(f"   ✍️  Digital Signatures: {signature_count}")
            print(f"   🔐 2FA Status: {'ON ✅' if user.is_2fa_enabled else 'OFF ❌'}")
            print(f"   🕐 Last Login: {user.last_login.strftime('%b %d, %Y %H:%M') if user.last_login else 'Never'}")
            print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        print("\n")

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else None
    check_stats(username)
