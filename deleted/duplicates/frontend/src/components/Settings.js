import React, { useState, useCallback, useMemo, memo } from 'react';
import styled, { keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { storage, validateEmail, DEFAULT_SETTINGS } from '../utils';

// Animations
const slideIn = keyframes`
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
`;

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

// Styled Components
const SettingsContainer = styled.div`
  display: flex;
  flex-direction: column;
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
  background: ${props => props.theme.colors.background};
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  direction: ${props => props.theme.direction};
  animation: ${fadeIn} 0.5s ease-out;
`;

const SettingsHeader = styled.div`
  text-align: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 2px solid ${props => props.theme.colors.gray[200]};
  
  h2 {
    margin: 0 0 8px 0;
    font-size: 1.8rem;
    font-weight: 700;
    color: ${props => props.theme.colors.text};
    background: linear-gradient(135deg, ${props => props.theme.colors.primary}, ${props => props.theme.colors.secondary});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  p {
    margin: 0;
    color: ${props => props.theme.colors.gray[600]};
    font-size: 1rem;
  }
`;

const SettingsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  
  @media (min-width: 768px) {
    grid-template-columns: 250px 1fr;
  }
`;

const SettingsNav = styled.nav`
  display: flex;
  flex-direction: column;
  gap: 8px;
  
  @media (max-width: 767px) {
    flex-direction: row;
    overflow-x: auto;
    padding-bottom: 8px;
    gap: 12px;
  }
`;

const NavItem = styled.button`
  padding: 12px 16px;
  border: none;
  border-radius: 12px;
  background: ${props => props.active ? 
    `linear-gradient(135deg, ${props.theme.colors.primary}, ${props.theme.colors.secondary})` : 
    'transparent'
  };
  color: ${props => props.active ? 'white' : props.theme.colors.text};
  font-size: 0.95rem;
  font-weight: ${props => props.active ? '600' : '400'};
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: ${props => props.theme.direction === 'rtl' ? 'right' : 'left'};
  white-space: nowrap;
  
  &:hover {
    background: ${props => props.active ? 
      `linear-gradient(135deg, ${props.theme.colors.primaryDark}, ${props.theme.colors.secondaryDark})` : 
      props.theme.colors.gray[100]
    };
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const SettingsContent = styled.div`
  min-height: 400px;
  animation: ${slideIn} 0.3s ease-out;
`;

const SettingsSection = styled.div`
  margin-bottom: 32px;
  
  h3 {
    margin: 0 0 16px 0;
    font-size: 1.3rem;
    font-weight: 600;
    color: ${props => props.theme.colors.text};
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  p {
    margin: 0 0 20px 0;
    color: ${props => props.theme.colors.gray[600]};
    font-size: 0.95rem;
    line-height: 1.5;
  }
`;

const SettingItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: ${props => props.theme.colors.gray[50]};
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid ${props => props.theme.colors.gray[200]};
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.theme.colors.gray[100]};
    border-color: ${props => props.theme.colors.primary};
  }
  
  .setting-info {
    flex: 1;
    
    .setting-title {
      font-weight: 600;
      color: ${props => props.theme.colors.text};
      margin-bottom: 4px;
      font-size: 0.95rem;
    }
    
    .setting-description {
      color: ${props => props.theme.colors.gray[600]};
      font-size: 0.85rem;
      line-height: 1.4;
    }
  }
  
  .setting-control {
    margin-${props => props.theme.direction === 'rtl' ? 'right' : 'left'}: 16px;
  }
`;

const Toggle = styled.div`
  position: relative;
  width: 48px;
  height: 24px;
  background: ${props => props.checked ? props.theme.colors.primary : props.theme.colors.gray[300]};
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.3s ease;
  
  &::after {
    content: '';
    position: absolute;
    top: 2px;
    ${props => props.theme.direction === 'rtl' ? 'right' : 'left'}: ${props => props.checked ? '26px' : '2px'};
    width: 20px;
    height: 20px;
    background: white;
    border-radius: 50%;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }
  
  &:hover {
    background: ${props => props.checked ? props.theme.colors.primaryDark : props.theme.colors.gray[400]};
  }
`;

const Select = styled.select`
  padding: 8px 12px;
  border: 1px solid ${props => props.theme.colors.gray[300]};
  border-radius: 8px;
  background: white;
  color: ${props => props.theme.colors.text};
  font-size: 0.9rem;
  cursor: pointer;
  min-width: 120px;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.primary}20;
  }
`;

const Input = styled.input`
  padding: 12px 16px;
  border: 1px solid ${props => props.theme.colors.gray[300]};
  border-radius: 8px;
  background: white;
  color: ${props => props.theme.colors.text};
  font-size: 0.95rem;
  width: 100%;
  margin-bottom: 12px;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.primary}20;
  }
  
  &::placeholder {
    color: ${props => props.theme.colors.gray[400]};
  }
