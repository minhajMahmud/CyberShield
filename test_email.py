"""
Test email configuration
"""
from app import app, mail
from flask_mail import Message

print("=" * 70)
print("Testing Email Configuration")
print("=" * 70)

with app.app_context():
    print("\n1. Email Configuration:")
    print(f"   Server: {app.config.get('MAIL_SERVER')}")
    print(f"   Port: {app.config.get('MAIL_PORT')}")
    print(f"   TLS: {app.config.get('MAIL_USE_TLS')}")
    print(f"   Username: {app.config.get('MAIL_USERNAME')}")
    print(f"   Password: {'*' * len(app.config.get('MAIL_PASSWORD', ''))}")
    
    print("\n2. Attempting to send test email...")
    try:
        msg = Message(
            subject="Test Email from CyberShield",
            recipients=["mahmudminhaj003@gmail.com"],
            body="This is a test email. If you receive this, email configuration is working!"
        )
        mail.send(msg)
        print("   ✅ Email sent successfully!")
        print("   Check your inbox: mahmudminhaj003@gmail.com")
    except Exception as e:
        print(f"   ❌ Email failed: {e}")
        print("\n3. Possible issues:")
        print("   - App password might be incorrect")
        print("   - App password might have spaces (should be removed)")
        print("   - Gmail might require additional verification")
        print("   - Check: https://myaccount.google.com/apppasswords")

print("\n" + "=" * 70)
