/**
 * AI Teddy Bear Frontend Types
 * Enterprise-grade TypeScript definitions
 */

// ============== User & Authentication ==============
export interface User {
  id: string;
  email: string;
  role: 'parent' | 'admin';
  children: Child[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Child {
  id: string;
  name: string;
  age: number;
  gender?: 'male' | 'female' | 'other';
  language: string;
  voicePreference: string;
  interests: string[];
  parentId: string;
  deviceId?: string;
  avatar?: string;
  createdAt: Date;
  updatedAt: Date;
}

// ============== Sessions & Conversations ==============
export interface Session {
  id: string;
  childId: string;
  startTime: Date;
  endTime?: Date;
  duration?: number;
  interactionCount: number;
  emotionSummary: EmotionSummary;
  status: 'active' | 'ended' | 'error';
}

export interface Conversation {
  id: string;
  sessionId: string;
  childId: string;
  timestamp: Date;
  transcription: string;
  response: string;
  emotion: EmotionData;
  activityType: ActivityType;
  audioUrl?: string;
  confidence: number;
}

// ============== Emotions & Analytics ==============
export interface EmotionData {
  primary: EmotionType;
  confidence: number;
  secondary?: Record<EmotionType, number>;
  valence: number; // -1 to 1
  arousal: number; // 0 to 1
}

export interface EmotionSummary {
  dominant: EmotionType;
  distribution: Record<EmotionType, number>;
  averageValence: number;
  averageArousal: number;
}

export type EmotionType = 
  | 'happy' 
  | 'sad' 
  | 'angry' 
  | 'scared' 
  | 'surprised' 
  | 'neutral'
  | 'excited';

export type ActivityType = 
  | 'conversation' 
  | 'story' 
  | 'game' 
  | 'learning' 
  | 'comfort' 
  | 'sleep_routine';

// ============== Dashboard & Analytics ==============
export interface DashboardStats {
  todayConversations: number;
  yesterdayConversations: number;
  averageEmotion: EmotionType;
  totalActiveTime: number; // minutes
  learningProgress: number; // percentage
  lastInteraction: Date;
  weeklyTrend: WeeklyTrend[];
}

export interface WeeklyTrend {
  date: Date;
  conversations: number;
  activeTime: number;
  dominantEmotion: EmotionType;
}

// ============== WebSocket Events ==============
export interface WebSocketMessage<T = any> {
  event: WebSocketEvent;
  data: T;
  timestamp: Date;
}

export type WebSocketEvent = 
  | 'session:start'
  | 'session:end'
  | 'conversation:new'
  | 'emotion:update'
  | 'device:status'
  | 'error';

export interface DeviceStatus {
  deviceId: string;
  isOnline: boolean;
  batteryLevel?: number;
  firmwareVersion: string;
  lastSeen: Date;
}

// ============== API Responses ==============
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  metadata?: {
    timestamp: Date;
    requestId: string;
  };
}

export interface ApiError {
  code: string;
  message: string;
  details?: any;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// ============== Settings & Preferences ==============
export interface ParentSettings {
  notifications: NotificationSettings;
  privacy: PrivacySettings;
  contentFilters: ContentFilterSettings;
  timeRestrictions: TimeRestriction[];
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  emotionAlerts: boolean;
  dailySummary: boolean;
  weeklyReport: boolean;
}

export interface PrivacySettings {
  dataRetention: number; // days
  shareAnalytics: boolean;
  recordConversations: boolean;
}

export interface ContentFilterSettings {
  enableProfanityFilter: boolean;
  enableSafeSearch: boolean;
  allowedTopics: string[];
  blockedTopics: string[];
}

export interface TimeRestriction {
  dayOfWeek: number; // 0-6
  startTime: string; // HH:mm
  endTime: string; // HH:mm
  enabled: boolean;
}

// ============== Forms & Validation ==============
export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => boolean;
  message: string;
}

export interface FormField<T = any> {
  value: T;
  error?: string;
  touched: boolean;
  rules: ValidationRule[];
}

// ============== Theme & UI ==============
export interface Theme {
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    error: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
  };
  typography: {
    fontFamily: string;
    fontSize: {
      xs: string;
      sm: string;
      md: string;
      lg: string;
      xl: string;
      xxl: string;
    };
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
    full: string;
  };
  shadows: {
    sm: string;
    md: string;
    lg: string;
  };
} 