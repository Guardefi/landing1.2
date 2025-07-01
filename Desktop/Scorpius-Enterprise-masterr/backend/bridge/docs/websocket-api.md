# WebSocket API Documentation

## Overview

The Scorpius Bridge WebSocket API provides real-time communication for dashboard integration, enabling live updates for bridge transactions, validator status, liquidity pools, and system events.

## Connection

### Endpoint
```
ws://localhost:8000/api/ws
wss://api.scorpius-bridge.com/api/ws (production)
```

### Authentication (Optional)
```
ws://localhost:8000/api/ws?token=your_jwt_token&client_id=your_client_id
```

### Connection Parameters
- `token` (optional): JWT authentication token
- `client_id` (optional): Unique client identifier for connection tracking

## Message Format

All WebSocket messages use JSON format with the following structure:

```json
{
  "type": "message_type",
  "data": {
    // Message-specific data
  }
}
```

## Client-to-Server Messages

### 1. Subscribe to Topic
```json
{
  "type": "subscribe",
  "data": {
    "topic": "events",
    "filters": {
      // Optional filters
    }
  }
}
```

### 2. Unsubscribe from Topic
```json
{
  "type": "unsubscribe", 
  "data": {
    "topic": "events"
  }
}
```

### 3. Ping
```json
{
  "type": "ping"
}
```

### 4. Get Current Statistics
```json
{
  "type": "get_stats"
}
```

### 5. Get Status
```json
{
  "type": "get_status",
  "data": {
    "status_type": "network", // or "chain"
    "chain_id": "ethereum" // required for chain status
  }
}
```

## Server-to-Client Messages

### 1. Connection Confirmation
```json
{
  "type": "connection",
  "status": "connected",
  "client_id": "uuid-client-id",
  "server_time": "2024-01-15T10:30:00Z"
}
```

### 2. Subscription Confirmation
```json
{
  "type": "subscription",
  "action": "subscribed", // or "unsubscribed"
  "topic": "events"
}
```

