import React from 'react';
import { DashboardMetrics } from '../types/agent';

interface MetricsCardsProps {
  metrics: DashboardMetrics;
  isLoading?: boolean;
}

export const MetricsCards: React.FC<MetricsCardsProps> = ({ metrics, isLoading = false }) => {
  const cards = [
    {
      title: 'Всего агентов',
      value: metrics.totalAgents,
      icon: '🤖',
      color: 'bg-blue-50 text-blue-600',
      change: '+2 за час'
    },
    {
      title: 'Активные агенты',
      value: metrics.activeAgents,
      icon: '⚡',
      color: 'bg-green-50 text-green-600',
      change: `${((metrics.activeAgents / metrics.totalAgents) * 100).toFixed(1)}%`
    },
    {
      title: 'Использовано токенов',
      value: metrics.totalTokensUsed.toLocaleString(),
      icon: '💎',
      color: 'bg-purple-50 text-purple-600',
      change: '+12.5K за час'
    },
    {
      title: 'Общие расходы',
      value: `$${metrics.totalCost.toFixed(2)}`,
      icon: '💰',
      color: 'bg-yellow-50 text-yellow-600',
      change: '+$45.20 за час'
    },
    {
      title: 'Среднее время ответа',
      value: `${metrics.avgResponseTime.toFixed(1)}с`,
      icon: '⏱️',
      color: 'bg-indigo-50 text-indigo-600',
      change: '-0.3с от вчера'
    },
    {
      title: 'Успешность',
      value: `${metrics.successRate.toFixed(1)}%`,
      icon: '✅',
      color: 'bg-emerald-50 text-emerald-600',
      change: '+2.1% от вчера'
    }
  ];

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="bg-white p-4 rounded-lg shadow animate-pulse">
            <div className="flex items-center justify-between mb-2">
              <div className="w-8 h-8 bg-gray-200 rounded"></div>
              <div className="w-4 h-4 bg-gray-200 rounded"></div>
            </div>
            <div className="w-16 h-6 bg-gray-200 rounded mb-1"></div>
            <div className="w-20 h-4 bg-gray-200 rounded mb-1"></div>
            <div className="w-12 h-3 bg-gray-200 rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {cards.map((card, index) => (
        <div key={index} className="bg-white p-4 rounded-lg shadow-lg hover:shadow-xl transition-shadow">
          <div className="flex items-center justify-between mb-2">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${card.color}`}>
              <span className="text-xl">{card.icon}</span>
            </div>
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          </div>
          
          <div className="mb-1">
            <div className="text-2xl font-bold text-gray-900">{card.value}</div>
            <div className="text-sm text-gray-600">{card.title}</div>
          </div>
          
          <div className="text-xs text-gray-500">{card.change}</div>
        </div>
      ))}
    </div>
  );
};