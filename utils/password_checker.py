"""
utils/password_checker.py
--------------------------
Password Strength Checker module.

Analyses a candidate password across multiple dimensions and returns
a composite score (0-100), a human label, concrete suggestions, and
a rough estimated offline crack time - all computed locally, no
external API calls, so the password is never transmitted anywhere.
"""

import math
import re

COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123", "letmein",
    "monkey", "111111", "welcome", "admin", "iloveyou", "123123",
    "password1", "1234567890", "sunshine", "princess", "football",
    "dragon", "master", "login", "passw0rd", "trustno1",
}

KEYBOARD_PATTERNS = [
    "qwerty", "asdfgh", "zxcvbn", "qwertyuiop", "1qaz2wsx", "123qwe",
]

SEQUENTIAL_PATTERNS = [
    "0123456789", "abcdefghijklmnopqrstuvwxyz",
]


def _has_sequential_run(password: str, run_length: int = 4) -> bool:
    lower = password.lower()
    for seq in SEQUENTIAL_PATTERNS:
        for i in range(len(seq) - run_length + 1):
            if seq[i:i + run_length] in lower:
                return True
            if seq[i:i + run_length][::-1] in lower:
                return True
    return False


def _has_repeated_chars(password: str, run_length: int = 3) -> bool:
    return bool(re.search(r"(.)\1{" + str(run_length - 1) + r",}", password))


def _has_keyboard_pattern(password: str) -> bool:
    lower = password.lower()
    return any(pattern in lower for pattern in KEYBOARD_PATTERNS)


def _has_dictionary_word(password: str) -> bool:
    lower = password.lower()
    return any(word in lower for word in COMMON_PASSWORDS)


def _charset_size(password: str) -> int:
    size = 0
    if re.search(r"[a-z]", password):
        size += 26
    if re.search(r"[A-Z]", password):
        size += 26
    if re.search(r"[0-9]", password):
        size += 10
    if re.search(r"[^a-zA-Z0-9]", password):
        size += 32
    return size or 1


def estimate_crack_time_seconds(password: str, guesses_per_second: float = 1e10) -> float:
    """
    Advanced entropy-based estimate that considers password weaknesses.
    
    Base assumptions:
    - Online attack: 1,000 guesses/sec (rate-limited API)
    - Offline attack (fast hash): 10 billion guesses/sec (GPU rig)
    - Offline attack (slow hash like bcrypt): 100,000 guesses/sec
    
    Adjusts based on:
    - Dictionary words (reduces search space dramatically)
    - Keyboard patterns (predictable sequences)
    - Repeated characters (reduces entropy)
    - Sequential patterns (highly predictable)
    """
    
    if not password:
        return 0
    
    length = len(password)
    charset = _charset_size(password)
    
    # Start with pure brute-force entropy
    entropy_bits = length * math.log2(charset)
    base_combinations = 2 ** entropy_bits
    
    # Apply weakness penalties (reduce effective search space)
    penalty_factor = 1.0
    
    # Dictionary word penalty - makes it 1000x easier to crack
    if _has_dictionary_word(password):
        penalty_factor *= 0.001  # Reduce to 0.1% of original strength
    
    # Keyboard pattern penalty - reduces by 100x
    if _has_keyboard_pattern(password):
        penalty_factor *= 0.01
    
    # Sequential characters - reduces by 50x
    if _has_sequential_run(password, 3):
        penalty_factor *= 0.02
    
    # Repeated characters - reduces by 10x
    if _has_repeated_chars(password, 3):
        penalty_factor *= 0.1
    
    # Short password additional penalty
    if length < 8:
        penalty_factor *= 0.1  # Very short passwords are 10x easier
    elif length < 12:
        penalty_factor *= 0.5  # Somewhat short passwords are 2x easier
    
    # Calculate effective combinations after penalties
    effective_combinations = base_combinations * penalty_factor
    
    # Assume offline attack with GPU (worst case for user)
    seconds = effective_combinations / guesses_per_second
    
    return max(0.001, seconds)  # Minimum 1ms