`;

const Button = styled.button`
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  background: ${props => props.variant === 'danger' ? '#f44336' : 
    props.variant === 'secondary' ? props.theme.colors.gray[200] : 
    `linear-gradient(135deg, ${props.theme.colors.primary}, ${props.theme.colors.secondary})`
  };
  color: ${props => props.variant === 'secondary' ? props.theme.colors.text : 'white'};
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-${props => props.theme.direction === 'rtl' ? 'left' : 'right'}: 8px;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const VoicePreview = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: ${props => props.theme.colors.gray[50]};
  border-radius: 8px;
  margin-bottom: 16px;
  
  .play-button {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background: ${props => props.theme.colors.primary};
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      transform: scale(1.1);
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }
  }
  
  .voice-info {
    flex: 1;
    
    .voice-name {
      font-weight: 600;
      color: ${props => props.theme.colors.text};
      margin-bottom: 2px;
    }
    
    .voice-description {
      font-size: 0.85rem;
      color: ${props => props.theme.colors.gray[600]};
    }
  }
`;

const SaveBanner = styled(motion.div)`
  position: fixed;
  top: 20px;
  ${props => props.theme.direction === 'rtl' ? 'left' : 'right'}: 20px;
  padding: 12px 20px;
  background: #4CAF50;
  color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
