/**
 * ALVO Platform - Load Test (k6)
 * API performance and stress testing
 * 
 * Usage: k6 run load_test.js
 *        k6 run --vus 10 --duration 30s load_test.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const apiLatency = new Trend('api_latency', true);

// Test configuration
export const options = {
  stages: [
    // Ramp-up
    { duration: '10s', target: 5 },   // 10s to 5 users
    { duration: '20s', target: 10 },  // 20s to 10 users
    { duration: '30s', target: 20 },  // 30s to 20 users (stress)
    // Ramp-down
    { duration: '10s', target: 5 },   // 10s back to 5
    { duration: '5s', target: 0 },    // 5s to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    errors: ['rate<0.1'],              // Error rate under 10%
    api_latency: ['p(99)<1000'],       // 99th percentile under 1s
  },
};

// Configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Test data
const endpoints = [
  { name: 'health', method: 'GET', path: '/api/health' },
  { name: 'list_agents', method: 'GET', path: '/api/agents' },
  { name: 'list_tasks', method: 'GET', path: '/api/tasks' },
  { name: 'settings', method: 'GET', path: '/api/settings' },
  { name: 'free_models', method: 'GET', path: '/api/free-models' },
];

// Main test function
export default function () {
  // Pick a random endpoint
  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  
  const url = `${BASE_URL}${endpoint.path}`;
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    tags: { name: endpoint.name },
  };
  
  let response;
  const startTime = Date.now();
  
  // Make request
  if (endpoint.method === 'GET') {
    response = http.get(url, params);
  } else if (endpoint.method === 'POST') {
    response = http.post(url, JSON.stringify({}), params);
  }
  
  const duration = Date.now() - startTime;
  apiLatency.add(duration);
  
  // Check response
  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'has valid body': (r) => r.body && r.body.length > 0,
  });
  
  errorRate.add(!success);
  
  // Think time between requests
  sleep(Math.random() * 0.5 + 0.1);  // 0.1-0.6s
}

// Setup function (runs once before test)
export function setup() {
  console.log(`Starting load test against ${BASE_URL}`);
  
  // Verify API is accessible
  const healthCheck = http.get(`${BASE_URL}/api/health`);
  if (healthCheck.status !== 200) {
    throw new Error(`API not accessible: ${healthCheck.status}`);
  }
  
  return { startTime: Date.now() };
}

// Teardown function (runs once after test)
export function teardown(data) {
  const duration = (Date.now() - data.startTime) / 1000;
  console.log(`Load test completed in ${duration.toFixed(1)}s`);
}

// Handle summary (custom report)
export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    duration: data.state.testRunDurationMs / 1000,
    vus: {
      max: data.metrics.vus_max?.values?.max || 0,
      avg: data.metrics.vus?.values?.avg || 0,
    },
    requests: {
      total: data.metrics.http_reqs?.values?.count || 0,
      rate: data.metrics.http_reqs?.values?.rate || 0,
    },
    latency: {
      avg: data.metrics.http_req_duration?.values?.avg || 0,
      p95: data.metrics.http_req_duration?.values?.['p(95)'] || 0,
      p99: data.metrics.http_req_duration?.values?.['p(99)'] || 0,
    },
    errors: {
      rate: data.metrics.errors?.values?.rate || 0,
    },
    checks: {
      rate: data.metrics.checks?.values?.rate || 0,
    },
  };
  
  console.log('\n' + '='.repeat(60));
  console.log('LOAD TEST RESULTS');
  console.log('='.repeat(60));
  console.log(`Duration: ${summary.duration.toFixed(1)}s`);
  console.log(`Max VUs: ${summary.vus.max}`);
  console.log(`Total Requests: ${summary.requests.total}`);
  console.log(`Request Rate: ${summary.requests.rate.toFixed(2)}/s`);
  console.log(`Avg Latency: ${summary.latency.avg.toFixed(2)}ms`);
  console.log(`P95 Latency: ${summary.latency.p95.toFixed(2)}ms`);
  console.log(`P99 Latency: ${summary.latency.p99.toFixed(2)}ms`);
  console.log(`Error Rate: ${(summary.errors.rate * 100).toFixed(2)}%`);
  console.log(`Check Pass Rate: ${(summary.checks.rate * 100).toFixed(2)}%`);
  console.log('='.repeat(60));
  
  // Return JSON report
  return {
    'load_test_results.json': JSON.stringify(summary, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

// Text summary helper (k6 built-in)
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';
