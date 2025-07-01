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

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '50px', textAlign: 'center' }}>
          <h2>عذراً، حدث خطأ ما</h2>
          <button onClick={() => window.location.reload()}>
            إعادة تحميل الصفحة
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 