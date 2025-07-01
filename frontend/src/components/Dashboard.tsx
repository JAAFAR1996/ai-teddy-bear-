import React from 'react';
import styled from 'styled-components';
import { FiUser, FiHeart, FiMessageCircle, FiClock } from 'react-icons/fi';

const DashboardContainer = styled.div`
  padding: 2rem;
`;

const Header = styled.h1`
  margin-bottom: 2rem;
  color: #333;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div`
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  
  h3 {
    margin: 0 0 0.5rem 0;
    color: #666;
    font-size: 0.9rem;
  }
  
  .value {
    font-size: 2rem;
    font-weight: bold;
    color: #333;
  }
  
  .icon {
    color: #4CAF50;
    margin-bottom: 0.5rem;
  }
`;

export const Dashboard: React.FC = () => {
  return (
    <DashboardContainer>
      <Header>لوحة تحكم الوالدين 👨‍👩‍👧‍👦</Header>
      
      <StatsGrid>
        <StatCard>
          <div className="icon"><FiMessageCircle size={24} /></div>
          <h3>إجمالي المحادثات</h3>
          <div className="value">42</div>
        </StatCard>
        
        <StatCard>
          <div className="icon"><FiHeart size={24} /></div>
          <h3>الحالة العاطفية</h3>
          <div className="value">ممتاز</div>
        </StatCard>
        
        <StatCard>
          <div className="icon"><FiClock size={24} /></div>
          <h3>وقت النشاط</h3>
          <div className="value">45 دقيقة</div>
        </StatCard>
        
        <StatCard>
          <div className="icon"><FiUser size={24} /></div>
          <h3>مستوى التعلم</h3>
          <div className="value">85%</div>
        </StatCard>
      </StatsGrid>
      
      <div style={{ background: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <h2>نشاط اليوم</h2>
        <p>سيتم عرض الرسوم البيانية والتحليلات هنا</p>
      </div>
    </DashboardContainer>
  );
};

export default Dashboard; 