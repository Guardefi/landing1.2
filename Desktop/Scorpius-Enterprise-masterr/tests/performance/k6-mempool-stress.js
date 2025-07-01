/**
 * K6 Load Test - Mempool Stream Stress Testing
 * Tests mempool transaction stream processing under various load conditions
 * Measures RPS vs CPU utilization for HPA scaling decisions
 */

import http from 'k6/http';
import ws from 'k6/ws';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend, Gauge } from 'k6/metrics';
import { SharedArray } from 'k6/data';

// Custom metrics
const mempoolTransactions = new Counter('mempool_transactions_total');
const mempoolErrors = new Counter('mempool_errors_total');
const mempoolLatency = new Trend('mempool_latency_ms');
const mempoolThroughput = new Rate('mempool_throughput_rps');
const websocketConnections = new Gauge('websocket_connections_active');
const cpuUtilization = new Gauge('cpu_utilization_percent');
const memoryUsage = new Gauge('memory_usage_mb');

// Test data - realistic transaction patterns
const transactionTemplates = new SharedArray('transactions', function () {
  return [
    {
      type: 'transfer',
      from: '0x742d35cc6635c0532925a3b8d5c9c1c8a6c2e5f1',
      to: '0x8ba1f109551bd432803012645hac136c34c8c8c2',
      value: '1000000000000000000', // 1 ETH
      gasPrice: '20000000000', // 20 Gwei
      gasLimit: '21000'
    },
    {
      type: 'contract_call',
      to: '0xa0b86a33e6c1b8c4d5e6f7a8b9c0d1e2f3a4b5c6',
      data: '0xa9059cbb000000000000000000000000742d35cc6635c0532925a3b8d5c9c1c8a6c2e5f1000000000000000000000000000000000000000000000000000000000000000a',
      gasPrice: '25000000000', // 25 Gwei
      gasLimit: '100000'
    },
    {
      type: 'swap',
      to: '0x7a250d5630b4cf539739df2c5dacb4c659f2488d', // Uniswap V2 Router
      value: '100000000000000000', // 0.1 ETH
      gasPrice: '30000000000', // 30 Gwei
      gasLimit: '200000'
    },
    {
      type: 'nft_mint',
      to: '0x495f947276749ce646f68ac8c248420045cb7b5e',
      gasPrice: '50000000000', // 50 Gwei
      gasLimit: '300000'
    },
    {
      type: 'defi_interaction',
      to: '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984',
      value: '500000000000000000', // 0.5 ETH
      gasPrice: '40000000000', // 40 Gwei
      gasLimit: '250000'
    }
  ];
});

// Load test configuration
export const options = {
  scenarios: {
    // Baseline load - normal operation
    baseline: {
      executor: 'constant-vus',
      vus: 10,
      duration: '2m',
      tags: { scenario: 'baseline' },
      env: { SCENARIO: 'baseline' }
    },
    
    // Ramp up test - gradual load increase
    ramp_up: {
      executor: 'ramping-vus',
      startVUs: 10,
      stages: [
        { duration: '1m', target: 50 },
        { duration: '2m', target: 100 },
        { duration: '2m', target: 200 },
        { duration: '1m', target: 300 },
        { duration: '2m', target: 300 }, // Sustained peak
        { duration: '2m', target: 0 }
      ],
      tags: { scenario: 'ramp_up' },
      env: { SCENARIO: 'ramp_up' }
    },
    
    // Spike test - sudden load spikes
    spike: {
      executor: 'ramping-vus',
      startVUs: 20,
      stages: [
        { duration: '30s', target: 20 },
        { duration: '10s', target: 500 }, // Sudden spike
        { duration: '1m', target: 500 },
        { duration: '10s', target: 20 },
        { duration: '30s', target: 20 }
      ],
      tags: { scenario: 'spike' },
      env: { SCENARIO: 'spike' }
    },
    
    // Soak test - extended duration
    soak: {
      executor: 'constant-vus',
      vus: 100,
      duration: '10m',
      tags: { scenario: 'soak' },
      env: { SCENARIO: 'soak' }
    },
    
    // WebSocket stream test
    websocket_stream: {
      executor: 'constant-vus',
      vus: 50,
      duration: '5m',
      exec: 'websocketTest',
      tags: { scenario: 'websocket' },
      env: { SCENARIO: 'websocket' }
    }
  },
  
  thresholds: {
    // Performance thresholds
    'http_req_duration': ['p(95)<2000'], // 95% of requests under 2s
    'http_req_failed': ['rate<0.05'], // Error rate under 5%
    'mempool_latency_ms': ['p(90)<1000'], // 90% of mempool operations under 1s
    'mempool_errors_total': ['count<100'], // Less than 100 total errors
    'websocket_connections_active': ['value>0'], // WebSocket connections active
    
    // Resource utilization thresholds
    'cpu_utilization_percent': ['value<80'], // CPU under 80%
    'memory_usage_mb': ['value<4096'], // Memory under 4GB
    
    // Throughput thresholds
    'mempool_throughput_rps': ['rate>10'], // At least 10 RPS throughput
  }
};

