import React, { memo } from 'react';
import styled, { keyframes } from 'styled-components';

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const LoaderContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
`;

const Spinner = styled.div`
  width: 48px;
  height: 48px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  margin-bottom: 1rem;
`;

const LoaderText = styled.div`
  color: #6b7280;
  font-size: 1rem;
  font-weight: 500;
`;

const DataLoader = ({ text = 'جاري التحميل...' }) => {
  return (
    <LoaderContainer>
      <Spinner />
      <LoaderText>{text}</LoaderText>
    </LoaderContainer>
  );
};

export default memo(DataLoader); 