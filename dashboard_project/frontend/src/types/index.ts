export interface Agent {
  id: string;
  name: string;
  type: 'ceo' | 'cto' | 'developer' | 'analyst' | 'qa' | 'devops' | 'security' | 'pm';
  status: 'active' | 'idle' | 'busy' | 'error' | 'offline';
  lastHeartbeat: string;
  currentTask?: string;
  tokensUsed: number;
  tokensLimit: number;
  tasksCompleted: number;
  tasksPending: number;
}

export interface TokenUsage {
  timestamp: string;
  agentId: string;
  agentName: string;
  tokensUsed: number;
  cost: number;
  model: string;
}

export interface TokenUsageSummary {
  totalTokens: number;
  totalCost: number;
  byAgent: {
    agentId: string;
    agentName: string;
    tokens: number;
    cost: number;
    percentage: number;
  }[];
  byModel: {
    model: string;
    tokens: number;
    cost: number;
    percentage: number;
  }[];
  hourlyUsage: {
    hour: string;
    tokens: number;
    cost: number;
  }[];
  dailyUsage: {
    date: string;
    tokens: number;
    cost: number;
  }[];
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'blocked';
  assignedTo?: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  createdAt: string;
  updatedAt: string;
}

export interface SystemMetrics {
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  activeAgents: number;
  totalAgents: number;
  activeTasks: number;
  completedTasks: number;
  uptime: string;
}

export interface WebSocketMessage {
  type: 'agent_status' | 'token_usage' | 'task_update' | 'system_metrics' | 'heartbeat';
  payload: any;
  timestamp: string;
}

export type TimeRange = '1h' | '6h' | '24h' | '7d' | '30d';
