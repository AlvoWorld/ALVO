import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { TokenUsageSummary } from '../types';
import { formatNumber, formatCurrency } from '../utils';

interface ModelDistributionChartProps {
  data: TokenUsageSummary;
}

const COLORS = ['#0ea5e9', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'];

export function ModelDistributionChart({ data }: ModelDistributionChartProps) {
  const agentData = data.byAgent.map((item, index) => ({
    name: item.agentName,
    value: item.tokens,
    cost: item.cost,
    percentage: item.percentage,
    color: COLORS[index % COLORS.length],
  }));

  const modelData = data.byModel.map((item, index) => ({
    name: item.model,
    value: item.tokens,
    cost: item.cost,
    percentage: item.percentage,
    color: COLORS[index % COLORS.length],
  }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* By Agent */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-1">Usage by Agent</h3>
        <p className="text-sm text-gray-500 mb-4">Token distribution across agents</p>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={agentData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={2}
                dataKey="value"
              >
                {agentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
                        <p className="font-medium text-gray-900">{data.name}</p>
                        <p className="text-sm text-gray-600">
                          {formatNumber(data.value)} tokens
                        </p>
                        <p className="text-sm text-gray-600">
                          {formatCurrency(data.cost)}
                        </p>
                        <p className="text-sm text-primary-600 font-medium">
                          {data.percentage.toFixed(1)}%
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="space-y-2 mt-4">
          {data.byAgent.slice(0, 5).map((item, index) => (
            <div key={item.agentId} className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div
                  className="h-3 w-3 rounded-full"
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                />
                <span className="text-sm text-gray-700">{item.agentName}</span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-500">
                  {formatNumber(item.tokens)}
                </span>
                <span className="text-sm font-medium text-gray-900 w-12 text-right">
                  {item.percentage.toFixed(1)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* By Model */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-1">Usage by Model</h3>
        <p className="text-sm text-gray-500 mb-4">Token distribution across AI models</p>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={modelData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={2}
                dataKey="value"
              >
                {modelData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
                        <p className="font-medium text-gray-900">{data.name}</p>
                        <p className="text-sm text-gray-600">
                          {formatNumber(data.value)} tokens
                        </p>
                        <p className="text-sm text-gray-600">
                          {formatCurrency(data.cost)}
                        </p>
                        <p className="text-sm text-primary-600 font-medium">
                          {data.percentage.toFixed(1)}%
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="space-y-2 mt-4">
          {data.byModel.map((item, index) => (
            <div key={item.model} className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div
                  className="h-3 w-3 rounded-full"
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                />
                <span className="text-sm text-gray-700">{item.model}</span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-500">
                  {formatNumber(item.tokens)}
                </span>
                <span className="text-sm font-medium text-gray-900 w-12 text-right">
                  {item.percentage.toFixed(1)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
