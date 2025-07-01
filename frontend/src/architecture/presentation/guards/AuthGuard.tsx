import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

export const AuthGuard: React.FC = () => {
  // Simple auth check - in production this would check real auth state
  const isAuthenticated = true; // For now, always authenticated

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}; 