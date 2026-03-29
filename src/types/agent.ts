export interface Agent {
  id: string;
  name: string;
  status: 'active' | 'idle' | 'offline' | 'error';
  type: 'coordinator' | 'worker' | 'specialist';
  tokensUsed: number;
  tokensLimit: number;
  lastActivity: string;
  performance: {
    tasksCompleted: number;
    successRate: number;
    avgResponseTime: number;
  };
  parent?: string;
  children?: string[];
}

export interface TokenUsage {
  timestamp: string;
  agentId: string;
  tokensUsed: number;
  tokensRemaining: number;
  cost: number;
}

export interface DashboardMetrics {
  totalAgents: number;
  activeAgents: number;
  totalTokensUsed: number;
  totalCost: number;
  avgResponseTime: number;
  successRate: number;
}