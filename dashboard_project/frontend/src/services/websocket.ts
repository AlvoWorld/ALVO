import { WebSocketMessage, Agent, SystemMetrics } from '../types';

type MessageHandler = (message: WebSocketMessage) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private handlers: Set<MessageHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private url: string;

  constructor(url: string = 'ws://localhost:8000/ws') {
    this.url = url;
  }

  connect(): void {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.handlers.forEach((handler) => handler(message));
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      this.attemptReconnect();
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      setTimeout(() => this.connect(), this.reconnectDelay);
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  subscribe(handler: MessageHandler): () => void {
    this.handlers.add(handler);
    return () => {
      this.handlers.delete(handler);
    };
  }

  send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }
}

// Simulated WebSocket for demo purposes
class SimulatedWebSocket {
  private handlers: Set<MessageHandler> = new Set();
  private intervalId: ReturnType<typeof setInterval> | null = null;

  connect(): void {
    console.log('Simulated WebSocket connected');
    this.startSimulation();
  }

  disconnect(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    console.log('Simulated WebSocket disconnected');
  }

  subscribe(handler: MessageHandler): () => void {
    this.handlers.add(handler);
    return () => {
      this.handlers.delete(handler);
    };
  }

  private startSimulation(): void {
    this.intervalId = setInterval(() => {
      const messageTypes: WebSocketMessage['type'][] = [
        'agent_status',
        'token_usage',
        'system_metrics',
        'heartbeat',
      ];

      const type = messageTypes[Math.floor(Math.random() * messageTypes.length)];
      let payload: any;

      switch (type) {
        case 'agent_status':
          payload = this.generateAgentStatus();
          break;
        case 'token_usage':
          payload = this.generateTokenUsage();
          break;
        case 'system_metrics':
          payload = this.generateSystemMetrics();
          break;
        case 'heartbeat':
          payload = { agentId: `agent-${Math.floor(Math.random() * 9) + 1}` };
          break;
      }

      const message: WebSocketMessage = {
        type,
        payload,
        timestamp: new Date().toISOString(),
      };

      this.handlers.forEach((handler) => handler(message));
    }, 3000);
  }

  private generateAgentStatus(): Partial<Agent> {
    const statuses: Agent['status'][] = ['active', 'idle', 'busy', 'error'];
    return {
      id: `agent-${Math.floor(Math.random() * 9) + 1}`,
      status: statuses[Math.floor(Math.random() * statuses.length)],
      lastHeartbeat: new Date().toISOString(),
    };
  }

  private generateTokenUsage() {
    return {
      agentId: `agent-${Math.floor(Math.random() * 9) + 1}`,
      tokens: Math.floor(Math.random() * 5000) + 500,
      model: ['claude-3-opus', 'claude-3-sonnet', 'gpt-4-turbo'][Math.floor(Math.random() * 3)],
    };
  }

  private generateSystemMetrics(): Partial<SystemMetrics> {
    return {
      cpuUsage: Math.random() * 30 + 30,
      memoryUsage: Math.random() * 20 + 55,
    };
  }

  send(_message: any): void {
    // No-op for simulation
  }
}

// Use simulated WebSocket in development, real one in production
export const wsService = process.env.NODE_ENV === 'production'
  ? new WebSocketService()
  : new SimulatedWebSocket();

export default wsService;
