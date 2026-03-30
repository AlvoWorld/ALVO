// AXIOM API Integration
const API = {
  base: '',
  async get(path) {
    try { return await fetch(this.base + path).then(r => r.json()); }
    catch(e) { console.error('API Error:', e); return null; }
  },
  async post(path, data) {
    try { return await fetch(this.base + path, {
      method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
    }).then(r => r.json()); }
    catch(e) { console.error('API Error:', e); return null; }
  }
};

// Transform API data to design format
async function loadFromAPI() {
  const [health, agents, tasks, stats, runs, failover] = await Promise.all([
    API.get('/api/health'),
    API.get('/api/agents'),
    API.get('/api/tasks'),
    API.get('/api/stats'),
    API.get('/api/runs'),
    API.get('/api/failover/status')
  ]);

  // Transform agents
  if (agents) {
    window._apiAgents = agents.map(a => ({
      id: a.id,
      name: a.name,
      model: a.model,
      status: a.status === 'running' ? 'running' : a.status === 'error' ? 'error' : 'idle',
      tokens_today: 0,
      cost_usd: 0,
      adapter: 'openrouter'
    }));
  }

  // Transform tasks
  if (tasks) {
    window._apiTasks = tasks.map(t => ({
      id: t.id,
      title: t.title,
      status: t.status === 'done' ? 'done' : t.status === 'pending' ? 'todo' : 'doing',
      priority: 'normal',
      assigned_to: t.assigned_to_name || '—',
      created_at: t.created_at,
      description: t.description || ''
    }));
  }

  // Transform stats
  if (stats) {
    window._apiStats = {
      daily_limit: 10.00,
      today_spend: stats.total_cost_usd || 0,
      tokens: stats.total_tokens_in || 0,
      budget_pct: Math.min(100, ((stats.total_cost_usd || 0) / 10.00) * 100),
      roas: 1.53,
      agents_total: stats.agents_total || 0,
      agents_running: stats.agents_running || 0,
      tasks_total: stats.tasks_total || 0,
      tasks_done: stats.tasks_done || 0,
      success_rate: stats.success_rate || 0
    };
  }

  // Transform runs
  if (runs) {
    window._apiRuns = runs.map(r => ({
      agent: r.agent_name || '—',
      status: r.status === 'completed' ? 'OK' : r.status === 'failed' ? 'ERR' : 'RUN',
      time: (r.finished_at || '').slice(11, 19),
      tokens: `${((r.input_tokens || 0) / 1000).toFixed(0)}K`,
      cost: `$${(r.cost_usd || 0).toFixed(4)}`
    }));
  }

  return { health, agents, tasks, stats, runs, failover };
}

// Auto-refresh
let _refreshInterval;
function startAutoRefresh(intervalMs = 30000) {
  if (_refreshInterval) clearInterval(_refreshInterval);
  _refreshInterval = setInterval(loadFromAPI, intervalMs);
}

// Init
loadFromAPI().then(() => {
  console.log('AXIOM API loaded');
  startAutoRefresh();
});
