import React, { memo } from 'react';
import styled from 'styled-components';

const StatCardContainer = styled.div`
  background: ${props => props.theme.colors.surface || 'white'};
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid ${props => props.theme.colors.border || '#e5e7eb'};
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  }
`;

const StatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
`;

const StatIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  background: ${props => {
    const colors = {
      primary: '#3b82f6',
      success: '#10b981',
      warning: '#f59e0b',
      danger: '#ef4444',
      info: '#06b6d4'
    };
    return colors[props.color] || colors.primary;
  }};
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text || '#1f2937'};
  margin-bottom: 0.5rem;
`;

const StatTitle = styled.h3`
  margin: 0;
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.theme.colors.gray?.[600] || '#6b7280'};
  margin-bottom: 0.5rem;
`;

const StatFooter = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.75rem;
  color: ${props => props.theme.colors.gray?.[500] || '#9ca3af'};
`;

const StatTrend = styled.span`
  color: ${props => {
    if (props.trend?.startsWith('+')) return '#10b981';
    if (props.trend?.startsWith('-')) return '#ef4444';
    return props.theme.colors.gray?.[500] || '#9ca3af';
  }};
  font-weight: 500;
`;

const StatCard = ({ 
  title, 
  value, 
  icon, 
  color = 'primary', 
  trend, 
  subtitle,
  className,
  style,
  ...props 
}) => {
  return (
    <StatCardContainer className={className} style={style} {...props}>
      <StatHeader>
        <div>
          <StatTitle>{title}</StatTitle>
          <StatValue>{value}</StatValue>
        </div>
        <StatIcon color={color}>
          {icon}
        </StatIcon>
      </StatHeader>
      
      {(trend || subtitle) && (
        <StatFooter>
          {subtitle && <span>{subtitle}</span>}
          {trend && <StatTrend trend={trend}>{trend}</StatTrend>}
        </StatFooter>
      )}
    </StatCardContainer>
  );
};

StatCard.displayName = 'StatCard';

export default memo(StatCard); 