### 3. Pong Response
```json
{
  "type": "pong",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 4. Event Messages
```json
{
  "type": "event",
  "event_type": "bridge_transaction_initiated",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "amount": "100",
    "token": "USDC",
    "source_chain": "ethereum",
    "target_chain": "polygon"
  },
  "source_chain": "ethereum",
  "target_chain": "polygon", 
  "transaction_id": "tx_123456",
  "user_id": "user_789",
  "severity": "info"
}
```

### 5. Statistics
```json
{
  "type": "stats",
  "data": {
    "total_transactions": 1234,
    "active_validators": 15,
    "total_liquidity": "1000000",
    "network_health": "healthy",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### 6. Network Status
```json
{
  "type": "network_status",
  "data": {
    "status": "operational",
    "supported_chains": ["ethereum", "polygon", "bsc"],
    "chain_status": {
      "ethereum": "operational",
      "polygon": "operational",
      "bsc": "maintenance"
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### 7. Chain Status
```json
{
  "type": "chain_status",
  "data": {
    "chain_id": "ethereum",
    "status": "operational",
    "block_height": 18500000,
    "gas_price": "25000000000",
    "last_update": "2024-01-15T10:30:00Z"
  }
}
```

### 8. Error Messages
```json
{
  "type": "error",
  "message": "Invalid topic name",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Available Topics

### Core Topics
- `events` - All system events
- `stats` - Real-time statistics  
- `network_status` - Network status updates
- `validator_status` - Validator status updates
- `liquidity_pools` - Liquidity pool data
- `transaction_history` - Transaction history updates

### Event-Specific Topics
- `events:bridge_transaction` - Bridge transaction events only
- `events:validator` - Validator events only
- `events:liquidity` - Liquidity pool events only
- `events:system` - System events only

### Chain-Specific Topics
- `chain:ethereum` - Ethereum-specific events
- `chain:polygon` - Polygon-specific events
- `chain:bsc` - BSC-specific events

### User-Specific Topics (Authentication Required)
- `user:{user_id}` - User-specific events
- `transaction:{transaction_id}` - Transaction-specific updates

## Event Types

### Bridge Transaction Events
- `bridge_transaction_initiated`
- `bridge_transaction_confirmed`
- `bridge_transaction_completed`
- `bridge_transaction_failed`

### Validator Events
- `validator_status_changed`
- `validator_joined`
- `validator_left`

### Liquidity Pool Events
- `liquidity_added`
- `liquidity_removed`
- `pool_created`
- `pool_status_changed`

### Network Events
- `network_status_changed`
- `chain_status_changed`

### System Events
- `system_alert`
- `maintenance_mode`

## Error Handling

### Connection Errors
- Invalid authentication token
- Rate limiting exceeded
- Server maintenance

### Message Errors
- Invalid JSON format
- Unknown message type
- Invalid topic name
- Missing required fields

## Rate Limiting

- Maximum 100 messages per minute per connection
- Maximum 10 subscriptions per connection
- Automatic disconnection for violations

## Best Practices

### For Dashboard Integration

1. **Connection Management**
   ```javascript
   // Implement reconnection logic
   function connectWebSocket() {
     const ws = new WebSocket('ws://localhost:8000/api/ws');
     
     ws.onopen = () => {
       console.log('Connected to Scorpius Bridge');
       // Subscribe to required topics
       subscribe('events');
       subscribe('stats');
     };
     
     ws.onclose = () => {
       console.log('Disconnected, reconnecting...');
       setTimeout(connectWebSocket, 5000);
     };
   }
   ```

2. **Event Handling**
   ```javascript
   ws.onmessage = (event) => {
     const message = JSON.parse(event.data);
     
     switch (message.type) {
       case 'event':
         handleBridgeEvent(message);
         break;
       case 'stats':
         updateDashboardStats(message.data);
         break;
       case 'network_status':
         updateNetworkStatus(message.data);
         break;
     }
   };
   ```

3. **Subscription Management**
   ```javascript
   function subscribe(topic) {
     ws.send(JSON.stringify({
       type: 'subscribe',
       data: { topic }
     }));
   }
   
   function unsubscribe(topic) {
     ws.send(JSON.stringify({
       type: 'unsubscribe',
       data: { topic }
     }));
   }
   ```

### For React Integration

```jsx
import { useEffect, useState, useRef } from 'react';

export function useWebSocket(url, token) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const ws = useRef(null);

  useEffect(() => {
    const connectWS = () => {
      const wsUrl = token ? `${url}?token=${token}` : url;
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        setIsConnected(true);
      };

      ws.current.onmessage = (event) => {
        const message = JSON.parse(event.data);
        setLastMessage(message);
      };

      ws.current.onclose = () => {
        setIsConnected(false);
        // Reconnect after 5 seconds
        setTimeout(connectWS, 5000);
      };
    };

    connectWS();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url, token]);

  const sendMessage = (message) => {
    if (ws.current && isConnected) {
      ws.current.send(JSON.stringify(message));
    }
  };

  return { isConnected, lastMessage, sendMessage };
}
```

## Testing

Use the built-in test page at `/api/ws/test` for development and testing purposes.

## Security Considerations

1. **Authentication**: Use JWT tokens for user-specific data access
2. **Rate Limiting**: Implement client-side rate limiting
3. **Data Validation**: Always validate incoming data
4. **SSL/TLS**: Use WSS in production environments
5. **Origin Checking**: Verify allowed origins in production

## Performance Tips

1. **Selective Subscriptions**: Only subscribe to needed topics
2. **Message Batching**: Group related updates when possible
3. **Connection Pooling**: Reuse connections across components
4. **Graceful Degradation**: Handle disconnections gracefully
5. **Memory Management**: Clean up event listeners and subscriptions
