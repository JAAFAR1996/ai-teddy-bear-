import React from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';

const spin = keyframes`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`;

const pulse = keyframes`
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(0.8);
    opacity: 0.5;
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  padding: ${({ theme }) => theme.spacing['2xl']};
`;

const SpinnerContainer = styled.div`
  position: relative;
  width: 60px;
  height: 60px;
`;

const Spinner = styled(motion.div)`
  width: 100%;
  height: 100%;
  border: 4px solid ${({ theme }) => theme.colors.border.light};
  border-top-color: ${({ theme }) => theme.colors.primary.main};
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
`;

const TeddyIcon = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 24px;
  animation: ${pulse} 2s ease-in-out infinite;
`;

const LoadingText = styled.p`
  margin-top: ${({ theme }) => theme.spacing.lg};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  color: ${({ theme }) => theme.colors.text.secondary};
`;

interface LoadingProps {
  text?: string;
  fullScreen?: boolean;
}

const FullScreenWrapper = styled.div`
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${({ theme }) => theme.colors.background.primary};
  z-index: 9999;
`;

export const Loading: React.FC<LoadingProps> = ({ text, fullScreen = false }) => {
  const content = (
    <LoadingContainer>
      <SpinnerContainer>
        <Spinner
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.3 }}
        />
        <TeddyIcon>🧸</TeddyIcon>
      </SpinnerContainer>
      {text && <LoadingText>{text}</LoadingText>}
    </LoadingContainer>
  );

  if (fullScreen) {
    return <FullScreenWrapper>{content}</FullScreenWrapper>;
  }

  return content;
};

// Skeleton Loading Component
const SkeletonPulse = keyframes`
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
`;

const SkeletonBase = styled.div`
  background: linear-gradient(
    90deg,
    ${({ theme }) => theme.colors.background.tertiary} 25%,
    ${({ theme }) => theme.colors.background.secondary} 50%,
    ${({ theme }) => theme.colors.background.tertiary} 75%
  );
  background-size: 200% 100%;
  animation: ${SkeletonPulse} 1.5s ease-in-out infinite;
  border-radius: ${({ theme }) => theme.borderRadius.md};
`;

export const SkeletonText = styled(SkeletonBase)<{ width?: string }>`
  height: 1em;
  width: ${({ width }) => width || '100%'};
  margin-bottom: ${({ theme }) => theme.spacing.sm};
`;

export const SkeletonBox = styled(SkeletonBase)<{ height?: string; width?: string }>`
  height: ${({ height }) => height || '100px'};
  width: ${({ width }) => width || '100%'};
`;

export const SkeletonAvatar = styled(SkeletonBase)<{ size?: string }>`
  width: ${({ size }) => size || '40px'};
  height: ${({ size }) => size || '40px'};
  border-radius: 50%;
`; 