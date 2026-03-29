import React, { useState, useEffect } from 'react';
import { Agent } from '../types';
import { formatNumber, getTimeAgo, cn, getStatusBgColor } from '../utils';

interface AgentStatusGridProps {
  agents: Agent[];
}

export function AgentStatusGrid({ agents: initialAgents }: AgentStatusGridProps) {
  const [agents, setAgents] = useState(initialAgents);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setAgents((prev) =>
        prev.map((agent) => {
          const rand = Math.random();
          let newStatus = agent.status;

          if (rand > 0.95) {
            const statuses: Agent['status'][] = ['active', 'idle', 'busy', 'error'];
            newStatus = statuses[Math.floor(Math.random() * statuses.length)];
          }

          return {
            ...agent,
            status: newStatus,
            lastHeartbeat:
              newStatus !== 'offline'
                ? new Date().toISOString()
                : agent.lastHeartbeat,
            tokensUsed:
              newStatus === 'busy'
                ? agent.tokensUsed + Math.floor(Math.random() * 500)
                : agent.tokensUsed,
          };
        })
      );
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const statusCounts = agents.reduce(
    (acc, agent) => {
      acc[agent.status] = (acc[agent.status] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Agent Status</h3>
          <p className="text-sm text-gray-500 mt-1">Real-time monitoring</p>
        </div>
        <div className="flex items-center space-x-3">
          <StatusBadge status="active" count={statusCounts.active || 0} />
          <StatusBadge status="busy" count={statusCounts.busy || 0} />
          <StatusBadge status="idle" count={statusCounts.idle || 0} />
          <StatusBadge status="error" count={statusCounts.error || 0} />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            onClick={() => setSelectedAgent(agent)}
            isSelected={selectedAgent?.id === agent.id}
          />
        ))}
      </div>

      {selectedAgent && (
        <AgentDetailModal
          agent={selectedAgent}
          onClose={() => setSelectedAgent(null)}
        />
      )}
    </div>
  );
}

function StatusBadge({ status, count }: { status: string; count: number }) {
  return (
    <div className="flex items-center space-x-1.5">
      <div className={cn('h-2 w-2 rounded-full', getStatusBgColor(status))} />
      <span className="text-xs text-gray-600 capitalize">
        {count} {status}
      </span>
    </div>
  );
}

function AgentCard({
  agent,
  onClick,
  isSelected,
}: {
  agent: Agent;
  onClick: () => void;
  isSelected: boolean;
}) {
  const usagePercent = (agent.tokensUsed / agent.tokensLimit) * 100;

  return (
    <button
      onClick={onClick}
      className={cn(
        'p-4 rounded-lg border-2 text-left transition-all hover:shadow-md',
        isSelected
          ? 'border-primary-500 bg-primary-50'
          : 'border-gray-200 hover:border-gray-300'
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center">
              <span className="text-lg">{getAgentIcon(agent.type)}</span>
            </div>
            <div
              className={cn(
                'absolute -bottom-0.5 -right-0.5 h-3.5 w-3.5 rounded-full border-2 border-white',
                getStatusBgColor(agent.status)
              )}
            />
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-900">{agent.name}</h4>
            <p className="text-xs text-gray-500 capitalize">{agent.type}</p>
          </div>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        {agent.currentTask && (
          <div className="text-xs text-gray-600">
            <span className="font-medium">Task:</span> {agent.currentTask}
          </div>
        )}

        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-500">Token Usage</span>
            <span className={cn(
              'font-medium',
              usagePercent > 80 ? 'text-red-600' : usagePercent > 50 ? 'text-yellow-600' : 'text-green-600'
            )}>
              {usagePercent.toFixed(0)}%
            </span>
          </div>
          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={cn(
                'h-full rounded-full transition-all',
                usagePercent > 80 ? 'bg-red-500' : usagePercent > 50 ? 'bg-yellow-500' : 'bg-green-500'
              )}
              style={{ width: `${Math.min(usagePercent, 100)}%` }}
            />
          </div>
          <div className="flex justify-between text-xs mt-1">
            <span className="text-gray-400">{formatNumber(agent.tokensUsed)}</span>
            <span className="text-gray-400">{formatNumber(agent.tokensLimit)}</span>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>✓ {agent.tasksCompleted} done</span>
          <span>⏳ {agent.tasksPending} pending</span>
          <span>{getTimeAgo(agent.lastHeartbeat)}</span>
        </div>
      </div>
    </button>
  );
}

function AgentDetailModal({ agent, onClose }: { agent: Agent; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-xl shadow-xl max-w-lg w-full mx-4 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <MetricCard label="Status" value={agent.status} />
            <MetricCard label="Type" value={agent.type} />
            <MetricCard label="Tokens Used" value={formatNumber(agent.tokensUsed)} />
            <MetricCard label="Token Limit" value={formatNumber(agent.tokensLimit)} />
            <MetricCard label="Tasks Completed" value={agent.tasksCompleted.toString()} />
            <MetricCard label="Tasks Pending" value={agent.tasksPending.toString()} />
          </div>
          {agent.currentTask && (
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Current Task</p>
              <p className="text-sm text-gray-900">{agent.currentTask}</p>
            </div>
          )}
          <div className="p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500 mb-1">Last Heartbeat</p>
            <p className="text-sm text-gray-900">
              {new Date(agent.lastHeartbeat).toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-3 bg-gray-50 rounded-lg">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm font-medium text-gray-900 capitalize">{value}</p>
    </div>
  );
}

function getAgentIcon(type: string): string {
  const icons: Record<string, string> = {
    ceo: '👔',
    cto: '🔧',
    developer: '💻',
    analyst: '📊',
    qa: '🧪',
    devops: '🚀',
    security: '🔒',
    pm: '📋',
  };
  return icons[type] || '🤖';
}
