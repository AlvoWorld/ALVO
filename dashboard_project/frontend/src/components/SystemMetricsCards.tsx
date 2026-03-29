import React, { useState, useEffect } from 'react';
import { SystemMetrics } from '../types';
import { cn } from '../utils';

interface SystemMetricsCardsProps {
  metrics: SystemMetrics;
}

export function SystemMetricsCards({ metrics: initialMetrics }: SystemMetricsCardsProps) {
  const [metrics, setMetrics] = useState(initialMetrics);

  // Simulate real-time metric updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((prev) => ({
        ...prev,
        cpuUsage: Math.max(0, Math.min(100, prev.cpuUsage + (Math.random() - 0.5) * 10)),
        memoryUsage: Math.max(0, Math.min(100, prev.memoryUsage + (Math.random() - 0.5) * 5)),
        diskUsage: Math.max(0, Math.min(100, prev.diskUsage + (Math.random() - 0.5) * 2)),
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricGaugeCard
        title="CPU Usage"
        value={metrics.cpuUsage}
        unit="%"
        icon="⚡"
        color={metrics.cpuUsage > 80 ? 'red' : metrics.cpuUsage > 50 ? 'yellow' : 'green'}
      />
      <MetricGaugeCard
        title="Memory Usage"
        value={metrics.memoryUsage}
        unit="%"
        icon="🧠"
        color={metrics.memoryUsage > 80 ? 'red' : metrics.memoryUsage > 50 ? 'yellow' : 'green'}
      />
      <MetricGaugeCard
        title="Disk Usage"
        value={metrics.diskUsage}
        unit="%"
        icon="💾"
        color={metrics.diskUsage > 80 ? 'red' : metrics.diskUsage > 50 ? 'yellow' : 'green'}
      />
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Active Agents</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {metrics.activeAgents}
              <span className="text-sm font-normal text-gray-500">
                /{metrics.totalAgents}
              </span>
            </p>
          </div>
          <div className="h-12 w-12 rounded-full bg-primary-100 flex items-center justify-center text-2xl">
            🤖
          </div>
        </div>
        <div className="mt-4 flex items-center justify-between text-sm">
          <div>
            <span className="text-gray-500">Tasks: </span>
            <span className="font-medium text-gray-900">{metrics.activeTasks}</span>
            <span className="text-gray-400"> active</span>
          </div>
          <div>
            <span className="font-medium text-green-600">{metrics.completedTasks}</span>
            <span className="text-gray-400"> done</span>
          </div>
        </div>
      </div>
    </div>
  );
}

interface MetricGaugeCardProps {
  title: string;
  value: number;
  unit: string;
  icon: string;
  color: 'green' | 'yellow' | 'red';
}

function MetricGaugeCard({ title, value, unit, icon, color }: MetricGaugeCardProps) {
  const colorClasses = {
    green: {
      bg: 'bg-green-100',
      text: 'text-green-600',
      stroke: 'stroke-green-500',
      fill: 'fill-green-500',
    },
    yellow: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-600',
      stroke: 'stroke-yellow-500',
      fill: 'fill-yellow-500',
    },
    red: {
      bg: 'bg-red-100',
      text: 'text-red-600',
      stroke: 'stroke-red-500',
      fill: 'fill-red-500',
    },
  };

  const colors = colorClasses[color];
  const circumference = 2 * Math.PI * 36;
  const strokeDashoffset = circumference - (value / 100) * circumference;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className={cn('text-2xl font-bold mt-1', colors.text)}>
            {value.toFixed(1)}
            <span className="text-sm font-normal text-gray-500">{unit}</span>
          </p>
        </div>
        <div className="relative h-16 w-16">
          <svg className="h-16 w-16 -rotate-90" viewBox="0 0 80 80">
            <circle
              cx="40"
              cy="40"
              r="36"
              fill="none"
              strokeWidth="6"
              className="stroke-gray-100"
            />
            <circle
              cx="40"
              cy="40"
              r="36"
              fill="none"
              strokeWidth="6"
              strokeLinecap="round"
              className={colors.stroke}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              style={{ transition: 'stroke-dashoffset 0.5s ease' }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center text-xl">
            {icon}
          </div>
        </div>
      </div>
    </div>
  );
}
