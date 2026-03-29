# ALVO Platform Dashboard - Frontend

A React-based web dashboard for monitoring AI agents, token usage, and system performance.

## Features

### Token Usage Analytics
- Real-time token usage charts (Area/Bar charts)
- Time range filtering (1H, 6H, 24H, 7D, 30D)
- Usage breakdown by agent and AI model
- Cost tracking and projections

### Agent Status Monitoring
- Real-time agent status grid with live updates
- Status indicators (Active, Idle, Busy, Error, Offline)
- Token usage progress bars per agent
- Task completion tracking
- Click-to-expand agent details

### System Health Metrics
- CPU, Memory, and Disk usage gauges
- Active agent count
- Task statistics
- Animated real-time updates

### Recent Tasks
- Task list with status and priority
- Assigned agent information
- Time tracking

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **WebSocket** - Real-time updates (simulated in dev)

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
cd dashboard_project/frontend
npm install
```

### Development

```bash
npm start
```

The dashboard will be available at `http://localhost:3000`

### Production Build

```bash
npm run build
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Layout.tsx          # Main layout with header
│   │   ├── TokenUsageChart.tsx # Token usage over time
│   │   ├── AgentStatusGrid.tsx # Real-time agent cards
│   │   ├── SystemMetricsCards.tsx # CPU/Memory/Disk gauges
│   │   ├── ModelDistributionChart.tsx # Pie charts
│   │   └── RecentTasks.tsx     # Task list
│   ├── hooks/
│   │   └── useWebSocket.ts     # WebSocket hook
│   ├── pages/
│   │   └── Dashboard.tsx       # Main dashboard page
│   ├── services/
│   │   ├── mockData.ts         # Mock data for development
│   │   └── websocket.ts        # WebSocket service
│   ├── types/
│   │   └── index.ts            # TypeScript types
│   ├── utils/
│   │   └── index.ts            # Utility functions
│   ├── App.tsx
│   ├── index.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── postcss.config.js
```

## WebSocket Integration

The dashboard supports real-time updates via WebSocket:

```typescript
// Connect to backend WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  // Handle: agent_status, token_usage, system_metrics, heartbeat
};
```

### Message Types

- `agent_status` - Agent status changes
- `token_usage` - New token usage data
- `system_metrics` - System metric updates
- `heartbeat` - Agent heartbeat signals

## Customization

### Adding New Charts

1. Create component in `src/components/`
2. Import Recharts components
3. Add to Dashboard page

### Connecting Real Backend

1. Replace mock data in `src/services/mockData.ts`
2. Update WebSocket URL in `src/services/websocket.ts`
3. Add API calls using fetch or axios

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
