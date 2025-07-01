/**
 * useWebSocket Hook
 * React hook for WebSocket connection management
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { WebSocketService, getWebSocketService } from '@services/websocket.service';
import { WebSocketEvent, WebSocketMessage } from '@types';

export interface UseWebSocketReturn {
  isConnected: boolean;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
  connect: () => Promise<void>;
  disconnect: () => void;
  send: <T = any>(event: WebSocketEvent, data: T) => void;
  on: <T = any>(event: WebSocketEvent, handler: (data: T) => void) => () => void;
  lastMessage?: WebSocketMessage;
  error?: Error;
}

export function useWebSocket(autoConnect = true): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<UseWebSocketReturn['connectionState']>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage>();
  const [error, setError] = useState<Error>();
  
  const wsRef = useRef<WebSocketService>();
  const handlersRef = useRef<Map<WebSocketEvent, Set<Function>>>(new Map());

  // Initialize WebSocket service
  useEffect(() => {
    try {
      wsRef.current = getWebSocketService();
    } catch {
      // Service not initialized yet
      wsRef.current = undefined;
    }
  }, []);

  // Connect to WebSocket
  const connect = useCallback(async () => {
    if (!wsRef.current) {
      const error = new Error('WebSocket service not initialized');
      setError(error);
      throw error;
    }

    try {
      setConnectionState('connecting');
      setError(undefined);
      await wsRef.current.connect();
      setIsConnected(true);
      setConnectionState('connected');
    } catch (err: any) {
      const error = err as Error;
      setError(error);
      setConnectionState('error');
      throw error;
    }
  }, []);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.disconnect();
      setIsConnected(false);
      setConnectionState('disconnected');
    }
  }, []);

  // Send message
  const send = useCallback(<T = any>(event: WebSocketEvent, data: T) => {
    if (!wsRef.current) {
      console.warn('WebSocket not initialized');
      return;
    }
    
    wsRef.current.send(event, data);
  }, []);

  // Subscribe to events
  const on = useCallback(<T = any>(
    event: WebSocketEvent, 
    handler: (data: T) => void
  ): (() => void) => {
    if (!wsRef.current) {
      console.warn('WebSocket not initialized');
      return () => {};
    }

    // Store handler reference
    if (!handlersRef.current.has(event)) {
      handlersRef.current.set(event, new Set());
    }
    handlersRef.current.get(event)!.add(handler);

    // Subscribe to WebSocket
    const unsubscribe = wsRef.current.on(event, (data: T) => {
      handler(data);
      setLastMessage({
        event,
        data,
        timestamp: new Date(),
      });
    });

    // Return cleanup function
    return () => {
      unsubscribe();
      handlersRef.current.get(event)?.delete(handler);
    };
  }, []);

  // Setup connection handlers
  useEffect(() => {
    if (!wsRef.current) return;

    const unsubscribeConnect = wsRef.current.onConnect(() => {
      setIsConnected(true);
      setConnectionState('connected');
    });

    const unsubscribeError = wsRef.current.onError((err: Error) => {
      setError(err);
      setConnectionState('error');
    });

    return () => {
      unsubscribeConnect();
      unsubscribeError();
    };
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect && wsRef.current && !isConnected) {
      connect().catch(console.error);
    }

    return () => {
      if (autoConnect && wsRef.current) {
        disconnect();
      }
    };
  }, [autoConnect, connect, disconnect, isConnected]);

  // Update connection state based on WebSocket state
  useEffect(() => {
    if (!wsRef.current) return;

    const interval = setInterval(() => {
      const state = wsRef.current!.getState();
      setConnectionState(state);
      setIsConnected(state === 'connected');
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return {
    isConnected,
    connectionState,
    connect,
    disconnect,
    send,
    on,
    lastMessage,
    error,
  };
} 