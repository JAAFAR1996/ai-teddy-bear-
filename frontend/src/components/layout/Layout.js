import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { FiHome, FiMessageCircle, FiUser, FiBarChart2, FiSettings, FiLogOut } from 'react-icons/fi';

const LayoutContainer = styled.div`
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
`;

const Sidebar = styled.aside`
  width: 250px;
  background-color: #fff;
  box-shadow: 2px 0 4px rgba(0,0,0,0.1);
  padding: 20px;
`;

const Logo = styled.div`
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const NavMenu = styled.nav`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 8px;
  color: #333;
  text-decoration: none;
  transition: all 0.2s;
  
  &:hover {
    background-color: #f0f0f0;
  }
  
  &.active {
    background-color: #3498db;
    color: white;
  }
`;

const MainContent = styled.main`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
`;

const Header = styled.header`
  background-color: white;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

export const Layout = () => {
  const location = useLocation();
  
  const menuItems = [
    { path: '/dashboard', icon: <FiHome />, label: 'الرئيسية' },
    { path: '/conversations', icon: <FiMessageCircle />, label: 'المحادثات' },
    { path: '/child-profile', icon: <FiUser />, label: 'ملف الطفل' },
    { path: '/reports', icon: <FiBarChart2 />, label: 'التقارير' },
    { path: '/settings', icon: <FiSettings />, label: 'الإعدادات' },
  ];
  
  return (
    <LayoutContainer>
      <Sidebar>
        <Logo>
          <span>🧸</span>
          <span>دب تيدي الذكي</span>
        </Logo>
        
        <NavMenu>
          {menuItems.map(item => (
            <NavLink 
              key={item.path} 
              to={item.path}
              className={location.pathname === item.path ? 'active' : ''}
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </NavMenu>
        
        <div style={{ marginTop: 'auto', paddingTop: '20px' }}>
          <NavLink to="/login">
            <FiLogOut />
            <span>تسجيل الخروج</span>
          </NavLink>
        </div>
      </Sidebar>
      
      <div style={{ flex: 1 }}>
        <Header>
          <h2>مرحباً بك!</h2>
          <div>التاريخ: {new Date().toLocaleDateString('ar-SA')}</div>
        </Header>
        
        <MainContent>
          <Outlet />
        </MainContent>
      </div>
    </LayoutContainer>
  );
}; 