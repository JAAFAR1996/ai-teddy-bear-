import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useService } from '../../dependency-injection';
import { SERVICE_TOKENS } from '../../dependency-injection/container';
import { AuthService } from '../../infrastructure/services/AuthService';
import { Loading } from '../../../components/common/Loading';

export const AuthGuard: React.FC = () => {
  const authService = useService<AuthService>(SERVICE_TOKENS.AUTH_SERVICE);
  const [isAuthenticated, setIsAuthenticated] = React.useState<boolean | null>(null);

  React.useEffect(() => {
    const checkAuth = async () => {
      try {
        const authenticated = await authService.isAuthenticated();
        setIsAuthenticated(authenticated);
      } catch (error) {
        console.error('Auth check failed:', error);
        setIsAuthenticated(false);
      }
    };

    checkAuth();
  }, [authService]);

  if (isAuthenticated === null) {
    return <Loading />;
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}; 