`;

// Settings data
const SETTINGS_SECTIONS = [
  { id: 'general', title: 'عام', icon: '⚙️' },
  { id: 'voice', title: 'الصوت والنطق', icon: '🎵' },
  { id: 'privacy', title: 'الخصوصية والأمان', icon: '🔒' },
  { id: 'notifications', title: 'الإشعارات', icon: '🔔' },
  { id: 'parental', title: 'الرقابة الأبوية', icon: '👨‍👩‍👧‍👦' },
  { id: 'data', title: 'البيانات والنسخ الاحتياطي', icon: '💾' }
];

const VOICE_OPTIONS = [
  { value: 'female-ar', label: 'صوت أنثوي عربي', description: 'صوت لطيف ومناسب للأطفال' },
  { value: 'male-ar', label: 'صوت ذكوري عربي', description: 'صوت دافئ وودود' },
  { value: 'child-ar', label: 'صوت طفولي عربي', description: 'صوت يشبه صوت الأطفال' }
];

const LANGUAGE_OPTIONS = [
  { value: 'ar-SA', label: 'العربية (السعودية)' },
  { value: 'ar-EG', label: 'العربية (مصر)' },
  { value: 'ar-AE', label: 'العربية (الإمارات)' },
  { value: 'en-US', label: 'English (US)' }
];

// Main Component
const Settings = ({ onSave, initialSettings = DEFAULT_SETTINGS }) => {
  const [activeSection, setActiveSection] = useState('general');
  const [settings, setSettings] = useState(initialSettings);
  const [hasChanges, setHasChanges] = useState(false);
  const [showSaveBanner, setShowSaveBanner] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  // Update setting value
  const updateSetting = useCallback((key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  }, []);

  // Save settings
  const handleSave = useCallback(async () => {
    try {
      // Save to localStorage
      storage.set('teddySettings', settings);
      
      // Call external save handler if provided
      if (onSave) {
        await onSave(settings);
      }
      
      setHasChanges(false);
      setShowSaveBanner(true);
      setTimeout(() => setShowSaveBanner(false), 3000);
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  }, [settings, onSave]);

  // Reset to defaults
  const handleReset = useCallback(() => {
    setSettings(DEFAULT_SETTINGS);
    setHasChanges(true);
  }, []);

  // Play voice preview
  const playVoicePreview = useCallback(async (voiceId) => {
    if (isPlaying) return;
    
    setIsPlaying(true);
    try {
      // This would integrate with your TTS service
      const audio = new Audio(`/api/voice-preview/${voiceId}`);
      await audio.play();
      audio.onended = () => setIsPlaying(false);
    } catch (error) {
      console.error('Failed to play voice preview:', error);
      setIsPlaying(false);
    }
  }, [isPlaying]);

  // Memoized sections
  const currentSection = useMemo(() => {
    return SETTINGS_SECTIONS.find(section => section.id === activeSection);
  }, [activeSection]);

  // Render setting sections
  const renderGeneralSettings = () => (
    <SettingsSection>
      <h3>
        <span>⚙️</span>
        الإعدادات العامة
      </h3>
      <p>تخصيص التجربة العامة لطفلك مع دبدوب الذكي</p>

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">اللغة</div>
          <div className="setting-description">اختر لغة التفاعل مع دبدوب</div>
        </div>
        <div className="setting-control">
          <Select
            value={settings.language}
            onChange={(e) => updateSetting('language', e.target.value)}
          >
            {LANGUAGE_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>
        </div>
      </SettingItem>

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">المظهر</div>
          <div className="setting-description">اختر بين المظهر الفاتح أو الداكن</div>
        </div>
        <div className="setting-control">
          <Select
            value={settings.theme}
            onChange={(e) => updateSetting('theme', e.target.value)}
          >
            <option value="light">فاتح</option>
            <option value="dark">داكن</option>
            <option value="auto">تلقائي</option>
          </Select>
        </div>
      </SettingItem>

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">تشغيل الردود تلقائياً</div>
          <div className="setting-description">تشغيل ردود دبدوب الصوتية تلقائياً</div>
        </div>
        <div className="setting-control">
          <Toggle
            checked={settings.autoPlayResponses}
            onClick={() => updateSetting('autoPlayResponses', !settings.autoPlayResponses)}
          />
        </div>
      </SettingItem>
    </SettingsSection>
  );

  const renderVoiceSettings = () => (
    <SettingsSection>
      <h3>
        <span>🎵</span>
        إعدادات الصوت والنطق
      </h3>
      <p>تخصيص صوت دبدوب وطريقة النطق</p>

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">نوع الصوت</div>
          <div className="setting-description">اختر نوع صوت دبدوب المفضل</div>
        </div>
        <div className="setting-control">
          <Select
            value={settings.voiceType || 'female-ar'}
            onChange={(e) => updateSetting('voiceType', e.target.value)}
          >
            {VOICE_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>
        </div>
      </SettingItem>

      {VOICE_OPTIONS.map(voice => (
        <VoicePreview key={voice.value}>
          <button
            className="play-button"
            onClick={() => playVoicePreview(voice.value)}
            disabled={isPlaying}
          >
            {isPlaying ? '⏸️' : '▶️'}
          </button>
          <div className="voice-info">
            <div className="voice-name">{voice.label}</div>
            <div className="voice-description">{voice.description}</div>
          </div>
        </VoicePreview>
      ))}

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">تفعيل الأصوات</div>
          <div className="setting-description">تشغيل أو إيقاف جميع الأصوات</div>
        </div>
        <div className="setting-control">
          <Toggle
            checked={settings.soundEnabled}
            onClick={() => updateSetting('soundEnabled', !settings.soundEnabled)}
          />
        </div>
      </SettingItem>
    </SettingsSection>
  );

  const renderPrivacySettings = () => (
    <SettingsSection>
      <h3>
        <span>🔒</span>
        الخصوصية والأمان
      </h3>
      <p>حماية بيانات طفلك وضمان تفاعل آمن</p>

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">حفظ المحادثات</div>
          <div className="setting-description">حفظ محادثات الطفل لتحسين التجربة</div>
        </div>
        <div className="setting-control">
          <Toggle
            checked={settings.saveConversations !== false}
            onClick={() => updateSetting('saveConversations', !settings.saveConversations)}
          />
        </div>
      </SettingItem>

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">تشفير البيانات</div>
          <div className="setting-description">تشفير جميع البيانات المرسلة والمستقبلة</div>
        </div>
        <div className="setting-control">
          <Toggle
            checked={settings.encryptData !== false}
            onClick={() => updateSetting('encryptData', !settings.encryptData)}
          />
        </div>
      </SettingItem>

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">مشاركة البيانات للتحسين</div>
          <div className="setting-description">مشاركة بيانات مجهولة لتحسين الخدمة</div>
        </div>
        <div className="setting-control">
          <Toggle
            checked={settings.shareAnalytics || false}
            onClick={() => updateSetting('shareAnalytics', !settings.shareAnalytics)}
          />
        </div>
      </SettingItem>
    </SettingsSection>
  );

  const renderNotificationSettings = () => (
    <SettingsSection>
      <h3>
        <span>🔔</span>
        إعدادات الإشعارات
      </h3>
      <p>تخصيص الإشعارات والتنبيهات</p>

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">تفعيل الإشعارات</div>
          <div className="setting-description">تلقي إشعارات من التطبيق</div>
        </div>
        <div className="setting-control">
          <Toggle
            checked={settings.notificationsEnabled}
            onClick={() => updateSetting('notificationsEnabled', !settings.notificationsEnabled)}
          />
        </div>
      </SettingItem>

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">إشعارات النشاط</div>
          <div className="setting-description">إشعارات عند بدء أو انتهاء النشاط</div>
        </div>
        <div className="setting-control">
          <Toggle
            checked={settings.activityNotifications !== false}
            onClick={() => updateSetting('activityNotifications', !settings.activityNotifications)}
          />
        </div>
      </SettingItem>

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">التقارير اليومية</div>
          <div className="setting-description">تلقي تقرير يومي عن نشاط الطفل</div>
        </div>
        <div className="setting-control">
          <Toggle
            checked={settings.dailyReports || false}
            onClick={() => updateSetting('dailyReports', !settings.dailyReports)}
          />
        </div>
      </SettingItem>
    </SettingsSection>
  );

  const renderParentalSettings = () => (
    <SettingsSection>
      <h3>
        <span>👨‍👩‍👧‍👦</span>
        الرقابة الأبوية
      </h3>
      <p>ضوابط الأمان والحماية للأطفال</p>

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">تفعيل الرقابة الأبوية</div>
          <div className="setting-description">تشغيل ميزات الحماية والرقابة</div>
        </div>
        <div className="setting-control">
          <Toggle
            checked={settings.parentalControlsEnabled}
            onClick={() => updateSetting('parentalControlsEnabled', !settings.parentalControlsEnabled)}
          />
        </div>
      </SettingItem>

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">تصفية المحتوى</div>
          <div className="setting-description">تصفية المحتوى غير المناسب للأطفال</div>
        </div>
        <div className="setting-control">
          <Toggle
            checked={settings.contentFiltering !== false}
            onClick={() => updateSetting('contentFiltering', !settings.contentFiltering)}
          />
        </div>
      </SettingItem>

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">حد وقت الاستخدام (بالدقائق)</div>
          <div className="setting-description">الحد الأقصى لوقت الاستخدام اليومي</div>
        </div>
        <div className="setting-control">
          <Select
            value={settings.dailyTimeLimit || 60}
            onChange={(e) => updateSetting('dailyTimeLimit', parseInt(e.target.value))}
          >
            <option value={30}>30 دقيقة</option>
            <option value={60}>60 دقيقة</option>
            <option value={90}>90 دقيقة</option>
            <option value={120}>120 دقيقة</option>
            <option value={0}>بدون حد</option>
          </Select>
        </div>
      </SettingItem>
    </SettingsSection>
  );

  const renderDataSettings = () => (
    <SettingsSection>
      <h3>
        <span>💾</span>
        البيانات والنسخ الاحتياطي
      </h3>
      <p>إدارة البيانات والنسخ الاحتياطية</p>

      <SettingItem>
        <div className="setting-info">
          <div className="setting-title">النسخ الاحتياطي التلقائي</div>
          <div className="setting-description">إنشاء نسخة احتياطية تلقائية للبيانات</div>
        </div>
        <div className="setting-control">
          <Toggle
            checked={settings.autoBackup !== false}
            onClick={() => updateSetting('autoBackup', !settings.autoBackup)}
          />
        </div>
      </SettingItem>

      <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
        <Button onClick={() => console.log('Export data')}>
          تصدير البيانات
        </Button>
        <Button variant="secondary" onClick={() => console.log('Import data')}>
          استيراد البيانات
        </Button>
        <Button variant="danger" onClick={() => console.log('Clear data')}>
          مسح جميع البيانات
        </Button>
      </div>
    </SettingsSection>
  );

  const renderCurrentSection = () => {
    switch (activeSection) {
      case 'general': return renderGeneralSettings();
      case 'voice': return renderVoiceSettings();
      case 'privacy': return renderPrivacySettings();
      case 'notifications': return renderNotificationSettings();
      case 'parental': return renderParentalSettings();
      case 'data': return renderDataSettings();
      default: return renderGeneralSettings();
    }
  };

  return (
    <>
      <SettingsContainer>
        <SettingsHeader>
          <h2>إعدادات دبدوب الذكي</h2>
          <p>تخصيص تجربة طفلك مع دبدوب الذكي</p>
        </SettingsHeader>

        <SettingsGrid>
          <SettingsNav>
            {SETTINGS_SECTIONS.map(section => (
              <NavItem
                key={section.id}
                active={activeSection === section.id}
                onClick={() => setActiveSection(section.id)}
              >
                <span style={{ marginInlineEnd: '8px' }}>{section.icon}</span>
                {section.title}
              </NavItem>
            ))}
          </SettingsNav>

          <SettingsContent>
            {renderCurrentSection()}
            
            {hasChanges && (
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '32px', gap: '12px' }}>
                <Button variant="secondary" onClick={handleReset}>
                  إعادة تعيين
                </Button>
                <Button onClick={handleSave}>
                  حفظ التغييرات
                </Button>
              </div>
            )}
          </SettingsContent>
        </SettingsGrid>
      </SettingsContainer>

      <AnimatePresence>
        {showSaveBanner && (
          <SaveBanner
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
          >
            <span>✅</span>
            تم حفظ الإعدادات بنجاح
          </SaveBanner>
        )}
      </AnimatePresence>
    </>
  );
};

Settings.displayName = 'Settings';

export default memo(Settings); 