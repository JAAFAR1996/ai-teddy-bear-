/**
 * Dashboard Component - Parent's main view
 * Real-time monitoring of child interactions
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '@hooks/useAuth';
import { useWebSocket } from '@hooks/useWebSocket';
import { useDashboard } from '@hooks/useDashboard';
import { 
  DashboardStats, 
  EmotionType, 
  WebSocketEvent,
  Conversation 
} from '@types';
import StatsCard from './StatsCard';
import EmotionChart from './EmotionChart';
import RecentConversations from './RecentConversations';
import ActivityTimeline from './ActivityTimeline';
import DeviceStatus from './DeviceStatus';
import styles from './Dashboard.module.css';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { isConnected, on } = useWebSocket();
  const { stats, loading, error, refreshStats } = useDashboard();
  const [realtimeData, setRealtimeData] = useState<{
    currentEmotion?: EmotionType;
    activeSession?: string;
    lastUpdate?: Date;
  }>({});

  // Subscribe to real-time updates
  useEffect(() => {
    const unsubscribeConversation = on<Conversation>('conversation:new', (data) => {
      setRealtimeData(prev => ({
        ...prev,
        currentEmotion: data.emotion.primary,
        lastUpdate: new Date(),
      }));
      
      // Refresh stats after new conversation
      refreshStats();
    });

    const unsubscribeEmotion = on<{ emotion: EmotionType }>('emotion:update', (data) => {
      setRealtimeData(prev => ({
        ...prev,
        currentEmotion: data.emotion,
        lastUpdate: new Date(),
      }));
    });

    const unsubscribeSession = on<{ sessionId: string }>('session:start', (data) => {
      setRealtimeData(prev => ({
        ...prev,
        activeSession: data.sessionId,
      }));
    });

    const unsubscribeSessionEnd = on('session:end', () => {
      setRealtimeData(prev => ({
        ...prev,
        activeSession: undefined,
      }));
      refreshStats();
    });

    return () => {
      unsubscribeConversation();
      unsubscribeEmotion();
      unsubscribeSession();
      unsubscribeSessionEnd();
    };
  }, [on, refreshStats]);

  if (loading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return <DashboardError error={error} onRetry={refreshStats} />;
  }

  if (!stats) {
    return null;
  }

  const emotionIcon = getEmotionIcon(realtimeData.currentEmotion || stats.averageEmotion);
  const connectionStatus = isConnected ? 'connected' : 'disconnected';

  return (
    <div className={styles.dashboard}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>
            مرحباً، {user?.name || 'ولي الأمر'} 👋
          </h1>
          <p className={styles.subtitle}>
            تابع نشاط أطفالك مع دبدوب الذكي
          </p>
        </div>
        <div className={styles.connectionStatus} data-status={connectionStatus}>
          <span className={styles.connectionDot} />
          {isConnected ? 'متصل' : 'غير متصل'}
        </div>
      </div>

      {/* Real-time Alert */}
      {realtimeData.activeSession && (
        <div className={styles.alert} data-type="info">
          <span className={styles.alertIcon}>🎤</span>
          <span>جلسة نشطة الآن</span>
          {realtimeData.lastUpdate && (
            <time className={styles.alertTime}>
              {formatRelativeTime(realtimeData.lastUpdate)}
            </time>
          )}
        </div>
      )}

      {/* Stats Grid */}
      <div className={styles.statsGrid}>
        <StatsCard
          title="المحادثات اليوم"
          value={stats.todayConversations}
          subtitle={`${stats.todayConversations - stats.yesterdayConversations >= 0 ? '+' : ''}${
            stats.todayConversations - stats.yesterdayConversations
          } من الأمس`}
          icon="💬"
          trend={stats.todayConversations >= stats.yesterdayConversations ? 'up' : 'down'}
        />

        <StatsCard
          title="الحالة العاطفية"
          value={emotionIcon}
          subtitle={getEmotionLabel(realtimeData.currentEmotion || stats.averageEmotion)}
          isLive={!!realtimeData.currentEmotion}
        />

        <StatsCard
          title="وقت النشاط"
          value={`${stats.totalActiveTime} دقيقة`}
          subtitle="اليوم"
          icon="⏱️"
        />

        <StatsCard
          title="التقدم التعليمي"
          value={`${stats.learningProgress}%`}
          subtitle={getLearningProgressLabel(stats.learningProgress)}
          icon="📚"
          progress={stats.learningProgress}
        />
      </div>

      {/* Charts Section */}
      <div className={styles.chartsSection}>
        <div className={styles.chartCard}>
          <h2 className={styles.chartTitle}>توزيع المشاعر</h2>
          <EmotionChart data={stats.weeklyTrend} />
        </div>

        <div className={styles.chartCard}>
          <h2 className={styles.chartTitle}>النشاط الأسبوعي</h2>
          <ActivityTimeline data={stats.weeklyTrend} />
        </div>
      </div>

      {/* Recent Activity */}
      <div className={styles.recentSection}>
        <div className={styles.recentCard}>
          <h2 className={styles.sectionTitle}>المحادثات الأخيرة</h2>
          <RecentConversations />
        </div>

        <div className={styles.deviceCard}>
          <h2 className={styles.sectionTitle}>حالة الجهاز</h2>
          <DeviceStatus />
        </div>
      </div>
    </div>
  );
};

