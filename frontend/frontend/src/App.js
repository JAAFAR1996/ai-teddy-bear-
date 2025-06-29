import React, { useState } from 'react';

// بسيط CSS-in-JS
const styles = {
  container: {
    minHeight: '100vh',
    background: '#f5f7fa',
    direction: 'rtl',
    fontFamily: "'Tajawal', sans-serif"
  },
  header: {
    background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
    color: 'white',
    padding: '1rem 2rem',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
  },
  title: {
    margin: 0,
    fontSize: '1.5rem',
    fontWeight: 700,
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem'
  },
  nav: {
    background: 'white',
    padding: '1rem 2rem',
    boxShadow: '0 2px 5px rgba(0,0,0,0.05)'
  },
  navList: {
    listStyle: 'none',
    margin: 0,
    padding: 0,
    display: 'flex',
    gap: '2rem'
  },
  navItem: {
    display: 'flex'
  },
  navLink: {
    textDecoration: 'none',
    color: '#374151',
    fontWeight: 500,
    padding: '0.5rem 1rem',
    borderRadius: '8px',
    transition: 'all 0.2s ease',
    cursor: 'pointer'
  },
  activeLink: {
    background: '#3b82f6',
    color: 'white'
  },
  main: {
    padding: '2rem',
    minHeight: 'calc(100vh - 140px)'
  },
  welcome: {
    background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
    color: 'white',
    padding: '2rem',
    borderRadius: '16px',
    marginBottom: '2rem',
    textAlign: 'center'
  },
  welcomeTitle: {
    margin: '0 0 1rem 0',
    fontSize: '2rem',
    fontWeight: 700
  },
  welcomeText: {
    margin: 0,
    fontSize: '1.1rem',
    opacity: 0.9
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '1.5rem',
    marginBottom: '2rem'
  },
  statCard: {
    background: 'white',
    padding: '1.5rem',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
  },
  statTitle: {
    fontSize: '0.875rem',
    color: '#6b7280',
    marginBottom: '0.5rem'
  },
  statValue: {
    fontSize: '2rem',
    fontWeight: 700,
    color: '#1f2937',
    marginBottom: '0.5rem'
  },
  statSubtitle: {
    fontSize: '0.75rem',
    color: '#9ca3af'
  },
  comingSoon: {
    padding: '2rem',
    textAlign: 'center',
    background: 'white',
    borderRadius: '16px',
    margin: '2rem auto',
    maxWidth: '600px'
  }
};

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const NavLink = ({ to, children, isActive }) => (
    <a 
      style={{
        ...styles.navLink,
        ...(isActive ? styles.activeLink : {})
      }}
      onClick={(e) => {
        e.preventDefault();
        setCurrentPage(to);
      }}
    >
      {children}
    </a>
  );

  const DashboardComponent = () => (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div style={styles.welcome}>
        <h2 style={styles.welcomeTitle}>🧸 مرحباً بك في دبدوب الذكي</h2>
        <p style={styles.welcomeText}>لوحة تحكم الوالدين - تابع نشاط أطفالك مع الذكاء الاصطناعي</p>
      </div>

      <div style={styles.statsGrid}>
        <div style={styles.statCard}>
          <div style={styles.statTitle}>المحادثات اليوم</div>
          <div style={styles.statValue}>8</div>
          <div style={styles.statSubtitle}>+2 من الأمس</div>
        </div>
        
        <div style={styles.statCard}>
          <div style={styles.statTitle}>الحالة العاطفية</div>
          <div style={styles.statValue}>😊 سعيد</div>
          <div style={styles.statSubtitle}>المتوسط العام</div>
        </div>
        
        <div style={styles.statCard}>
          <div style={styles.statTitle}>وقت النشاط</div>
          <div style={styles.statValue}>45 دقيقة</div>
          <div style={styles.statSubtitle}>اليوم</div>
        </div>
        
        <div style={styles.statCard}>
          <div style={styles.statTitle}>التقدم التعليمي</div>
          <div style={styles.statValue}>85%</div>
          <div style={styles.statSubtitle}>ممتاز</div>
        </div>
      </div>
    </div>
  );

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <DashboardComponent />;
      case 'conversations':
        return (
          <div style={styles.comingSoon}>
            <h2>💬 المحادثات</h2>
            <p>قريباً - تتبع محادثات طفلك مع دبدوب الذكي</p>
          </div>
        );
      case 'profile':
        return (
          <div style={styles.comingSoon}>
            <h2>👶 ملف الطفل</h2>
            <p>قريباً - إدارة ملف الطفل الشخصي</p>
          </div>
        );
      case 'settings':
        return (
          <div style={styles.comingSoon}>
            <h2>⚙️ الإعدادات</h2>
            <p>قريباً - تخصيص إعدادات التطبيق</p>
          </div>
        );
      default:
        return <DashboardComponent />;
    }
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>
          <span>🧸</span>
          دبدوب الذكي - لوحة التحكم
        </h1>
      </header>

      <nav style={styles.nav}>
        <ul style={styles.navList}>
          <li style={styles.navItem}>
            <NavLink to="dashboard" isActive={currentPage === 'dashboard'}>
              📊 لوحة التحكم
            </NavLink>
          </li>
          <li style={styles.navItem}>
            <NavLink to="conversations" isActive={currentPage === 'conversations'}>
              💬 المحادثات
            </NavLink>
          </li>
          <li style={styles.navItem}>
            <NavLink to="profile" isActive={currentPage === 'profile'}>
              👶 ملف الطفل
            </NavLink>
          </li>
          <li style={styles.navItem}>
            <NavLink to="settings" isActive={currentPage === 'settings'}>
              ⚙️ الإعدادات
            </NavLink>
          </li>
        </ul>
      </nav>

      <main style={styles.main}>
        {renderCurrentPage()}
      </main>
    </div>
  );
}

export default App; 