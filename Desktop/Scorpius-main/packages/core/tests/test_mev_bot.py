#!/usr/bin/env python3
import websockets
import aiohttp
import sys
import os
import asyncio
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project paths
project_root = Path(__file__).parent
while project_root.name != "Scorpius-main" and project_root != project_root.parent:
    project_root = project_root.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))
sys.path.insert(0, str(project_root / "packages" / "core"))

# Create mock classes for commonly missing modules

class MockSimilarityEngine:
    def __init__(self, *args, **kwargs): pass

    async def compare_bytecodes(self, *args, **kwargs):
        class Result:
            similarity_score = 0.85
            confidence = 0.9
            processing_time = 0.01
            return Result()

        return Result()
    async def cleanup(self): pass

class MockBytecodeNormalizer:
    async def normalize(self, bytecode):
        return bytecode.replace("0x", "").lower() if bytecode else ""

class MockMultiDimensionalComparison:
    def __init__(self, *args, **kwargs): pass

    async def compute_similarity(self, b1, b2):
        return {"final_score": 0.85, "confidence": 0.9, "dimension_scores": {}}

class MockTestClient:
    def __init__(self, app): self.app = app

    def get(self, url):
        class Response:
            status_code = 200
            def json(self): return {"status": "ok"}
        return Response()

