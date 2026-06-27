import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

// API Base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Axios instance with interceptor
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is logged in on mount
  useEffect(() => {
    console.log('[AUTH] Checking for existing session...');
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    console.log('[AUTH] Token found:', !!token);
    console.log('[AUTH] User data found:', !!userData);
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        console.log('[AUTH] Parsed user data:', parsedUser);
        setUser(parsedUser);
        console.log('[AUTH] Session restored for user:', parsedUser.username);
      } catch (error) {
        console.error('[AUTH] Failed to parse user data:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    } else {
      console.log('[AUTH] No existing session found');
    }
    
    setLoading(false);
    console.log('[AUTH] Auth initialization complete');
  }, []);

  const login = async (username, password) => {
    try {
      console.log('[AUTH] Login attempt:', username);
      
      // Login request using FormData for OAuth2PasswordRequestForm
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      console.log('[AUTH] Sending login request to:', `${API_BASE_URL}/auth/login`);
      const response = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      console.log('[AUTH] Login response received:', response.data);
      const { access_token } = response.data;

      // Store token
      console.log('[AUTH] Storing token in localStorage');
      localStorage.setItem('token', access_token);
      console.log('[AUTH] Token stored:', access_token.substring(0, 50) + '...');

      // Get user info
      console.log('[AUTH] Fetching user info from:', `${API_BASE_URL}/auth/me`);
      const userResponse = await axios.get(`${API_BASE_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      });

      console.log('[AUTH] User info received:', userResponse.data);
      const userData = userResponse.data;
      localStorage.setItem('user', JSON.stringify(userData));
      console.log('[AUTH] User data stored in localStorage');
      
      setUser(userData);
      console.log('[AUTH] AuthContext user state updated:', userData);

      return { success: true, user: userData };
    } catch (error) {
      console.error('[AUTH] Login error:', error);
      console.error('[AUTH] Error details:', error.response?.data);
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed. Please check your credentials.',
      };
    }
  };

  const logout = () => {
    console.log('[AUTH] Logout initiated');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    console.log('[AUTH] Logout complete - token and user cleared');
  };

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
    api, // Expose api instance for authenticated requests
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
