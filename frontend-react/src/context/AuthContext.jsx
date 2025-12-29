import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await authAPI.getCurrentUser();
        setUser(response.data);
      } catch (error) {
        localStorage.removeItem('token');
        localStorage.removeItem('email');
        localStorage.removeItem('isAdmin');
      }
    }
    setLoading(false);
  };

  const login = async (usernameOrEmail, password) => {
    const response = await authAPI.login(usernameOrEmail, password);
    const { access_token, username, email, is_admin } = response.data;
    
    localStorage.setItem('token', access_token);
    localStorage.setItem('username', username);
    localStorage.setItem('email', email);
    localStorage.setItem('isAdmin', is_admin);
    
    setUser({ username, email, is_admin });
    return response.data;
  };

  const signup = async (username, email, password) => {
    return await authAPI.signup(username, email, password);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('email');
    localStorage.removeItem('isAdmin');
    setUser(null);
  };

  const value = {
    user,
    login,
    signup,
    logout,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.is_admin || false,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
