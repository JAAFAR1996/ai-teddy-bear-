import React, { memo } from 'react';
import styled from 'styled-components';

const DashboardContainer = styled.div`
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
`;

const WelcomeCard = styled.div`
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  padding: 2rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  text-align: center;
  
  h1 {
    margin: 0 0 1rem 0;
    font-size: 2rem;
    font-weight: 700;
  }
  
  p {
    margin: 0;
    font-size: 1.1rem;
    opacity: 0.9;
  }
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
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  
  .stat-title {
    font-size: 0.875rem;
    color: #6b7280;
    margin-bottom: 0.5rem;
  }
  
  .stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 0.5rem;
  }
  
  .stat-subtitle {
    font-size: 0.75rem;
    color: #9ca3af;
  }
`;

const ContentCard = styled.div`
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  margin-bottom: 1.5rem;
  
  h3 {
    margin: 0 0 1rem 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: #1f2937;
  }
  
  p {
    margin: 0;
    color: #6b7280;
    line-height: 1.6;
  }
`;

const FeatureList = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
`;

const FeatureItem = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  
  .icon {
    font-size: 2rem;
  }
  
  .content {
    flex: 1;
    
    h4 {
      margin: 0 0 0.5rem 0;
      font-size: 1rem;
      font-weight: 600;
      color: #1f2937;
    }
    
    p {
      margin: 0;
      font-size: 0.875rem;
      color: #6b7280;
    }
  }
`;

const SimpleDashboard = () => {
  return (
    <DashboardContainer>
      <WelcomeCard>
        <h1>🧸 مرحباً بك في دبدوب الذكي</h1>
        <p>لوحة تحكم الوالدين - تابع نشاط أطفالك مع الذكاء الاصطناعي</p>
      </WelcomeCard>

      <StatsGrid>
        <StatCard>
          <div className="stat-title">المحادثات اليوم</div>
          <div className="stat-value">8</div>
          <div className="stat-subtitle">+2 من الأمس</div>
        </StatCard>
        
        <StatCard>
          <div className="stat-title">الحالة العاطفية</div>
          <div className="stat-value">😊 سعيد</div>
          <div className="stat-subtitle">المتوسط العام</div>
        </StatCard>
        
        <StatCard>
          <div className="stat-title">وقت النشاط</div>
          <div className="stat-value">45 دقيقة</div>
          <div className="stat-subtitle">اليوم</div>
        </StatCard>
        
        <StatCard>
          <div className="stat-title">التقدم التعليمي</div>
          <div className="stat-value">85%</div>
          <div className="stat-subtitle">ممتاز</div>
        </StatCard>
      </StatsGrid>

      <ContentCard>
        <h3>📊 تحليل الأنشطة</h3>
        <p>
          يُظهر طفلك تقدماً ممتازاً في التفاعل مع دبدوب الذكي. المحادثات تتضمن 
          مواضيع تعليمية وترفيهية متنوعة، مما يساهم في تطوير مهاراته اللغوية والفكرية.
        </p>
      </ContentCard>

      <ContentCard>
        <h3>🎯 الميزات المتاحة</h3>
        <FeatureList>
          <FeatureItem>
            <span className="icon">💬</span>
            <div className="content">
              <h4>المحادثات التفاعلية</h4>
              <p>محادثات ذكية مخصصة لعمر ومستوى طفلك</p>
            </div>
          </FeatureItem>
          
          <FeatureItem>
            <span className="icon">📈</span>
            <div className="content">
              <h4>تحليل المشاعر</h4>
              <p>مراقبة الحالة العاطفية وتقديم الدعم المناسب</p>
            </div>
          </FeatureItem>
          
          <FeatureItem>
            <span className="icon">🎓</span>
            <div className="content">
              <h4>المحتوى التعليمي</h4>
              <p>دروس وألعاب تفاعلية لتطوير المهارات</p>
            </div>
          </FeatureItem>
          
          <FeatureItem>
            <span className="icon">🔒</span>
            <div className="content">
              <h4>الأمان والخصوصية</h4>
              <p>حماية كاملة لبيانات طفلك وخصوصيته</p>
            </div>
          </FeatureItem>
        </FeatureList>
      </ContentCard>

      <ContentCard>
        <h3>📱 تصفح الأقسام</h3>
        <p>
          استخدم الشريط العلوي للتنقل بين أقسام التطبيق المختلفة:
          <br />
          • <strong>لوحة التحكم</strong>: الإحصائيات والملخص العام
          <br />
          • <strong>المحادثات</strong>: عرض وإدارة محادثات طفلك
          <br />
          • <strong>ملف الطفل</strong>: معلومات وإعدادات الطفل الشخصية
          <br />
          • <strong>الإعدادات</strong>: تخصيص تجربة الاستخدام
        </p>
      </ContentCard>
    </DashboardContainer>
  );
};

SimpleDashboard.displayName = 'SimpleDashboard';

export default memo(SimpleDashboard); 