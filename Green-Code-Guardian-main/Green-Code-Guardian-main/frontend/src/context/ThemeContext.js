import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(() => {
    // Check localStorage or default to dark
    const saved = localStorage.getItem('theme');
    return saved !== null ? saved === 'dark' : true;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
      // Dark theme properties
      root.style.setProperty('--green-primary', '#22c55e');
      root.style.setProperty('--green-dim', '#16a34a');
      root.style.setProperty('--green-glow', 'rgba(34, 197, 94, 0.3)');
      root.style.setProperty('--bg-primary', '#020b02');
      root.style.setProperty('--bg-secondary', '#050f05');
      root.style.setProperty('--bg-card', '#0a1a0a');
      root.style.setProperty('--bg-card-hover', '#0d2110');
      root.style.setProperty('--text-primary', '#e2ffe2');
      root.style.setProperty('--text-secondary', '#86efac');
      root.style.setProperty('--text-muted', '#4ade80');
      root.style.setProperty('--border-color', 'rgba(34, 197, 94, 0.2)');
    } else {
      root.classList.remove('dark');
      // Light theme properties
      root.style.setProperty('--green-primary', '#16a34a');
      root.style.setProperty('--green-dim', '#15803d');
      root.style.setProperty('--green-glow', 'rgba(22, 163, 74, 0.3)');
      root.style.setProperty('--bg-primary', '#f0fdf4');
      root.style.setProperty('--bg-secondary', '#dcfce7');
      root.style.setProperty('--bg-card', '#ffffff');
      root.style.setProperty('--bg-card-hover', '#f0fdf4');
      root.style.setProperty('--text-primary', '#052e16');
      root.style.setProperty('--text-secondary', '#14532d');
      root.style.setProperty('--text-muted', '#166534');
      root.style.setProperty('--border-color', 'rgba(22, 163, 74, 0.2)');
    }
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  const toggleTheme = () => {
    setIsDark(!isDark);
  };

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};