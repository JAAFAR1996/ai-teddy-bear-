import React, { memo } from 'react';
import styled, { keyframes } from 'styled-components';

const shimmer = keyframes`
  0% {
    background-position: -468px 0;
  }
  100% {
    background-position: 468px 0;
  }
`;

const SkeletonContainer = styled.div`
  background: #f6f7f8;
  background-image: linear-gradient(
    to right,
    #f6f7f8 0%,
    #edeef1 20%,
    #f6f7f8 40%,
    #f6f7f8 100%
  );
  background-repeat: no-repeat;
  background-size: 800px 104px;
  border-radius: 8px;
  animation: ${shimmer} 1s linear infinite;
  
  height: ${props => props.height || '20px'};
  width: ${props => props.width || '100%'};
  margin: ${props => props.margin || '0'};
`;

const SkeletonLoader = ({ 
  height, 
  width, 
  margin,
  className,
  style,
  ...props 
}) => {
  return (
    <SkeletonContainer
      height={height}
      width={width}
      margin={margin}
      className={className}
      style={style}
      {...props}
    />
  );
};

SkeletonLoader.displayName = 'SkeletonLoader';

export default memo(SkeletonLoader); 