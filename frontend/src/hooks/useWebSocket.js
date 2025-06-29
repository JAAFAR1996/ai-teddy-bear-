import { useState, useEffect, useRef, useCallback } from 'react';
import { toast } from 'react-hot-toast';

/**
 * 🔔 WebSocket Hook for Real-time Notifications
 * Advanced WebSocket management for AI Teddy Bear Dashboard
 */

// WebSocket connection states
export const WS_STATES = {
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  DISCONNECTED: 'disconnected',
  ERROR: 'error',
  RECONNECTING: 'reconnecting'
};

// Default configuration
const DEFAULT_CONFIG = {
  url: null, // Will be constructed based on environment
  protocols: [],
  reconnectInterval: 3000,
  maxReconnectAttempts: 5,
  heartbeatInterval: 30000,
  timeout: 10000,
  binaryType: 'blob',
  autoConnect: true,
  debug: process.env.NODE_ENV === 'development'
};

// Message types for the teddy bear system
export const MESSAGE_TYPES = {
  // Alert types
  EMOTION_ALERT: 'emotion_alert',
  HEALTH_ALERT: 'health_alert',
  ACTIVITY_ALERT: 'activity_alert',
  SYSTEM_ALERT: 'system_alert',
  
  // Data updates
  EMOTION_UPDATE: 'emotion_update',
  CONVERSATION_UPDATE: 'conversation_update',
  ACHIEVEMENT_UPDATE: 'achievement_update',
  STATS_UPDATE: 'stats_update',
  
  // System messages
  CONNECTION_ACK: 'connection_ack',
  HEARTBEAT: 'heartbeat',
  ERROR: 'error',
  
  // Device messages
  DEVICE_ONLINE: 'device_online',
  DEVICE_OFFLINE: 'device_offline',
  DEVICE_STATUS: 'device_status'
};

/**
 * Custom hook for WebSocket connections with real-time notifications
 * @param {String} deviceId - Child/Device identifier
 * @param {Object} config - WebSocket configuration
 * @returns {Object} WebSocket state and methods
 */
