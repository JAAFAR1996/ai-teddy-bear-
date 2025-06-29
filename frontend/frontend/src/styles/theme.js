import styled, { createGlobalStyle } from 'styled-components';

// Color palette
export const colors = {
  // Primary colors
  primary: '#007bff',
  primaryLight: '#66b3ff',
  primaryDark: '#0056b3',
  
  // Secondary colors
  secondary: '#6c757d',
  secondaryLight: '#9ca0a5',
  secondaryDark: '#495057',
  
  // Status colors
  success: '#28a745',
  successLight: '#6bbf73',
  successDark: '#1e7e34',
  
  danger: '#dc3545',
  dangerLight: '#e5838b',
  dangerDark: '#a71e2a',
  
  warning: '#ffc107',
  warningLight: '#ffe066',
  warningDark: '#d49c04',
  
  info: '#17a2b8',
  infoLight: '#6cc5d0',
  infoDark: '#117a8b',
  
  // Neutral colors
  light: '#f8f9fa',
  lightGray: '#e9ecef',
  gray: '#6c757d',
  darkGray: '#495057',
  dark: '#343a40',
  darker: '#212529',
  
  // Background colors
  background: '#f5f7fa',
  backgroundDark: '#1a1d21',
  surface: '#ffffff',
  surfaceDark: '#2d3748',
  
  // Text colors
  text: '#2d3748',
  textSecondary: '#4a5568',
  textMuted: '#718096',
  textLight: '#ffffff',
  
  // Border colors
  border: '#e2e8f0',
  borderLight: '#f1f5f9',
  borderDark: '#2d3748',
  
  // Gradient colors
  gradientPrimary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  gradientSecondary: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  gradientSuccess: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  
  // Teddy Bear brand colors
  teddyBrown: '#8B4513',
  teddyBrownLight: '#CD853F',
  teddyBrownDark: '#654321',
  teddyGold: '#FFD700',
  teddyRed: '#DC143C',
};

// Spacing system (rem units)
export const spacing = {
  xs: '0.25rem',    // 4px
  sm: '0.5rem',     // 8px
  md: '1rem',       // 16px
  lg: '1.5rem',     // 24px
  xl: '2rem',       // 32px
  xxl: '3rem',      // 48px
  xxxl: '4rem',     // 64px
};

// Typography
export const typography = {
  // Font families
  fontFamily: {
    arabic: "'Tajawal', sans-serif",
    english: "'Inter', sans-serif",
    monospace: "'Fira Code', 'Consolas', monospace",
  },
  
  // Font sizes
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem', // 36px
    '5xl': '3rem',    // 48px
    '6xl': '4rem',    // 64px
  },
  
  // Font weights
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
    black: 900,
  },
  
  // Line heights
  lineHeight: {
    tight: 1.25,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 2,
  },
};

// Shadows
export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
  none: 'none',
};

// Border radius
export const borderRadius = {
  none: '0',
  sm: '0.125rem',
  base: '0.25rem',
  md: '0.375rem',
  lg: '0.5rem',
  xl: '0.75rem',
  '2xl': '1rem',
  '3xl': '1.5rem',
  full: '9999px',
};

// Breakpoints for responsive design
export const breakpoints = {
  xs: '320px',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

// Media queries helper
export const mediaQueries = {
  xs: `@media (min-width: ${breakpoints.xs})`,
  sm: `@media (min-width: ${breakpoints.sm})`,
  md: `@media (min-width: ${breakpoints.md})`,
  lg: `@media (min-width: ${breakpoints.lg})`,
  xl: `@media (min-width: ${breakpoints.xl})`,
  '2xl': `@media (min-width: ${breakpoints['2xl']})`,
  
  // Max width queries
  maxXs: `@media (max-width: ${breakpoints.xs})`,
  maxSm: `@media (max-width: ${breakpoints.sm})`,
  maxMd: `@media (max-width: ${breakpoints.md})`,
  maxLg: `@media (max-width: ${breakpoints.lg})`,
  maxXl: `@media (max-width: ${breakpoints.xl})`,
  
  // Orientation
  landscape: '@media (orientation: landscape)',
  portrait: '@media (orientation: portrait)',
  
  // Retina displays
  retina: '@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi)',
};

// Complete theme object
export const theme = {
  colors,
  spacing,
  typography,
  shadows,
  borderRadius,
  breakpoints,
  mediaQueries,
};

export default theme;