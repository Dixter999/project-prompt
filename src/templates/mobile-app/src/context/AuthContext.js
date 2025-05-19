import React, { createContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authService } from '../services/authService';

// Create the auth context
export const AuthContext = createContext();

/**
 * AuthProvider component for managing authentication state
 * Handles login, logout, token management, and user data
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for existing token on app start
  useEffect(() => {
    const bootstrapAsync = async () => {
      try {
        // Retrieve stored token
        const storedToken = await AsyncStorage.getItem('userToken');
        
        if (storedToken) {
          // Validate token and get user data
          const userData = await authService.getUserProfile(storedToken);
          setUser(userData);
          setToken(storedToken);
        }
      } catch (error) {
        console.error('Authentication restore error:', error);
      } finally {
        setLoading(false);
      }
    };

    bootstrapAsync();
  }, []);

  // Login function
  const login = async (email, password) => {
    try {
      setLoading(true);
      const response = await authService.login(email, password);
      
      // Store the token
      await AsyncStorage.setItem('userToken', response.token);
      
      // Set context state
      setUser(response.user);
      setToken(response.token);
      
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.message || 'Failed to login' 
      };
    } finally {
      setLoading(false);
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      setLoading(true);
      const response = await authService.register(userData);
      return { success: true, data: response };
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.message || 'Failed to register' 
      };
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    try {
      setLoading(true);
      
      // Clear stored token
      await AsyncStorage.removeItem('userToken');
      
      // Reset context state
      setUser(null);
      setToken(null);
      
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  // Context value with authentication state and functions
  const authContext = {
    user,
    token,
    loading,
    isAuthenticated: !!token,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={authContext}>
      {children}
    </AuthContext.Provider>
  );
};