// Skeleton loader
const DashboardSkeleton: React.FC = () => (
  <div className={styles.skeleton}>
    <div className={styles.skeletonHeader} />
    <div className={styles.skeletonGrid}>
      {[1, 2, 3, 4].map(i => (
        <div key={i} className={styles.skeletonCard} />
      ))}
    </div>
    <div className={styles.skeletonCharts}>
      <div className={styles.skeletonChart} />
      <div className={styles.skeletonChart} />
    </div>
  </div>
);

// Error component
interface DashboardErrorProps {
  error: Error;
  onRetry: () => void;
}

const DashboardError: React.FC<DashboardErrorProps> = ({ error, onRetry }) => (
  <div className={styles.error}>
    <div className={styles.errorContent}>
      <span className={styles.errorIcon}>⚠️</span>
      <h2>حدث خطأ</h2>
      <p>{error.message || 'لم نتمكن من تحميل البيانات'}</p>
      <button className={styles.retryButton} onClick={onRetry}>
        إعادة المحاولة
      </button>
    </div>
  </div>
);

// Helper functions
function getEmotionIcon(emotion: EmotionType): string {
  const emotionIcons: Record<EmotionType, string> = {
    happy: '😊',
    sad: '😢',
    angry: '😠',
    scared: '😨',
    surprised: '😮',
    neutral: '😐',
    excited: '🤗',
  };
  return emotionIcons[emotion] || '😐';
}

function getEmotionLabel(emotion: EmotionType): string {
  const emotionLabels: Record<EmotionType, string> = {
    happy: 'سعيد',
    sad: 'حزين',
    angry: 'غاضب',
    scared: 'خائف',
    surprised: 'متفاجئ',
    neutral: 'محايد',
    excited: 'متحمس',
  };
  return emotionLabels[emotion] || 'محايد';
}

function getLearningProgressLabel(progress: number): string {
  if (progress >= 90) return 'ممتاز';
  if (progress >= 70) return 'جيد جداً';
  if (progress >= 50) return 'جيد';
  return 'يحتاج تحسين';
}

function formatRelativeTime(date: Date): string {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  
  if (seconds < 60) return 'الآن';
  if (seconds < 3600) return `منذ ${Math.floor(seconds / 60)} دقيقة`;
  if (seconds < 86400) return `منذ ${Math.floor(seconds / 3600)} ساعة`;
  return `منذ ${Math.floor(seconds / 86400)} يوم`;
}

export default Dashboard; 