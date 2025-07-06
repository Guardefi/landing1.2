import { apiClient } from "@/lib/api-client";

interface ServiceTest {
  name: string;
  endpoint: string;
  expectedResponse?: string;
  testData?: any;
}

const API_TESTS: ServiceTest[] = [
  { name: "Main API Health", endpoint: "/health" },
  { name: "Scanner Health", endpoint: "/api/scanner/health" },
  { name: "Honeypot Health", endpoint: "/api/honeypot/health" },
  { name: "Mempool Health", endpoint: "/api/mempool/health" },
  { name: "Bridge Health", endpoint: "/api/bridge/health" },
  { name: "Bytecode Health", endpoint: "/api/bytecode/health" },
  { name: "Wallet Health", endpoint: "/api/wallet/health" },
  { name: "Time Machine Health", endpoint: "/api/time-machine/health" },
  { name: "Quantum Health", endpoint: "/api/quantum/health" },
];

export interface TestResult {
  name: string;
  status: "success" | "error" | "timeout";
  responseTime: number;
  error?: string;
  response?: any;
}

export async function testApiConnection(
  test: ServiceTest,
  timeout = 5000,
): Promise<TestResult> {
  const startTime = Date.now();

  try {
    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error("Request timeout")), timeout),
    );

    const apiPromise = test.testData
      ? apiClient.post(test.endpoint, test.testData)
      : apiClient.get(test.endpoint);

    const response = await Promise.race([apiPromise, timeoutPromise]);
    const responseTime = Date.now() - startTime;

    return {
      name: test.name,
      status: "success",
      responseTime,
      response,
    };
  } catch (error: any) {
    const responseTime = Date.now() - startTime;

    return {
      name: test.name,
      status: error.message === "Request timeout" ? "timeout" : "error",
      responseTime,
      error: error.message || "Unknown error",
    };
  }
}

export async function testAllApis(): Promise<TestResult[]> {
  console.log("🔍 Testing API connections...");

  const results = await Promise.all(
    API_TESTS.map((test) => testApiConnection(test)),
  );

  const successCount = results.filter((r) => r.status === "success").length;
  const totalCount = results.length;

  console.log(
    `✅ API Test Results: ${successCount}/${totalCount} services online`,
  );
  results.forEach((result) => {
    const emoji = result.status === "success" ? "✅" : "❌";
    console.log(
      `${emoji} ${result.name}: ${result.status} (${result.responseTime}ms)`,
    );
    if (result.error) {
      console.log(`   Error: ${result.error}`);
    }
  });

  return results;
}

// Specific service tests
export async function testScannerConnection(): Promise<TestResult> {
  return testApiConnection({
    name: "Scanner Service",
    endpoint: "/api/scanner/health",
  });
}

export async function testHoneypotConnection(): Promise<TestResult> {
  return testApiConnection({
    name: "Honeypot Service",
    endpoint: "/api/honeypot/health",
  });
}

export async function testMempoolConnection(): Promise<TestResult> {
  return testApiConnection({
    name: "Mempool Service",
    endpoint: "/api/mempool/health",
  });
}

// Test with sample data
export async function testScannerFunctionality(): Promise<TestResult> {
  return testApiConnection({
    name: "Scanner Functionality",
    endpoint: "/api/scanner/scan",
    testData: {
      target_type: "contract_address",
      target: "0x1234567890123456789012345678901234567890",
      scan_type: "quick",
    },
  });
}

export async function testHoneypotFunctionality(): Promise<TestResult> {
  return testApiConnection({
    name: "Honeypot Functionality",
    endpoint: "/api/honeypot/analyze",
    testData: {
      address: "0x1234567890123456789012345678901234567890",
    },
  });
}

// Get service status summary
export function getServiceStatusSummary(results: TestResult[]) {
  const online = results.filter((r) => r.status === "success").length;
  const offline = results.filter((r) => r.status === "error").length;
  const timeout = results.filter((r) => r.status === "timeout").length;

  return {
    total: results.length,
    online,
    offline,
    timeout,
    averageResponseTime:
      results
        .filter((r) => r.status === "success")
        .reduce((sum, r) => sum + r.responseTime, 0) / (online || 1),
  };
}

// Auto-test on module load for development
if (import.meta.env.DEV && import.meta.env.VITE_DEBUG_MODE === "true") {
  setTimeout(() => {
    testAllApis().catch(console.error);
  }, 2000);
}

export default {
  testAllApis,
  testApiConnection,
  testScannerConnection,
  testHoneypotConnection,
  testMempoolConnection,
  testScannerFunctionality,
  testHoneypotFunctionality,
  getServiceStatusSummary,
};
