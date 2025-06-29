import React, { memo, useState } from 'react';
import styled from 'styled-components';

const ProfileContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
`;

const ProfileCard = styled.div`
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
`;

const ProfileHeader = styled.div`
  text-align: center;
  margin-bottom: 2rem;
  
  h2 {
    margin: 0 0 0.5rem 0;
    color: #1f2937;
    font-size: 1.75rem;
  }
  
  p {
    margin: 0;
    color: #6b7280;
    font-size: 1rem;
  }
`;

const Avatar = styled.div`
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  margin: 0 auto 1rem auto;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  color: white;
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #374151;
  }
  
  input, select, textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 1rem;
    box-sizing: border-box;
    
    &:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
  }
  
  textarea {
    resize: vertical;
    min-height: 80px;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
`;

const Button = styled.button`
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  
  ${props => props.variant === 'primary' ? `
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    color: white;
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
  ` : `
    background: #f3f4f6;
    color: #374151;
    border-color: #d1d5db;
    
    &:hover {
      background: #e5e7eb;
    }
  `}
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
`;

const StatItem = styled.div`
  text-align: center;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  
  .value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #3b82f6;
    margin-bottom: 0.25rem;
  }
  
  .label {
    font-size: 0.875rem;
    color: #6b7280;
  }
`;

const Profile = ({ onSave, onCancel }) => {
  const [profileData, setProfileData] = useState({
    name: 'أحمد محمد',
    age: '7',
    gender: 'ذكر',
    favoriteTopics: 'الحيوانات، الفضاء، الرياضة',
    specialNeeds: '',
    parentEmail: 'parent@example.com',
    notes: 'طفل نشيط ومحب للتعلم'
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave && onSave(profileData);
  };

  return (
    <ProfileContainer>
      <ProfileCard>
        <ProfileHeader>
          <Avatar>👶</Avatar>
          <h2>ملف الطفل الشخصي</h2>
          <p>إدارة معلومات وإعدادات طفلك</p>
        </ProfileHeader>

        <StatsGrid>
          <StatItem>
            <div className="value">156</div>
            <div className="label">إجمالي المحادثات</div>
          </StatItem>
          <StatItem>
            <div className="value">23</div>
            <div className="label">يوماً نشطاً</div>
          </StatItem>
          <StatItem>
            <div className="value">4.8</div>
            <div className="label">متوسط السعادة</div>
          </StatItem>
          <StatItem>
            <div className="value">92%</div>
            <div className="label">معدل التعلم</div>
          </StatItem>
        </StatsGrid>

        <form onSubmit={handleSubmit}>
          <FormGroup>
            <label htmlFor="name">اسم الطفل</label>
            <input
              type="text"
              id="name"
              name="name"
              value={profileData.name}
              onChange={handleChange}
              required
            />
          </FormGroup>

          <FormGroup>
            <label htmlFor="age">العمر</label>
            <select
              id="age"
              name="age"
              value={profileData.age}
              onChange={handleChange}
              required
            >
              <option value="">اختر العمر</option>
              {[...Array(15)].map((_, i) => (
                <option key={i + 3} value={i + 3}>
                  {i + 3} سنوات
                </option>
              ))}
            </select>
          </FormGroup>

          <FormGroup>
            <label htmlFor="gender">الجنس</label>
            <select
              id="gender"
              name="gender"
              value={profileData.gender}
              onChange={handleChange}
            >
              <option value="ذكر">ذكر</option>
              <option value="أنثى">أنثى</option>
            </select>
          </FormGroup>

          <FormGroup>
            <label htmlFor="favoriteTopics">المواضيع المفضلة</label>
            <input
              type="text"
              id="favoriteTopics"
              name="favoriteTopics"
              value={profileData.favoriteTopics}
              onChange={handleChange}
              placeholder="مثال: الحيوانات، الرياضة، العلوم"
            />
          </FormGroup>

          <FormGroup>
            <label htmlFor="specialNeeds">احتياجات خاصة (اختياري)</label>
            <textarea
              id="specialNeeds"
              name="specialNeeds"
              value={profileData.specialNeeds}
              onChange={handleChange}
              placeholder="أي احتياجات خاصة أو ملاحظات طبية"
            />
          </FormGroup>

          <FormGroup>
            <label htmlFor="parentEmail">بريد الوالد الإلكتروني</label>
            <input
              type="email"
              id="parentEmail"
              name="parentEmail"
              value={profileData.parentEmail}
              onChange={handleChange}
              required
            />
          </FormGroup>

          <FormGroup>
            <label htmlFor="notes">ملاحظات إضافية</label>
            <textarea
              id="notes"
              name="notes"
              value={profileData.notes}
              onChange={handleChange}
              placeholder="أي ملاحظات مهمة عن شخصية أو اهتمامات الطفل"
            />
          </FormGroup>

          <ButtonGroup>
            <Button type="submit" variant="primary">
              💾 حفظ التغييرات
            </Button>
            <Button type="button" onClick={onCancel}>
              ❌ إلغاء
            </Button>
          </ButtonGroup>
        </form>
      </ProfileCard>
    </ProfileContainer>
  );
};

Profile.displayName = 'Profile';

export default memo(Profile); 