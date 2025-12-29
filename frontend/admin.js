const API_URL = 'http://localhost:8000';

const token = localStorage.getItem('token');
const isAdmin = localStorage.getItem('isAdmin') === 'true';

if (!token || !isAdmin) {
    window.location.href = 'login.html';
}

async function fetchUsers() {
    try {
        const response = await fetch(`${API_URL}/admin/users`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.status === 401 || response.status === 403) {
            localStorage.clear();
            window.location.href = 'login.html';
            return;
        }

        const users = await response.json();
        displayUsers(users);
        updateStats(users);
    } catch (error) {
        document.getElementById('usersTableContainer').innerHTML = 
            '<p style="color: var(--danger);">Failed to load users. Please refresh the page.</p>';
    }
}

function displayUsers(users) {
    const container = document.getElementById('usersTableContainer');
    
    if (users.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--gray);">No users found.</p>';
        return;
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Role</th>
                    <th>Created At</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    users.forEach(user => {
        const createdDate = new Date(user.created_at).toLocaleDateString();
        html += `
            <tr>
                <td>${user.email}</td>
                <td>
                    <span class="badge ${user.is_active ? 'badge-active' : 'badge-inactive'}">
                        ${user.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td>
                    <span class="badge ${user.is_admin ? 'badge-admin' : 'badge-user'}">
                        ${user.is_admin ? 'Admin' : 'User'}
                    </span>
                </td>
                <td>${createdDate}</td>
                <td>
                    <button class="action-btn btn-toggle" onclick="toggleAdmin(${user.id})">
                        ${user.is_admin ? 'Remove Admin' : 'Make Admin'}
                    </button>
                    <button class="action-btn btn-delete" onclick="deleteUser(${user.id}, '${user.email}')">
                        Delete
                    </button>
                </td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

function updateStats(users) {
    document.getElementById('totalUsers').textContent = users.length;
    document.getElementById('adminUsers').textContent = users.filter(u => u.is_admin).length;
    document.getElementById('activeUsers').textContent = users.filter(u => u.is_active).length;
}

async function toggleAdmin(userId) {
    if (!confirm('Are you sure you want to change this user\'s admin status?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/admin/users/${userId}/toggle-admin`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            fetchUsers();
        } else {
            alert(data.detail || 'Failed to update admin status');
        }
    } catch (error) {
        alert('Network error. Please try again.');
    }
}

async function deleteUser(userId, email) {
    if (!confirm(`Are you sure you want to delete user: ${email}?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/admin/users/${userId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            fetchUsers();
        } else {
            alert(data.detail || 'Failed to delete user');
        }
    } catch (error) {
        alert('Network error. Please try again.');
    }
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.clear();
        window.location.href = 'login.html';
    }
}

fetchUsers();
