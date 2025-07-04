"""
WebSocket Tests for Scorpius Real-Time Communication
Tests WebSocket connections, subscriptions, and real-time updates
"""

import pytest
import asyncio
import websockets
import json
import time
from typing import Dict, Any, List
import concurrent.futures

class WebSocketTester:
    """Helper class for testing WebSocket functionality."""
    
    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.received_messages = []
        
    async def connect_and_test(self, endpoint: str, test_messages: List[Dict], timeout: int = 10):
        """Connect to WebSocket endpoint and test message exchange."""
        uri = f"{self.base_url}{endpoint}"
        
        try:
            async with websockets.connect(uri, timeout=timeout) as websocket:
                # Send test messages
                for message in test_messages:
                    await websocket.send(json.dumps(message))
                    print(f"📤 Sent: {message}")
                
                # Listen for responses
                received_count = 0
                start_time = time.time()
                
                while received_count < len(test_messages) and (time.time() - start_time) < timeout:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2)
                        message_data = json.loads(response)
                        self.received_messages.append(message_data)
                        print(f"📥 Received: {message_data}")
                        received_count += 1
                    except asyncio.TimeoutError:
                        print("⏱️ Timeout waiting for response")
                        break
                
                return len(self.received_messages) > 0
                
        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
            return False

class TestWebSocketBasic:
    """Basic WebSocket functionality tests."""
    
    def test_websocket_connection(self):
        """Test basic WebSocket connection."""
        async def test():
            try:
                uri = "ws://localhost:8000/api/ws?client_id=test"
                async with websockets.connect(uri, timeout=5) as websocket:
                    # Send ping
                    message = {"type": "ping", "data": {"timestamp": time.time()}}
                    await websocket.send(json.dumps(message))
                    
                    # Wait for response
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    data = json.loads(response)
                    print(f"✅ WebSocket response: {data}")
                    return True
            except Exception as e:
                print(f"❌ WebSocket test failed: {e}")
                return False
        
        result = asyncio.run(test())
        assert result, "WebSocket connection test failed"

class TestWebSocketCommunication:
    """Test WebSocket real-time communication features."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.ws_tester = WebSocketTester()
    
    def test_basic_websocket_connection(self):
        """Test basic WebSocket connection and ping/pong."""
        test_messages = [
            {"type": "ping", "data": {"timestamp": time.time()}},
            {"type": "subscribe", "data": {"topic": "health"}},
        ]
        
        result = asyncio.run(
            self.ws_tester.connect_and_test("/api/ws?client_id=test-basic", test_messages)
        )
        assert result, "Basic WebSocket connection failed"
    
    def test_bridge_websocket_subscriptions(self):
        """Test bridge-specific WebSocket subscriptions."""
        test_messages = [
            {"type": "subscribe", "data": {"topic": "bridge_events"}},
            {"type": "subscribe", "data": {"topic": "transfer_updates"}},
            {"type": "get_stats", "data": {}},
        ]
        
        result = asyncio.run(
            self.ws_tester.connect_and_test("/api/ws/bridge?client_id=test-bridge", test_messages)
        )
        assert result, "Bridge WebSocket subscription failed"
    
    def test_validator_websocket_updates(self):
        """Test validator status WebSocket updates."""
        test_messages = [
            {"type": "subscribe", "data": {"topic": "validator_status"}},
            {"type": "ping", "data": {"client": "validator_monitor"}},
        ]
        
        result = asyncio.run(
            self.ws_tester.connect_and_test("/api/ws/validator?client_id=test-validator", test_messages)
        )
        assert result, "Validator WebSocket updates failed"
    
    def test_multiple_concurrent_connections(self):
        """Test multiple concurrent WebSocket connections."""
        async def create_connection(client_id: str):
            tester = WebSocketTester()
            messages = [{"type": "ping", "data": {"client_id": client_id}}]
            return await tester.connect_and_test(f"/api/ws?client_id={client_id}", messages)
        
        async def test_concurrent():
            tasks = [
                create_connection(f"client-{i}") 
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return all(isinstance(r, bool) and r for r in results)
        
        result = asyncio.run(test_concurrent())
        assert result, "Multiple concurrent connections failed"
    
    def test_websocket_error_handling(self):
        """Test WebSocket error handling and reconnection."""
        test_messages = [
            {"type": "invalid_message_type", "data": {}},
            {"type": "subscribe", "data": {"topic": "nonexistent_topic"}},
            {"type": "ping", "data": {"valid": "message"}},
        ]
        
        # Should still work despite invalid messages
        result = asyncio.run(
            self.ws_tester.connect_and_test("/api/ws?client_id=test-error", test_messages)
        )
        assert result, "WebSocket error handling failed"

class TestWebSocketStats:
    """Test WebSocket statistics and monitoring."""
    
    def test_websocket_stats_endpoint(self):
        """Test WebSocket statistics HTTP endpoint."""
        import requests
        
        try:
            response = requests.get("http://localhost:8000/api/ws/stats", timeout=5)
            assert response.status_code == 200
            
            stats = response.json()
            assert "active_connections" in stats
            assert isinstance(stats["active_connections"], int)
            print(f"✅ WebSocket Stats: {stats}")
            
        except Exception as e:
            pytest.fail(f"WebSocket stats endpoint failed: {e}")
    
    def test_websocket_load_simulation(self):
        """Simulate load on WebSocket connections."""
        async def simulate_client_load(client_count: int = 10, message_count: int = 5):
            """Simulate multiple clients sending messages."""
            
            async def client_session(client_id: int):
                uri = f"ws://localhost:8000/api/ws?client_id=load-test-{client_id}"
                messages_sent = 0
                
                try:
                    async with websockets.connect(uri, timeout=10) as websocket:
                        for i in range(message_count):
                            message = {
                                "type": "ping",
                                "data": {
                                    "client_id": client_id,
                                    "message_num": i,
                                    "timestamp": time.time()
                                }
                            }
                            await websocket.send(json.dumps(message))
                            messages_sent += 1
                            
                            # Wait for response
                            try:
                                response = await asyncio.wait_for(websocket.recv(), timeout=2)
                                data = json.loads(response)
                            except asyncio.TimeoutError:
                                print(f"⏱️ Client {client_id} timeout on message {i}")
                            
                            await asyncio.sleep(0.1)  # Small delay between messages
                            
                except Exception as e:
                    print(f"❌ Client {client_id} failed: {e}")
                
                return messages_sent
            
            # Run multiple clients concurrently
            tasks = [client_session(i) for i in range(client_count)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_clients = sum(1 for r in results if isinstance(r, int) and r > 0)
            total_messages = sum(r for r in results if isinstance(r, int))
            
            print(f"✅ Load test: {successful_clients}/{client_count} clients successful")
            print(f"✅ Total messages sent: {total_messages}")
            
            return successful_clients >= client_count * 0.8  # 80% success rate
        
        result = asyncio.run(simulate_client_load())
        assert result, "WebSocket load simulation failed"

if __name__ == "__main__":
    print("🔄 Running WebSocket Tests...")
    pytest.main([__file__, "-v"]) 