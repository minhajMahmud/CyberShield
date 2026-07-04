// CyberShield - main.js
// Global small enhancements (auto-dismiss alerts, etc.)

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach((alertEl) => {
    setTimeout(() => {
      const alert = bootstrap.Alert.getOrCreateInstance(alertEl);
      alert.close();
    }, 6000);
  });
});
