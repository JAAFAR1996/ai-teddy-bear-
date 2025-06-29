import React, { memo } from 'react';
import styled from 'styled-components';

const CardContainer = styled.div`
  background: ${props => props.theme.colors.surface || 'white'};
  border-radius: ${props => props.theme.borderRadius?.lg || '12px'};
  padding: ${props => props.theme.spacing?.lg || '1.5rem'};
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid ${props => props.theme.colors.border || '#e5e7eb'};
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    transform: translateY(-1px);
  }
`;

const CardHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing?.sm || '0.5rem'};
  margin-bottom: ${props => props.theme.spacing?.md || '1rem'};
  
  h3 {
    margin: 0;
    font-size: ${props => props.theme.typography?.fontSize?.lg || '1.125rem'};
    font-weight: 600;
    color: ${props => props.theme.colors.text || '#1f2937'};
  }
  
  .icon {
    color: ${props => props.theme.colors.primary || '#3b82f6'};
    font-size: 1.25rem;
  }
`;

const CardContent = styled.div`
  color: ${props => props.theme.colors.text || '#1f2937'};
`;

const Card = ({ title, icon, children, className, style, ...props }) => {
  return (
    <CardContainer className={className} style={style} {...props}>
      {(title || icon) && (
        <CardHeader>
          {icon && <span className="icon">{icon}</span>}
          {title && <h3>{title}</h3>}
        </CardHeader>
      )}
      <CardContent>
        {children}
      </CardContent>
    </CardContainer>
  );
};

Card.displayName = 'Card';

export default memo(Card); 