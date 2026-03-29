import React, { useState, useEffect } from 'react';
import { Agent, TokenUsage, DashboardMetrics } from '../types/agent';
import { useWebSocket } from '../hooks/useWebSocket';
import { MetricsCards } from '../components/MetricsCards';
import { TokenUsageChart } from '../components/TokenUsageChart';
import { AgentStatusGrid } from '../components/AgentStatusGrid';
import { AgentHierarchy } from '../components/AgentHierarchy';

export const Dashboard: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tokenUsage, setTokenUsage] = useState<TokenUsage[]>([]);
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    totalAgents: 0,
    activeAgents: 0,
    totalTokensUsed: 0,
    totalCost: 0,
    avgResponseTime: 0,
    successRate: 0
  });
  const [timeRange, setTimeRange] = useState<'1h' | '24h' | '7d' | '30d'>('24h');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

  // WebSocket для real-time обновлений
  const { isConnected, lastMessage } = useWebSocket({
    url: process.env.REACT_APP_WS_URL || 'ws://localhost:8080/ws',
    onMessage: (data) => {
      switch (data.type) {
        case 'agent_update':
          setAgents(prev => prev.map(agent => 
            agent.id === data.agent.id ? { ...agent, ...data.agent } : agent
          ));
          break;
        case 'token_usage':
          setTokenUsage(prev => [...prev.slice(-99), data.usage]);
          break;
        case 'metrics_update':
          setMetrics(data.metrics);
          break;
        default:
          break;
      }
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
    }
  });

  // Загрузка начальных данных
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        // Симуляция загрузки данных
        const mockAgents: Agent[] = [
          {
            id: 'coordinator-1',
            name: 'Main Coordinator',
            status: 'active',
            type: 'coordinator',
            tokensUsed: 15000,
            tokensLimit: 100000,
            lastActivity: new Date().toISOString(),
            performance: {
              tasksCompleted: 145,
              successRate: 98.2,
              avgResponseTime: 1.2
            }
          },
          {
            id: 'worker-1',
            name: 'Data Processor',
            status: 'active',
            type: 'worker',
            tokensUsed: 8500,
            tokensLimit: 50000,
            lastActivity: new Date().toISOString(),
            performance: {
              tasksCompleted: 89,
              successRate: 95.5,
              avgResponseTime: 0.8
            },
            parent: 'coordinator-1'
          },
          {
            id: 'specialist-1',
            name: 'ML Analyst',
            status: 'idle',
            type: 'specialist',
            tokensUsed: 12000,
            tokensLimit: 75000,
            lastActivity: new Date(Date.now() - 300000).toISOString(),
            performance: {
              tasksCompleted: 34,
              successRate: 99.1,
              avgResponseTime: 2.1
            },
            parent: 'coordinator-1'
          },
          {
            id: 'worker-2',
            name: 'API Handler',
            status: 'error',
            type: 'worker',
            tokensUsed: 3200,
            tokensLimit: 25000,
            lastActivity: new Date(Date.now() - 600000).toISOString(),
            performance: {
              tasksCompleted: 23,
              successRate: 87.0,
              avgResponseTime: 1.8
            },
            parent: 'coordinator-1'
          }
        ];

        const mockTokenUsage: TokenUsage[] = Array.from({ length: 24 }, (_, i) => ({
          timestamp: new Date(Date.now() - (23 - i) * 60 * 60 * 1000).toISOString(),
          agentId: mockAgents[Math.floor(Math.random() * mockAgents.length)].id,
          tokensUsed: Math.floor(Math.random() * 1000) + 100,
          tokensRemaining: Math.floor(Math.random() * 10000) + 5000,
          cost: Math.random() * 5 + 0.1
        }));

        const mockMetrics: DashboardMetrics = {
          totalAgents: mockAgents.length,
          activeAgents: mockAgents.filter(a => a.status === 'active').length,
          totalTokensUsed: mockAgents.reduce((sum, a) => sum + a.tokensUsed, 0),
          totalCost: mockTokenUsage.reduce((sum, t) => sum + t.cost, 0),
          avgResponseTime: mockAgents.reduce((sum, a) => sum + a.performance.avgResponseTime, 0) / mockAgents.length,
          successRate: mockAgents.reduce((sum, a) => sum + a.performance.successRate, 0) / mockAgents.length
        };

        setAgents(mockAgents);
        setTokenUsage(mockTokenUsage);
        setMetrics(mockMetrics);
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to load initial data:', error);
        setIsLoading(false);
      }
    };

    loadInitialData();
  }, []);

  const handleAgentClick = (agent: Agent) => {
    setSelectedAgent(agent);
  };

  const filteredTokenUsage = tokenUsage.filter(usage => {
    const now = new Date();
    const usageDate = new Date(usage.timestamp);
    const diffHours = (now.getTime() - usageDate.getTime()) / (1000 * 60 * 60);
    
    switch (timeRange) {
      case '1h':
        return diffHours <= 1;
      case '24h':
        return diffHours <= 24;
      case '7d':
        return diffHours <= 24 * 7;
      case '30d':
        return diffHours <= 24 * 30;
      default:
        return true;
    }
  });

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">ALVO Platform Dashboard</h1>
            <p className="text-gray-600">Мониторинг агентов и использования ресурсов</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
              isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span>{isConnected ? 'Подключено' : 'Отключено'}</span>
            </div>
            <select 
              value={timeRange} 
              onChange={(e) => setTimeRange(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="1h">Последний час</option>
              <option value="24h">Последние 24 часа</option>
              <option value="7d">Последние 7 дней</option>
              <option value="30d">Последние 30 дней</option>
            </select>
          </div>
        </div>

        {/* Metrics Cards */}
        <MetricsCards metrics={metrics} isLoading={isLoading} />

        {/* Charts and Status */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TokenUsageChart data={filteredTokenUsage} timeRange={timeRange} />
          <AgentHierarchy agents={agents} />
        </div>

        {/* Agent Status Grid */}
        <AgentStatusGrid agents={agents} onAgentClick={handleAgentClick} />

        {/* Selected Agent Modal */}
        {selectedAgent && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Детали агента</h3>
                <button 
                  onClick={() => setSelectedAgent(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              <div className="space-y-3">
                <div><strong>Имя:</strong> {selectedAgent.name}</div>
                <div><strong>ID:</strong> {selectedAgent.id}</div>
                <div><strong>Тип:</strong> {selectedAgent.type}</div>
                <div><strong>Статус:</strong> {selectedAgent.status}</div>
                <div><strong>Токены:</strong> {selectedAgent.tokensUsed.toLocaleString()}/{selectedAgent.tokensLimit.toLocaleString()}</div>
                <div><strong>Задачи выполнено:</strong> {selectedAgent.performance.tasksCompleted}</div>
                <div><strong>Успешность:</strong> {selectedAgent.performance.successRate}%</div>
                <div><strong>Среднее время ответа:</strong> {selectedAgent.performance.avgResponseTime}с</div>
                <div><strong>Последняя активность:</strong> {new Date(selectedAgent.lastActivity).toLocaleString('ru-RU')}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};