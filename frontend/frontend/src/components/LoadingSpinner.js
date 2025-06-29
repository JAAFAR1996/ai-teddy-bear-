import React from 'react';
import styled, { keyframes } from 'styled-components';

// Spinner animations
const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
`;

const bounce = keyframes`
  0%, 80%, 100% { 
    transform: scale(0);
    opacity: 0.5;
  }
  40% { 
    transform: scale(1);
    opacity: 1;
  }
`;

const wave = keyframes`
  0%, 60%, 100% { transform: initial; }
  30% { transform: translateY(-15px); }
`;

// Container styles
const SpinnerContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: ${props => props.fullScreen ? '100vh' : '200px'};
  background: ${props => props.fullScreen ? 
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 
    'transparent'};
  padding: ${props => props.theme.spacing.xl};
  position: ${props => props.overlay ? 'fixed' : 'static'};
  top: ${props => props.overlay ? '0' : 'auto'};
  left: ${props => props.overlay ? '0' : 'auto'};
  right: ${props => props.overlay ? '0' : 'auto'};
  bottom: ${props => props.overlay ? '0' : 'auto'};
  z-index: ${props => props.overlay ? props.theme.zIndex.overlay : 'auto'};
  backdrop-filter: ${props => props.overlay ? 'blur(5px)' : 'none'};
`;

// Teddy Bear themed spinner
const TeddySpinner = styled.div`
  width: ${props => props.size || '60px'};
  height: ${props => props.size || '60px'};
  border: 4px solid ${props => props.theme.colors.teddyBrownLight};
  border-top: 4px solid ${props => props.theme.colors.teddyBrown};
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  position: relative;
  margin-bottom: ${props => props.theme.spacing.lg};
  
  &::before {
    content: '🧸';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: ${props => props.size ? `calc(${props.size} * 0.4)` : '24px'};
    animation: ${pulse} 1.5s ease-in-out infinite;
  }
`;

// Classic spinner
const ClassicSpinner = styled.div`
  width: ${props => props.size || '50px'};
  height: ${props => props.size || '50px'};
  border: 3px solid ${props => props.theme.colors.lightGray};
  border-top: 3px solid ${props => props.theme.colors.primary};
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Dots spinner
const DotsSpinner = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const Dot = styled.div`
  width: 12px;
  height: 12px;
  background: ${props => props.theme.colors.primary};
  border-radius: 50%;
  animation: ${bounce} 1.4s ease-in-out infinite both;
  animation-delay: ${props => props.delay || '0s'};
`;

// Wave spinner
const WaveSpinner = styled.div`
  display: flex;
  gap: 4px;
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const WaveBar = styled.div`
  width: 4px;
  height: 40px;
  background: ${props => props.theme.colors.primary};
  border-radius: 2px;
  animation: ${wave} 1.2s ease-in-out infinite;
  animation-delay: ${props => props.delay || '0s'};
`;

// Loading text
const LoadingText = styled.div`
  color: ${props => props.fullScreen ? props.theme.colors.textLight : props.theme.colors.text};
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  text-align: center;
  margin-bottom: ${props => props.theme.spacing.md};
  animation: ${pulse} 1.5s ease-in-out infinite;
`;

// Progress text
const ProgressText = styled.div`
  color: ${props => props.fullScreen ? props.theme.colors.textLight : props.theme.colors.textSecondary};
  font-size: ${props => props.theme.typography.fontSize.sm};
  text-align: center;
  margin-top: ${props => props.theme.spacing.sm};
`;

// Progress bar
const ProgressBarContainer = styled.div`
  width: 200px;
  height: 4px;
  background: ${props => props.fullScreen ? 'rgba(255,255,255,0.2)' : props.theme.colors.lightGray};
  border-radius: ${props => props.theme.borderRadius.full};
  overflow: hidden;
  margin-top: ${props => props.theme.spacing.md};
`;

const ProgressBarFill = styled.div`
  height: 100%;
  background: ${props => props.fullScreen ? props.theme.colors.textLight : props.theme.colors.primary};
  border-radius: ${props => props.theme.borderRadius.full};
  width: ${props => props.progress || 0}%;
  transition: width 0.3s ease;
`;

