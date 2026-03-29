import { Agent, TokenUsageSummary, Task, SystemMetrics } from '../types';

export const mockAgents: Agent[] = [
  {
    id: 'ceo-001',
    name: 'CEO Agent',
    type: 'ceo',
    status: 'active',
    lastHeartbeat: new Date().toISOString(),
    currentTask: 'Strategic planning review',
    tokensUsed: 125000,
    tokensLimit: 500000,
    tasksCompleted: 45,
    tasksPending: 3,
  },
  {
    id: 'cto-001',
    name: 'CTO Agent',
    type: 'cto',
    status: 'busy',
    lastHeartbeat: new Date(Date.now() - 30000).toISOString(),
    currentTask: 'Architecture review',
    tokensUsed: 280000,
    tokensLimit: 500000,
    tasksCompleted: 78,
    tasksPending: 5,
  },
  {
    id: 'dev-001',
    name: 'Frontend Developer',
    type: 'developer',
    status: 'active',
    lastHeartbeat: new Date(Date.now() - 15000).toISOString(),
    currentTask: 'Dashboard UI implementation',
    tokensUsed: 195000,
    tokensLimit: 500000,
    tasksCompleted: 120,
    tasksPending: 8,
  },
  {
    id: 'dev-002',
    name: 'Backend Developer',
    type: 'developer',
    status: 'active',
    lastHeartbeat: new Date(Date.now() - 45000).toISOString(),
    currentTask: 'API optimization',
    tokensUsed: 210000,
    tokensLimit: 500000,
    tasksCompleted: 95,
    tasksPending: 6,
  },
  {
    id: 'analyst-001',
    name: 'Data Analyst',
    type: 'analyst',
    status: 'idle',
    lastHeartbeat: new Date(Date.now() - 120000).toISOString(),
    tokensUsed: 85000,
    tokensLimit: 300000,
    tasksCompleted: 34,
    tasksPending: 1,
  },
  {
    id: 'qa-001',
    name: 'QA Lead',
    type: 'qa',
    status: 'active',
    lastHeartbeat: new Date(Date.now() - 10000).toISOString(),
    currentTask: 'E2E test suite review',
    tokensUsed: 145000,
    tokensLimit: 400000,
    tasksCompleted: 67,
    tasksPending: 4,
  },
  {
    id: 'devops-001',
    name: 'DevOps Engineer',
    type: 'devops',
    status: 'active',
    lastHeartbeat: new Date(Date.now() - 5000).toISOString(),
    currentTask: 'CI/CD pipeline optimization',
    tokensUsed: 110000,
    tokensLimit: 400000,
    tasksCompleted: 89,
    tasksPending: 2,
  },
  {
    id: 'security-001',
    name: 'Security Architect',
    type: 'security',
    status: 'error',
    lastHeartbeat: new Date(Date.now() - 300000).toISOString(),
    tokensUsed: 95000,
    tokensLimit: 400000,
    tasksCompleted: 23,
    tasksPending: 7,
  },
  {
    id: 'pm-001',
    name: 'Project Manager',
    type: 'pm',
    status: 'active',
    lastHeartbeat: new Date(Date.now() - 20000).toISOString(),
    currentTask: 'Sprint planning',
    tokensUsed: 75000,
    tokensLimit: 300000,
    tasksCompleted: 56,
    tasksPending: 12,
  },
];

