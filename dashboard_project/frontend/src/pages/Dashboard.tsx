import React, { useState, useEffect } from 'react';
import { Layout } from '../components/Layout';
import { TokenUsageChart } from '../components/TokenUsageChart';
import { AgentStatusGrid } from '../components/AgentStatusGrid';
import { SystemMetricsCards } from '../components/SystemMetricsCards';
import { ModelDistributionChart } from '../components/ModelDistributionChart';
import { RecentTasks } from '../components/RecentTasks';
import {
  mockAgents,
  mockTokenUsageSummary,
  mockTasks,
  mockSystemMetrics,
} from '../services/mockData';
import { formatNumber, formatCurrency } from '../utils';

export default function Dashboard() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <Layout>
        <LoadingSkeleton />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-8">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-sm text-gray-500 mt-1">
              Monitor your AI agents, token usage, and system performance
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex items-center space-x-3">
            <span className="text-sm text-gray-500">Last updated: just now</span>
            <button className="px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors">
              Refresh
            </button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <QuickStat
            label="Total Tokens"
            value={formatNumber(mockTokenUsageSummary.totalTokens)}
            change="+12.5%"
            positive
          />
          <QuickStat
            label="Total Cost"
            value={formatCurrency(mockTokenUsageSummary.totalCost)}
            change="+8.3%"
            positive={false}
          />
          <QuickStat
            label="Active Agents"
            value={`${mockSystemMetrics.activeAgents}/${mockSystemMetrics.totalAgents}`}
            change="+1"
            positive
          />
          <QuickStat
            label="Completed Tasks"
            value={formatNumber(mockSystemMetrics.completedTasks)}
            change="+24"
            positive
          />
        </div>

        {/* System Metrics */}
        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">System Health</h2>
          <SystemMetricsCards metrics={mockSystemMetrics} />
        </section>

        {/* Token Usage Chart */}
        <section>
          <TokenUsageChart data={mockTokenUsageSummary} />
        </section>

        {/* Agent Status */}
        <section>
          <AgentStatusGrid agents={mockAgents} />
        </section>

        {/* Distribution Charts */}
        <section>
          <ModelDistributionChart data={mockTokenUsageSummary} />
        </section>

        {/* Recent Tasks */}
        <section>
          <RecentTasks tasks={mockTasks} agents={mockAgents} />
        </section>
      </div>
    </Layout>
  );
}

function QuickStat({
  label,
  value,
  change,
  positive,
}: {
  label: string;
  value: string;
  change: string;
  positive: boolean;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-xl font-bold text-gray-900 mt-1">{value}</p>
      <p
        className={`text-xs mt-1 ${
          positive ? 'text-green-600' : 'text-orange-600'
        }`}
      >
        {change} from last period
      </p>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="flex justify-between items-center">
        <div>
          <div className="h-8 w-48 bg-gray-200 rounded" />
          <div className="h-4 w-64 bg-gray-200 rounded mt-2" />
        </div>
        <div className="h-10 w-24 bg-gray-200 rounded-lg" />
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="h-4 w-20 bg-gray-200 rounded" />
            <div className="h-6 w-24 bg-gray-200 rounded mt-2" />
            <div className="h-3 w-16 bg-gray-200 rounded mt-2" />
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="bg-white rounded-xl border border-gray-200 p-6 h-32"
          />
        ))}
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 h-96" />
    </div>
  );
}
