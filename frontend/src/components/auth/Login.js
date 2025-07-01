import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
`;

const LoginForm = styled.form`
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
`;

export const Login = () => {
  const handleSubmit = (e) => {
    e.preventDefault();
    window.location.href = '/dashboard';
  };

  return (
    <Container>
      <LoginForm onSubmit={handleSubmit}>
        <h2>تسجيل الدخول</h2>
        <input type="email" placeholder="البريد الإلكتروني" required />
        <input type="password" placeholder="كلمة المرور" required />
        <button type="submit">دخول</button>
      </LoginForm>
    </Container>
  );
}; 