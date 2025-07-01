import { useState, useEffect, useCallback, useRef } from 'react';
import { websocketService, WebSocketState, WebSocketMessage } from '../services/websocket.service';

export interface UseWebSocketOptions {
  autoConnect?: boolean;
  reconnectOnError?: boolean;
  onOpen?: () => void;
  onClose?: (event: CloseEvent) => void;
  onError?: (error: Error) => void;
  onMessage?: (message: WebSocketMessage) => void;
  onReconnecting?: (attempt: number) => void;
}

export interface UseWebSocketReturn {
  isConnected: boolean;
  state: WebSocketState;
  lastMessage: WebSocketMessage | null;
  sendMessage: (message: Partial<WebSocketMessage>) => void;
  connect: () => void;
  disconnect: () => void;
  reconnectAttempts: number;
}

/**
 * Custom hook for WebSocket connections
 * Provides a declarative API for WebSocket communication
 */
export const useWebSocket = (url?: string, options: UseWebSocketOptions = {}): UseWebSocketReturn => {
  const [state, setState] = useState<WebSocketState>(WebSocketState.CLOSED);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const optionsRef = useRef(options);

  // Update options ref
  useEffect(() => {
    optionsRef.current = options;
  }, [options]);

  // Set up event listeners
  useEffect(() => {
    const handleOpen = () => {
      setState(WebSocketState.OPEN);
      setReconnectAttempts(0);
      optionsRef.current.onOpen?.();
    };

    const handleClose = (event: CloseEvent) => {
      setState(WebSocketState.CLOSED);
      optionsRef.current.onClose?.(event);
    };

    const handleError = (error: Error) => {
      optionsRef.current.onError?.(error);
    };

    const handleMessage = (message: WebSocketMessage) => {
      setLastMessage(message);
      optionsRef.current.onMessage?.(message);
    };

    const handleReconnecting = (attempt: number) => {
      setState(WebSocketState.RECONNECTING);
      setReconnectAttempts(attempt);
      optionsRef.current.onReconnecting?.(attempt);
    };

    const handleConnecting = () => {
      setState(WebSocketState.CONNECTING);
    };

    // Subscribe to events
    websocketService.on('open', handleOpen);
    websocketService.on('close', handleClose);
    websocketService.on('error', handleError);
    websocketService.on('message', handleMessage);
    websocketService.on('reconnecting', handleReconnecting);
    websocketService.on('connecting', handleConnecting);

    // Auto-connect if requested
    if (options.autoConnect && websocketService.getState() === WebSocketState.CLOSED) {
      websocketService.connect();
    }

    // Cleanup
    return () => {
      websocketService.off('open', handleOpen);
      websocketService.off('close', handleClose);
      websocketService.off('error', handleError);
      websocketService.off('message', handleMessage);
      websocketService.off('reconnecting', handleReconnecting);
      websocketService.off('connecting', handleConnecting);
    };
  }, [options.autoConnect]);

  // Methods
  const connect = useCallback(() => {
    websocketService.connect();
  }, []);

  const disconnect = useCallback(() => {
    websocketService.disconnect();
  }, []);

  const sendMessage = useCallback((message: Partial<WebSocketMessage>) => {
    websocketService.send(message);
  }, []);

  return {
    isConnected: state === WebSocketState.OPEN,
    state,
    lastMessage,
    sendMessage,
    connect,
    disconnect,
    reconnectAttempts
  };
};

// Message type specific hooks
export const useNotificationWebSocket = (deviceId: string) => {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const { isConnected, sendMessage } = useWebSocket(undefined, {
    autoConnect: true,
    onMessage: (message) => {
      if (message.type.includes('alert') || message.type.includes('notification')) {
        setNotifications(prev => [...prev, message]);
        setUnreadCount(prev => prev + 1);
      }
    }
  });

  const markAsRead = useCallback((notificationId: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
    setUnreadCount(0);
  }, []);

  return {
    isConnected,
    notifications,
    unreadCount,
    markAsRead,
    clearNotifications,
    sendMessage
  };
};

// Export specific message types
export { WebSocketState } from '../services/websocket.service';
export type { WebSocketMessage } from '../services/websocket.service'; 