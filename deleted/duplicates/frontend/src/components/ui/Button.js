import React, { memo } from 'react';
import styled, { css } from 'styled-components';

const StyledButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  line-height: 1.5;
  text-decoration: none;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none !important;
  }
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
  
  ${props => props.variant === 'primary' && css`
    background: linear-gradient(135deg, ${props.theme.colors.primary || '#3b82f6'}, ${props.theme.colors.secondary || '#1d4ed8'});
    color: white;
    border-color: ${props.theme.colors.primary || '#3b82f6'};
    
    &:hover:not(:disabled) {
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
  `}
  
  ${props => props.variant === 'outline' && css`
    background: transparent;
    color: ${props.theme.colors.primary || '#3b82f6'};
    border-color: ${props.theme.colors.primary || '#3b82f6'};
    
    &:hover:not(:disabled) {
      background: ${props.theme.colors.primary || '#3b82f6'};
      color: white;
    }
  `}
  
  ${props => props.variant === 'secondary' && css`
    background: ${props.theme.colors.gray?.[100] || '#f3f4f6'};
    color: ${props.theme.colors.text || '#1f2937'};
    border-color: ${props.theme.colors.gray?.[300] || '#d1d5db'};
    
    &:hover:not(:disabled) {
      background: ${props.theme.colors.gray?.[200] || '#e5e7eb'};
    }
  `}
  
  ${props => props.size === 'sm' && css`
    padding: 0.5rem 1rem;
    font-size: 0.75rem;
  `}
  
  ${props => props.size === 'lg' && css`
    padding: 1rem 2rem;
    font-size: 1rem;
  `}
`;

const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md',
  disabled = false,
  type = 'button',
  onClick,
  className,
  style,
  ...props 
}) => {
  return (
    <StyledButton
      type={type}
      variant={variant}
      size={size}
      disabled={disabled}
      onClick={onClick}
      className={className}
      style={style}
      {...props}
    >
      {children}
    </StyledButton>
  );
};

Button.displayName = 'Button';

export default memo(Button); 