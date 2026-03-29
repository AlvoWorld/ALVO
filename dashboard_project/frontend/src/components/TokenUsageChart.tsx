import React, { useState, useMemo } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend,
} from 'recharts';
import { TokenUsageSummary, TimeRange } from '../types';
import { formatNumber, formatCurrency, cn } from '../utils';

interface TokenUsageChartProps {
  data: TokenUsageSummary;
}

export function TokenUsageChart({ data }: TokenUsageChartProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>('24h');
  const [chartType, setChartType] = useState<'area' | 'bar'>('area');

  const chartData = useMemo(() => {
    if (timeRange === '1h' || timeRange === '6h' || timeRange === '24h') {
      return data.hourlyUsage.slice(-24).map((item) => ({
        time: new Date(item.hour).toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
        }),
        tokens: item.tokens,
        cost: parseFloat(item.cost.toFixed(4)),
      }));
    }
    return data.dailyUsage.map((item) => ({
      time: new Date(item.date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      }),
      tokens: item.tokens,
      cost: parseFloat(item.cost.toFixed(4)),
    }));
  }, [data, timeRange]);

  const timeRanges: { value: TimeRange; label: string }[] = [
    { value: '1h', label: '1H' },
    { value: '6h', label: '6H' },
    { value: '24h', label: '24H' },
    { value: '7d', label: '7D' },
    { value: '30d', label: '30D' },
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Token Usage Over Time</h3>
          <p className="text-sm text-gray-500 mt-1">
            Total: {formatNumber(data.totalTokens)} tokens ({formatCurrency(data.totalCost)})
          </p>
        </div>
        <div className="flex items-center space-x-2 mt-4 sm:mt-0">
          <div className="flex bg-gray-100 rounded-lg p-1">
            {timeRanges.map((range) => (
              <button
                key={range.value}
                onClick={() => setTimeRange(range.value)}
                className={cn(
                  'px-3 py-1 text-xs font-medium rounded-md transition-colors',
                  timeRange === range.value
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                {range.label}
              </button>
            ))}
          </div>
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setChartType('area')}
              className={cn(
                'px-3 py-1 text-xs font-medium rounded-md transition-colors',
                chartType === 'area'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600'
              )}
            >
              Area
            </button>
            <button
              onClick={() => setChartType('bar')}
              className={cn(
                'px-3 py-1 text-xs font-medium rounded-md transition-colors',
                chartType === 'bar'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600'
              )}
            >
              Bar
            </button>
          </div>
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === 'area' ? (
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorTokens" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="time"
                tick={{ fontSize: 12, fill: '#6b7280' }}
                tickLine={false}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <YAxis
                yAxisId="left"
                tick={{ fontSize: 12, fill: '#6b7280' }}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => formatNumber(value)}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                tick={{ fontSize: 12, fill: '#6b7280' }}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `$${value.toFixed(2)}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                }}
                formatter={(value: number, name: string) => [
                  name === 'tokens' ? formatNumber(value) : formatCurrency(value),
                  name === 'tokens' ? 'Tokens' : 'Cost',
                ]}
              />
              <Area
                yAxisId="left"
                type="monotone"
                dataKey="tokens"
                stroke="#0ea5e9"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorTokens)"
              />
              <Area
                yAxisId="right"
                type="monotone"
                dataKey="cost"
                stroke="#22c55e"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorCost)"
              />
            </AreaChart>
          ) : (
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="time"
                tick={{ fontSize: 12, fill: '#6b7280' }}
                tickLine={false}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <YAxis
                tick={{ fontSize: 12, fill: '#6b7280' }}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => formatNumber(value)}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
                formatter={(value: number, name: string) => [
                  name === 'tokens' ? formatNumber(value) : formatCurrency(value),
                  name === 'tokens' ? 'Tokens' : 'Cost',
                ]}
              />
              <Legend />
              <Bar dataKey="tokens" fill="#0ea5e9" radius={[4, 4, 0, 0]} name="Tokens" />
              <Bar dataKey="cost" fill="#22c55e" radius={[4, 4, 0, 0]} name="Cost ($)" />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
