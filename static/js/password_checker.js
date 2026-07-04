// CyberShield - password_checker.js
// Calls the /api/password-check endpoint and returns the parsed result.

async function cybershieldCheckPassword(password) {
  const response = await fetch('/api/password-check', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  });
  if (!response.ok) {
    return { score: 0, label: 'Error', suggestions: [], estimated_crack_time: '—' };
  }
  return response.json();
}

function cybershieldBarColor(score) {
  if (score >= 85) return 'bar-very-strong';
  if (score >= 65) return 'bar-strong';
  if (score >= 45) return 'bar-good';
  if (score >= 25) return 'bar-fair';
  return 'bar-weak';
}
