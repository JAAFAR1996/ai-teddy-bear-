import { EventEmitter } from 'events';

export enum WebSocketState {
  CONNECTING = 'CONNECTING',
  OPEN = 'OPEN',
  CLOSING = 'CLOSING',
  CLOSED = 'CLOSED',
  RECONNECTING = 'RECONNECTING'
}

export interface WebSocketConfig {
  url: string;
  protocols?: string[];
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  timeout?: number;
  autoConnect?: boolean;
  debug?: boolean;
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: number;
  id?: string;
}

/**
 * WebSocket Service for real-time communication
 * Implements automatic reconnection, heartbeat, and message queueing
 */
export class WebSocketService extends EventEmitter {
  private ws: WebSocket | null = null;
  private config: Required<WebSocketConfig>;
  private state: WebSocketState = WebSocketState.CLOSED;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private messageQueue: WebSocketMessage[] = [];
  private isIntentionallyClosed = false;

  constructor(config: WebSocketConfig) {
    super();
    this.config = {
      url: config.url,
      protocols: config.protocols || [],
      reconnectInterval: config.reconnectInterval || 3000,
      maxReconnectAttempts: config.maxReconnectAttempts || 5,
      heartbeatInterval: config.heartbeatInterval || 30000,
      timeout: config.timeout || 10000,
      autoConnect: config.autoConnect !== false,
      debug: config.debug || false
    };

    if (this.config.autoConnect) {
      this.connect();
    }
  }

  private log(message: string, ...args: any[]): void {
    if (this.config.debug) {
      console.log(`[WebSocket] ${message}`, ...args);
    }
  }

  connect(): void {
    if (this.state === WebSocketState.OPEN || this.state === WebSocketState.CONNECTING) {
      this.log('Already connected or connecting');
      return;
    }

    this.isIntentionallyClosed = false;
    this.state = WebSocketState.CONNECTING;
    this.emit('connecting');

    try {
      this.ws = new WebSocket(this.config.url, this.config.protocols);
      this.setupEventHandlers();
    } catch (error) {
      this.log('Connection error:', error);
      this.handleError(error);
    }
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      this.log('Connected');
      this.state = WebSocketState.OPEN;
      this.reconnectAttempts = 0;
      this.emit('open');
      this.startHeartbeat();
      this.flushMessageQueue();
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        this.log('Message received:', message.type);
        this.emit('message', message);
        this.emit(message.type, message.data);
      } catch (error) {
        this.log('Failed to parse message:', error);
        this.emit('error', error);
      }
    };

    this.ws.onerror = (error) => {
      this.log('WebSocket error:', error);
      this.handleError(error);
    };

    this.ws.onclose = (event) => {
      this.log('Connection closed:', event.code, event.reason);
      this.state = WebSocketState.CLOSED;
      this.stopHeartbeat();
      this.emit('close', event);

      if (!this.isIntentionallyClosed && this.shouldReconnect()) {
        this.scheduleReconnect();
      }
    };
  }

  private handleError(error: any): void {
    this.emit('error', error);
    if (this.state === WebSocketState.CONNECTING) {
      this.state = WebSocketState.CLOSED;
      if (this.shouldReconnect()) {
        this.scheduleReconnect();
      }
    }
  }

  private shouldReconnect(): boolean {
    return this.reconnectAttempts < this.config.maxReconnectAttempts;
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    this.state = WebSocketState.RECONNECTING;
    this.reconnectAttempts++;
    const delay = this.config.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1);

    this.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    this.emit('reconnecting', this.reconnectAttempts);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected()) {
        this.send({ type: 'heartbeat', data: { timestamp: Date.now() } });
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.isConnected()) {
      const message = this.messageQueue.shift();
      if (message) {
        this.send(message);
      }
    }
  }

  send(message: Partial<WebSocketMessage>): void {
    const fullMessage: WebSocketMessage = {
      type: message.type || 'message',
      data: message.data,
      timestamp: message.timestamp || Date.now(),
      id: message.id || this.generateMessageId()
    };

    if (this.isConnected() && this.ws) {
      try {
        this.ws.send(JSON.stringify(fullMessage));
        this.log('Message sent:', fullMessage.type);
      } catch (error) {
        this.log('Failed to send message:', error);
        this.messageQueue.push(fullMessage);
      }
    } else {
      this.log('Queueing message:', fullMessage.type);
      this.messageQueue.push(fullMessage);
    }
  }

  disconnect(): void {
    this.isIntentionallyClosed = true;
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    this.stopHeartbeat();

    if (this.ws) {
      this.state = WebSocketState.CLOSING;
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }

    this.state = WebSocketState.CLOSED;
    this.messageQueue = [];
  }

  isConnected(): boolean {
    return this.state === WebSocketState.OPEN && this.ws?.readyState === WebSocket.OPEN;
  }

  getState(): WebSocketState {
    return this.state;
  }

  private generateMessageId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Create singleton instance
const wsConfig: WebSocketConfig = {
  url: process.env['REACT_APP_WS_URL'] || 'ws://localhost:8000/ws',
  autoConnect: false,
  debug: process.env['NODE_ENV'] === 'development'
};

export const websocketService = new WebSocketService(wsConfig);
export default websocketService; 