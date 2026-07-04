/**
 * CyberShield Session Manager
 * 
 * Manages cross-tab logout detection and automatic session synchronization.
 * When a user logs out from one tab, all other tabs are automatically logged out.
 */

(function () {
    'use strict';

    // Session key in localStorage
    const SESSION_KEY = 'cybershield_session_active';
    const SESSION_CHECK_INTERVAL = 1000; // Check every 1 second

    // Generate unique session ID when user logs in
    function generateSessionId() {
        return Date.now() + '_' + Math.random().toString(36).substring(2, 15);
    }

    // Check if user is currently on an authenticated page
    function isAuthenticatedPage() {
        // Check if user info is in the navbar (means logged in)
        return document.querySelector('.navbar .dropdown-toggle') !== null;
    }

    // Initialize session on login
    function initSession() {
        if (isAuthenticatedPage()) {
            const sessionId = generateSessionId();
            localStorage.setItem(SESSION_KEY, sessionId);
            console.log('[Session Manager] Session initialized:', sessionId);
        }
    }

    // Clear session on logout
    function clearSession() {
        localStorage.removeItem(SESSION_KEY);
        console.log('[Session Manager] Session cleared');
    }

    // Monitor session changes (cross-tab communication)
    function monitorSession() {
        let lastSessionId = localStorage.getItem(SESSION_KEY);

        setInterval(() => {
            const currentSessionId = localStorage.getItem(SESSION_KEY);

            // If session was active but now removed, user logged out from another tab
            if (lastSessionId && !currentSessionId) {
                console.log('[Session Manager] Session removed in another tab. Logging out...');
                handleCrossTabLogout();
            }

            lastSessionId = currentSessionId;
        }, SESSION_CHECK_INTERVAL);
    }

    // Handle logout detected from another tab
    function handleCrossTabLogout() {
        // Show notification
        showLogoutNotification();

        // Redirect to login page after a short delay
        setTimeout(() => {
            window.location.href = '/login?reason=session_expired';
        }, 2000);
    }

    // Show logout notification
    function showLogoutNotification() {
        // Create alert element
        const alert = document.createElement('div');
        alert.className = 'alert alert-warning alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
        alert.style.zIndex = '9999';
        alert.style.minWidth = '400px';
        alert.innerHTML = `
            <i class="bi bi-exclamation-triangle-fill"></i>
            <strong>Session Ended</strong><br>
            You have been logged out from another tab. Redirecting to login...
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alert);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    // Listen for storage events (fires when localStorage changes in other tabs)
    window.addEventListener('storage', (event) => {
        if (event.key === SESSION_KEY && event.oldValue && !event.newValue) {
            // Session was removed in another tab
            console.log('[Session Manager] Storage event: Session removed');
            handleCrossTabLogout();
        }
    });

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', () => {
        if (isAuthenticatedPage()) {
            // User is logged in, ensure session is active
            if (!localStorage.getItem(SESSION_KEY)) {
                initSession();
            }

            // Start monitoring for cross-tab changes
            monitorSession();

            console.log('[Session Manager] Active session monitoring started');
        }
    });

    // Expose function to be called on logout
    window.cybershieldClearSession = clearSession;

})();
