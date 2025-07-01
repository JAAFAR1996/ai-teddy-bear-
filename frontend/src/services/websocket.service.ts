/**
 * WebSocket Service for AI Teddy Bear
 * Real-time communication with auto-reconnection
 */

import { WebSocketMessage, WebSocketEvent } from '@types';

export interface WebSocketConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  debug?: boolean;
}

type EventHandler<T = any> = (data: T) => void;
type ConnectionHandler = () => void;
type ErrorHandler = (error: Error) => void;

export class WebSocketService {
  private ws: WebSocket | null = null;
  private config: Required<WebSocketConfig>;
  private reconnectAttempts = 0;
  private isIntentionallyClosed = false;
  private eventHandlers: Map<WebSocketEvent, Set<EventHandler>> = new Map();
  private connectionHandlers: Set<ConnectionHandler> = new Set();
  private errorHandlers: Set<ErrorHandler> = new Set();
  private messageQueue: WebSocketMessage[] = [];
  private heartbeatTimer?: number;
  private reconnectTimer?: number;

  constructor(config: WebSocketConfig) {
    this.config = {
      reconnectInterval: 5000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
      debug: false,
      ...config,
    };
  }

  /**
   * Connect to WebSocket server
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      try {
        this.ws = new WebSocket(this.config.url);
        this.setupEventListeners();

        const onOpen = () => {
          this.log('WebSocket connected');
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.flushMessageQueue();
          this.notifyConnectionHandlers();
          resolve();
        };

        const onError = (error: Event) => {
          this.log('WebSocket connection error', error);
          reject(new Error('Failed to connect to WebSocket'));
        };

        this.ws.addEventListener('open', onOpen, { once: true });
        this.ws.addEventListener('error', onError, { once: true });
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.isIntentionallyClosed = true;
    this.stopHeartbeat();
    this.clearReconnectTimer();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  /**
   * Send message through WebSocket
   */
  send<T = any>(event: WebSocketEvent, data: T): void {
    const message: WebSocketMessage<T> = {
      event,
      data,
      timestamp: new Date(),
    };

    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
      this.log('Message sent:', message);
    } else {
      // Queue message if not connected
      this.messageQueue.push(message);
      this.log('Message queued:', message);
      
      // Try to reconnect if not already attempting
      if (!this.reconnectTimer && !this.isIntentionallyClosed) {
        this.reconnect();
      }
    }
  }

  /**
   * Subscribe to WebSocket events
   */
  on<T = any>(event: WebSocketEvent, handler: EventHandler<T>): () => void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    
    this.eventHandlers.get(event)!.add(handler);

    // Return unsubscribe function
    return () => {
      this.eventHandlers.get(event)?.delete(handler);
    };
  }

  /**
   * Subscribe to connection events
   */
  onConnect(handler: ConnectionHandler): () => void {
    this.connectionHandlers.add(handler);
    return () => this.connectionHandlers.delete(handler);
  }

  /**
   * Subscribe to error events
   */
  onError(handler: ErrorHandler): () => void {
    this.errorHandlers.add(handler);
    return () => this.errorHandlers.delete(handler);
  }

  /**
   * Get connection status
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Get connection state
   */
  getState(): 'connecting' | 'connected' | 'disconnected' | 'error' {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
      case WebSocket.CLOSED:
        return this.reconnectAttempts > 0 ? 'error' : 'disconnected';
      default:
        return 'disconnected';
    }
  }

  // Private methods

  private setupEventListeners(): void {
    if (!this.ws) return;

    this.ws.addEventListener('message', this.handleMessage.bind(this));
    this.ws.addEventListener('close', this.handleClose.bind(this));
    this.ws.addEventListener('error', this.handleError.bind(this));
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      this.log('Message received:', message);

      // Handle heartbeat
      if (message.event === 'heartbeat' as WebSocketEvent) {
        return;
      }

      // Notify event handlers
      const handlers = this.eventHandlers.get(message.event);
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(message.data);
          } catch (error) {
            console.error('Error in event handler:', error);
          }
        });
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }

  private handleClose(event: CloseEvent): void {
    this.log('WebSocket closed:', event.code, event.reason);
    this.stopHeartbeat();

    if (!this.isIntentionallyClosed && 
        this.reconnectAttempts < this.config.maxReconnectAttempts) {
      this.reconnect();
    }
  }

  private handleError(event: Event): void {
    const error = new Error('WebSocket error');
    this.log('WebSocket error:', event);
    this.notifyErrorHandlers(error);
  }

  private reconnect(): void {
    if (this.reconnectTimer) return;

    const delay = Math.min(
      this.config.reconnectInterval * Math.pow(2, this.reconnectAttempts),
      30000 // Max 30 seconds
    );

    this.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1})`);

    this.reconnectTimer = setTimeout(async () => {
      this.reconnectTimer = undefined;
      this.reconnectAttempts++;

      try {
        await this.connect();
      } catch (error) {
        this.log('Reconnection failed:', error);
        
        if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
          this.notifyErrorHandlers(new Error('Max reconnection attempts reached'));
        }
      }
    }, delay);
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    
    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          event: 'heartbeat',
          timestamp: new Date(),
        }));
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = undefined;
    }
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = undefined;
    }
  }

  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.ws?.readyState === WebSocket.OPEN) {
      const message = this.messageQueue.shift()!;
      this.ws.send(JSON.stringify(message));
      this.log('Queued message sent:', message);
    }
  }

  private notifyConnectionHandlers(): void {
    this.connectionHandlers.forEach(handler => {
      try {
        handler();
      } catch (error) {
        console.error('Error in connection handler:', error);
      }
    });
  }

  private notifyErrorHandlers(error: Error): void {
    this.errorHandlers.forEach(handler => {
      try {
        handler(error);
      } catch (err) {
        console.error('Error in error handler:', err);
      }
    });
  }

  private log(...args: any[]): void {
    if (this.config.debug) {
      console.log('[WebSocket]', ...args);
    }
  }
}

// Singleton instance
let wsInstance: WebSocketService | null = null;

export const getWebSocketService = (config?: WebSocketConfig): WebSocketService => {
  if (!wsInstance && config) {
    wsInstance = new WebSocketService(config);
  }
  
  if (!wsInstance) {
    throw new Error('WebSocket service not initialized');
  }
  
  return wsInstance;
};

export const initWebSocket = (config: WebSocketConfig): WebSocketService => {
  wsInstance = new WebSocketService(config);
  return wsInstance;
}; 