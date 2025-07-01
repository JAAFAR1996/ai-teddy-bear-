import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  padding: 20px;
`;

export const Settings = () => {
  return (
    <Container>
      <h2>الإعدادات</h2>
      <p>إعدادات النظام ستظهر هنا</p>
    </Container>
  );
}; 