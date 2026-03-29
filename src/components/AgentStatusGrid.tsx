import React from 'react';
import { Agent } from '../types/agent';

interface AgentStatusGridProps {
  agents: Agent[];
  onAgentClick?: (agent: Agent) => void;
}

export const AgentStatusGrid: React.FC<AgentStatusGridProps> = ({ agents, onAgentClick }) => {
  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'idle':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'offline':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTypeIcon = (type: Agent['type']) => {
    switch (type) {
      case 'coordinator':
        return '👑';
      case 'worker':
        return '⚡';
      case 'specialist':
        return '🎯';
      default:
        return '🤖';
    }
  };

  const getStatusText = (status: Agent['status']) => {
    switch (status) {
      case 'active':
        return 'Активен';
      case 'idle':
        return 'Ожидание';
      case 'offline':
        return 'Офлайн';
      case 'error':
        return 'Ошибка';
      default:
        return 'Неизвестно';
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Статус агентов</h3>
        <p className="text-sm text-gray-600">Текущее состояние всех агентов в системе</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`border rounded-lg p-4 cursor-pointer transition-all hover:shadow-md ${getStatusColor(agent.status)}`}
            onClick={() => onAgentClick?.(agent)}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{getTypeIcon(agent.type)}</span>
                <span className="font-medium text-sm truncate">{agent.name}</span>
              </div>
              <div className="flex items-center">
                <div className={`w-2 h-2 rounded-full ${
                  agent.status === 'active' ? 'bg-green-500 animate-pulse' :
                  agent.status === 'idle' ? 'bg-yellow-500' :
                  agent.status === 'offline' ? 'bg-gray-500' :
                  'bg-red-500'
                }`}></div>
              </div>
            </div>
            
            <div className="text-xs space-y-1">
              <div className="flex justify-between">
                <span>Статус:</span>
                <span className="font-medium">{getStatusText(agent.status)}</span>
              </div>
              
              <div className="flex justify-between">
                <span>Токены:</span>
                <span className="font-medium">
                  {agent.tokensUsed.toLocaleString()}/{agent.tokensLimit.toLocaleString()}
                </span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                <div 
                  className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
                  style={{ width: `${(agent.tokensUsed / agent.tokensLimit) * 100}%` }}
                ></div>
              </div>
              
              <div className="flex justify-between pt-1">
                <span>Задачи:</span>
                <span className="font-medium">{agent.performance.tasksCompleted}</span>
              </div>
              
              <div className="flex justify-between">
                <span>Успешность:</span>
                <span className="font-medium">{agent.performance.successRate}%</span>
              </div>
              
              <div className="text-xs text-gray-500 pt-1">
                Последняя активность: {new Date(agent.lastActivity).toLocaleTimeString('ru-RU')}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};