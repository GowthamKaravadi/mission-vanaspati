const API_URL = 'http://localhost:8000';

function showAlert(message, type = 'error') {
    const alert = document.getElementById('alert');
    alert.textContent = message;
    alert.className = `alert alert-${type} show`;
    
    setTimeout(() => {
        alert.classList.remove('show');
    }, 5000);
}

if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const loginBtn = document.getElementById('loginBtn');
        
        loginBtn.disabled = true;
        loginBtn.textContent = 'Signing in...';
        
        try {
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);
            
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('email', data.email);
                localStorage.setItem('isAdmin', data.is_admin);
                
                showAlert('Login successful! Redirecting...', 'success');
                
                setTimeout(() => {
                    if (data.is_admin) {
                        window.location.href = 'admin.html';
                    } else {
                        window.location.href = 'index.html';
                    }
                }, 1000);
            } else {
                showAlert(data.detail || 'Login failed. Please check your credentials.');
            }
        } catch (error) {
            showAlert('Network error. Please try again.');
        } finally {
            loginBtn.disabled = false;
            loginBtn.textContent = 'Sign In';
        }
    });
}

if (document.getElementById('signupForm')) {
    document.getElementById('signupForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const signupBtn = document.getElementById('signupBtn');
        
        if (password !== confirmPassword) {
            showAlert('Passwords do not match!');
            return;
        }
        
        if (password.length < 8) {
            showAlert('Password must be at least 8 characters long');
            return;
        }
        
        if (!/[A-Z]/.test(password)) {
            showAlert('Password must contain at least one uppercase letter');
            return;
        }
        
        if (!/[0-9]/.test(password)) {
            showAlert('Password must contain at least one number');
            return;
        }
        
        signupBtn.disabled = true;
        signupBtn.textContent = 'Creating account...';
        
        try {
            const response = await fetch(`${API_URL}/auth/signup?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showAlert('Account created successfully! Redirecting to login...', 'success');
                
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000);
            } else {
                showAlert(data.detail || 'Signup failed. Please try again.');
            }
        } catch (error) {
            showAlert('Network error. Please try again.');
        } finally {
            signupBtn.disabled = false;
            signupBtn.textContent = 'Create Account';
        }
    });
}
