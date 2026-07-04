# 📸 Screenshot Capture Guide

## Overview
This guide helps you capture professional screenshots for the CyberShield README and documentation.

---

## 🎯 Required Screenshots

### 1. **Landing Page** (`landing.png`)
**URL:** `http://localhost:5000/`

**What to capture:**
- Full hero section with "CyberShield" branding
- Feature cards (4 security modules)
- Call-to-action buttons
- Navigation bar

**Tips:**
- Make sure logged out
- Capture full page or above-the-fold content
- Include navbar

---

### 2. **Login Page** (`login.png`)
**URL:** `http://localhost:5000/login`

**What to capture:**
- Login form (username/email and password fields)
- CyberShield branding
- "Register here" link at bottom

**Tips:**
- Show clean, empty form
- Dark theme should be visible

---

### 3. **2FA Verification** (`2fa-verify.png`)
**URL:** `http://localhost:5000/login` (after entering credentials with 2FA enabled)

**What to capture:**
- 6-digit code input field
- Instructions in both English and Bangla
- "Verify & Login" button
- Alert box with instructions

**Tips:**
- Login with 2FA-enabled account
- Show the verification screen
- Don't enter actual code (keep it 000000 placeholder)

---

### 4. **Dashboard** (`dashboard.png`)
**URL:** `http://localhost:5000/dashboard`

**What to capture:**
- Welcome message with username
- All 4 stat cards:
  - 2FA Status (ON/OFF)
  - Encrypted Files (count)
  - Digital Signatures (count)
  - Password Checks (count)
- Quick action buttons
- Recent Activity table (at least 3-5 entries)
- "Last updated" timestamp

**Tips:**
- Use account with some activity (uploaded files, checked passwords)
- Enable 2FA to show "ON" status
- Capture full dashboard or main content area

---

### 5. **File Storage** (`file-storage.png`)
**URL:** `http://localhost:5000/file-storage`

**What to capture:**
- File upload section
- Files table with at least 2-3 files:
  - Filename
  - Size
  - Upload date
  - Download/Delete buttons
- Storage statistics (if displayed)

**Tips:**
- Upload a few test files first
- Show variety of file types (PDF, images, documents)
- Include file sizes and dates

---

### 6. **Password Strength Checker** (`password-checker.png`)
**URL:** `http://localhost:5000/password-checker`

**What to capture:**
- Password input field (with example password typed)
- Strength meter/progress bar showing colored indicator
- Strength score (e.g., "Strong (75/100)")
- Estimated crack time breakdown:
  - Online Attack time
  - Offline Fast Hash time
  - Offline Slow Hash time
  - Entropy bits
- Suggestions section (if password is weak)

**Tips:**
- Use a medium-strength password for demo (e.g., "MyP@ssw0rd123")
- Show the detailed crack time analysis
- Capture the complete analysis card

---

### 7. **Digital Signature** (`digital-signature.png`)
**URL:** `http://localhost:5000/digital-signature`

**What to capture:**
- Document name input field
- File upload option
- "Generate Signature" button
- OR: Signature result showing:
  - Document hash
  - Signature value
  - Public key
  - Status (Signed/Verified)

**Tips:**
- Either show the form or the result after signing
- If showing result, include signature details
- Make sure all fields are visible

---

### 8. **2FA Setup** (`2fa-setup.png`)
**URL:** `http://localhost:5000/2fa-settings`

**What to capture:**
- Instructions in both English and Bangla
- QR code (large and centered on white background)
- 6-digit code input field
- "Enable 2FA" button
- Step-by-step instructions (1, 2, 3)

**Tips:**
- Use account with 2FA disabled to show setup screen
- QR code should be clearly visible
- Include all instruction text

---

### 9. **Admin Dashboard** (`admin-dashboard.png`)
**URL:** `http://localhost:5000/admin` (admin account only)

**What to capture:**
- Users table with:
  - Username
  - Email
  - Role
  - Status (Active/Inactive)
  - 2FA status
  - Action buttons (Enable/Disable/Promote)
- Recent activity logs
- Statistics (total users, active users, etc.)

**Tips:**
- Login as admin user
- Should show at least 3-4 users in table
- Include some activity log entries

---

## 🛠️ Tools for Screenshot Capture

### Windows (Recommended)
1. **Snipping Tool**
   - Press `Win + Shift + S`
   - Select area to capture
   - Auto-copies to clipboard
   - Paste into Paint and save as PNG

2. **Snip & Sketch**
   - Press `Win + Shift + S`
   - Choose rectangular snip
   - Click notification to edit
   - Save as PNG