export const mockTokenUsageSummary: TokenUsageSummary = {
  totalTokens: 1320000,
  totalCost: 26.40,
  byAgent: [
    { agentId: 'cto-001', agentName: 'CTO Agent', tokens: 280000, cost: 5.60, percentage: 21.2 },
    { agentId: 'dev-002', agentName: 'Backend Developer', tokens: 210000, cost: 4.20, percentage: 15.9 },
    { agentId: 'dev-001', agentName: 'Frontend Developer', tokens: 195000, cost: 3.90, percentage: 14.8 },
    { agentId: 'qa-001', agentName: 'QA Lead', tokens: 145000, cost: 2.90, percentage: 11.0 },
    { agentId: 'ceo-001', agentName: 'CEO Agent', tokens: 125000, cost: 2.50, percentage: 9.5 },
    { agentId: 'devops-001', agentName: 'DevOps Engineer', tokens: 110000, cost: 2.20, percentage: 8.3 },
    { agentId: 'security-001', agentName: 'Security Architect', tokens: 95000, cost: 1.90, percentage: 7.2 },
    { agentId: 'analyst-001', agentName: 'Data Analyst', tokens: 85000, cost: 1.70, percentage: 6.4 },
    { agentId: 'pm-001', agentName: 'Project Manager', tokens: 75000, cost: 1.50, percentage: 5.7 },
  ],
  byModel: [
    { model: 'claude-3-opus', tokens: 520000, cost: 15.60, percentage: 39.4 },
    { model: 'claude-3-sonnet', tokens: 380000, cost: 5.70, percentage: 28.8 },
    { model: 'gpt-4-turbo', tokens: 250000, cost: 7.50, percentage: 18.9 },
    { model: 'gpt-3.5-turbo', tokens: 120000, cost: 0.24, percentage: 9.1 },
    { model: 'mistral-large', tokens: 50000, cost: 0.50, percentage: 3.8 },
  ],
  hourlyUsage: generateHourlyUsage(),
  dailyUsage: generateDailyUsage(),
};

function generateHourlyUsage() {
  const hours = [];
  for (let i = 23; i >= 0; i--) {
    const date = new Date();
    date.setHours(date.getHours() - i);
    hours.push({
      hour: date.toISOString(),
      tokens: Math.floor(Math.random() * 50000) + 20000,
      cost: (Math.random() * 1.5 + 0.4),
    });
  }
  return hours;
}

function generateDailyUsage() {
  const days = [];
  for (let i = 29; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    days.push({
      date: date.toISOString().split('T')[0],
      tokens: Math.floor(Math.random() * 100000) + 30000,
      cost: (Math.random() * 3 + 0.6),
    });
  }
  return days;
}

export const mockTasks: Task[] = [
  {
    id: 'task-001',
    title: 'Implement real-time WebSocket updates',
    description: 'Add WebSocket support for live agent status updates',
    status: 'in_progress',
    assignedTo: 'dev-001',
    priority: 'high',
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'task-002',
    title: 'Optimize database queries',
    description: 'Review and optimize slow database queries',
    status: 'pending',
    assignedTo: 'dev-002',
    priority: 'medium',
    createdAt: new Date(Date.now() - 172800000).toISOString(),
    updatedAt: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: 'task-003',
    title: 'Security audit report',
    description: 'Complete quarterly security audit',
    status: 'blocked',
    assignedTo: 'security-001',
    priority: 'critical',
    createdAt: new Date(Date.now() - 259200000).toISOString(),
    updatedAt: new Date(Date.now() - 300000).toISOString(),
  },
  {
    id: 'task-004',
    title: 'API documentation update',
    description: 'Update OpenAPI specs for new endpoints',
    status: 'completed',
    assignedTo: 'pm-001',
    priority: 'low',
    createdAt: new Date(Date.now() - 345600000).toISOString(),
    updatedAt: new Date(Date.now() - 7200000).toISOString(),
  },
  {
    id: 'task-005',
    title: 'E2E test coverage expansion',
    description: 'Add E2E tests for dashboard components',
    status: 'in_progress',
    assignedTo: 'qa-001',
    priority: 'medium',
    createdAt: new Date(Date.now() - 432000000).toISOString(),
    updatedAt: new Date(Date.now() - 1800000).toISOString(),
  },
];

export const mockSystemMetrics: SystemMetrics = {
  cpuUsage: 45.2,
  memoryUsage: 68.5,
  diskUsage: 32.1,
  activeAgents: 7,
  totalAgents: 9,
  activeTasks: 15,
  completedTasks: 607,
  uptime: '7d 14h 32m',
};
