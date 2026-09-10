import { createContext, useState, useEffect, useContext } from 'react';
import * as api from '../services/api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      if (token) {
        try {
          const user = await api.getMe();
          setCurrentUser(user);
        } catch (err) {
          console.error("Session expired or invalid", err);
          logout();
        }
      }
      setLoading(false);
    }
    
    loadUser();
  }, [token]);

  const login = async (email, password) => {
    try {
      const response = await api.login(email, password);
      const access_token = response.access_token;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Token will trigger useEffect to load currentUser, but we can do it immediately:
      const user = await api.getMe();
      setCurrentUser(user);
      return true;
    } catch (err) {
      console.error("Login failed", err);
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setCurrentUser(null);
  };

  const value = {
    currentUser,
    token,
    isAuthenticated: !!currentUser,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
