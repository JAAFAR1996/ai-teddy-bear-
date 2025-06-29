import React, { memo, useMemo } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiMessageCircle, FiHeart, FiStar, FiTrendingUp, 
  FiBook, FiMusic, FiSmile, FiZap, FiAward,
  FiClock, FiCalendar, FiUser
} from 'react-icons/fi';
import { formatDistanceToNow } from 'date-fns';
import { ar } from 'date-fns/locale';

// Styled components
const TimelineContainer = styled.div`
  width: 100%;
  max-height: 400px;
  overflow-y: auto;
  padding-right: ${props => props.theme.spacing.xs};
  
  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-track {
    background: ${props => props.theme.colors.surfaceLight};
    border-radius: 2px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.border};
    border-radius: 2px;
    
    &:hover {
      background: ${props => props.theme.colors.textSecondary};
    }
  }
`;

const TimelineItem = styled(motion.div)`
  display: flex;
  align-items: flex-start;
  gap: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md} 0;
  border-bottom: 1px solid ${props => props.theme.colors.borderLight};
  position: relative;
  
  &:last-child {
    border-bottom: none;
  }
  
  &:before {
    content: '';
    position: absolute;
    left: 20px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: ${props => props.theme.colors.borderLight};
  }
  
  &:last-child:before {
    bottom: 50%;
  }
`;

const IconContainer = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: white;
  background: ${props => props.color || props.theme.colors.primary};
  box-shadow: 0 2px 8px ${props => props.color || props.theme.colors.primary}33;
  position: relative;
  z-index: 1;
  flex-shrink: 0;
`;

const ContentContainer = styled.div`
  flex: 1;
  min-width: 0;
`;

const ActivityHeader = styled.div`
  display: flex;
  justify-content: between;
  align-items: flex-start;
  gap: ${props => props.theme.spacing.sm};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const ActivityTitle = styled.h4`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.base};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  color: ${props => props.theme.colors.text};
  line-height: 1.4;
  flex: 1;
`;

const ActivityTime = styled.span`
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.textSecondary};
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const ActivityDescription = styled.p`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.textSecondary};
  line-height: 1.5;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const ActivityMeta = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.sm};
  margin-top: ${props => props.theme.spacing.sm};
`;

const MetaTag = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: ${props => props.theme.colors.surfaceLight};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.full};
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.textSecondary};
`;

const EmotionIndicator = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: ${props => props.color}22;
  border: 1px solid ${props => props.color};
  border-radius: ${props => props.theme.borderRadius.full};
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.color};
  font-weight: 500;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.xl};
  text-align: center;
  color: ${props => props.theme.colors.textSecondary};
  
  .icon {
    font-size: 2.5rem;
    margin-bottom: ${props => props.theme.spacing.md};
    opacity: 0.5;
  }
  
  .message {
    font-size: ${props => props.theme.typography.fontSize.base};
    margin-bottom: ${props => props.theme.spacing.sm};
  }
  
  .description {
    font-size: ${props => props.theme.typography.fontSize.sm};
    max-width: 250px;
    opacity: 0.8;
  }
