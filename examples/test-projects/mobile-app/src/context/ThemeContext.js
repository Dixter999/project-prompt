import React, { createContext, useState, useEffect } from 'react';
import { useColorScheme } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Define theme colors
const themes = {
  light: {
    primary: '#4F6D7A',
    secondary: '#86BBD8',
    background: '#F5FCFF',
    card: '#FFFFFF',
    text: '#333333',
    border: '#DDDDDD',
    notification: '#FF6B6B',
    success: '#4BB543',
    warning: '#FFCC00',
    error: '#FF3B30',
  },
  dark: {
    primary: '#4F6D7A',
    secondary: '#6B98B2',
    background: '#121212',
    card: '#1E1E1E',
    text: '#F5F5F5',
    border: '#444444',
    notification: '#FF6B6B',
    success: '#4BB543',
    warning: '#FFCC00',
    error: '#FF3B30',
  }
};

// Create theme context
export const ThemeContext = createContext();

/**
 * Theme provider component that manages app theme settings
 * Supports system theme, light theme, and dark theme
 */
export const ThemeProvider = ({ children }) => {
  // Get system color scheme
  const deviceTheme = useColorScheme();
  
  // Initialize theme state
  const [themeMode, setThemeMode] = useState('system');
  const [loading, setLoading] = useState(true);
  
  // Load saved theme preference on mount
  useEffect(() => {
    const loadThemePreference = async () => {
      try {
        const savedThemeMode = await AsyncStorage.getItem('themeMode');
        if (savedThemeMode) {
          setThemeMode(savedThemeMode);
        }
      } catch (error) {
        console.error('Failed to load theme preference:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadThemePreference();
  }, []);
  
  // Save theme preference when it changes
  useEffect(() => {
    const saveThemePreference = async () => {
      try {
        if (!loading) {
          await AsyncStorage.setItem('themeMode', themeMode);
        }
      } catch (error) {
        console.error('Failed to save theme preference:', error);
      }
    };
    
    saveThemePreference();
  }, [themeMode, loading]);
  
  // Determine active theme based on theme mode
  const getActiveTheme = () => {
    if (themeMode === 'system') {
      return deviceTheme === 'dark' ? themes.dark : themes.light;
    } else {
      return themeMode === 'dark' ? themes.dark : themes.light;
    }
  };
  
  // Change theme function
  const changeTheme = (newThemeMode) => {
    if (['light', 'dark', 'system'].includes(newThemeMode)) {
      setThemeMode(newThemeMode);
    }
  };
  
  // Theme context value with current theme and functions
  const themeContext = {
    theme: getActiveTheme(),
    themeMode,
    isDark: themeMode === 'dark' || (themeMode === 'system' && deviceTheme === 'dark'),
    changeTheme,
    loading,
  };
  
  return (
    <ThemeContext.Provider value={themeContext}>
      {children}
    </ThemeContext.Provider>
  );
};
