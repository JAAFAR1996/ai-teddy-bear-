import React, { useState, useEffect, useMemo, useCallback, memo, useRef } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiUser, FiHeart, FiMessageCircle, FiDownload, FiSettings,
  FiBarChart3, FiClock, FiAlertCircle, FiSmile, FiTrendingUp,
  FiCalendar, FiActivity, FiZap, FiShield, FiFileText, FiEye,
  FiWifi, FiWifiOff, FiBell, FiRefreshCw
} from 'react-icons/fi';
import { toast, Toaster } from 'react-hot-toast';

// Custom hooks and services
import { useQuery } from '../hooks/useQuery';
import { dashboardAPI, childAPI, analyticsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useDashboardNotifications } from '../hooks/useWebSocket';

// PDF utilities
import { exportDashboardPDF } from '../utils/pdf';

// UI Components (Memoized)
import LoadingSpinner, { DataLoader, SkeletonLoader } from './LoadingSpinner';
import Card from './ui/Card';
import Button from './ui/Button';
import StatCard from './ui/StatCard';
import Chart, { ActivityChart, PerformanceChart } from './ui/Chart';
import EmotionChart from './ui/EmotionChart';
import ActivityTimeline, { ConversationTimeline, AchievementTimeline } from './ui/ActivityTimeline';

// Styled components (moved outside component to prevent recreation)
const DashboardContainer = styled.div`
  padding: ${props => props.theme.spacing.xl};
  max-width: 1400px;
  margin: 0 auto;
  
  ${props => props.theme.mediaQueries.maxMd} {
    padding: ${props => props.theme.spacing.md};
  }
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.xl};
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.md};
`;

const Title = styled.h1`
  color: ${props => props.theme.colors.text};
  font-size: ${props => props.theme.typography.fontSize['3xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  margin: 0;
  
  ${props => props.theme.mediaQueries.maxSm} {
    font-size: ${props => props.theme.typography.fontSize['2xl']};
  }
`;

const Subtitle = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.typography.fontSize.lg};
  margin: ${props => props.theme.spacing.sm} 0 0 0;
`;

const ActionsGroup = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  align-items: center;
  flex-wrap: wrap;
`;

const ConnectionStatus = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.full};
  font-size: ${props => props.theme.typography.fontSize.xs};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  
  background: ${props => props.connected 
    ? props.theme.colors.successLight + '22' 
    : props.theme.colors.dangerLight + '22'};
  color: ${props => props.connected 
    ? props.theme.colors.success 
    : props.theme.colors.danger};
  border: 1px solid ${props => props.connected 
    ? props.theme.colors.success 
    : props.theme.colors.danger};
`;

const NotificationBadge = styled.div`
  position: relative;
  
  &::after {
    content: '${props => props.count || ''}';
    position: absolute;
    top: -8px;
    right: -8px;
    background: ${props => props.theme.colors.danger};
    color: white;
    border-radius: 50%;
    width: 18px;
    height: 18px;
    font-size: 10px;
    font-weight: bold;
    display: ${props => props.count > 0 ? 'flex' : 'none'};
    align-items: center;
    justify-content: center;
    min-width: 18px;
  }
`;

const PDFButtonGroup = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.xs};
  
  .pdf-dropdown {
    position: relative;
  }
  
  .pdf-options {
    position: absolute;
    top: 100%;
    right: 0;
    background: ${props => props.theme.colors.surface};
    border: 1px solid ${props => props.theme.colors.border};
    border-radius: ${props => props.theme.borderRadius.lg};
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    padding: ${props => props.theme.spacing.sm};
    min-width: 200px;
    z-index: 1000;
    margin-top: ${props => props.theme.spacing.xs};
    
    button {
      display: flex;
      align-items: center;
      gap: ${props => props.theme.spacing.sm};
      width: 100%;
      padding: ${props => props.theme.spacing.sm};
      border: none;
      background: transparent;
      color: ${props => props.theme.colors.text};
      font-size: ${props => props.theme.typography.fontSize.sm};
      border-radius: ${props => props.theme.borderRadius.md};
      cursor: pointer;
      transition: background-color 0.2s ease;
      
      &:hover {
        background: ${props => props.theme.colors.surfaceLight};
      }
    }
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
  
  ${props => props.theme.mediaQueries.maxLg} {
    grid-template-columns: 1fr;
  }
`;

const ActivitiesGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${props => props.theme.spacing.lg};
  
  ${props => props.theme.mediaQueries.maxMd} {
    grid-template-columns: 1fr;
  }
`;

const ChildSelector = styled.select`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  background: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.text};
  font-size: ${props => props.theme.typography.fontSize.base};
  min-width: 200px;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.primary}33;
  }
`;

const ErrorMessage = styled.div`
  background: ${props => props.theme.colors.dangerLight}22;
  border: 1px solid ${props => props.theme.colors.danger};
  color: ${props => props.theme.colors.danger};
  padding: ${props => props.theme.spacing.lg};
  border-radius: ${props => props.theme.borderRadius.lg};
  text-align: center;
  margin: ${props => props.theme.spacing.xl} 0;
`;

const WelcomeCard = styled(Card)`
  background: ${props => props.theme.colors.gradientPrimary};
  color: ${props => props.theme.colors.textLight};
  margin-bottom: ${props => props.theme.spacing.xl};
  
  h2 {
    color: ${props => props.theme.colors.textLight};
    margin-bottom: ${props => props.theme.spacing.sm};
  }
  
  p {
    color: rgba(255, 255, 255, 0.9);
    opacity: 0.9;
  }
`;

// Memoized Statistics Cards Component
const StatisticsSection = memo(({ dashboardData, isLoading }) => {
  const statsData = useMemo(() => {
    if (!dashboardData?.stats) return null;
    
    return [
      {
        title: "إجمالي المحادثات",
        value: dashboardData.stats.totalConversations || 0,
        icon: <FiMessageCircle />,
        color: "primary",
        trend: "+12%",
        subtitle: "هذا الأسبوع"
      },
      {
        title: "الحالة العاطفية",
        value: dashboardData.stats.emotionScore || 'ممتاز',
        icon: <FiHeart />,
        color: "success",
        trend: "مستقر",
        subtitle: "المتوسط الأسبوعي"
      },
      {
        title: "وقت النشاط",
        value: `${dashboardData.stats.activeMinutes || 45} دقيقة`,
        icon: <FiClock />,
        color: "info",
        trend: "+8 دقائق",
        subtitle: "اليوم"
      },
      {
        title: "مستوى التعلم",
        value: dashboardData.stats.learningProgress || '85%',
        icon: <FiTrendingUp />,
        color: "warning",
        trend: "+5%",
        subtitle: "تحسن ملحوظ"
      }
    ];
  }, [dashboardData?.stats]);

  if (isLoading) {
    return (
      <StatsGrid>
        {Array.from({ length: 4 }, (_, i) => (
          <SkeletonLoader key={i} height="120px" />
        ))}
      </StatsGrid>
    );
  }

  if (!statsData) {
    return (
      <StatsGrid>
        {Array.from({ length: 4 }, (_, i) => (
          <SkeletonLoader key={i} height="120px" />
        ))}
      </StatsGrid>
    );
  }

  return (
    <StatsGrid>
      {statsData.map((stat, index) => (
        <StatCard
          key={stat.title}
          {...stat}
        />
      ))}
    </StatsGrid>
  );
});

StatisticsSection.displayName = 'StatisticsSection';

// Memoized Charts Section Component
const ChartsSection = memo(({ analyticsData, dashboardData, analyticsLoading, dashboardLoading }) => {
  const emotionChartData = useMemo(() => {
    return analyticsData?.emotions || null;
  }, [analyticsData?.emotions]);

  const activityChartData = useMemo(() => {
    return dashboardData?.dailyActivity || null;
  }, [dashboardData?.dailyActivity]);

  return (
    <ChartsGrid>
      <Card title="تحليل المشاعر - آخر 7 أيام" icon={<FiBarChart3 />}>
        {analyticsLoading ? (
          <SkeletonLoader height="300px" />
        ) : emotionChartData ? (
          <EmotionChart 
            data={emotionChartData} 
            height={300}
            showSummary={true}
            title="تطور المشاعر"
          />
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#6c757d' }}>
            لا توجد بيانات متاحة
          </div>
        )}
      </Card>

      <Card title="النشاط اليومي" icon={<FiActivity />}>
        {dashboardLoading ? (
          <SkeletonLoader height="300px" />
        ) : activityChartData ? (
          <ActivityChart 
            data={activityChartData} 
            height={300}
            xDataKey="date"
            yDataKeys={['activeMinutes', 'conversationTime']}
          />
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#6c757d' }}>
            لا توجد بيانات متاحة
          </div>
        )}
      </Card>
    </ChartsGrid>
  );
});

ChartsSection.displayName = 'ChartsSection';

// Memoized Activities Section Component
const ActivitiesSection = memo(({ dashboardData, isLoading }) => {
  const conversationsData = useMemo(() => {
    return dashboardData?.recentConversations || [];
  }, [dashboardData?.recentConversations]);

  const achievementsData = useMemo(() => {
    return dashboardData?.achievements || [];
  }, [dashboardData?.achievements]);

  const renderSkeletonItems = useCallback(() => (
    <div>
      {Array.from({ length: 3 }, (_, i) => (
        <SkeletonLoader key={i} height="60px" margin="0 0 1rem 0" />
      ))}
    </div>
  ), []);

  return (
    <ActivitiesGrid>
      <Card title="المحادثات الأخيرة" icon={<FiMessageCircle />}>
        {isLoading ? (
          renderSkeletonItems()
        ) : (
          <ConversationTimeline 
            activities={conversationsData}
            maxItems={8}
            showEmotions={true}
          />
        )}
      </Card>

      <Card title="الإنجازات والتقدم" icon={<FiZap />}>
        {isLoading ? (
          renderSkeletonItems()
        ) : (
          <AchievementTimeline 
            activities={achievementsData}
            maxItems={8}
            showMeta={true}
          />
        )}
      </Card>
    </ActivitiesGrid>
  );
});

ActivitiesSection.displayName = 'ActivitiesSection';

// Memoized Quick Actions Component
const QuickActions = memo(() => {
  const actionButtons = useMemo(() => [
    { icon: <FiUser />, text: "عرض الملف الشخصي", variant: "outline" },
    { icon: <FiBarChart3 />, text: "التحليلات التفصيلية", variant: "outline" },
    { icon: <FiSettings />, text: "إعدادات الإشعارات", variant: "outline" },
    { icon: <FiShield />, text: "إعدادات الأمان", variant: "outline" }
  ], []);

  return (
    <Card title="إجراءات سريعة" style={{ marginTop: '2rem' }}>
      <div style={{ 
        display: 'flex', 
        gap: '1rem', 
        flexWrap: 'wrap',
        justifyContent: 'center'
      }}>
        {actionButtons.map((action, index) => (
          <Button key={index} variant={action.variant}>
            {action.icon}
            {action.text}
          </Button>
        ))}
      </div>
    </Card>
  );
});

QuickActions.displayName = 'QuickActions';

// Main Dashboard Component (Memoized)
const Dashboard = memo(({ childId: propChildId }) => {
  const { user } = useAuth();
  const [selectedChildId, setSelectedChildId] = useState(propChildId || null);
  const [timeRange, setTimeRange] = useState('7d');
  const [showPDFOptions, setShowPDFOptions] = useState(false);
  const [pdfGenerating, setPdfGenerating] = useState(false);
  
  // Refs
  const dashboardRef = useRef(null);
  const pdfOptionsRef = useRef(null);
  
  // WebSocket notifications
  const {
    isConnected: wsConnected,
    notifications,
    unreadCount,
    markAsRead,
    clearNotifications
  } = useDashboardNotifications(selectedChildId);

  // Memoized query options
  const childrenQueryOptions = useMemo(() => ({
    staleTime: 10 * 60 * 1000 // 10 minutes
  }), []);

  const dashboardQueryOptions = useMemo(() => ({
    enabled: !!selectedChildId,
    staleTime: 5 * 60 * 1000 // 5 minutes
  }), [selectedChildId]);

  const analyticsQueryOptions = useMemo(() => ({
    enabled: !!selectedChildId,
    staleTime: 5 * 60 * 1000
  }), [selectedChildId]);

  // Fetch children list
  const { 
    data: children, 
    isLoading: childrenLoading, 
    error: childrenError 
  } = useQuery(
    'children', 
    dashboardAPI.getChildren,
    childrenQueryOptions
  );

  // Fetch dashboard data for selected child
  const { 
    data: dashboardData, 
    isLoading: dashboardLoading, 
    error: dashboardError,
    refetch: refetchDashboard
  } = useQuery(
    ['dashboard', selectedChildId], 
    useCallback(() => selectedChildId ? dashboardAPI.getDashboard(selectedChildId) : null, [selectedChildId]),
    dashboardQueryOptions
  );

  // Fetch analytics data
  const { 
    data: analyticsData, 
    isLoading: analyticsLoading 
  } = useQuery(
    ['analytics', selectedChildId, timeRange], 
    useCallback(() => selectedChildId ? analyticsAPI.getEmotionTrends(selectedChildId, timeRange) : null, [selectedChildId, timeRange]),
    analyticsQueryOptions
  );

  // Auto-select first child if no child is selected
  useEffect(() => {
    if (children && children.length > 0 && !selectedChildId) {
      setSelectedChildId(children[0].udid);
    }
  }, [children, selectedChildId]);

  // Memoized event handlers
  const handleChildChange = useCallback((e) => {
    setSelectedChildId(e.target.value);
  }, []);

  const handleExportData = useCallback(async () => {
    try {
      await dashboardAPI.exportData(selectedChildId, 'json');
      toast.success('تم تصدير البيانات بنجاح');
    } catch (error) {
      console.error('Export failed:', error);
      toast.error('فشل في تصدير البيانات');
    }
  }, [selectedChildId]);

  const handleRefresh = useCallback(() => {
    refetchDashboard();
    toast.success('تم تحديث البيانات');
  }, [refetchDashboard]);

  // PDF Generation handlers
  const handlePDFGeneration = useCallback(async (method = 'professional') => {
    if (!selectedChild || !dashboardData) {
      toast.error('لا توجد بيانات لإنشاء التقرير');
      return;
    }

    setPdfGenerating(true);
    setShowPDFOptions(false);

    try {
      const childData = {
        child: selectedChild,
        reportDate: new Date(),
        summary: dashboardData.stats,
        emotions: analyticsData,
        activities: dashboardData.recentConversations || [],
        stats: dashboardData.stats,
        trends: dashboardData.trends,
        recommendations: dashboardData.recommendations || []
      };

      const result = await exportDashboardPDF('dashboard-content', childData, {
        method,
        includeCharts: true,
        includeTimeline: true,
        filename: `تقرير-${selectedChild.name}-${new Date().toISOString().split('T')[0]}.pdf`
      });

      if (result.success) {
        toast.success(`تم إنشاء التقرير بنجاح! (${(result.size / 1024 / 1024).toFixed(1)} MB)`);
      }
    } catch (error) {
      console.error('PDF generation failed:', error);
      toast.error(`فشل في إنشاء التقرير: ${error.message}`);
    } finally {
      setPdfGenerating(false);
    }
  }, [selectedChild, dashboardData, analyticsData]);

  const handleNotificationClick = useCallback((notification) => {
    markAsRead(notification.id);
    // Handle navigation based on notification type
    switch (notification.type) {
      case 'emotion_alert':
        // Navigate to emotion analysis
        break;
      case 'achievement_update':
        // Navigate to achievements
        break;
      default:
        break;
    }
  }, [markAsRead]);

  // Click outside handler for PDF options
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (pdfOptionsRef.current && !pdfOptionsRef.current.contains(event.target)) {
        setShowPDFOptions(false);
      }
    };

    if (showPDFOptions) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showPDFOptions]);

  // Memoized selected child
  const selectedChild = useMemo(() => {
    return children?.find(child => child.udid === selectedChildId);
  }, [children, selectedChildId]);

  // Memoized child options for selector
  const childOptions = useMemo(() => {
    return children?.map(child => ({
      value: child.udid,
      label: `${child.name} (${child.age} سنوات)`
    })) || [];
  }, [children]);

  // Loading state
  if (childrenLoading) {
    return <DataLoader text="جاري تحميل بيانات الأطفال..." />;
  }

  // Error state
  if (childrenError) {
    return (
      <DashboardContainer>
        <ErrorMessage>
          <FiAlertCircle size={24} style={{ marginBottom: '8px' }} />
          <div>حدث خطأ في تحميل البيانات. يرجى المحاولة لاحقاً.</div>
        </ErrorMessage>
      </DashboardContainer>
    );
  }

  // No children state
  if (!children || children.length === 0) {
    return (
      <DashboardContainer>
        <WelcomeCard>
          <h2>مرحباً بك في نظام دب تيدي الذكي! 🧸</h2>
          <p>لم يتم العثور على أطفال مسجلين بعد. يرجى إضافة طفل للبدء في استخدام النظام.</p>
          <Button style={{ marginTop: '1rem' }}>
            إضافة طفل جديد
          </Button>
        </WelcomeCard>
      </DashboardContainer>
    );
  }

  return (
    <DashboardContainer id="dashboard-content" ref={dashboardRef}>
      {/* Toast Container */}
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            iconTheme: {
              primary: '#10B981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#EF4444',
              secondary: '#fff',
            },
          },
        }}
      />

      {/* Header */}
      <Header>
        <div>
          <Title>لوحة تحكم الوالدين 👨‍👩‍👧‍👦</Title>
          <Subtitle>
            مرحباً {user?.name}، إليك ملخص نشاط أطفالك
            <ConnectionStatus connected={wsConnected}>
              {wsConnected ? <FiWifi size={12} /> : <FiWifiOff size={12} />}
              {wsConnected ? 'متصل' : 'غير متصل'}
            </ConnectionStatus>
          </Subtitle>
        </div>
        
        <ActionsGroup>
          {children.length > 1 && (
            <ChildSelector value={selectedChildId || ''} onChange={handleChildChange}>
              <option value="">اختر طفل</option>
              {childOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </ChildSelector>
          )}

          {/* Notifications */}
          {unreadCount > 0 && (
            <NotificationBadge count={unreadCount}>
              <Button 
                variant="outline" 
                onClick={() => toast('عرض الإشعارات قريباً')}
                title={`${unreadCount} إشعار جديد`}
              >
                <FiBell />
              </Button>
            </NotificationBadge>
          )}
          
          <Button 
            variant="outline" 
            onClick={handleRefresh}
            disabled={dashboardLoading}
          >
            <FiRefreshCw className={dashboardLoading ? 'animate-spin' : ''} />
            تحديث
          </Button>

          {/* PDF Generation Dropdown */}
          <PDFButtonGroup>
            <div className="pdf-dropdown" ref={pdfOptionsRef}>
              <Button 
                variant="primary"
                onClick={() => setShowPDFOptions(!showPDFOptions)}
                disabled={!selectedChildId || pdfGenerating}
              >
                {pdfGenerating ? (
                  <>
                    <FiRefreshCw className="animate-spin" />
                    جاري الإنشاء...
                  </>
                ) : (
                  <>
                    <FiDownload />
                    تحميل PDF
                  </>
                )}
              </Button>

              {showPDFOptions && (
                <motion.div
                  className="pdf-options"
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                >
                  <button onClick={() => handlePDFGeneration('professional')}>
                    <FiFileText />
                    تقرير احترافي
                  </button>
                  <button onClick={() => handlePDFGeneration('screenshot')}>
                    <FiEye />
                    لقطة شاشة
                  </button>
                </motion.div>
              )}
            </div>
          </PDFButtonGroup>
          
          <Button 
            variant="outline"
            onClick={handleExportData}
            disabled={!selectedChildId}
          >
            <FiDownload />
            تصدير البيانات
          </Button>
        </ActionsGroup>
      </Header>

      {/* Selected Child Dashboard */}
      {selectedChild && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Welcome Card for Selected Child */}
          <WelcomeCard>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{ fontSize: '3rem' }}>🧸</div>
              <div>
                <h2>مرحباً، {selectedChild.name}!</h2>
                <p>العمر: {selectedChild.age} سنوات • آخر نشاط: منذ {selectedChild.lastActivity || 'ساعتين'}</p>
              </div>
            </div>
          </WelcomeCard>

          {/* Statistics Cards */}
          <StatisticsSection 
            dashboardData={dashboardData} 
            isLoading={dashboardLoading} 
          />

          {/* Charts Section */}
          <ChartsSection
            analyticsData={analyticsData}
            dashboardData={dashboardData}
            analyticsLoading={analyticsLoading}
            dashboardLoading={dashboardLoading}
          />

          {/* Activities Section */}
          <ActivitiesSection 
            dashboardData={dashboardData} 
            isLoading={dashboardLoading} 
          />

          {/* Quick Actions */}
          <QuickActions />
        </motion.div>
      )}
    </DashboardContainer>
  );
});

Dashboard.displayName = 'Dashboard';

export default Dashboard; 