import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { TokenUsage } from '../types/agent';

interface TokenUsageChartProps {
  data: TokenUsage[];
  timeRange: '1h' | '24h' | '7d' | '30d';
}

export const TokenUsageChart: React.FC<TokenUsageChartProps> = ({ data, timeRange }) => {
  const formatXAxis = (tickItem: string) => {
    const date = new Date(tickItem);
    switch (timeRange) {
      case '1h':
        return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
      case '24h':
        return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
      case '7d':
        return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
      case '30d':
        return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
      default:
        return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    }
  };

  const aggregatedData = data.reduce((acc, curr) => {
    const key = curr.timestamp;
    if (!acc[key]) {
      acc[key] = {
        timestamp: key,
        totalTokensUsed: 0,
        totalCost: 0,
        count: 0
      };
    }
    acc[key].totalTokensUsed += curr.tokensUsed;
    acc[key].totalCost += curr.cost;
    acc[key].count += 1;
    return acc;
  }, {} as Record<string, any>);

  const chartData = Object.values(aggregatedData).sort((a: any, b: any) => 
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Использование токенов</h3>
        <p className="text-sm text-gray-600">
          Динамика использования токенов за {timeRange === '1h' ? 'час' : timeRange === '24h' ? 'сутки' : timeRange === '7d' ? 'неделю' : 'месяц'}
        </p>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={formatXAxis}
            tick={{ fontSize: 12 }}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip 
            labelFormatter={(value) => `Время: ${formatXAxis(value)}`}
            formatter={(value: number, name: string) => [
              name === 'totalTokensUsed' ? `${value.toLocaleString()} токенов` : `$${value.toFixed(2)}`,
              name === 'totalTokensUsed' ? 'Токены' : 'Стоимость'
            ]}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="totalTokensUsed"
            stackId="1"
            stroke="#3B82F6"
            fill="#3B82F6"
            fillOpacity={0.6}
            name="Токены"
          />
          <Area
            type="monotone"
            dataKey="totalCost"
            stackId="2"
            stroke="#10B981"
            fill="#10B981"
            fillOpacity={0.6}
            name="Стоимость ($)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};