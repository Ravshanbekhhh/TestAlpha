/**
 * Admin authentication logic
 */

const API_BASE = window.location.origin;
let authToken = null;

// Check if logged in
function isLoggedIn() {
    authToken = localStorage.getItem('adminToken');
    return !!authToken;
}

// Show/hide pages
function showLoginPage() {
    document.getElementById('login-page').classList.remove('hidden');
    document.getElementById('admin-panel').classList.add('hidden');
}

function showAdminPanel() {
    document.getElementById('login-page').classList.add('hidden');
    document.getElementById('admin-panel').classList.remove('hidden');
}

// Login
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            throw new Error('Login yoki parol noto\'g\'ri');
        }

        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('adminToken', authToken);

        showAdminPanel();
        loadDashboard();
    } catch (error) {
        alert('Kirish muvaffaqiyatsiz: ' + error.message);
    }
});

// Logout
document.getElementById('logout-btn').addEventListener('click', () => {
    localStorage.removeItem('adminToken');
    authToken = null;
    showLoginPage();
});

// API helper with auth
async function apiRequest(url, options = {}) {
    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
    };

    const response = await fetch(API_BASE + url, options);

    if (response.status === 401) {
        localStorage.removeItem('adminToken');
        showLoginPage();
        throw new Error('Ruxsat berilmagan');
    }

    if (!response.ok) {
        let errorMsg = `Server xatoligi (${response.status})`;
        try {
            const errorData = await response.json();
            if (errorData.detail) {
                if (typeof errorData.detail === 'string') {
                    errorMsg = errorData.detail;
                } else if (Array.isArray(errorData.detail)) {
                    errorMsg = errorData.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ');
                }
            }
        } catch (e) { /* response wasn't JSON */ }
        throw new Error(errorMsg);
    }

    return response;
}

// Initialize
if (isLoggedIn()) {
    showAdminPanel();
} else {
    showLoginPage();
}

window.apiRequest = apiRequest;