def humanize_seconds(seconds: float) -> str:
    """
    Convert seconds to human-readable time format with detailed breakdown.
    """
    if seconds < 0.001:
        return "instantly"
    
    if seconds < 1:
        return f"{seconds * 1000:.1f} milliseconds"
    
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    
    if seconds < 3600:  # Less than 1 hour
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    
    if seconds < 86400:  # Less than 1 day
        hours = seconds / 3600
        return f"{hours:.1f} hours"
    
    if seconds < 2592000:  # Less than 30 days
        days = seconds / 86400
        return f"{days:.1f} days"
    
    if seconds < 31536000:  # Less than 1 year
        months = seconds / 2592000
        return f"{months:.1f} months"
    
    if seconds < 3153600000:  # Less than 100 years
        years = seconds / 31536000
        return f"{years:.1f} years"
    
    if seconds < 31536000000:  # Less than 1000 years
        centuries = seconds / 3153600000
        return f"{centuries:.1f} centuries"
    
    if seconds < 31536000000000:  # Less than 1 million years
        millennia = seconds / 31536000000
        return f"{millennia:.1f} millennia"
    
    # Beyond comprehension
    return "billions of years (effectively uncrackable)"


def check_password_strength(password: str) -> dict:
    """
    Returns a dict:
    {
        score: int (0-100),
        label: str,
        suggestions: [str, ...],
        estimated_crack_time: str,
        checks: {rule_name: bool, ...}
    }
    """
    suggestions = []
    checks = {}

    length = len(password)
    checks["length_ok"] = length >= 12
    checks["has_upper"] = bool(re.search(r"[A-Z]", password))
    checks["has_lower"] = bool(re.search(r"[a-z]", password))
    checks["has_digit"] = bool(re.search(r"[0-9]", password))
    checks["has_special"] = bool(re.search(r"[^a-zA-Z0-9]", password))
    checks["no_repeats"] = not _has_repeated_chars(password)
    checks["no_dictionary_word"] = not _has_dictionary_word(password)
    checks["no_keyboard_pattern"] = not _has_keyboard_pattern(password)
    checks["no_sequential"] = not _has_sequential_run(password)

    # --- Scoring (weighted, out of 100) ---
    score = 0
    score += min(length, 20) * 2          # up to 40 pts for length (20 chars = max)
    score += 10 if checks["has_upper"] else 0
    score += 10 if checks["has_lower"] else 0
    score += 10 if checks["has_digit"] else 0
    score += 15 if checks["has_special"] else 0
    score += 5 if checks["no_repeats"] else -10
    score += 5 if checks["no_dictionary_word"] else -25
    score += 5 if checks["no_keyboard_pattern"] else -15
    score += 5 if checks["no_sequential"] else -10
    score = max(0, min(100, score))

    # --- Suggestions ---
    if not checks["length_ok"]:
        suggestions.append("Use at least 12 characters.")
    if not checks["has_upper"]:
        suggestions.append("Add at least one uppercase letter.")
    if not checks["has_lower"]:
        suggestions.append("Add at least one lowercase letter.")
    if not checks["has_digit"]:
        suggestions.append("Add at least one number.")
    if not checks["has_special"]:
        suggestions.append("Add at least one special character (e.g. !@#$%).")
    if not checks["no_repeats"]:
        suggestions.append("Avoid repeating the same character multiple times in a row.")
    if not checks["no_dictionary_word"]:
        suggestions.append("Avoid common dictionary words or well-known passwords.")
    if not checks["no_keyboard_pattern"]:
        suggestions.append("Avoid keyboard patterns like 'qwerty' or 'asdfgh'.")
    if not checks["no_sequential"]:
        suggestions.append("Avoid sequential characters like '1234' or 'abcd'.")

    if score >= 85:
        label = "Very Strong"
    elif score >= 65:
        label = "Strong"
    elif score >= 45:
        label = "Good"
    elif score >= 25:
        label = "Fair"
    else:
        label = "Weak"

    crack_seconds = estimate_crack_time_seconds(password)
    crack_time_str = humanize_seconds(crack_seconds)
    
    # Calculate attack scenario times
    online_attack_seconds = crack_seconds * 10000  # Online is 10000x slower
    bcrypt_attack_seconds = crack_seconds / 100  # bcrypt is 100x slower than fast hash

    return {
        "score": score,
        "label": label,
        "suggestions": suggestions,
        "estimated_crack_time": crack_time_str,
        "online_attack_time": humanize_seconds(online_attack_seconds),
        "offline_fast_hash": crack_time_str,
        "offline_slow_hash": humanize_seconds(bcrypt_attack_seconds),
        "checks": checks,
        "entropy_bits": len(password) * math.log2(_charset_size(password)),
    }