export const useWebSocket = (deviceId, config = {}) => {
  // Merge configuration with defaults
  const wsConfig = { ...DEFAULT_CONFIG, ...config };
  
  // WebSocket URL construction
  const wsUrl = wsConfig.url || (() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const base = process.env.REACT_APP_WS_URL || `${protocol}//${host}`;
    return deviceId ? `${base}/ws/${deviceId}` : `${base}/ws`;
  })();

  // State management
  const [connectionState, setConnectionState] = useState(WS_STATES.DISCONNECTED);
  const [lastMessage, setLastMessage] = useState(null);
  const [messageHistory, setMessageHistory] = useState([]);
  const [error, setError] = useState(null);

  // Refs for persistent values
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const heartbeatIntervalRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const messageQueueRef = useRef([]);

  // Debug logging
  const log = useCallback((message, data = null) => {
    if (wsConfig.debug) {
      console.log(`[WebSocket] ${message}`, data || '');
    }
  }, [wsConfig.debug]);

  // Clear timers
  const clearTimers = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
  }, []);

  // Send message through WebSocket
  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
        wsRef.current.send(messageStr);
        log('Message sent', message);
        return true;
      } catch (err) {
        log('Send error', err);
        setError(err);
        return false;
      }
    } else {
      // Queue message for later if not connected
      messageQueueRef.current.push(message);
      log('Message queued (not connected)', message);
      return false;
    }
  }, [log]);

  // Send queued messages
  const sendQueuedMessages = useCallback(() => {
    if (messageQueueRef.current.length > 0) {
      log(`Sending ${messageQueueRef.current.length} queued messages`);
      messageQueueRef.current.forEach(message => {
        sendMessage(message);
      });
      messageQueueRef.current = [];
    }
  }, [sendMessage, log]);

  // Start heartbeat
  const startHeartbeat = useCallback(() => {
    if (wsConfig.heartbeatInterval > 0) {
      heartbeatIntervalRef.current = setInterval(() => {
        sendMessage({
          type: MESSAGE_TYPES.HEARTBEAT,
          timestamp: Date.now()
        });
      }, wsConfig.heartbeatInterval);
      log('Heartbeat started');
    }
  }, [sendMessage, wsConfig.heartbeatInterval, log]);

  // Handle incoming messages
  const handleMessage = useCallback((event) => {
    try {
      const data = JSON.parse(event.data);
      log('Message received', data);
      
      setLastMessage(data);
      setMessageHistory(prev => [...prev.slice(-49), data]); // Keep last 50 messages
      
      // Handle different message types
      switch (data.type) {
        case MESSAGE_TYPES.EMOTION_ALERT:
          handleEmotionAlert(data);
          break;
          
        case MESSAGE_TYPES.HEALTH_ALERT:
          handleHealthAlert(data);
          break;
          
        case MESSAGE_TYPES.ACTIVITY_ALERT:
          handleActivityAlert(data);
          break;
          
        case MESSAGE_TYPES.SYSTEM_ALERT:
          handleSystemAlert(data);
          break;
          
        case MESSAGE_TYPES.DEVICE_ONLINE:
          handleDeviceOnline(data);
          break;
          
        case MESSAGE_TYPES.DEVICE_OFFLINE:
          handleDeviceOffline(data);
          break;
          
        case MESSAGE_TYPES.CONNECTION_ACK:
          log('Connection acknowledged', data);
          break;
          
        case MESSAGE_TYPES.HEARTBEAT:
          // Silent heartbeat response
          break;
          
        default:
          log('Unknown message type', data.type);
      }
    } catch (err) {
      log('Message parse error', err);
      setError(err);
    }
  }, [log]);

  // Alert handlers
  const handleEmotionAlert = useCallback((data) => {
    const { emotion, severity, child, message } = data;
    
    const emotionEmojis = {
      sadness: '😢',
      anger: '😠',
      fear: '😰',
      anxiety: '😰',
      distress: '😞'
    };
    
    const emoji = emotionEmojis[emotion] || '⚠️';
    const alertMessage = message || `${child?.name || 'الطفل'} يظهر مشاعر ${emotion}`;
    
    if (severity === 'high') {
      toast.error(`${emoji} تنبيه مهم: ${alertMessage}`, {
        duration: 8000,
        position: 'top-center',
        style: {
          background: '#FEE2E2',
          border: '1px solid #F87171',
          color: '#991B1B'
        }
      });
    } else {
      toast(`${emoji} ${alertMessage}`, {
        duration: 5000,
        style: {
          background: '#FEF3C7',
          border: '1px solid #F59E0B',
          color: '#92400E'
        }
      });
    }
  }, []);

  const handleHealthAlert = useCallback((data) => {
    const { type, severity, message } = data;
    
    toast.error(`🏥 تنبيه صحي: ${message}`, {
      duration: 10000,
      position: 'top-center',
      style: {
        background: '#FEE2E2',
        border: '1px solid #EF4444',
        color: '#991B1B'
      }
    });
  }, []);

  const handleActivityAlert = useCallback((data) => {
    const { activity, message, child } = data;
    
    toast(`🎯 ${message || `نشاط جديد: ${activity}`}`, {
      duration: 4000,
      style: {
        background: '#DBEAFE',
        border: '1px solid #3B82F6',
        color: '#1E40AF'
      }
    });
  }, []);

  const handleSystemAlert = useCallback((data) => {
    const { message, severity } = data;
    
    if (severity === 'error') {
      toast.error(`⚠️ خطأ في النظام: ${message}`, {
        duration: 6000,
        position: 'top-center'
      });
    } else {
      toast(`ℹ️ ${message}`, {
        duration: 4000
      });
    }
  }, []);

  const handleDeviceOnline = useCallback((data) => {
    const { deviceId: onlineDeviceId, child } = data;
    
    toast.success(`🧸 ${child?.name || 'دبدوب'} متصل الآن!`, {
      duration: 3000,
      position: 'bottom-right',
      style: {
        background: '#D1FAE5',
        border: '1px solid #10B981',
        color: '#047857'
      }
    });
  }, []);

  const handleDeviceOffline = useCallback((data) => {
    const { deviceId: offlineDeviceId, child } = data;
    
    toast(`🔌 ${child?.name || 'دبدوب'} غير متصل`, {
      duration: 4000,
      position: 'bottom-right',
      style: {
        background: '#FEF3C7',
        border: '1px solid #F59E0B',
        color: '#92400E'
      }
    });
  }, []);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      log('Already connected');
      return;
    }

    log('Connecting to', wsUrl);
    setConnectionState(WS_STATES.CONNECTING);
    setError(null);

    try {
      wsRef.current = new WebSocket(wsUrl, wsConfig.protocols);
      wsRef.current.binaryType = wsConfig.binaryType;

      // Connection timeout
      const timeoutId = setTimeout(() => {
        if (wsRef.current?.readyState === WebSocket.CONNECTING) {
          wsRef.current.close();
          setError(new Error('Connection timeout'));
          setConnectionState(WS_STATES.ERROR);
        }
      }, wsConfig.timeout);

      wsRef.current.onopen = () => {
        clearTimeout(timeoutId);
        log('Connected');
        setConnectionState(WS_STATES.CONNECTED);
        setError(null);
        reconnectAttemptsRef.current = 0;
        
        // Send connection acknowledgment
        sendMessage({
          type: MESSAGE_TYPES.CONNECTION_ACK,
          deviceId,
          timestamp: Date.now(),
          userAgent: navigator.userAgent
        });
        
        // Start heartbeat and send queued messages
        startHeartbeat();
        sendQueuedMessages();
      };

      wsRef.current.onmessage = handleMessage;

      wsRef.current.onclose = (event) => {
        clearTimeout(timeoutId);
        clearTimers();
        log('Disconnected', { code: event.code, reason: event.reason });
        setConnectionState(WS_STATES.DISCONNECTED);
        
        // Attempt reconnection if not intentional
        if (event.code !== 1000 && reconnectAttemptsRef.current < wsConfig.maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          setConnectionState(WS_STATES.RECONNECTING);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            log(`Reconnect attempt ${reconnectAttemptsRef.current}`);
            connect();
          }, wsConfig.reconnectInterval);
        }
      };

      wsRef.current.onerror = (event) => {
        clearTimeout(timeoutId);
        log('Error', event);
        setError(new Error('WebSocket connection error'));
        setConnectionState(WS_STATES.ERROR);
      };

    } catch (err) {
      log('Connection failed', err);
      setError(err);
      setConnectionState(WS_STATES.ERROR);
    }
  }, [wsUrl, wsConfig, deviceId, log, sendMessage, startHeartbeat, sendQueuedMessages, clearTimers, handleMessage]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    log('Disconnecting');
    clearTimers();
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnect');
      wsRef.current = null;
    }
    
    setConnectionState(WS_STATES.DISCONNECTED);
    reconnectAttemptsRef.current = 0;
  }, [log, clearTimers]);

  // Subscribe to specific message types
  const subscribe = useCallback((messageType, callback) => {
    // This would be implemented with a message filter system
    // For now, we'll use the messageHistory to filter
    log('Subscribed to', messageType);
    return () => log('Unsubscribed from', messageType);
  }, [log]);

  // Auto-connect effect
  useEffect(() => {
    if (wsConfig.autoConnect && deviceId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [wsConfig.autoConnect, deviceId, connect, disconnect]);

  // Connection status helpers
  const isConnected = connectionState === WS_STATES.CONNECTED;
  const isConnecting = connectionState === WS_STATES.CONNECTING;
  const isReconnecting = connectionState === WS_STATES.RECONNECTING;
  const hasError = connectionState === WS_STATES.ERROR;

  return {
    // Connection state
    connectionState,
    isConnected,
    isConnecting,
    isReconnecting,
    hasError,
    error,
    
    // Message data
    lastMessage,
    messageHistory,
    
    // Connection methods
    connect,
    disconnect,
    sendMessage,
    subscribe,
    
    // Utility methods
    clearHistory: () => setMessageHistory([]),
    clearError: () => setError(null),
    
    // Debug info
    reconnectAttempts: reconnectAttemptsRef.current,
    wsUrl
  };
};

/**
 * Hook specifically for dashboard notifications
 * @param {String} deviceId - Device/Child ID
 * @returns {Object} Notification-specific WebSocket state
 */
export const useDashboardNotifications = (deviceId) => {
  const {
    isConnected,
    lastMessage,
    sendMessage,
    connectionState,
    error
  } = useWebSocket(deviceId, {
    heartbeatInterval: 60000, // Longer heartbeat for dashboard
    maxReconnectAttempts: 10,
    debug: true
  });

  // Filter messages for dashboard-relevant notifications
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if (lastMessage) {
      const relevantTypes = [
        MESSAGE_TYPES.EMOTION_ALERT,
        MESSAGE_TYPES.HEALTH_ALERT,
        MESSAGE_TYPES.ACTIVITY_ALERT,
        MESSAGE_TYPES.ACHIEVEMENT_UPDATE,
        MESSAGE_TYPES.DEVICE_ONLINE,
        MESSAGE_TYPES.DEVICE_OFFLINE
      ];

      if (relevantTypes.includes(lastMessage.type)) {
        setNotifications(prev => [
          { ...lastMessage, id: Date.now(), read: false },
          ...prev.slice(0, 19) // Keep last 20 notifications
        ]);
      }
    }
  }, [lastMessage]);

  const markAsRead = useCallback((notificationId) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === notificationId ? { ...notif, read: true } : notif
      )
    );
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  return {
    isConnected,
    connectionState,
    error,
    notifications,
    unreadCount,
    markAsRead,
    clearNotifications,
    sendMessage
  };
};

export default useWebSocket; 