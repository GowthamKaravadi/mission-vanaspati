import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { useAuth } from '../../context/AuthContext';
import { adminAPI } from '../../services/api';
import Analytics from './Analytics';
import { TableSkeleton } from '../LoadingSkeleton';
import './Admin.css';

const AdminPanel = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'users', 'analytics', 'feedback'
  const [feedback, setFeedback] = useState([]);
  
  const { logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAdmin) {
      navigate('/');
      return;
    }
    loadUsers();
    if (activeTab === 'feedback') {
      loadFeedback();
    }
  }, [isAdmin, navigate, activeTab]);

  const loadUsers = async () => {
    try {
      const response = await adminAPI.getUsers();
      setUsers(response.data);
    } catch (err) {
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const loadFeedback = async () => {
    try {
      const response = await adminAPI.getFeedback();
      setFeedback(response.data.feedback || []);
    } catch (err) {
      toast.error('Failed to load feedback');
    }
  };

  const handleUpdateFeedbackStatus = async (feedbackId, status) => {
    try {
      await adminAPI.updateFeedbackStatus(feedbackId, status);
      await loadFeedback();
      toast.success(`Feedback marked as ${status}`);
    } catch (err) {
      toast.error('Failed to update feedback status');
    }
  };

  const handleToggleAdmin = async (userId) => {
    try {
      await adminAPI.toggleAdmin(userId);
      await loadUsers();
      toast.success('Admin status updated');
    } catch (err) {
      toast.error('Failed to toggle admin status');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    
    try {
      await adminAPI.deleteUser(userId);
      await loadUsers();
      toast.success('User deleted successfully');
    } catch (err) {
      toast.error('Failed to delete user');
    }
  };

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
    navigate('/login');
  };

  const stats = {
    total: users.length,
    admins: users.filter(u => u.is_admin).length,
    active: users.filter(u => u.is_active).length,
    newThisWeek: users.filter(u => {
      const createdDate = new Date(u.created_at);
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      return createdDate >= weekAgo;
    }).length,
  };

  if (loading) {
    return (
      <div className="admin-panel">
        <header className="admin-header">
          <div className="header-content">
            <div className="logo">
              <span className="logo-icon">A</span>
              <h1>Admin Panel</h1>
            </div>
          </div>
        </header>
        <main className="admin-main">
          <TableSkeleton />
        </main>
      </div>
    );
  }

  return (
    <motion.div 
      className="admin-panel"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <header className="admin-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">🌿</span>
            <h1>Admin Panel</h1>
          </div>
          <div className="header-actions">
            <motion.button 
              onClick={() => navigate('/')} 
              className="btn btn-secondary"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Dashboard
            </motion.button>
            <motion.button 
              onClick={handleLogout} 
              className="btn btn-outline"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Logout
            </motion.button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="admin-tabs">
        <motion.button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
          whileHover={{ y: -2 }}
          whileTap={{ scale: 0.98 }}
        >
          OVERVIEW
        </motion.button>
        <motion.button
          className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
          whileHover={{ y: -2 }}
          whileTap={{ scale: 0.98 }}
        >
          USERS
        </motion.button>
        <motion.button
          className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
          whileHover={{ y: -2 }}
          whileTap={{ scale: 0.98 }}
        >
          ANALYTICS
        </motion.button>
        <motion.button
          className={`tab-btn ${activeTab === 'feedback' ? 'active' : ''}`}
          onClick={() => setActiveTab('feedback')}
          whileHover={{ y: -2 }}
          whileTap={{ scale: 0.98 }}
        >
          FEEDBACK
        </motion.button>
      </div>

      <main className="admin-main">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <div className="stats-grid">
              <motion.div 
                className="stat-card"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
              >
                <div className="stat-icon">U</div>
                <div className="stat-info">
                  <div className="stat-value">{stats.total}</div>
                  <div className="stat-label">Total Users</div>
                </div>
              </motion.div>
              <motion.div 
                className="stat-card"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2 }}
                whileHover={{ scale: 1.05, y: -5 }}
              >
                <div className="stat-icon">A</div>
                <div className="stat-info">
                  <div className="stat-value">{stats.admins}</div>
                  <div className="stat-label">Administrators</div>
                </div>
              </motion.div>
              <motion.div 
                className="stat-card"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.3 }}
                whileHover={{ scale: 1.05, y: -5 }}
              >
                <div className="stat-icon">✓</div>
                <div className="stat-info">
                  <div className="stat-value">{stats.active}</div>
                  <div className="stat-label">Active Users</div>
                </div>
              </motion.div>
              <motion.div 
                className="stat-card"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.4 }}
                whileHover={{ scale: 1.05, y: -5 }}
              >
                <div className="stat-icon">+</div>
                <div className="stat-info">
                  <div className="stat-value">{stats.newThisWeek}</div>
                  <div className="stat-label">New This Week</div>
                </div>
              </motion.div>
            </div>

            {/* Quick Actions */}
            <motion.div 
              className="quick-actions"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <h3>QUICK ACTIONS</h3>
              <div className="actions-grid">
                <motion.button 
                  className="action-card"
                  onClick={() => setActiveTab('users')}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span className="action-icon">U</span>
                  <span className="action-label">Manage Users</span>
                </motion.button>
                <motion.button 
                  className="action-card"
                  onClick={() => setActiveTab('analytics')}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span className="action-icon">A</span>
                  <span className="action-label">View Analytics</span>
                </motion.button>
                <motion.button 
                  className="action-card"
                  onClick={() => navigate('/')}
                  whileHover={{ scale: 1.02, boxShadow: "0 8px 16px rgba(45, 106, 79, 0.2)" }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span className="action-icon">🌿</span>
                  <span className="action-label">Go to Dashboard</span>
                </motion.button>
                <motion.button 
                  className="action-card"
                  onClick={() => window.location.reload()}
                  whileHover={{ scale: 1.02, boxShadow: "0 8px 16px rgba(45, 106, 79, 0.2)" }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span className="action-icon">🔄</span>
                  <span className="action-label">Refresh Data</span>
                </motion.button>
              </div>
            </motion.div>

            {/* Recent Users */}
            <motion.div 
              className="recent-users"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <h3>🆕 Recent Users (Last 5)</h3>
              <div className="recent-users-list">
                {users
                  .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                  .slice(0, 5)
                  .map((user, index) => (
                    <motion.div 
                      key={user.id} 
                      className="recent-user-card"
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: 0.7 + index * 0.1 }}
                    >
                      <div className="user-avatar">
                        {user.username[0].toUpperCase()}
                      </div>
                      <div className="user-details">
                        <strong>{user.username}</strong>
                        <small>{new Date(user.created_at).toLocaleString()}</small>
                      </div>
                      <span className={`role-badge ${user.is_admin ? 'admin' : 'user'}`}>
                        {user.is_admin ? 'Admin' : 'User'}
                      </span>
                    </motion.div>
                  ))}
              </div>
            </motion.div>
          </motion.div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <motion.div
            className="users-section"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <h2>User Management</h2>
            <div className="users-table-container">
              <table className="users-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Role</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user, index) => (
                    <motion.tr 
                      key={user.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <td>{user.id}</td>
                      <td>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          <strong>{user.username}</strong>
                          <small style={{ color: 'var(--text-secondary)', fontSize: '0.85em' }}>{user.email}</small>
                        </div>
                      </td>
                      <td>
                        <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>
                        <span className={`role-badge ${user.is_admin ? 'admin' : 'user'}`}>
                          {user.is_admin ? 'Admin' : 'User'}
                        </span>
                      </td>
                      <td>{new Date(user.created_at).toLocaleDateString()}</td>
                      <td>
                        <div className="action-buttons">
                          <motion.button 
                            onClick={() => handleToggleAdmin(user.id)}
                            className="btn-action btn-toggle"
                            title="Toggle admin status"
                            whileHover={{ scale: 1.2 }}
                            whileTap={{ scale: 0.9 }}
                          >
                            {user.is_admin ? 'U' : 'A'}
                          </motion.button>
                          <motion.button 
                            onClick={() => handleDeleteUser(user.id)}
                            className="btn-action btn-delete"
                            title="Delete user"
                            whileHover={{ scale: 1.2 }}
                            whileTap={{ scale: 0.9 }}
                          >
                            ×
                          </motion.button>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <Analytics users={users} />
        )}

        {/* Feedback Tab */}
        {activeTab === 'feedback' && (
          <motion.div
            className="users-section"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h2>User Feedback & Bug Reports</h2>
            {feedback.length === 0 ? (
              <p style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                No feedback submitted yet
              </p>
            ) : (
              <div className="feedback-list">
                {feedback.map((item) => (
                  <motion.div
                    key={item.id}
                    className="feedback-card"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    whileHover={{ y: -2 }}
                  >
                    <div className="feedback-header-row">
                      <div className="feedback-meta">
                        <span className={`feedback-type ${item.type}`}>
                          {item.type === 'bug' ? 'BUG' : item.type === 'feature' ? 'FEATURE' : 'GENERAL'}
                        </span>
                        <span className={`feedback-status ${item.status}`}>
                          {item.status.toUpperCase()}
                        </span>
                      </div>
                      <small className="feedback-date">
                        {new Date(item.created_at).toLocaleString()}
                      </small>
                    </div>
                    
                    <h3>{item.subject}</h3>
                    <p className="feedback-message">{item.message}</p>
                    
                    <div className="feedback-footer">
                      <span className="feedback-email">{item.email}</span>
                      <div className="feedback-actions">
                        {item.status !== 'reviewed' && (
                          <motion.button
                            onClick={() => handleUpdateFeedbackStatus(item.id, 'reviewed')}
                            className="btn-status btn-reviewed"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            Mark Reviewed
                          </motion.button>
                        )}
                        {item.status !== 'resolved' && (
                          <motion.button
                            onClick={() => handleUpdateFeedbackStatus(item.id, 'resolved')}
                            className="btn-status btn-resolved"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            Mark Resolved
                          </motion.button>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </main>
    </motion.div>
  );
};

export default AdminPanel;