3. **Browser DevTools (Best Quality)**
   - Press `F12` to open DevTools
   - Press `Ctrl + Shift + P`
   - Type "screenshot"
   - Choose "Capture full size screenshot" or "Capture node screenshot"
   - Saves directly to Downloads

### Browser Extensions
- **Awesome Screenshot** (Chrome/Firefox)
- **Nimbus Screenshot** (Chrome)
- **FireShot** (Chrome/Firefox)

---

## 📐 Screenshot Specifications

### Format
- **File Type:** PNG (for best quality and transparency)
- **Recommended Resolution:** 1920x1080 or 1280x720
- **Aspect Ratio:** 16:9 preferred

### Quality Settings
- **DPI:** 96-144 DPI
- **Color Depth:** 24-bit true color
- **Compression:** PNG-8 or PNG-24

### Naming Convention
```
landing.png           (lowercase, hyphenated)
login.png
2fa-verify.png
dashboard.png
file-storage.png
password-checker.png
digital-signature.png
2fa-setup.png
admin-dashboard.png
```

### File Size
- Target: Under 500KB per image
- Use online compression: https://tinypng.com/
- Or ImageOptim (Mac) / FileOptimizer (Windows)

---

## ✨ Screenshot Best Practices

### Do's ✅
- Use consistent browser window size
- Capture same zoom level (100%)
- Show real data (but not sensitive info)
- Include enough context (navbar, etc.)
- Use clean, professional examples
- Crop unnecessary whitespace

### Don'ts ❌
- Don't include personal information
- Don't show real passwords
- Don't use Lorem Ipsum (use real-looking test data)
- Don't capture with browser extensions visible
- Don't include desktop background
- Avoid low resolution or blurry images

---

## 🎨 Editing Screenshots

### Basic Edits (Optional)
1. **Crop** to relevant content area
2. **Add border** (1-2px, subtle gray)
3. **Add shadow** for depth (optional)
4. **Annotate** important features (arrows, highlights)

### Tools
- **Paint.NET** (Windows, Free)
- **GIMP** (Cross-platform, Free)
- **Photopea** (Web-based, Free)
- **Canva** (Web-based, Free/Paid)

### Example Edit Workflow
```
1. Take screenshot with DevTools
2. Open in Paint.NET
3. Crop to content area
4. Resize if needed (keep aspect ratio)
5. Add 1px border (optional)
6. Export as PNG-24
7. Compress with TinyPNG
8. Save to docs/screenshots/
```

---

## 📋 Screenshot Checklist

Before finalizing, ensure:

- [ ] All 9 required screenshots captured
- [ ] Files named correctly (lowercase, hyphens)
- [ ] Saved in `docs/screenshots/` folder
- [ ] PNG format, under 500KB each
- [ ] Resolution 1280x720 or higher
- [ ] No sensitive information visible
- [ ] Dark theme consistent across all
- [ ] Clear and readable text
- [ ] Professional appearance
- [ ] README.md image links working

---

## 🔍 Testing Screenshot Links

After adding screenshots:

```bash
# Navigate to project root
cd e:\CyberShield

# Check if files exist
dir docs\screenshots\

# Verify in README
# Open README.md in browser or GitHub
```

### View README with Images
```bash
# Install markdown viewer (optional)
pip install grip

# Run local server
grip README.md

# Visit http://localhost:6419
```

---

## 📤 Final Steps

1. **Verify all screenshots display correctly**
   - Open README.md in GitHub
   - Or use Markdown preview in VS Code
   - Check that all images load

2. **Optimize file sizes**
   ```bash
   # Use TinyPNG or similar
   # Target: <500KB per image
   ```

3. **Commit to Git**
   ```bash
   git add docs/screenshots/
   git commit -m "Add project screenshots for documentation"
   git push
   ```

4. **Update README if needed**
   - Add captions to screenshots
   - Include descriptions
   - Highlight key features

---

## 🎓 Tips for Professional Screenshots

1. **Consistency is Key**
   - Same browser, same zoom level
   - Same window size for all captures
   - Consistent data across screenshots

2. **Tell a Story**
   - Screenshots should flow logically
   - Landing → Login → Dashboard → Features

3. **Showcase Features**
   - Highlight unique functionality
   - Show real use cases
   - Demonstrate value

4. **Quality Over Quantity**
   - Better to have 5 great screenshots
   - Than 10 mediocre ones

---

## 📞 Need Help?

If you encounter issues:
- Browser not rendering correctly → Clear cache, restart
- Images too large → Use TinyPNG compression
- Can't access admin page → Use default admin account
- 2FA not working → Check Google Authenticator setup

---

**Happy Screenshot Capturing!** 📸✨

For the best README presentation, take your time and ensure each screenshot clearly demonstrates the feature it represents.
