// WebSocket utilities and connection management
export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp?: number;
}

export interface WebSocketConfig {
  url?: string;
  reconnectAttempts?: number;
  reconnectDelay?: number;
  heartbeatInterval?: number;
}

export class WebSocketManager {
  private socket: WebSocket | null = null;
  private config: Required<WebSocketConfig>;
  private reconnectCount = 0;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private isConnecting = false;
  private messageHandlers = new Map<string, Set<(data: any) => void>>();
  private connectionHandlers = new Set<(connected: boolean) => void>();

  constructor(config: WebSocketConfig = {}) {
    this.config = {
      url: this.getWebSocketUrl(),
      reconnectAttempts: 5,
      reconnectDelay: 1000,
      heartbeatInterval: 30000,
      ...config,
    };
  }

  private getWebSocketUrl(): string {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}/ws`;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnecting || this.isConnected()) {
        resolve();
        return;
      }

      this.isConnecting = true;

      try {
        this.socket = new WebSocket(this.config.url);

        this.socket.onopen = () => {
          console.log("WebSocket connected");
          this.isConnecting = false;
          this.reconnectCount = 0;
          this.startHeartbeat();
          this.notifyConnectionHandlers(true);
          resolve();
        };

        this.socket.onmessage = (event) => {
          this.handleMessage(event.data);
        };

        this.socket.onclose = (event) => {
          console.log("WebSocket disconnected", event.code, event.reason);
          this.isConnecting = false;
          this.stopHeartbeat();
          this.notifyConnectionHandlers(false);
          this.attemptReconnect();
        };

        this.socket.onerror = (error) => {
          console.error("WebSocket error:", error);
          this.isConnecting = false;
          if (this.reconnectCount === 0) {
            reject(error);
          }
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  disconnect(): void {
    this.stopHeartbeat();
    if (this.socket) {
      this.socket.close(1000, "Manual disconnect");
      this.socket = null;
    }
    this.reconnectCount = this.config.reconnectAttempts;
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }

  send(message: WebSocketMessage): void {
    if (this.isConnected() && this.socket) {
      const messageWithTimestamp = {
        ...message,
        timestamp: Date.now(),
      };
      this.socket.send(JSON.stringify(messageWithTimestamp));
    } else {
      console.warn("WebSocket not connected, message not sent:", message);
    }
  }

  subscribe(messageType: string, handler: (data: any) => void): () => void {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, new Set());
    }
    this.messageHandlers.get(messageType)!.add(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(messageType);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          this.messageHandlers.delete(messageType);
        }
      }
    };
  }

  onConnectionChange(handler: (connected: boolean) => void): () => void {
    this.connectionHandlers.add(handler);
    
    // Return unsubscribe function
    return () => {
      this.connectionHandlers.delete(handler);
    };
  }

  private handleMessage(data: string): void {
    try {
      const message: WebSocketMessage = JSON.parse(data);
      
      // Handle heartbeat responses
      if (message.type === "pong") {
        return;
      }

      // Notify specific message type handlers
      const handlers = this.messageHandlers.get(message.type);
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(message.data);
          } catch (error) {
            console.error(`Error in message handler for ${message.type}:`, error);
          }
        });
      }

      // Notify wildcard handlers
      const wildcardHandlers = this.messageHandlers.get("*");
      if (wildcardHandlers) {
        wildcardHandlers.forEach(handler => {
          try {
            handler(message);
          } catch (error) {
            console.error("Error in wildcard message handler:", error);
          }
        });
      }
    } catch (error) {
      console.error("Error parsing WebSocket message:", error);
    }
  }

  private notifyConnectionHandlers(connected: boolean): void {
    this.connectionHandlers.forEach(handler => {
      try {
        handler(connected);
      } catch (error) {
        console.error("Error in connection handler:", error);
      }
    });
  }

  private attemptReconnect(): void {
    if (this.reconnectCount >= this.config.reconnectAttempts) {
      console.log("Max reconnection attempts reached");
      return;
    }

    const delay = this.config.reconnectDelay * Math.pow(2, this.reconnectCount);
    this.reconnectCount++;

    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectCount})`);

    setTimeout(() => {
      if (!this.isConnected()) {
        this.connect().catch(error => {
          console.error("Reconnection failed:", error);
        });
      }
    }, delay);
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected()) {
        this.send({ type: "ping", data: {} });
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }
}

// Singleton instance for global use
export const wsManager = new WebSocketManager();

// Helper functions for common operations
export function subscribeToExecutionUpdates(handler: (execution: any) => void): () => void {
  return wsManager.subscribe("execucao_atualizada", handler);
}

export function subscribeToNewExecutions(handler: (execution: any) => void): () => void {
  return wsManager.subscribe("execucao_criada", handler);
}

export function subscribeToInvoiceApprovals(handler: (invoice: any) => void): () => void {
  const unsubscribeApproved = wsManager.subscribe("fatura_aprovada", handler);
  const unsubscribeRejected = wsManager.subscribe("fatura_rejeitada", handler);
  
  return () => {
    unsubscribeApproved();
    unsubscribeRejected();
  };
}

export function subscribeToSystemStatus(handler: (status: any) => void): () => void {
  return wsManager.subscribe("sistema_status", handler);
}

export function subscribeToAllMessages(handler: (message: WebSocketMessage) => void): () => void {
  return wsManager.subscribe("*", handler);
}

// Auto-connect when module is imported
if (typeof window !== "undefined") {
  wsManager.connect().catch(error => {
    console.error("Failed to establish initial WebSocket connection:", error);
  });
}
