import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import { useTranslation } from 'react-i18next';
import { FiActivity, FiSmile, FiClock, FiTrendingUp } from 'react-icons/fi';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import { ar } from 'date-fns/locale';

// Domain & Application imports
import { useService } from '../architecture/dependency-injection';
import { SERVICE_TOKENS } from '../architecture/dependency-injection/container';
import { DashboardService } from '../architecture/application/services/DashboardService';
import { AnalyticsService } from '../architecture/application/services/AnalyticsService';

// Types
interface DashboardStats {
  dailyConversations: number;
  emotionalState: string;
  activityTime: number;
  educationalProgress: number;
  conversationTrend: Array<{ date: string; count: number }>;
  emotionDistribution: Array<{ emotion: string; value: number }>;
  topicAnalysis: Array<{ topic: string; frequency: number }>;
}

// Styled Components
const DashboardContainer = styled.div`
  padding: ${({ theme }) => theme.spacing['2xl']};
  max-width: 1400px;
  margin: 0 auto;
  
  @media (max-width: ${({ theme }) => theme.breakpoints.md}) {
    padding: ${({ theme }) => theme.spacing.lg};
  }
`;

const Header = styled.div`
  margin-bottom: ${({ theme }) => theme.spacing['2xl']};
`;

const Title = styled.h1`
  font-size: ${({ theme }) => theme.typography.fontSize['3xl']};
  color: ${({ theme }) => theme.colors.text.primary};
  margin-bottom: ${({ theme }) => theme.spacing.sm};
`;

const Subtitle = styled.p`
  font-size: ${({ theme }) => theme.typography.fontSize.lg};
  color: ${({ theme }) => theme.colors.text.secondary};
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: ${({ theme }) => theme.spacing.lg};
  margin-bottom: ${({ theme }) => theme.spacing['2xl']};
`;

const StatCard = styled(motion.div)`
  background: ${({ theme }) => theme.colors.background.primary};
  border-radius: ${({ theme }) => theme.borderRadius.xl};
  padding: ${({ theme }) => theme.spacing.xl};
  box-shadow: ${({ theme }) => theme.shadows.md};
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.lg};
  transition: ${({ theme }) => theme.transitions.base};
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: ${({ theme }) => theme.shadows.lg};
  }
`;

const StatIcon = styled.div<{ color: string }>`
  width: 64px;
  height: 64px;
  border-radius: ${({ theme }) => theme.borderRadius.lg};
  background: ${({ color }) => color}20;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  svg {
    width: 32px;
    height: 32px;
    color: ${({ color }) => color};
  }
`;

const StatContent = styled.div`
  flex: 1;
`;

const StatLabel = styled.p`
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  color: ${({ theme }) => theme.colors.text.secondary};
  margin-bottom: ${({ theme }) => theme.spacing.xs};
`;

const StatValue = styled.h3`
  font-size: ${({ theme }) => theme.typography.fontSize['2xl']};
  font-weight: ${({ theme }) => theme.typography.fontWeight.bold};
  color: ${({ theme }) => theme.colors.text.primary};
  margin: 0;
`;

const StatChange = styled.span<{ positive?: boolean }>`
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  color: ${({ theme, positive }) =>
    positive ? theme.colors.status.success : theme.colors.status.error};
  font-weight: ${({ theme }) => theme.typography.fontWeight.medium};
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: ${({ theme }) => theme.spacing.xl};
`;

const ChartCard = styled(motion.div)`
  background: ${({ theme }) => theme.colors.background.primary};
  border-radius: ${({ theme }) => theme.borderRadius.xl};
  padding: ${({ theme }) => theme.spacing.xl};
  box-shadow: ${({ theme }) => theme.shadows.md};
`;

const ChartTitle = styled.h3`
  font-size: ${({ theme }) => theme.typography.fontSize.xl};
  font-weight: ${({ theme }) => theme.typography.fontWeight.semibold};
  color: ${({ theme }) => theme.colors.text.primary};
  margin-bottom: ${({ theme }) => theme.spacing.lg};
`;

export const Dashboard: React.FC = () => {
  const { t, i18n } = useTranslation();
  const dashboardService = useService<DashboardService>(SERVICE_TOKENS.DASHBOARD_SERVICE);
  const analyticsService = useService<AnalyticsService>(SERVICE_TOKENS.ANALYTICS_SERVICE);

  const { data: stats, isLoading } = useQuery<DashboardStats>(
    'dashboardStats',
    async () => {
      const [basicStats, analytics] = await Promise.all([
        dashboardService.getStats(),
        analyticsService.getAnalytics(),
      ]);
      return { ...basicStats, ...analytics };
    },
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  const emotionColors = {
    happy: '#fbbf24',
    sad: '#60a5fa',
    angry: '#f87171',
    neutral: '#9ca3af',
    excited: '#f59e0b',
    calm: '#34d399',
  };

  const statsConfig = [
    {
      icon: FiActivity,
      label: t('dashboard.stats.dailyConversations'),
      value: stats?.dailyConversations || 0,
      color: '#3b82f6',
      change: '+2',
      positive: true,
    },
    {
      icon: FiSmile,
      label: t('dashboard.stats.emotionalState'),
      value: t(`dashboard.emotions.${stats?.emotionalState || 'neutral'}`),
      color: emotionColors[stats?.emotionalState as keyof typeof emotionColors] || '#9ca3af',
    },
    {
      icon: FiClock,
      label: t('dashboard.stats.activityTime'),
      value: `${stats?.activityTime || 0} ${t('common.minutes')}`,
      color: '#8b5cf6',
    },
    {
      icon: FiTrendingUp,
      label: t('dashboard.stats.educationalProgress'),
      value: `${stats?.educationalProgress || 0}%`,
      color: '#10b981',
      change: '+5%',
      positive: true,
    },
  ];

  if (isLoading) {
    return <div>{t('common.loading')}</div>;
  }

  return (
    <DashboardContainer>
      <Header>
        <Title>{t('dashboard.title')}</Title>
        <Subtitle>{t('dashboard.subtitle')}</Subtitle>
      </Header>

      <StatsGrid>
        {statsConfig.map((stat, index) => (
          <StatCard
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <StatIcon color={stat.color}>
              <stat.icon />
            </StatIcon>
            <StatContent>
              <StatLabel>{stat.label}</StatLabel>
              <StatValue>{stat.value}</StatValue>
              {stat.change && (
                <StatChange positive={stat.positive}>{stat.change}</StatChange>
              )}
            </StatContent>
          </StatCard>
        ))}
      </StatsGrid>

      <ChartsGrid>
        <ChartCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <ChartTitle>{t('dashboard.charts.conversationTrend')}</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={stats?.conversationTrend || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={(date) =>
                  format(new Date(date), 'MMM d', {
                    locale: i18n.language === 'ar' ? ar : undefined,
                  })
                }
              />
              <YAxis />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="count"
                stroke="#3b82f6"
                fill="#3b82f680"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <ChartTitle>{t('dashboard.charts.emotionDistribution')}</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={stats?.emotionDistribution || []}
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {(stats?.emotionDistribution || []).map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={emotionColors[entry.emotion as keyof typeof emotionColors]}
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          style={{ gridColumn: 'span 2' }}
        >
          <ChartTitle>{t('dashboard.charts.topicAnalysis')}</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats?.topicAnalysis || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="topic" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="frequency" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </ChartsGrid>
    </DashboardContainer>
  );
}; 