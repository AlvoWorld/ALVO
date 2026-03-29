import React from 'react';
import { Task, Agent } from '../types';
import { getTimeAgo, cn, getPriorityColor } from '../utils';

interface RecentTasksProps {
  tasks: Task[];
  agents: Agent[];
}

export function RecentTasks({ tasks, agents }: RecentTasksProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Recent Tasks</h3>
          <p className="text-sm text-gray-500 mt-1">Active work items</p>
        </div>
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          View All →
        </button>
      </div>

      <div className="space-y-4">
        {tasks.map((task) => {
          const assignedAgent = agents.find((a) => a.id === task.assignedTo);
          return (
            <TaskItem key={task.id} task={task} agent={assignedAgent} />
          );
        })}
      </div>
    </div>
  );
}

function TaskItem({ task, agent }: { task: Task; agent?: Agent }) {
  return (
    <div className="flex items-start space-x-4 p-4 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors">
      <div className="flex-shrink-0 mt-1">
        <TaskStatusIcon status={task.status} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center space-x-2">
          <h4 className="text-sm font-medium text-gray-900 truncate">
            {task.title}
          </h4>
          <span
            className={cn(
              'px-2 py-0.5 text-xs font-medium rounded-full',
              getPriorityColor(task.priority)
            )}
          >
            {task.priority}
          </span>
        </div>
        <p className="text-xs text-gray-500 mt-1 line-clamp-1">
          {task.description}
        </p>
        <div className="flex items-center space-x-4 mt-2">
          {agent && (
            <div className="flex items-center space-x-1.5">
              <div className="h-5 w-5 rounded-full bg-gray-100 flex items-center justify-center text-xs">
                {getAgentIcon(agent.type)}
              </div>
              <span className="text-xs text-gray-600">{agent.name}</span>
            </div>
          )}
          <span className="text-xs text-gray-400">
            Updated {getTimeAgo(task.updatedAt)}
          </span>
        </div>
      </div>
      <div className="flex-shrink-0">
        <span
          className={cn(
            'px-2.5 py-1 text-xs font-medium rounded-full capitalize',
            task.status === 'completed'
              ? 'bg-green-100 text-green-700'
              : task.status === 'in_progress'
              ? 'bg-blue-100 text-blue-700'
              : task.status === 'blocked'
              ? 'bg-red-100 text-red-700'
              : 'bg-gray-100 text-gray-700'
          )}
        >
          {task.status.replace('_', ' ')}
        </span>
      </div>
    </div>
  );
}

function TaskStatusIcon({ status }: { status: Task['status'] }) {
  const icons: Record<string, { icon: string; bg: string }> = {
    pending: { icon: '○', bg: 'bg-gray-100 text-gray-500' },
    in_progress: { icon: '◐', bg: 'bg-blue-100 text-blue-500' },
    completed: { icon: '●', bg: 'bg-green-100 text-green-500' },
    blocked: { icon: '⊘', bg: 'bg-red-100 text-red-500' },
  };

  const { icon, bg } = icons[status] || icons.pending;

  return (
    <div
      className={cn(
        'h-8 w-8 rounded-full flex items-center justify-center text-lg',
        bg
      )}
    >
      {icon}
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
