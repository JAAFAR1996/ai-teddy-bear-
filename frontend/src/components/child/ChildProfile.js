import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  padding: 20px;
`;

export const ChildProfile = () => {
  return (
    <Container>
      <h2>ملف الطفل</h2>
      <p>معلومات الطفل ستظهر هنا</p>
    </Container>
  );
}; 