// Main LoadingSpinner component
const LoadingSpinner = ({
  type = 'teddy', // 'teddy', 'classic', 'dots', 'wave'
  size = null,
  text = 'جاري التحميل...',
  subText = null,
  fullScreen = false,
  overlay = false,
  progress = null,
  className = '',
}) => {
  const renderSpinner = () => {
    switch (type) {
      case 'teddy':
        return <TeddySpinner size={size} />;
      case 'classic':
        return <ClassicSpinner size={size} />;
      case 'dots':
        return (
          <DotsSpinner>
            <Dot delay="0s" />
            <Dot delay="0.16s" />
            <Dot delay="0.32s" />
          </DotsSpinner>
        );
      case 'wave':
        return (
          <WaveSpinner>
            <WaveBar delay="0s" />
            <WaveBar delay="0.1s" />
            <WaveBar delay="0.2s" />
            <WaveBar delay="0.3s" />
            <WaveBar delay="0.4s" />
          </WaveSpinner>
        );
      default:
        return <TeddySpinner size={size} />;
    }
  };

  return (
    <SpinnerContainer 
      fullScreen={fullScreen}
      overlay={overlay}
      className={className}
    >
      {renderSpinner()}
      
      {text && (
        <LoadingText fullScreen={fullScreen}>
          {text}
        </LoadingText>
      )}
      
      {subText && (
        <ProgressText fullScreen={fullScreen}>
          {subText}
        </ProgressText>
      )}
      
      {progress !== null && (
        <>
          <ProgressBarContainer fullScreen={fullScreen}>
            <ProgressBarFill progress={progress} fullScreen={fullScreen} />
          </ProgressBarContainer>
          <ProgressText fullScreen={fullScreen}>
            {Math.round(progress)}%
          </ProgressText>
        </>
      )}
    </SpinnerContainer>
  );
};

// Specialized spinner components
export const TeddyLoader = (props) => (
  <LoadingSpinner 
    type="teddy" 
    text="دب تيدي يحضر بياناتك..." 
    {...props} 
  />
);

export const PageLoader = (props) => (
  <LoadingSpinner 
    type="wave" 
    fullScreen={true}
    text="جاري تحميل الصفحة..."
    {...props} 
  />
);

export const DataLoader = (props) => (
  <LoadingSpinner 
    type="dots"
    text="جاري تحميل البيانات..."
    {...props} 
  />
);

export const OverlayLoader = (props) => (
  <LoadingSpinner 
    type="classic"
    overlay={true}
    text="يرجى الانتظار..."
    {...props} 
  />
);

export const ProgressLoader = ({ progress, ...props }) => (
  <LoadingSpinner 
    type="classic"
    progress={progress}
    text="جاري المعالجة..."
    {...props} 
  />
);

// Skeleton loader for content placeholders
export const SkeletonLoader = styled.div`
  background: linear-gradient(
    90deg,
    ${props => props.theme.colors.lightGray} 25%,
    ${props => props.theme.colors.border} 50%,
    ${props => props.theme.colors.lightGray} 75%
  );
  background-size: 200% 100%;
  animation: ${wave} 1.5s infinite;
  border-radius: ${props => props.theme.borderRadius.md};
  height: ${props => props.height || '20px'};
  width: ${props => props.width || '100%'};
  margin: ${props => props.margin || '0'};
`;

// Text skeleton
export const TextSkeleton = ({ lines = 1, ...props }) => (
  <>
    {Array.from({ length: lines }, (_, index) => (
      <SkeletonLoader
        key={index}
        height="16px"
        width={index === lines - 1 ? '70%' : '100%'}
        margin="8px 0"
        {...props}
      />
    ))}
  </>
);

// Card skeleton
export const CardSkeleton = (props) => (
  <div style={{ padding: '1rem', border: '1px solid #e2e8f0', borderRadius: '12px' }}>
    <SkeletonLoader height="200px" margin="0 0 1rem 0" />
    <SkeletonLoader height="24px" width="80%" margin="0 0 0.5rem 0" />
    <TextSkeleton lines={2} />
  </div>
);

export default LoadingSpinner; 