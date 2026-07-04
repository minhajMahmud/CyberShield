"""
Check 2FA status for all users
"""
from app import create_app, db
from models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    
    print("\n" + "="*60)
    print("2FA STATUS CHECK")
    print("="*60)
    
    if not users:
        print("\n⚠️  No users found in database!")
    
    for user in users:
        print(f"\nUsername: {user.username}")
        print(f"Email: {user.email}")
        print(f"is_2fa_enabled: {user.is_2fa_enabled}")
        print(f"twofa_secret exists: {'Yes' if user.twofa_secret else 'No'}")
        print(f"twofa_secret value: {user.twofa_secret[:10] + '...' if user.twofa_secret else 'None'}")
        print("-" * 60)
    
    print("\n")
