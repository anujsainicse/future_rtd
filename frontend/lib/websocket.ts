import { io, Socket } from 'socket.io-client';
import { WebSocketMessage, ConnectionStatus } from '@/types';

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectInterval: NodeJS.Timeout | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners: { [key: string]: ((data: any) => void)[] } = {};
  private connectionStatus: ConnectionStatus = {
    connected: false,
    connecting: false,
    error: null,
    lastConnected: null
  };

  connect(url: string = 'ws://localhost:8000/ws') {
    if (this.socket && (this.socket.readyState === WebSocket.CONNECTING || this.socket.readyState === WebSocket.OPEN)) {
      return;
    }

    this.connectionStatus.connecting = true;
    this.connectionStatus.error = null;
    this.emit('connection-status', this.connectionStatus);

    try {
      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        console.log('WebSocket connected');
        this.connectionStatus = {
          connected: true,
          connecting: false,
          error: null,
          lastConnected: new Date()
        };
        this.reconnectAttempts = 0;
        this.emit('connection-status', this.connectionStatus);
        
        if (this.reconnectInterval) {
          clearInterval(this.reconnectInterval);
          this.reconnectInterval = null;
        }
      };

      this.socket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.emit(message.type, message.data);
          this.emit('message', message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.socket.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.connectionStatus = {
          connected: false,
          connecting: false,
          error: event.reason || 'Connection closed',
          lastConnected: this.connectionStatus.lastConnected
        };
        this.emit('connection-status', this.connectionStatus);
        
        if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect();
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.connectionStatus = {
          connected: false,
          connecting: false,
          error: 'Connection error',
          lastConnected: this.connectionStatus.lastConnected
        };
        this.emit('connection-status', this.connectionStatus);
      };

    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      this.connectionStatus = {
        connected: false,
        connecting: false,
        error: 'Failed to create connection',
        lastConnected: this.connectionStatus.lastConnected
      };
      this.emit('connection-status', this.connectionStatus);
    }
  }

  disconnect() {
    if (this.reconnectInterval) {
      clearInterval(this.reconnectInterval);
      this.reconnectInterval = null;
    }

    if (this.socket) {
      this.socket.close(1000, 'Client disconnect');
      this.socket = null;
    }

    this.connectionStatus = {
      connected: false,
      connecting: false,
      error: null,
      lastConnected: this.connectionStatus.lastConnected
    };
    this.emit('connection-status', this.connectionStatus);
  }

  send(data: any) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(typeof data === 'string' ? data : JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  on(event: string, callback: (data: any) => void) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  off(event: string, callback?: (data: any) => void) {
    if (!this.listeners[event]) return;

    if (callback) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    } else {
      this.listeners[event] = [];
    }
  }

  private emit(event: string, data: any) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in WebSocket event listener for ${event}:`, error);
        }
      });
    }
  }

  private scheduleReconnect() {
    if (this.reconnectInterval) return;

    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000);

    console.log(`Scheduling reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);

    this.reconnectInterval = setTimeout(() => {
      this.reconnectInterval = null;
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.connect();
      } else {
        console.error('Max reconnection attempts reached');
        this.connectionStatus.error = 'Max reconnection attempts reached';
        this.emit('connection-status', this.connectionStatus);
      }
    }, delay);
  }

  getConnectionStatus(): ConnectionStatus {
    return { ...this.connectionStatus };
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();
export default websocketService;