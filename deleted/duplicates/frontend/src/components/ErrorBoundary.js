import React from 'react';
import styled from 'styled-components';
import { FiAlertTriangle, FiRefreshCw, FiHome } from 'react-icons/fi';

const ErrorContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: ${props => props.theme.spacing.lg};
`;

const ErrorCard = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius['2xl']};
  box-shadow: ${props => props.theme.shadows['2xl']};
  padding: ${props => props.theme.spacing.xxl};
  max-width: 500px;
  width: 100%;
  text-align: center;
  
  ${props => props.theme.mediaQueries.maxSm} {
    padding: ${props => props.theme.spacing.xl};
    margin: ${props => props.theme.spacing.md};
  }
`;

const ErrorIcon = styled.div`
  color: ${props => props.theme.colors.danger};
  font-size: 4rem;
  margin-bottom: ${props => props.theme.spacing.lg};
  
  svg {
    width: 4rem;
    height: 4rem;
  }
`;

const ErrorTitle = styled.h1`
  color: ${props => props.theme.colors.text};
  font-size: ${props => props.theme.typography.fontSize['2xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const ErrorMessage = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.typography.fontSize.base};
  line-height: ${props => props.theme.typography.lineHeight.relaxed};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const ErrorDetails = styled.details`
  margin: ${props => props.theme.spacing.lg} 0;
  text-align: right;
  
  summary {
    cursor: pointer;
    color: ${props => props.theme.colors.primary};
    margin-bottom: ${props => props.theme.spacing.sm};
    font-weight: ${props => props.theme.typography.fontWeight.medium};
    
    &:hover {
      text-decoration: underline;
    }
  }
  
  pre {
    background: ${props => props.theme.colors.lightGray};
    border-radius: ${props => props.theme.borderRadius.md};
    padding: ${props => props.theme.spacing.md};
    font-size: ${props => props.theme.typography.fontSize.sm};
    font-family: ${props => props.theme.typography.fontFamily.monospace};
    text-align: left;
    direction: ltr;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-word;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  justify-content: center;
  flex-wrap: wrap;
  
  ${props => props.theme.mediaQueries.maxSm} {
    flex-direction: column;
  }
`;

const Button = styled.button`
  display: inline-flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  background: ${props => props.primary ? props.theme.colors.primary : props.theme.colors.secondary};
  color: ${props => props.theme.colors.textLight};
  border: none;
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.xl};
  font-size: ${props => props.theme.typography.fontSize.base};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.primary ? props.theme.colors.primaryDark : props.theme.colors.secondaryDark};
    transform: translateY(-1px);
    box-shadow: ${props => props.theme.shadows.md};
  }
  
  &:active {
    transform: translateY(0);
  }
  
  svg {
    width: 1.2rem;
    height: 1.2rem;
  }
`;

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      eventId: null,
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }
    
    // Update state with error details
    this.setState({
      error,
      errorInfo,
    });
    
    // Log error to external service (in production)
    if (process.env.NODE_ENV === 'production') {
      this.logErrorToService(error, errorInfo);
    }
  }

  logErrorToService = (error, errorInfo) => {
    // Log to external error tracking service
    // This could be Sentry, LogRocket, or custom error API
    try {
      const errorData = {
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        userId: localStorage.getItem('userId') || 'anonymous',
      };
      
      // Send to error tracking API
      fetch('/api/errors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(errorData),
      }).catch(err => {
        console.error('Failed to log error to service:', err);
      });
      
    } catch (loggingError) {
      console.error('Failed to prepare error for logging:', loggingError);
    }
  };

  handleRefresh = () => {
    // Reset error state and reload page
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
    window.location.reload();
  };

  handleGoHome = () => {
    // Reset error state and navigate to home
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
    window.location.href = '/dashboard';
  };

  render() {
    if (this.state.hasError) {
      const { error, errorInfo } = this.state;
      
      // Get user-friendly error message
      const getErrorMessage = (error) => {
        if (error?.message?.includes('ChunkLoadError')) {
          return 'حدث خطأ في تحميل التطبيق. يرجى تحديث الصفحة.';
        }
        if (error?.message?.includes('Network')) {
          return 'خطأ في الاتصال بالشبكة. تأكد من اتصال الإنترنت.';
        }
        return 'حدث خطأ غير متوقع في التطبيق. نعتذر عن الإزعاج.';
      };
      
      return (
        <ErrorContainer>
          <ErrorCard>
            <ErrorIcon>
              <FiAlertTriangle />
            </ErrorIcon>
            
            <ErrorTitle>عذراً، حدث خطأ!</ErrorTitle>
            
            <ErrorMessage>
              {getErrorMessage(error)}
            </ErrorMessage>
            
            {process.env.NODE_ENV === 'development' && error && (
              <ErrorDetails>
                <summary>تفاصيل الخطأ (للمطورين)</summary>
                <pre>
                  <strong>Error:</strong> {error.message}
                  {'\n\n'}
                  <strong>Stack:</strong>
                  {'\n'}
                  {error.stack}
                  {errorInfo && (
                    <>
                      {'\n\n'}
                      <strong>Component Stack:</strong>
                      {'\n'}
                      {errorInfo.componentStack}
                    </>
                  )}
                </pre>
              </ErrorDetails>
            )}
            
            <ButtonGroup>
              <Button primary onClick={this.handleRefresh}>
                <FiRefreshCw />
                تحديث الصفحة
              </Button>
              
              <Button onClick={this.handleGoHome}>
                <FiHome />
                العودة للرئيسية
              </Button>
            </ButtonGroup>
            
            <ErrorMessage style={{ marginTop: '1.5rem', fontSize: '0.875rem' }}>
              إذا استمر الخطأ، يرجى التواصل مع الدعم التقني.
            </ErrorMessage>
          </ErrorCard>
        </ErrorContainer>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 