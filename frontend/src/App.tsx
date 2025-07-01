import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { HelmetProvider } from 'react-helmet-async';
import { I18nextProvider } from 'react-i18next';
import { ThemeProvider } from 'styled-components';
import { AnimatePresence } from 'framer-motion';

// Clean Architecture imports
import { DIProvider } from './architecture/dependency-injection';
import { container } from './architecture/dependency-injection/container';

// Domain imports
import { AuthGuard } from './architecture/presentation/guards/AuthGuard';

// Presentation Layer Components
import { Layout } from './components/layout/Layout';
import Dashboard from './components/Dashboard';
import { Conversations } from './components/conversations/Conversations';
import { ChildProfile } from './components/child/ChildProfile';
import { Settings } from './components/settings/Settings';
import { Login } from './components/auth/Login';
import { Reports } from './components/reports/Reports';
import { Emergency } from './components/emergency/Emergency';
import { Analytics } from './components/analytics/Analytics';
import { ErrorBoundary } from './components/ErrorBoundary';

// Styles and themes
import { GlobalStyles } from './styles/GlobalStyles';
import { theme } from './styles/theme';
import i18n from './config/i18n';

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const App: React.FC = () => {
  return (
    <HelmetProvider>
      <I18nextProvider i18n={i18n}>
        <QueryClientProvider client={queryClient}>
          <DIProvider container={container}>
            <ThemeProvider theme={theme}>
              <GlobalStyles />
              <ErrorBoundary>
                <Router>
                  <AnimatePresence mode="wait">
                    <Routes>
                      {/* Public routes */}
                      <Route path="/login" element={<Login />} />
                      
                      {/* Protected routes */}
                      <Route element={<AuthGuard />}>
                        <Route element={<Layout />}>
                          <Route path="/" element={<Navigate to="/dashboard" replace />} />
                          <Route path="/dashboard" element={<Dashboard />} />
                          <Route path="/conversations" element={<Conversations />} />
                          <Route path="/conversations/:conversationId" element={<Conversations />} />
                          <Route path="/child-profile" element={<ChildProfile />} />
                          <Route path="/reports" element={<Reports />} />
                          <Route path="/analytics" element={<Analytics />} />
                          <Route path="/emergency" element={<Emergency />} />
                          <Route path="/settings" element={<Settings />} />
                        </Route>
                      </Route>
                      
                      {/* 404 route */}
                      <Route path="*" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                  </AnimatePresence>
                </Router>
              </ErrorBoundary>
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: theme.colors.background.secondary,
                    color: theme.colors.text.primary,
                  },
                  success: {
                    iconTheme: {
                      primary: theme.colors.status.success,
                      secondary: '#fff',
                    },
                  },
                  error: {
                    iconTheme: {
                      primary: theme.colors.status.error,
                      secondary: '#fff',
                    },
                  },
                }}
              />
            </ThemeProvider>
          </DIProvider>
        </QueryClientProvider>
      </I18nextProvider>
    </HelmetProvider>
  );
};

export default App; 