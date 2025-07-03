#!/usr/bin/env python3
"""
SCORPIUS Bytecode Similarity Engine - Demo Script
Interactive demonstration of the similarity engine capabilities
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict, List

import aiohttp
import websockets


class SCORPIUSDemo:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.ws_url = api_base_url.replace("http", "ws") + "/ws"

    async def test_api_connection(self) -> bool:
        """Test if the API is accessible"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/api/v1/health"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ API connection successful: {data['status']}")
                        return True
                    else:
                        print(f"❌ API connection failed: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ API connection error: {e}")
            return False

    async def test_websocket_connection(self) -> bool:
        """Test WebSocket connection"""
        try:
            async with websockets.connect(self.ws_url) as websocket:
                # Send ping
                await websocket.send(json.dumps({"type": "ping"}))

                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)

                if data.get("type") == "pong":
                    print("✅ WebSocket connection successful")
                    return True
                else:
                    print(f"❌ Unexpected WebSocket response: {data}")
                    return False

        except Exception as e:
            print(f"❌ WebSocket connection error: {e}")
            return False

    async def load_sample_contracts(self) -> Dict[str, str]:
        """Load sample contracts from JSON file"""
        contracts_file = Path(__file__).parent / "sample_contracts.json"

        if contracts_file.exists():
            with open(contracts_file, "r") as f:
                data = json.load(f)
                # Extract bytecode from the loaded data structure
                contracts = {}
                for key, value in data.items():
                    if isinstance(value, str):
                        contracts[key] = value
                return contracts
        else:
            # Return built-in samples if file doesn't exist
            return {
                "simple_storage_1": "608060405234801561001057600080fd5b5060c78061001f6000396000f3fe6080604052348015600f57600080fd5b506004361060325760003560e01c80636d4ce63c146037578063b43f15731460535760405162461bcd60e51b815260040160405180910390fd5b60005460405190815260200160405180910390f35b606081600055806000556040517f28ca10e5bf7979fdac94fbf3b4cea4b3",
                "simple_storage_2": "608060405234801561001057600080fd5b5060c78061001f6000396000f3fe6080604052348015600f57600080fd5b506004361060325760003560e01c80636d4ce63c146037578063b43f15731460535760405162461bcd60e51b815260040160405180910390fd5b60005460405190815260200160405180910390f35b606081600055806000556040517f28ca10e5bf7979fdac94fbf3b4cea4b4",
                "malicious_contract": "608060405234801561001057600080fd5b5060c78061001f6000396000f3fe6080604052348015600f57600080fd5b506004361060325760003560e01c80636d4ce63c146037578063b43f15731460535760405162461bcd60e51b815260040160405180910390fd5b60005460405190815260200160405180910390f35b60608160005580600055ff",
            }

    async def test_bytecode_comparison(
        self, bytecode1: str, bytecode2: str, description: str = ""
    ) -> Dict[str, Any]:
        """Test bytecode comparison"""
        print(f"\n🔍 Testing comparison: {description}")

        payload = {
            "bytecode1": bytecode1,
            "bytecode2": bytecode2,
            "threshold": 0.7,
            "use_neural_network": True,
        }

        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/api/v1/compare",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    processing_time = time.time() - start_time

                    if response.status == 200:
                        result = await response.json()

                        print(f"   Similarity Score: {result['similarity_score']:.3f}")
                        print(f"   Confidence: {result['confidence']:.3f}")
                        print(f"   Is Similar: {result['is_similar']}")
                        print(f"   Processing Time: {processing_time:.3f}s")

                        # Print dimension scores
                        if "dimension_scores" in result:
                            print("   Dimension Scores:")
                            for dim, score in result["dimension_scores"].items():
                                print(f"     {dim}: {score:.3f}")

                        return result
                    else:
                        error_text = await response.text()
                        print(f"❌ Comparison failed: {response.status} - {error_text}")
                        return {}

        except Exception as e:
            print(f"❌ Comparison error: {e}")
            return {}

    async def test_engine_stats(self) -> Dict[str, Any]:
        """Test engine statistics"""
        print("\n📊 Testing engine statistics...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/api/v1/stats") as response:
                    if response.status == 200:
                        stats = await response.json()
                        print(f"✅ Engine Stats Retrieved:")
                        print(
                            f"   Total Indexed: {stats.get('total_indexed_bytecodes', 0)}"
                        )
                        print(f"   Cache Size: {stats.get('cache_size', 0)}")
                        print(f"   Device: {stats.get('device', 'unknown')}")
                        print(f"   Model Loaded: {stats.get('model_loaded', False)}")

                        return stats
                    else:
                        error_text = await response.text()
                        print(
                            f"❌ Stats retrieval failed: {response.status} - {error_text}"
                        )
                        return {}

        except Exception as e:
            print(f"❌ Stats error: {e}")
            return {}

    async def monitor_websocket_feed(self, duration: int = 10):
        """Monitor WebSocket feed for real-time updates"""
        print(f"\n📡 Monitoring WebSocket feed for {duration} seconds...")

        try:
            async with websockets.connect(self.ws_url) as websocket:
                # Subscribe to updates
                await websocket.send(
                    json.dumps({"type": "subscribe", "subscription": "all"})
                )

                start_time = time.time()
                message_count = 0

                while time.time() - start_time < duration:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        data = json.loads(message)
                        message_count += 1

                        print(
                            f"   📨 {data.get('type', 'unknown')}: {data.get('timestamp', 'no-time')}"
                        )

                    except asyncio.TimeoutError:
                        continue

                print(f"✅ Received {message_count} WebSocket messages")

        except Exception as e:
            print(f"❌ WebSocket monitoring error: {e}")

    async def run_full_demo(self):
        """Run the complete demo"""
        print("🚀 SCORPIUS Bytecode Similarity Engine - Demo")
        print("=" * 50)

        # Test API connection
        if not await self.test_api_connection():
            print("❌ Cannot proceed without API connection")
            print("💡 Make sure the API server is running: python -m api.main")
            return

        # Test WebSocket connection
        await self.test_websocket_connection()

        # Load sample contracts
        contracts = await self.load_sample_contracts()
        print(f"\n📄 Loaded {len(contracts)} sample contracts")

        # Get engine stats
        await self.test_engine_stats()

        # Test comparisons
        contract_names = list(contracts.keys())
        if len(contract_names) >= 2:
            # High similarity test
            await self.test_bytecode_comparison(
                contracts[contract_names[0]],
                contracts[contract_names[1]],
                f"Similarity Test: {contract_names[0]} vs {contract_names[1]}",
            )

            # Different contracts test
            if len(contract_names) >= 3:
                await self.test_bytecode_comparison(
                    contracts[contract_names[0]],
                    contracts[contract_names[2]],
                    f"Different: {contract_names[0]} vs {contract_names[2]}",
                )

        # Monitor WebSocket feed
        await self.monitor_websocket_feed(10)

        print("\n✅ Demo completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Open dashboard: http://localhost:5173")
        print("   2. Try the Bytecode Analyzer page")
        print("   3. Monitor real-time updates")
        print("   4. Check API docs: http://localhost:8000/docs")


async def main():
    """Main demo function"""
    demo = SCORPIUSDemo()
    await demo.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main())
