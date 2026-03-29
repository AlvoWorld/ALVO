export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(2) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
};

export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 4,
    maximumFractionDigits: 4,
  }).format(amount);
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

export const formatTime = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date);
};

export const getTimeAgo = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
};

export const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    active: 'text-green-500',
    idle: 'text-yellow-500',
    busy: 'text-blue-500',
    error: 'text-red-500',
    offline: 'text-gray-500',
    pending: 'text-gray-500',
    in_progress: 'text-blue-500',
    completed: 'text-green-500',
    blocked: 'text-red-500',
  };
  return colors[status] || 'text-gray-500';
};

export const getStatusBgColor = (status: string): string => {
  const colors: Record<string, string> = {
    active: 'bg-green-500',
    idle: 'bg-yellow-500',
    busy: 'bg-blue-500',
    error: 'bg-red-500',
    offline: 'bg-gray-500',
    pending: 'bg-gray-400',
    in_progress: 'bg-blue-500',
    completed: 'bg-green-500',
    blocked: 'bg-red-500',
  };
  return colors[status] || 'bg-gray-500';
};

export const getPriorityColor = (priority: string): string => {
  const colors: Record<string, string> = {
    low: 'text-gray-500 bg-gray-100',
    medium: 'text-blue-500 bg-blue-100',
    high: 'text-orange-500 bg-orange-100',
    critical: 'text-red-500 bg-red-100',
  };
  return colors[priority] || 'text-gray-500 bg-gray-100';
};

export const cn = (...classes: (string | boolean | undefined | null)[]): string => {
  return classes.filter(Boolean).join(' ');
};
