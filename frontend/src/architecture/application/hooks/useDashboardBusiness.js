/**
 * Dashboard Business Logic Hook
 * 
 * Contains all business logic for dashboard functionality
 * Separated from UI concerns following Clean Architecture
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import { 
  ChildManagementUseCases,
  ConversationManagementUseCases 
} from '../useCases';
import { 
  ChildRepository,
  ConversationRepository 
} from '../../infrastructure/repositories';
import { ApiClient } from '../../infrastructure/api/ApiClient';
import { LocalStorageService } from '../../infrastructure/storage/LocalStorageService';
import { useDashboardNotifications } from './useDashboardNotifications';

// Initialize infrastructure dependencies
const apiClient = new ApiClient({});
const localStorageService = new LocalStorageService({});
const eventBus = { emit: async (event, data) => console.log('Event:', event, data) };

const childRepository = new ChildRepository({ apiClient, localStorageService });
const conversationRepository = new ConversationRepository({ apiClient, localStorageService });

// Initialize use cases
const childManagement = new ChildManagementUseCases({ childRepository, eventBus });
const conversationManagement = new ConversationManagementUseCases({ 
  conversationRepository, 
  childRepository, 
  eventBus,
  aiService: { generateResponse: async () => ({ text: 'مرحبا', emotionalState: 'happy', topics: [] }) }
});

export const useDashboardBusiness = (selectedChildId, timeRange = '7d') => {
  const queryClient = useQueryClient();
  const [currentChildId, setCurrentChildId] = useState(selectedChildId);
  
  // WebSocket notifications
  const {
    isConnected,
    notifications,
    unreadCount,
    markAsRead,
    clearNotifications
  } = useDashboardNotifications(currentChildId);

  // Fetch children list
  const {
    data: children,
    isLoading: childrenLoading,
    error: childrenError,
    refetch: refetchChildren
  } = useQuery(
    'children',
    async () => {
      const parentId = 'current_parent'; // This would come from auth context
      return await childManagement.getChildrenByParent(parentId);
    },
    {
      staleTime: 10 * 60 * 1000, // 10 minutes
      cacheTime: 30 * 60 * 1000, // 30 minutes
      refetchOnWindowFocus: false,
      retry: 2
    }
  );

  // Fetch dashboard data for selected child
  const {
    data: dashboardData,
    isLoading: dashboardLoading,
    error: dashboardError,
    refetch: refetchDashboard
  } = useQuery(
    ['dashboard', currentChildId],
    async () => {
      if (!currentChildId) return null;
      
      // Get child data
      const child = await childManagement.getChildById(currentChildId);
      
      // Get recent conversations
      const conversations = await conversationManagement.getConversationsByChild(
        currentChildId,
        { limit: 10 }
      );
      
      // Get today's conversations for activity tracking
      const todayConversations = await conversationManagement.getTodayConversations(currentChildId);
      
      // Calculate stats
      const stats = calculateDashboardStats(child, conversations, todayConversations);
      
      return {
        child,
        stats,
        recentConversations: conversations,
        todayConversations,
        dailyActivity: generateDailyActivityData(conversations)
      };
    },
    {
      enabled: !!currentChildId,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 15 * 60 * 1000, // 15 minutes
      refetchOnWindowFocus: false,
      retry: 2
    }
  );

  // Fetch analytics data
  const {
    data: analyticsData,
    isLoading: analyticsLoading,
    error: analyticsError,
    refetch: refetchAnalytics
  } = useQuery(
    ['analytics', currentChildId, timeRange],
    async () => {
      if (!currentChildId) return null;
      
      const conversations = await conversationManagement.getConversationsByChild(
        currentChildId,
        { limit: 50 }
      );
      
      return {
        emotions: analyzeEmotions(conversations, timeRange),
        topics: analyzeTopics(conversations, timeRange),
        activityTrends: analyzeActivityTrends(conversations, timeRange)
      };
    },
    {
      enabled: !!currentChildId,
      staleTime: 5 * 60 * 1000,
      cacheTime: 15 * 60 * 1000,
      refetchOnWindowFocus: false,
      retry: 2
    }
  );

  // Business logic functions
  const selectChild = useCallback(async (childId) => {
    setCurrentChildId(childId);
    // Invalidate related queries to force refresh
    queryClient.invalidateQueries(['dashboard', childId]);
    queryClient.invalidateQueries(['analytics', childId]);
  }, [queryClient]);

  const refreshDashboard = useCallback(async () => {
    await Promise.all([
      refetchChildren(),
      refetchDashboard(),
      refetchAnalytics()
    ]);
  }, [refetchChildren, refetchDashboard, refetchAnalytics]);

  const exportPDF = useCallback(async (options) => {
    if (!currentChildId || !dashboardData) {
      throw new Error('لا توجد بيانات لتصديرها');
    }

    // Business logic for PDF export
    const exportData = {
      child: dashboardData.child,
      stats: dashboardData.stats,
      conversations: dashboardData.recentConversations,
      analytics: analyticsData,
      timeRange,
      generatedAt: new Date().toISOString()
    };

    // This would use a PDF service in infrastructure layer
    return await generatePDFReport(exportData, options);
  }, [currentChildId, dashboardData, analyticsData, timeRange]);

  const createChild = useCallback(async (childData) => {
    const newChild = await childManagement.createChild(childData);
    queryClient.invalidateQueries('children');
    return newChild;
  }, [queryClient]);

  const updateChild = useCallback(async (childId, updates) => {
    const updatedChild = await childManagement.updateChildProfile(childId, updates);
    queryClient.invalidateQueries(['dashboard', childId]);
    queryClient.invalidateQueries('children');
    return updatedChild;
  }, [queryClient]);

  // Computed values
  const isLoading = useMemo(() => {
    return childrenLoading || dashboardLoading || analyticsLoading;
  }, [childrenLoading, dashboardLoading, analyticsLoading]);

  const error = useMemo(() => {
    return childrenError || dashboardError || analyticsError;
  }, [childrenError, dashboardError, analyticsError]);

  const hasData = useMemo(() => {
    return children && children.length > 0 && dashboardData;
  }, [children, dashboardData]);

  // Auto-refresh dashboard data periodically
  useEffect(() => {
    if (!currentChildId) return;

    const interval = setInterval(() => {
      refetchDashboard();
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [currentChildId, refetchDashboard]);

  return {
    // Data
    children,
    dashboardData,
    analyticsData,
    notifications,
    
    // Loading states
    isLoading,
    childrenLoading,
    dashboardLoading,
    analyticsLoading,
    
    // Error states
    error,
    hasData,
    
    // Actions
    selectChild,
    refreshDashboard,
    exportPDF,
    createChild,
    updateChild,
    
    // Connection status
    isConnected,
    unreadCount,
    markAsRead,
    clearNotifications
  };
};

// Helper functions for business logic
function calculateDashboardStats(child, conversations, todayConversations) {
  if (!child || !conversations) return {};

  const totalConversations = conversations.length;
  const todayActiveMinutes = todayConversations.reduce((total, conv) => {
    return total + (conv.getDurationMinutes ? conv.getDurationMinutes() : 0);
  }, 0);

  // Calculate emotional state
  const recentEmotions = conversations
    .slice(0, 10)
    .map(conv => conv.emotionalState)
    .filter(emotion => emotion && emotion !== 'neutral');

  const emotionScore = calculateEmotionScore(recentEmotions);

  // Calculate learning progress
  const educationalConversations = conversations.filter(conv => 
    conv.hasEducationalContent ? conv.hasEducationalContent() : false
  );
  const learningProgress = Math.round((educationalConversations.length / totalConversations) * 100);

  return {
    totalConversations,
    activeMinutes: todayActiveMinutes,
    emotionScore,
    learningProgress: `${learningProgress}%`
  };
}

function calculateEmotionScore(emotions) {
  if (!emotions || emotions.length === 0) return 'متوسط';

  const emotionScores = {
    happy: 5,
    excited: 4,
    content: 3,
    neutral: 2,
    sad: 1,
    angry: 0
  };

  const avgScore = emotions.reduce((sum, emotion) => {
    return sum + (emotionScores[emotion] || 2);
  }, 0) / emotions.length;

  if (avgScore >= 4) return 'ممتاز';
  if (avgScore >= 3) return 'جيد';
  if (avgScore >= 2) return 'متوسط';
  return 'يحتاج تحسين';
}

function generateDailyActivityData(conversations) {
  // Group conversations by date and calculate daily activity
  const dailyData = {};
  
  conversations.forEach(conv => {
    const date = new Date(conv.startTime).toISOString().split('T')[0];
    if (!dailyData[date]) {
      dailyData[date] = {
        date,
        activeMinutes: 0,
        conversationTime: 0,
        conversationCount: 0
      };
    }
    
    dailyData[date].activeMinutes += conv.getDurationMinutes ? conv.getDurationMinutes() : 0;
    dailyData[date].conversationTime += conv.getDurationMinutes ? conv.getDurationMinutes() : 0;
    dailyData[date].conversationCount += 1;
  });

  return Object.values(dailyData).sort((a, b) => new Date(a.date) - new Date(b.date));
}

function analyzeEmotions(conversations, timeRange) {
  // Analyze emotions over time range
  const emotions = conversations.map(conv => ({
    date: new Date(conv.startTime).toISOString().split('T')[0],
    emotion: conv.emotionalState,
    score: getEmotionScore(conv.emotionalState)
  }));

  // Group by date and calculate average scores
  const dailyEmotions = {};
  emotions.forEach(({ date, emotion, score }) => {
    if (!dailyEmotions[date]) {
      dailyEmotions[date] = { date, emotions: [], totalScore: 0, count: 0 };
    }
    dailyEmotions[date].emotions.push(emotion);
    dailyEmotions[date].totalScore += score;
    dailyEmotions[date].count += 1;
  });

  return Object.values(dailyEmotions).map(day => ({
    ...day,
    averageScore: day.totalScore / day.count,
    dominantEmotion: findDominantEmotion(day.emotions)
  }));
}

function analyzeTopics(conversations, timeRange) {
  const topicCounts = {};
  
  conversations.forEach(conv => {
    if (conv.topics && Array.isArray(conv.topics)) {
      conv.topics.forEach(topic => {
        topicCounts[topic] = (topicCounts[topic] || 0) + 1;
      });
    }
  });

  return Object.entries(topicCounts)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 10)
    .map(([topic, count]) => ({ topic, count }));
}

function analyzeActivityTrends(conversations, timeRange) {
  // Similar to generateDailyActivityData but with more detailed analysis
  return generateDailyActivityData(conversations);
}

function getEmotionScore(emotion) {
  const scores = {
    happy: 5,
    excited: 4,
    content: 3,
    neutral: 2,
    sad: 1,
    angry: 0
  };
  return scores[emotion] || 2;
}

function findDominantEmotion(emotions) {
  const counts = {};
  emotions.forEach(emotion => {
    counts[emotion] = (counts[emotion] || 0) + 1;
  });
  
  return Object.entries(counts)
    .sort(([,a], [,b]) => b - a)[0]?.[0] || 'neutral';
}

async function generatePDFReport(data, options) {
  // This would be implemented in infrastructure layer
  console.log('Generating PDF report with data:', data);
  return { success: true, filename: `report_${Date.now()}.pdf` };
} 