`;

// Activity type configurations
const ACTIVITY_TYPES = {
  conversation: {
    icon: FiMessageCircle,
    color: '#3b82f6',
    label: 'محادثة'
  },
  emotion: {
    icon: FiHeart,
    color: '#ef4444',
    label: 'مشاعر'
  },
  achievement: {
    icon: FiAward,
    color: '#f59e0b',
    label: 'إنجاز'
  },
  learning: {
    icon: FiBook,
    color: '#10b981',
    label: 'تعلم'
  },
  play: {
    icon: FiMusic,
    color: '#8b5cf6',
    label: 'لعب'
  },
  milestone: {
    icon: FiStar,
    color: '#f97316',
    label: 'إنجاز مهم'
  },
  progress: {
    icon: FiTrendingUp,
    color: '#06b6d4',
    label: 'تقدم'
  },
  interaction: {
    icon: FiSmile,
    color: '#84cc16',
    label: 'تفاعل'
  }
};

const EMOTION_COLORS = {
  joy: '#fbbf24',
  happiness: '#10b981',
  excitement: '#f59e0b',
  curiosity: '#3b82f6',
  calm: '#06b6d4',
  sadness: '#6366f1',
  fear: '#8b5cf6',
  anger: '#ef4444',
  tiredness: '#6b7280',
  neutral: '#9ca3af'
};

// Utility functions
const formatRelativeTime = (date) => {
  try {
    return formatDistanceToNow(new Date(date), { 
      addSuffix: true, 
      locale: ar 
    });
  } catch (error) {
    return 'منذ قليل';
  }
};

const getActivityIcon = (type, subType) => {
  const config = ACTIVITY_TYPES[type] || ACTIVITY_TYPES.interaction;
  return config.icon;
};

const getActivityColor = (type, emotion) => {
  if (type === 'emotion' && emotion && EMOTION_COLORS[emotion]) {
    return EMOTION_COLORS[emotion];
  }
  const config = ACTIVITY_TYPES[type] || ACTIVITY_TYPES.interaction;
  return config.color;
};

// Main ActivityTimeline component
const ActivityTimeline = memo(({
  activities = [],
  type = 'mixed', // 'conversations', 'achievements', 'mixed'
  maxItems = 10,
  showEmotions = true,
  showMeta = true,
  emptyMessage,
  className,
  ...props
}) => {
  // Process and validate activities
  const processedActivities = useMemo(() => {
    if (!activities || !Array.isArray(activities)) {
      return [];
    }

    // Filter by type if specified
    let filtered = activities;
    if (type === 'conversations') {
      filtered = activities.filter(activity => 
        activity.type === 'conversation' || activity.type === 'interaction'
      );
    } else if (type === 'achievements') {
      filtered = activities.filter(activity => 
        activity.type === 'achievement' || activity.type === 'milestone' || activity.type === 'progress'
      );
    }

    // Sort by timestamp (newest first)
    const sorted = filtered.sort((a, b) => {
      const dateA = new Date(a.timestamp || a.createdAt || a.date);
      const dateB = new Date(b.timestamp || b.createdAt || b.date);
      return dateB - dateA;
    });

    // Limit items
    return sorted.slice(0, maxItems);
  }, [activities, type, maxItems]);

  // Render individual activity item
  const renderActivity = (activity, index) => {
    const IconComponent = getActivityIcon(activity.type, activity.subType);
    const color = getActivityColor(activity.type, activity.emotion);
    const timestamp = activity.timestamp || activity.createdAt || activity.date;

    return (
      <TimelineItem
        key={activity.id || index}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ 
          duration: 0.3, 
          delay: index * 0.1,
          type: "spring",
          stiffness: 100 
        }}
      >
        <IconContainer color={color}>
          <IconComponent />
        </IconContainer>
        
        <ContentContainer>
          <ActivityHeader>
            <ActivityTitle>{activity.title || activity.message || 'نشاط جديد'}</ActivityTitle>
            <ActivityTime>
              <FiClock size={12} />
              {formatRelativeTime(timestamp)}
            </ActivityTime>
          </ActivityHeader>
          
          {activity.description && (
            <ActivityDescription>
              {activity.description}
            </ActivityDescription>
          )}
          
          {(activity.content || activity.text) && (
            <ActivityDescription>
              {activity.content || activity.text}
            </ActivityDescription>
          )}
          
          {showMeta && (
            <ActivityMeta>
              {/* Activity type */}
              <MetaTag>
                {ACTIVITY_TYPES[activity.type]?.label || activity.type}
              </MetaTag>
              
              {/* Emotion indicator */}
              {showEmotions && activity.emotion && (
                <EmotionIndicator color={EMOTION_COLORS[activity.emotion]}>
                  {activity.emotion === 'joy' && '😊'}
                  {activity.emotion === 'happiness' && '😄'}
                  {activity.emotion === 'excitement' && '🤩'}
                  {activity.emotion === 'curiosity' && '🤔'}
                  {activity.emotion === 'calm' && '😌'}
                  {activity.emotion === 'sadness' && '😢'}
                  {activity.emotion === 'fear' && '😰'}
                  {activity.emotion === 'anger' && '😠'}
                  {activity.emotion === 'tiredness' && '😴'}
                  {activity.emotion === 'neutral' && '😐'}
                  {activity.emotion}
                </EmotionIndicator>
              )}
              
              {/* Duration for conversations */}
              {activity.duration && (
                <MetaTag>
                  ⏱️ {activity.duration}
                </MetaTag>
              )}
              
              {/* Confidence score */}
              {activity.confidence && (
                <MetaTag>
                  📊 {Math.round(activity.confidence * 100)}%
                </MetaTag>
              )}
              
              {/* Achievement points */}
              {activity.points && (
                <MetaTag>
                  ⭐ +{activity.points} نقطة
                </MetaTag>
              )}
              
              {/* Category */}
              {activity.category && (
                <MetaTag>
                  📁 {activity.category}
                </MetaTag>
              )}
            </ActivityMeta>
          )}
        </ContentContainer>
      </TimelineItem>
    );
  };

  // Empty state
  if (processedActivities.length === 0) {
    const defaultMessages = {
      conversations: {
        icon: '💬',
        message: 'لا توجد محادثات حديثة',
        description: 'ستظهر هنا آخر المحادثات مع دبدوب'
      },
      achievements: {
        icon: '🏆',
        message: 'لا توجد إنجازات حديثة',
        description: 'ستظهر هنا إنجازات الطفل ومعالمه المهمة'
      },
      mixed: {
        icon: '📝',
        message: 'لا توجد أنشطة حديثة',
        description: 'ستظهر هنا جميع الأنشطة والتفاعلات'
      }
    };

    const emptyConfig = defaultMessages[type] || defaultMessages.mixed;

    return (
      <EmptyState className={className} {...props}>
        <div className="icon">{emptyConfig.icon}</div>
        <div className="message">
          {emptyMessage || emptyConfig.message}
        </div>
        <div className="description">
          {emptyConfig.description}
        </div>
      </EmptyState>
    );
  }

  return (
    <TimelineContainer className={className} {...props}>
      <AnimatePresence>
        {processedActivities.map((activity, index) => 
          renderActivity(activity, index)
        )}
      </AnimatePresence>
    </TimelineContainer>
  );
});

ActivityTimeline.displayName = 'ActivityTimeline';

// Preset components for specific use cases
export const ConversationTimeline = memo((props) => (
  <ActivityTimeline
    type="conversations"
    showEmotions={true}
    showMeta={true}
    {...props}
  />
));

export const AchievementTimeline = memo((props) => (
  <ActivityTimeline
    type="achievements"
    showEmotions={false}
    showMeta={true}
    {...props}
  />
));

export default ActivityTimeline; 