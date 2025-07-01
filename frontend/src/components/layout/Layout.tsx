import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import {
  FiGrid,
  FiMessageCircle,
  FiUser,
  FiFileText,
  FiActivity,
  FiAlertTriangle,
  FiSettings,
  FiLogOut,
  FiMenu,
  FiX,
  FiGlobe,
} from 'react-icons/fi';
import toast from 'react-hot-toast';
import { useService } from '../../architecture/dependency-injection';
import { SERVICE_TOKENS } from '../../architecture/dependency-injection/container';
import { AuthService } from '../../architecture/infrastructure/services/AuthService';

const LayoutContainer = styled.div`
  display: flex;
  height: 100vh;
  background: ${({ theme }) => theme.colors.background.secondary};
`;

const Sidebar = styled(motion.aside)<{ isOpen: boolean }>`
  width: ${({ isOpen }) => (isOpen ? '280px' : '0')};
  background: ${({ theme }) => theme.colors.background.primary};
  box-shadow: ${({ theme }) => theme.shadows.lg};
  overflow: hidden;
  transition: width ${({ theme }) => theme.transitions.base};
  
  @media (min-width: ${({ theme }) => theme.breakpoints.lg}) {
    width: 280px;
  }
`;

const SidebarContent = styled.div`
  width: 280px;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: ${({ theme }) => theme.spacing.xl};
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.md};
  margin-bottom: ${({ theme }) => theme.spacing['2xl']};
  font-size: ${({ theme }) => theme.typography.fontSize.xl};
  font-weight: ${({ theme }) => theme.typography.fontWeight.bold};
  color: ${({ theme }) => theme.colors.primary.main};
`;

const Nav = styled.nav`
  flex: 1;
`;

const NavItem = styled(NavLink)`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.md};
  padding: ${({ theme }) => theme.spacing.md} ${({ theme }) => theme.spacing.lg};
  margin-bottom: ${({ theme }) => theme.spacing.sm};
  border-radius: ${({ theme }) => theme.borderRadius.lg};
  text-decoration: none;
  color: ${({ theme }) => theme.colors.text.secondary};
  transition: ${({ theme }) => theme.transitions.fast};
  
  &:hover {
    background: ${({ theme }) => theme.colors.background.secondary};
    color: ${({ theme }) => theme.colors.text.primary};
  }
  
  &.active {
    background: ${({ theme }) => theme.colors.primary.main};
    color: ${({ theme }) => theme.colors.primary.contrast};
    
    &:hover {
      background: ${({ theme }) => theme.colors.primary.dark};
    }
  }
  
  svg {
    width: 20px;
    height: 20px;
  }
`;

const NavLabel = styled.span`
  font-size: ${({ theme }) => theme.typography.fontSize.base};
  font-weight: ${({ theme }) => theme.typography.fontWeight.medium};
`;

const BottomActions = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.sm};
  padding-top: ${({ theme }) => theme.spacing.xl};
  border-top: 1px solid ${({ theme }) => theme.colors.border.light};
`;

const LanguageToggle = styled.button`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.md};
  padding: ${({ theme }) => theme.spacing.md} ${({ theme }) => theme.spacing.lg};
  border-radius: ${({ theme }) => theme.borderRadius.lg};
  background: transparent;
  color: ${({ theme }) => theme.colors.text.secondary};
  transition: ${({ theme }) => theme.transitions.fast};
  width: 100%;
  text-align: start;
  
  &:hover {
    background: ${({ theme }) => theme.colors.background.secondary};
    color: ${({ theme }) => theme.colors.text.primary};
  }
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const Header = styled.header`
  background: ${({ theme }) => theme.colors.background.primary};
  padding: ${({ theme }) => theme.spacing.lg} ${({ theme }) => theme.spacing.xl};
  box-shadow: ${({ theme }) => theme.shadows.sm};
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const MenuToggle = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  background: transparent;
  color: ${({ theme }) => theme.colors.text.primary};
  transition: ${({ theme }) => theme.transitions.fast};
  
  &:hover {
    background: ${({ theme }) => theme.colors.background.secondary};
  }
  
  @media (min-width: ${({ theme }) => theme.breakpoints.lg}) {
    display: none;
  }
`;

const Content = styled.div`
  flex: 1;
  overflow-y: auto;
  background: ${({ theme }) => theme.colors.background.secondary};
`;

const Overlay = styled(motion.div)`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  
  @media (min-width: ${({ theme }) => theme.breakpoints.lg}) {
    display: none;
  }
`;

export const Layout: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const authService = useService<AuthService>(SERVICE_TOKENS.AUTH_SERVICE);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const navItems = [
    { path: '/dashboard', icon: FiGrid, label: t('navigation.dashboard') },
    { path: '/conversations', icon: FiMessageCircle, label: t('navigation.conversations') },
    { path: '/child-profile', icon: FiUser, label: t('navigation.childProfile') },
    { path: '/reports', icon: FiFileText, label: t('navigation.reports') },
    { path: '/analytics', icon: FiActivity, label: t('navigation.analytics') },
    { path: '/emergency', icon: FiAlertTriangle, label: t('navigation.emergency') },
  ];

  const handleLogout = async () => {
    try {
      await authService.logout();
      toast.success(t('auth.logoutSuccess'));
      navigate('/login');
    } catch (error) {
      toast.error(t('auth.logoutError'));
    }
  };

  const toggleLanguage = () => {
    const newLang = i18n.language === 'ar' ? 'en' : 'ar';
    i18n.changeLanguage(newLang);
    document.dir = newLang === 'ar' ? 'rtl' : 'ltr';
  };

  return (
    <LayoutContainer>
      <AnimatePresence>
        {isSidebarOpen && (
          <Overlay
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      <Sidebar isOpen={isSidebarOpen} style={{ zIndex: 1000 }}>
        <SidebarContent>
          <Logo>
            <span>🧸</span>
            <span>{t('common.appName')}</span>
          </Logo>

          <Nav>
            {navItems.map((item) => (
              <NavItem
                key={item.path}
                to={item.path}
                onClick={() => setIsSidebarOpen(false)}
              >
                <item.icon />
                <NavLabel>{item.label}</NavLabel>
              </NavItem>
            ))}
          </Nav>

          <BottomActions>
            <LanguageToggle onClick={toggleLanguage}>
              <FiGlobe />
              <NavLabel>{i18n.language === 'ar' ? 'English' : 'العربية'}</NavLabel>
            </LanguageToggle>
            
            <NavItem as="button" onClick={() => navigate('/settings')}>
              <FiSettings />
              <NavLabel>{t('navigation.settings')}</NavLabel>
            </NavItem>
            
            <NavItem as="button" onClick={handleLogout}>
              <FiLogOut />
              <NavLabel>{t('common.logout')}</NavLabel>
            </NavItem>
          </BottomActions>
        </SidebarContent>
      </Sidebar>

      <MainContent>
        <Header>
          <MenuToggle onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
            {isSidebarOpen ? <FiX /> : <FiMenu />}
          </MenuToggle>
          
          <div>
            {/* User info or other header content */}
          </div>
        </Header>

        <Content>
          <Outlet />
        </Content>
      </MainContent>
    </LayoutContainer>
  );
}; 