// Base URL configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const WS_URL = __ENV.WS_URL || 'ws://localhost:8000';

// Authentication token
let authToken = null;

export function setup() {
  // Authenticate and get token
  const loginResponse = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
    username: __ENV.TEST_USERNAME || 'test@scorpius.com',
    password: __ENV.TEST_PASSWORD || 'testpassword'
  }), {
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (loginResponse.status === 200) {
    authToken = loginResponse.json('access_token');
    console.log('Authentication successful');
  } else {
    console.error('Authentication failed:', loginResponse.status);
  }
  
  return { authToken };
}

export default function (data) {
  const scenario = __ENV.SCENARIO || 'baseline';
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${data.authToken}`
  };
  
  // Simulate mempool transaction processing
  testMempoolAPI(headers, scenario);
  
  // Add some realistic think time
  sleep(Math.random() * 2 + 0.5); // 0.5-2.5 seconds
}

function testMempoolAPI(headers, scenario) {
  const startTime = Date.now();
  
  // Test mempool status endpoint
  const statusResponse = http.get(`${BASE_URL}/api/mempool/status`, { headers });
  
  check(statusResponse, {
    'mempool status is 200': (r) => r.status === 200,
    'mempool status has pending count': (r) => r.json('pending_transactions') !== undefined,
  });
  
  if (statusResponse.status !== 200) {
    mempoolErrors.add(1);
    return;
  }
  
  // Submit transaction to mempool
  const transaction = transactionTemplates[Math.floor(Math.random() * transactionTemplates.length)];
  const txPayload = {
    ...transaction,
    nonce: Math.floor(Math.random() * 1000000),
    timestamp: Date.now(),
    hash: generateTransactionHash()
  };
  
  const submitResponse = http.post(
    `${BASE_URL}/api/mempool/submit`,
    JSON.stringify(txPayload),
    { headers }
  );
  
  const submitSuccess = check(submitResponse, {
    'submit transaction is 200': (r) => r.status === 200,
    'submit returns transaction hash': (r) => r.json('hash') !== undefined,
  });
  
  if (submitSuccess) {
    mempoolTransactions.add(1);
    mempoolThroughput.add(1);
    
    const txHash = submitResponse.json('hash');
    
    // Query transaction status
    const queryResponse = http.get(
      `${BASE_URL}/api/mempool/transaction/${txHash}`,
      { headers }
    );
    
    check(queryResponse, {
      'query transaction is 200': (r) => r.status === 200,
      'query returns transaction data': (r) => r.json('status') !== undefined,
    });
    
    // Test MEV analysis if available
    if (Math.random() < 0.3) { // 30% of transactions
      const mevResponse = http.post(
        `${BASE_URL}/api/mempool/analyze-mev`,
        JSON.stringify({ transaction_hash: txHash }),
        { headers }
      );
      
      check(mevResponse, {
        'MEV analysis completes': (r) => r.status === 200 || r.status === 202,
      });
    }
    
  } else {
    mempoolErrors.add(1);
  }
  
  // Record latency
  const latency = Date.now() - startTime;
  mempoolLatency.add(latency);
  
  // Simulate different load patterns based on scenario
  if (scenario === 'spike' && Math.random() < 0.1) {
    // 10% chance of batch operation during spike
    batchTransactionTest(headers);
  }
  
  // Collect system metrics periodically
  if (Math.random() < 0.05) { // 5% of requests
    collectSystemMetrics(headers);
  }
}

export function websocketTest(data) {
  const headers = {
    'Authorization': `Bearer ${data.authToken}`
  };
  
  const url = `${WS_URL}/api/mempool/stream`;
  
  const response = ws.connect(url, { headers }, function (socket) {
    websocketConnections.add(1);
    
    socket.on('open', function () {
      console.log('WebSocket connection opened');
      
      // Subscribe to mempool updates
      socket.send(JSON.stringify({
        type: 'subscribe',
        channels: ['transactions', 'blocks', 'mev_opportunities']
      }));
    });
    
    socket.on('message', function (message) {
      const data = JSON.parse(message);
      
      check(data, {
        'message has type': (d) => d.type !== undefined,
        'message has valid timestamp': (d) => d.timestamp !== undefined,
      });
      
      // Simulate processing different message types
      switch (data.type) {
        case 'transaction':
          mempoolTransactions.add(1);
          break;
        case 'block':
          // Process block data
          break;
        case 'mev_opportunity':
          // Process MEV opportunity
          break;
      }
    });
    
    socket.on('error', function (e) {
      console.error('WebSocket error:', e);
      mempoolErrors.add(1);
    });
    
    socket.on('close', function () {
      console.log('WebSocket connection closed');
      websocketConnections.add(-1);
    });
    
    // Keep connection alive for test duration
    socket.setTimeout(function () {
      socket.close();
    }, 30000); // 30 seconds
    
  });
  
  check(response, {
    'websocket connection established': (r) => r && r.status === 101,
  });
}

function batchTransactionTest(headers) {
  // Test batch transaction submission
  const batchSize = Math.floor(Math.random() * 10) + 5; // 5-14 transactions
  const batch = [];
  
  for (let i = 0; i < batchSize; i++) {
    const transaction = transactionTemplates[Math.floor(Math.random() * transactionTemplates.length)];
    batch.push({
      ...transaction,
      nonce: Math.floor(Math.random() * 1000000) + i,
      timestamp: Date.now(),
      hash: generateTransactionHash()
    });
  }
  
  const batchResponse = http.post(
    `${BASE_URL}/api/mempool/batch-submit`,
    JSON.stringify({ transactions: batch }),
    { headers }
  );
  
  const batchSuccess = check(batchResponse, {
    'batch submit is 200': (r) => r.status === 200,
    'batch returns all hashes': (r) => r.json('hashes') && r.json('hashes').length === batchSize,
  });
  
  if (batchSuccess) {
    mempoolTransactions.add(batchSize);
  } else {
    mempoolErrors.add(1);
  }
}

function collectSystemMetrics(headers) {
  // Get system metrics from monitoring endpoint
  const metricsResponse = http.get(`${BASE_URL}/api/mempool/metrics`, { headers });
  
  if (metricsResponse.status === 200) {
    const metrics = metricsResponse.json();
    
    if (metrics.cpu_usage_percent !== undefined) {
      cpuUtilization.add(metrics.cpu_usage_percent);
    }
    
    if (metrics.memory_usage_mb !== undefined) {
      memoryUsage.add(metrics.memory_usage_mb);
    }
    
    // Additional custom metrics
    if (metrics.active_connections !== undefined) {
      websocketConnections.add(metrics.active_connections);
    }
  }
}

function generateTransactionHash() {
  // Generate a realistic-looking transaction hash
  const chars = '0123456789abcdef';
  let hash = '0x';
  for (let i = 0; i < 64; i++) {
    hash += chars[Math.floor(Math.random() * chars.length)];
  }
  return hash;
}

export function teardown(data) {
  console.log('Load test completed');
  
  // Optional: Clean up test data
  if (data.authToken) {
    const cleanupResponse = http.post(
      `${BASE_URL}/api/mempool/cleanup-test-data`,
      null,
      {
        headers: {
          'Authorization': `Bearer ${data.authToken}`
        }
      }
    );
    
    if (cleanupResponse.status === 200) {
      console.log('Test data cleanup completed');
    }
  }
}

// Export custom summary for detailed reporting
export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    test_duration: data.state.testRunDurationMs,
    scenarios: {},
    metrics: {},
    thresholds: {}
  };
  
  // Process scenario results
  Object.keys(data.metrics).forEach(metricName => {
    const metric = data.metrics[metricName];
    summary.metrics[metricName] = {
      count: metric.values.count || 0,
      rate: metric.values.rate || 0,
      avg: metric.values.avg || 0,
      min: metric.values.min || 0,
      max: metric.values.max || 0,
      p90: metric.values['p(90)'] || 0,
      p95: metric.values['p(95)'] || 0,
      p99: metric.values['p(99)'] || 0
    };
  });
  
  // Process threshold results
  Object.keys(data.thresholds).forEach(thresholdName => {
    const threshold = data.thresholds[thresholdName];
    summary.thresholds[thresholdName] = {
      passed: !threshold.failed,
      values: threshold.values
    };
  });
  
  return {
    'stdout': JSON.stringify(summary, null, 2),
    'mempool-load-test-results.json': JSON.stringify(summary, null, 2),
    'mempool-load-test-summary.html': generateHTMLReport(summary)
  };
}

function generateHTMLReport(summary) {
  return `
<!DOCTYPE html>
<html>
<head>
    <title>Mempool Load Test Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f4f4f4; padding: 15px; border-radius: 5px; }
        .metric { margin: 10px 0; padding: 10px; border-left: 4px solid #007cba; }
        .passed { border-left-color: #28a745; }
        .failed { border-left-color: #dc3545; }
        .table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .table th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Mempool Stream Load Test Results</h1>
        <p><strong>Test Duration:</strong> ${(summary.test_duration / 1000 / 60).toFixed(2)} minutes</p>
        <p><strong>Timestamp:</strong> ${summary.timestamp}</p>
    </div>
    
    <h2>Key Metrics</h2>
    <table class="table">
        <tr>
            <th>Metric</th>
            <th>Count/Rate</th>
            <th>Average</th>
            <th>P90</th>
            <th>P95</th>
            <th>P99</th>
        </tr>
        ${Object.keys(summary.metrics).map(name => `
        <tr>
            <td>${name}</td>
            <td>${summary.metrics[name].count || summary.metrics[name].rate}</td>
            <td>${summary.metrics[name].avg.toFixed(2)}</td>
            <td>${summary.metrics[name].p90.toFixed(2)}</td>
            <td>${summary.metrics[name].p95.toFixed(2)}</td>
            <td>${summary.metrics[name].p99.toFixed(2)}</td>
        </tr>
        `).join('')}
    </table>
    
    <h2>Threshold Results</h2>
    ${Object.keys(summary.thresholds).map(name => `
    <div class="metric ${summary.thresholds[name].passed ? 'passed' : 'failed'}">
        <strong>${name}:</strong> ${summary.thresholds[name].passed ? 'PASSED' : 'FAILED'}
    </div>
    `).join('')}
</body>
</html>
  `;
}
