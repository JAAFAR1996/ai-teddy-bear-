import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authAPI, apiUtils } from '../services/api';
import toast from 'react-hot-toast';

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Action types
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  LOAD_USER_START: 'LOAD_USER_START',
  LOAD_USER_SUCCESS: 'LOAD_USER_SUCCESS',
  LOAD_USER_FAILURE: 'LOAD_USER_FAILURE',
  UPDATE_USER: 'UPDATE_USER',
  CLEAR_ERROR: 'CLEAR_ERROR',
};

// Reducer function
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
    case AUTH_ACTIONS.LOAD_USER_START:
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_SUCCESS:
    case AUTH_ACTIONS.LOAD_USER_SUCCESS:
      return {
        ...state,
        isLoading: false,
        isAuthenticated: true,
        user: action.payload,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_FAILURE:
    case AUTH_ACTIONS.LOAD_USER_FAILURE:
      return {
        ...state,
        isLoading: false,
        isAuthenticated: false,
        user: null,
        error: action.payload,
      };

    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        isLoading: false,
        isAuthenticated: false,
        user: null,
        error: null,
      };

    case AUTH_ACTIONS.UPDATE_USER:
      return {
        ...state,
        user: { ...state.user, ...action.payload },
      };

    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    default:
      return state;
  }
};

// Create context
const AuthContext = createContext();

// AuthProvider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Load user on app start
  useEffect(() => {
    const loadUser = async () => {
      if (apiUtils.isAuthenticated()) {
        dispatch({ type: AUTH_ACTIONS.LOAD_USER_START });
        
        try {
          // Try to get user from localStorage first
          const cachedUser = apiUtils.getUserData();
          if (cachedUser) {
            dispatch({ 
              type: AUTH_ACTIONS.LOAD_USER_SUCCESS, 
              payload: cachedUser 
            });
            
            // Verify token validity in background
            try {
              const user = await authAPI.getCurrentUser();
              dispatch({ 
                type: AUTH_ACTIONS.UPDATE_USER, 
                payload: user 
              });
            } catch (error) {
              // Token invalid, logout silently
              if (error.response?.status === 401) {
                logout();
              }
            }
          } else {
            // No cached user, fetch from server
            const user = await authAPI.getCurrentUser();
            dispatch({ 
              type: AUTH_ACTIONS.LOAD_USER_SUCCESS, 
              payload: user 
            });
          }
        } catch (error) {
          dispatch({ 
            type: AUTH_ACTIONS.LOAD_USER_FAILURE, 
            payload: apiUtils.formatError(error) 
          });
          apiUtils.clearAuthData();
        }
      } else {
        dispatch({ type: AUTH_ACTIONS.LOAD_USER_FAILURE, payload: null });
      }
    };

    loadUser();
  }, []);

  // Login function
  const login = async (credentials) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });
    
    try {
      const response = await authAPI.login(credentials);
      
      dispatch({ 
        type: AUTH_ACTIONS.LOGIN_SUCCESS, 
        payload: response.user 
      });
      
      toast.success(`مرحباً ${response.user.name}! تم تسجيل الدخول بنجاح.`);
      return response;
    } catch (error) {
      const errorMessage = apiUtils.formatError(error);
      dispatch({ 
        type: AUTH_ACTIONS.LOGIN_FAILURE, 
        payload: errorMessage 
      });
      throw error;
    }
  };

  // Register function
  const register = async (userData) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });
    
    try {
      const response = await authAPI.register(userData);
      
      // Auto-login after registration
      if (response.token) {
        dispatch({ 
          type: AUTH_ACTIONS.LOGIN_SUCCESS, 
          payload: response.user 
        });
        
        toast.success(`مرحباً ${response.user.name}! تم إنشاء حسابك بنجاح.`);
      }
      
      return response;
    } catch (error) {
      const errorMessage = apiUtils.formatError(error);
      dispatch({ 
        type: AUTH_ACTIONS.LOGIN_FAILURE, 
        payload: errorMessage 
      });
      throw error;
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
      toast.success('تم تسجيل الخروج بنجاح.');
    }
  };

  // Update user data
  const updateUser = (userData) => {
    dispatch({ 
      type: AUTH_ACTIONS.UPDATE_USER, 
      payload: userData 
    });
    
    // Update localStorage
    const currentUser = apiUtils.getUserData();
    const updatedUser = { ...currentUser, ...userData };
    localStorage.setItem('userData', JSON.stringify(updatedUser));
  };

  // Clear error
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // Refresh token
  const refreshToken = async () => {
    try {
      await authAPI.refreshToken();
      return true;
    } catch (error) {
      logout();
      return false;
    }
  };

  // Context value
  const value = {
    // State
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    error: state.error,
    
    // Actions
    login,
    register,
    logout,
    updateUser,
    clearError,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

// HOC for protected routes
export const withAuth = (Component) => {
  return function AuthenticatedComponent(props) {
    const { isAuthenticated, isLoading } = useAuth();
    
    if (isLoading) {
      return (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div style={{ marginTop: '20px', color: '#007bff' }}>
            جاري تحميل بيانات المستخدم...
          </div>
        </div>
      );
    }
    
    if (!isAuthenticated) {
      window.location.href = '/login';
      return null;
    }
    
    return <Component {...props} />;
  };
};

export default AuthContext; 