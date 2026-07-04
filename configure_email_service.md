# 📧 Configure Email Service for Verification Codes

## Current Behavior
- Verification codes are **DISPLAYED ON SCREEN**
- Codes are **NOT sent via email** (email service not configured)
- This is intentional for development/testing

## To Send Codes via Email

### Step 1: Get Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security**
3. Enable **2-Step Verification** (if not already enabled)
4. Scroll to **App passwords**
5. Create new app password:
   - Select app: **Mail**
   - Select device: **Other (Custom name)**
   - Name it: **CyberShield**
6. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### Step 2: Update .env File

Open `e:\CyberShield\.env` and update these lines:

```env
# Flask-Mail (used for OTP delivery)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-actual-email@gmail.com
MAIL_PASSWORD=abcdefghijklmnop
MAIL_DEFAULT_SENDER=your-actual-email@gmail.com
```

**Replace:**
- `your-actual-email@gmail.com` → Your Gmail address
- `abcdefghijklmnop` → Your 16-character app password (no spaces)

### Step 3: Update auth_routes.py

Open `e:\CyberShield\routes\auth_routes.py` and find the registration route.

**Replace this code:**
```python
# Display OTP code on screen (email service removed)
flash(f"Registration successful! Your email verification code is: {otp.otp_code} (Valid for 30 minutes)", "success")
flash("Please verify your email to complete registration.", "info")
```

**With this code:**
```python
# Send verification code via email
from app import mail
from flask_mail import Message

try:
    msg = Message(
        subject="Verify Your CyberShield Account",
        recipients=[user.email],
        body=f"""
Welcome to CyberShield!

Your email verification code is: {otp.otp_code}

This code will expire in 30 minutes.

Please enter this code on the verification page to complete your registration.

If you didn't create this account, please ignore this email.

Best regards,
CyberShield Security Team
        """
    )
    mail.send(msg)
    flash("Registration successful! A verification code has been sent to your email.", "success")
    flash(f"Check {user.email} for your verification code.", "info")
except Exception as e:
    # Fallback if email fails
    flash(f"Registration successful! Your email verification code is: {otp.otp_code} (Valid for 30 minutes)", "success")
    flash(f"(Email sending failed: {str(e)})", "warning")
```

### Step 4: Update Resend Route

In the same file, find the `resend_verification` route.

**Replace this code:**
```python
# Display OTP code on screen (email service removed)
flash(f"New verification code sent! Your code is: {otp.otp_code} (Valid for 30 minutes)", "info")
```

**With this code:**
```python
# Send new code via email
from app import mail
from flask_mail import Message

try:
    msg = Message(
        subject="New Verification Code - CyberShield",
        recipients=[user.email],
        body=f"""
Your new verification code is: {otp.otp_code}

This code will expire in 30 minutes.

If you didn't request this code, please ignore this email.

Best regards,
CyberShield Security Team
        """
    )
    mail.send(msg)
    flash("A new verification code has been sent to your email!", "success")
except Exception as e:
    flash(f"New verification code: {otp.otp_code} (Valid for 30 minutes)", "info")
    flash(f"(Email sending failed: {str(e)})", "warning")
```

### Step 5: Restart Server

Stop and restart the Flask application:
```bash
# Press Ctrl+C to stop
# Then run:
python app.py
```

### Step 6: Test

1. Register a new account
2. Check your email inbox
3. You should receive the verification code
4. Enter code on verification page

---

## 📝 For Testing Without Email

If you just want to test the feature **without configuring email**:

1. Register a new account
2. **Look at the green message** at the top of the page
3. It will show: "Your email verification code is: 123456"
4. Copy that code
5. Enter it on the verification page
6. Done! ✅

---

## ⚠️ Troubleshooting

### Email Not Received?

**Check:**
1. Spam/Junk folder
2. Gmail app password correct (16 characters, no spaces)
3. Gmail address correct in `.env`
4. 2-Step Verification enabled on Google Account
5. Check Flask server logs for errors

### Still Not Working?

**Verify configuration:**
```python
# Test email config
from app import app, mail
from flask_mail import Message

with app.app_context():
    msg = Message(
        subject="Test Email",
        recipients=["your-email@gmail.com"],
        body="This is a test email from CyberShield"
    )
    mail.send(msg)
    print("Email sent successfully!")
```

Run this test script to check if email sending works.

---

## 🎯 Recommended Approach

**For Development:**
- Keep codes displayed on screen (current behavior)
- Faster testing, no email config needed

**For Production:**
- Configure email service
- Send codes via email
- More professional user experience

---

**Current Status:** Codes displayed on screen (working as intended for development)
**To Enable Email:** Follow steps above