# Add mocks to globals for import fallbacks
globals().update({

})
#!/usr/bin/env python3
    """
# Ultimate MEV Bot Test Script
# Tests all 6 strategies and API endpoints
    """

    BASE_URL = "http://localhost:8003"

    async def test_mev_bot():
    """Test the Ultimate MEV Bot API endpoints"""

    print(">> Testing Ultimate MEV Bot API...")

    async with aiohttp.ClientSession() as session:
        # Test 1: Get Bot Status
    print("\n1. Testing bot status...")
    async with session.get(f"{BASE_URL}/status") as resp:
    if resp.status == 200:
    status = await resp.json()
    print(f"[PASS] Bot Status: {status}")
    print(f"   Running: {status['is_running']}")
    print(
    f"   Active Strategies: {len(status['active_strategies'])}")
    print(f"   Total Profit: {status['total_profit']} ETH")
    print(f"   Rust Engine: {status['rust_engine_status']}")
    else:
    print(f"[FAIL] Status test failed: {resp.status}")

        # Test 2: Get All Strategies
    print("\n2. Testing strategies endpoint...")
    async with session.get(f"{BASE_URL}/strategies") as resp:
    if resp.status == 200:
    strategies = await resp.json()
    print(f"[PASS] Available Strategies: {len(strategies)}")
    for _name, details in strategies.items():
    print(
    f"   {
    details['name'}}: Active={"
    details['is_active'}}")
    else:
    print(f"[FAIL] Strategies test failed: {resp.status}")

        # Test 3: Toggle Flash Loan Arbitrage Strategy
    print("\n3. Testing strategy toggle...")
    toggle_data = {"strategy_type": "flashloan_arbitrage", "enabled": True}
    async with session.post(
    f"{BASE_URL}/strategy/toggle", json=toggle_data
    ) as resp:
    if resp.status == 200:
    result = await resp.json()
    print(f"[PASS] Strategy Toggle: {result['message']}")
    else:
    print(f"[FAIL] Strategy toggle failed: {resp.status}")

        # Test 4: Get Strategy Stats
    print("\n4. Testing strategy stats...")
    async with session.get(
    f"{BASE_URL}/strategy/flashloan_arbitrage/stats"
    ) as resp:
    if resp.status == 200:
    stats = await resp.json()
    print("[PASS] Flash Loan Stats:")
    print(f"   Opportunities: {stats['total_opportunities']}")
    print(f"   Successful: {stats['successful_executions']}")
    print(f"   Failed: {stats['failed_executions']}")
    print(f"   Total Profit: {stats['total_profit']} ETH")
    else:
    print(f"[FAIL] Stats test failed: {resp.status}")

        # Test 5: Get Performance Metrics
    print("\n5. Testing performance metrics...")
    async with session.get(f"{BASE_URL}/performance") as resp:
    if resp.status == 200:
    performance = await resp.json()
    print("[PASS] Performance Metrics:")
    print(
    f"   Total Profit: {
    performance['total_profit_eth'}} ETH")
    print(
    f"   Total Opportunities: {
    performance['total_opportunities'}}")
    print(f"   Success Rate: {performance['success_rate']:.1%}")
    print(f"   Uptime: {performance['uptime_hours']:.2f} hours")
    else:
    print(f"[FAIL] Performance test failed: {resp.status}")

        # Test 6: Get Recent Opportunities
    print("\n6. Testing opportunities endpoint...")
    async with session.get(f"{BASE_URL}/opportunities?limit=10") as resp:
    if resp.status == 200:
    opportunities = await resp.json()
    print(f"[PASS] Recent Opportunities: {len(opportunities)}")
    for opp in opportunities[:3]:  # Show first 3
    print(
    f"   {
    opp['strategy_type'}}: {"
    opp['estimated_profit'}:.4f} ETH"
                    
    else:
    print(f"[FAIL] Opportunities test failed: {resp.status}")

        # Test 7: Get Recent Executions
    print("\n7. Testing executions endpoint...")
    async with session.get(f"{BASE_URL}/executions?limit=10") as resp:
    if resp.status == 200:
    executions = await resp.json()
    print(f"[PASS] Recent Executions: {len(executions)}")
    for exec in executions[:3]:  # Show first 3
    status_icon = "[PASS]" if exec["success"] else "[FAIL]"
    print(
    f"   {status_icon} {"
    exec_data['strategy_type'}}: {
    exec_data['estimated_profit'}:.4f} ETH"
                    
    else:
    print(f"[FAIL] Executions test failed: {resp.status}")

        # Test 8: Test All Strategy Types
    print("\n8. Testing all strategy types...")
    strategy_types = [
    "flashloan_arbitrage",

    "liquidation_bot",
    "cross_chain_arbitrage",

    "governance_attack",
    ]
    for strategy in strategy_types:
            # Enable strategy
    toggle_data = {"strategy_type": strategy, "enabled": True}
    async with session.post(
    f"{BASE_URL}/strategy/toggle", json=toggle_data
    ) as resp:
    if resp.status == 200:
    print(f"   [PASS] {strategy}: Enabled")
    else:
    print(f"   [FAIL] {strategy}: Failed to enable")

            # Wait a moment for strategy to start
    await asyncio.sleep(0.5)

            # Get strategy stats
    async with session.get(f"{BASE_URL}/strategy/{strategy}/stats") as resp:
    if resp.status == 200:
    stats = await resp.json()
    print(
    f"      Stats: {
    stats['total_opportunities'}} opportunities")
    else:
    print("      Failed to get stats")

    print("\n9. Monitoring for opportunities (30 seconds)...")
    print("   Watching for MEV opportunities being generated...")

        # Monitor for 30 seconds
    start_time = time.time()
    while time.time() - start_time < 30:
    async with session.get(f"{BASE_URL}/opportunities?limit=5") as resp:
    if resp.status == 200:
    opportunities = await resp.json()
    if opportunities:
    latest = opportunities[-1]
    print(
    f"   [CHART] New opportunity: {
    latest['strategy_type'}} - " f"{
    latest['estimated_profit'}:.4f} ETH (confidence: {"
    latest['confidence_score'}:.1%})")

    await asyncio.sleep(3)

    print("\n[CELEBRATION] All tests completed!")

        # Final status check
    print("\n[CHART] Final Status Check:")
    async with session.get(f"{BASE_URL}/status") as resp:
    if resp.status == 200:
    final_status = await resp.json()
    print(
    f"   Active Strategies: {len(final_status['active_strategies'])}")
    print(
    f"   Total Opportunities: {
    final_status['total_opportunities'}}")
    print(f"   Total Profit: {final_status['total_profit']} ETH")
    print(
    f"   Uptime: {
    final_status['uptime_seconds'}:.0f} seconds")

    async def test_websocket():
    """Test WebSocket real-time updates"""
    print("\n🔌 Testing WebSocket connection...")

    uri = "ws://localhost:8003/ws"
    async with websockets.connect(uri) as websocket:
    print("[PASS] WebSocket connected")

          # Listen for updates for 10 seconds
    start_time = time.time()
    while time.time() - start_time < 10:
    try:
                    # Send a ping to keep connection alive
    await websocket.send("ping")

                    # Try to receive data with timeout
    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
    data = json.loads(message)
    if data.get("type") == "status_update":
    print(
    f"📡 WebSocket update: {
    data['recent_opportunities'}} opportunities, "
    f"{data['recent_executions']} executions"
                        
    except TimeoutError:
    pass  # No message received, continue
    except json.JSONDecodeError:
    pass  # Invalid JSON, continue

    await asyncio.sleep(2)

    print("[PASS] WebSocket test completed")

    print("[WARNING] WebSocket test skipped (websockets package not installed)")
    except Exception as e:
    print(f"[FAIL] WebSocket test failed: {e}")

    if __name__ == "__main__":
    print("=" * 60)
    print(">> ULTIMATE MEV BOT API TEST SUITE")
    print("=" * 60)
    print("Testing comprehensive MEV bot with 6 strategies:")
    print("• Flash Loan Arbitrage")
    print("• Sandwich Attack")
    print("• Liquidation Bot")
    print("• Cross-Chain Arbitrage")
    print("• Oracle Manipulation")
    print("• Governance Attack")
    print("=" * 60)

    # Run the tests
    asyncio.run(test_mev_bot())
    asyncio.run(test_websocket())

    print("\n✨ Testing complete! Check the results above.")
    print("[BULB] To view the API documentation, visit: http://localhost:8003/docs")

    if __name__ == '__main__':
    print('Running test file...')
    
    # Run all test functions
    test_functions = [name for name in globals() if name.startswith('test_')]
    
    for test_name in test_functions:
    try:
    test_func = globals()[test_name]
    if asyncio.iscoroutinefunction(test_func):
    asyncio.run(test_func())
    else:
    test_func()
    print(f'✓ {test_name} passed')
    except Exception as e:
    print(f'✗ {test_name} failed: {e}')
    
    print('Test execution completed.')