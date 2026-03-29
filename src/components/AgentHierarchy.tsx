import React, { useState } from 'react';
import { Agent } from '../types/agent';

interface AgentHierarchyProps {
  agents: Agent[];
}

export const AgentHierarchy: React.FC<AgentHierarchyProps> = ({ agents }) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  const toggleNode = (agentId: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(agentId)) {
      newExpanded.delete(agentId);
    } else {
      newExpanded.add(agentId);
    }
    setExpandedNodes(newExpanded);
  };

  const buildHierarchy = (agents: Agent[]) => {
    const agentMap = new Map(agents.map(agent => [agent.id, agent]));
    const roots: Agent[] = [];
    
    agents.forEach(agent => {
      if (!agent.parent) {
        roots.push(agent);
      }
    });
    
    return roots;
  };

  const getChildren = (parentId: string) => {
    return agents.filter(agent => agent.parent === parentId);
  };

  const getStatusIcon = (status: Agent['status']) => {
    switch (status) {
      case 'active':
        return '🟢';
      case 'idle':
        return '🟡';
      case 'offline':
        return '⚫';
      case 'error':
        return '🔴';
      default:
        return '⚪';
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

  const renderAgent = (agent: Agent, level: number = 0) => {
    const children = getChildren(agent.id);
    const hasChildren = children.length > 0;
    const isExpanded = expandedNodes.has(agent.id);

    return (
      <div key={agent.id} className="mb-2">
        <div 
          className="flex items-center p-2 hover:bg-gray-50 rounded cursor-pointer"
          style={{ marginLeft: `${level * 20}px` }}
          onClick={() => hasChildren && toggleNode(agent.id)}
        >
          <div className="flex items-center space-x-2 flex-1">
            {hasChildren && (
              <span className="text-gray-400 w-4">
                {isExpanded ? '▼' : '▶'}
              </span>
            )}
            {!hasChildren && <span className="w-4"></span>}
            
            <span>{getStatusIcon(agent.status)}</span>
            <span>{getTypeIcon(agent.type)}</span>
            
            <div className="flex-1">
              <div className="font-medium text-sm">{agent.name}</div>
              <div className="text-xs text-gray-500">
                {agent.tokensUsed.toLocaleString()}/{agent.tokensLimit.toLocaleString()} токенов
              </div>
            </div>
            
            <div className="text-xs text-gray-400">
              {agent.performance.tasksCompleted} задач
            </div>
          </div>
        </div>
        
        {hasChildren && isExpanded && (
          <div>
            {children.map(child => renderAgent(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  const rootAgents = buildHierarchy(agents);

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Иерархия агентов</h3>
        <p className="text-sm text-gray-600">Структура подчинения и взаимодействия агентов</p>
      </div>
      
      <div className="max-h-96 overflow-y-auto">
        {rootAgents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <span className="text-4xl">🤖</span>
            <p className="mt-2">Агенты не найдены</p>
          </div>
        ) : (
          rootAgents.map(agent => renderAgent(agent))
        )}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1">
              <span>🟢</span><span>Активен</span>
            </span>
            <span className="flex items-center space-x-1">
              <span>🟡</span><span>Ожидание</span>
            </span>
            <span className="flex items-center space-x-1">
              <span>⚫</span><span>Офлайн</span>
            </span>
            <span className="flex items-center space-x-1">
              <span>🔴</span><span>Ошибка</span>
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1">
              <span>👑</span><span>Координатор</span>
            </span>
            <span className="flex items-center space-x-1">
              <span>⚡</span><span>Рабочий</span>
            </span>
            <span className="flex items-center space-x-1">
              <span>🎯</span><span>Специалист</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};