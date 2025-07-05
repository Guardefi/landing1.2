import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  TextField,
  Button,
  Grid,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  FilterList,
  Refresh,
  Timeline as TimelineIcon,
  AccessTime,
  Event as EventIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { TimelineEvent } from '../types';
import { api } from '../services/api';

interface TimelineProps {
  onError: (message: string) => void;
  onSuccess: (message: string) => void;
}

// Event type color mapping for consistent theming
const EVENT_TYPE_COLORS = {
  transaction: '#2196f3',
  state_change: '#4caf50', 
  contract_deploy: '#ff9800',
  error: '#f44336',
  gas_analysis: '#9c27b0',
  security: '#e91e63',
  defi: '#00bcd4',
} as const;

// Maximum events to keep in memory for performance
const MAX_EVENTS_IN_MEMORY = 1000;

export const Timeline: React.FC<TimelineProps> = ({ onError, onSuccess }) => {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('');
  const [eventTypes, setEventTypes] = useState<string[]>([]);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  // Memoized demo events generator for performance
  const generateDemoEvents = useCallback((): TimelineEvent[] => {
    const now = new Date();
    
    const demoEvents: TimelineEvent[] = [
      {
        id: 'demo-1',
        timestamp: new Date(now.getTime() - (1 * 60000)).toISOString(),
        event_type: 'transaction',
        description: 'Large ETH transfer detected: 1000 ETH moved to unknown address',
        metadata: {
          block_number: 18500020,
          gas_used: 21000,
          transaction_hash: '0xabcd1234ef567890abcd1234ef567890abcd1234ef567890abcd1234ef567890',
          from: '0x1234567890123456789012345678901234567890',
          to: '0x9876543210987654321098765432109876543210',
          value: '1000000000000000000000'
        },
        session_id: 'forensic-session-1',
        job_id: 'investigation-job-1'
      },
      {
        id: 'demo-2',
        timestamp: new Date(now.getTime() - (2 * 60000)).toISOString(),
        event_type: 'security',
        description: 'Reentrancy vulnerability detected in smart contract',
        metadata: {
          block_number: 18500019,
          gas_used: 85000,
          contract_address: '0xdeadbeefcafebabe123456789012345678901234',
          vulnerability_type: 'reentrancy',
          severity: 'critical'
        },
        session_id: 'forensic-session-1',
        job_id: 'security-audit-1'
      },
      {
        id: 'demo-3',
        timestamp: new Date(now.getTime() - (3 * 60000)).toISOString(),
        event_type: 'contract_deploy',
        description: 'Suspicious proxy contract deployed with admin backdoor',
        metadata: {
          block_number: 18500018,
          gas_used: 2100000,
          contract_address: '0xcafebabe123456789012345678901234567890ab',
          deployer: '0x1111222233334444555566667777888899990000',
          bytecode_hash: '0x567890abcdef1234567890abcdef1234567890ab'
        },
        session_id: 'forensic-session-1',
        job_id: 'contract-analysis-1'
      },
      {
        id: 'demo-4',
        timestamp: new Date(now.getTime() - (4 * 60000)).toISOString(),
        event_type: 'gas_analysis',
        description: 'Gas optimization opportunity found: 30% reduction possible',
        metadata: {
          block_number: 18500017,
          gas_used: 150000,
          potential_savings: 45000,
          optimization_type: 'storage_packing',
          contract: '0xabcdef1234567890abcdef1234567890abcdef12'
        },
        session_id: 'forensic-session-1',
        job_id: 'gas-audit-1'
      },
      {
        id: 'demo-5',
        timestamp: new Date(now.getTime() - (5 * 60000)).toISOString(),
        event_type: 'state_change',
        description: 'Critical state variable modified: owner changed',
        metadata: {
          block_number: 18500016,
          gas_used: 29000,
          contract: '0xfedcba0987654321fedcba0987654321fedcba09',
          variable: 'owner',
          old_value: '0x1111111111111111111111111111111111111111',
          new_value: '0x2222222222222222222222222222222222222222'
        },
        session_id: 'forensic-session-1',
        job_id: 'state-monitoring-1'
      },
      {
        id: 'demo-6',
        timestamp: new Date(now.getTime() - (6 * 60000)).toISOString(),
        event_type: 'transaction',
        description: 'MEV sandwich attack detected on Uniswap transaction',
        metadata: {
          block_number: 18500015,
          gas_used: 180000,
          victim_tx: '0x111222333444555666777888999aaabbbcccdddeeefffaaa',
          frontrun_tx: '0x222333444555666777888999aaabbbcccdddeeefffbbb',
          backrun_tx: '0x333444555666777888999aaabbbcccdddeeefffccc',
          profit_extracted: '15.5'
        },
        session_id: 'forensic-session-2',
        job_id: 'mev-analysis-1'
      },
      {
        id: 'demo-7',
        timestamp: new Date(now.getTime() - (7 * 60000)).toISOString(),
        event_type: 'error',
        description: 'Transaction reverted: insufficient funds for gas',
        metadata: {
          block_number: 18500014,
          gas_used: 0,
          transaction_hash: '0x444555666777888999aaabbbcccdddeeefffggg',
          error_message: 'insufficient funds for gas * price + value',
          sender: '0x5555666677778888999900001111222233334444'
        },
        session_id: 'forensic-session-2',
        job_id: 'error-analysis-1'
      },
      {
        id: 'demo-8',
        timestamp: new Date(now.getTime() - (8 * 60000)).toISOString(),
        event_type: 'defi',
        description: 'Flash loan arbitrage executed across 3 DEXs',
        metadata: {
          block_number: 18500013,
          gas_used: 420000,
          loan_amount: '1000000',
          profit: '5.2',
          dexs: ['Uniswap', 'SushiSwap', 'Curve'],
          token_pair: 'USDC/ETH'
        },
        session_id: 'forensic-session-2',
        job_id: 'defi-analysis-1'
      },
      {
        id: 'demo-9',
        timestamp: new Date(now.getTime() - (9 * 60000)).toISOString(),
        event_type: 'security',
        description: 'Price oracle manipulation attempt detected',
        metadata: {
          block_number: 18500012,
          gas_used: 350000,
          oracle_contract: '0x777888999aaabbbcccdddeeefffggghhh',
          price_deviation: '25%',
          affected_protocol: 'LendingProtocol',
          severity: 'high'
        },
        session_id: 'forensic-session-2',
        job_id: 'oracle-monitoring-1'
      },
      {
        id: 'demo-10',
        timestamp: new Date(now.getTime() - (10 * 60000)).toISOString(),
        event_type: 'transaction',
        description: 'Cross-chain bridge deposit: 500 ETH locked',
        metadata: {
          block_number: 18500011,
          gas_used: 95000,
          bridge_contract: '0x888999aaabbbcccdddeeefffggghhhiii',
          amount: '500',
          destination_chain: 'Polygon',
          recipient: '0x999aaabbbcccdddeeefffggghhhiiijjj'
        },
        session_id: 'forensic-session-3',
        job_id: 'bridge-monitoring-1'
      },
      {
        id: 'demo-11',
        timestamp: new Date(now.getTime() - (11 * 60000)).toISOString(),
        event_type: 'contract_deploy',
        description: 'NFT collection deployed with hidden minting function',
        metadata: {
          block_number: 18500010,
          gas_used: 3200000,
          contract_address: '0xaaabbbcccdddeeefffggghhhiiijjjkkk',
          collection_name: 'SuspiciousApes',
          hidden_function: 'secretMint()',
          max_supply: '10000'
        },
        session_id: 'forensic-session-3',
        job_id: 'nft-analysis-1'
      },
      {
        id: 'demo-12',
        timestamp: new Date(now.getTime() - (12 * 60000)).toISOString(),
        event_type: 'state_change',
        description: 'Governance proposal executed: protocol parameters changed',
        metadata: {
          block_number: 18500009,
          gas_used: 180000,
          dao_contract: '0xbbbcccdddeeefffggghhhiiijjjkkklll',
          proposal_id: '42',
          parameter: 'lending_rate',
          old_value: '5.0%',
          new_value: '8.5%'
        },
        session_id: 'forensic-session-3',
        job_id: 'governance-monitoring-1'
      },
      {
        id: 'demo-13',
        timestamp: new Date(now.getTime() - (13 * 60000)).toISOString(),
        event_type: 'gas_analysis',
        description: 'Unusual gas price spike detected: 200+ gwei',
        metadata: {
          block_number: 18500008,
          gas_price: '220000000000',
          average_gas_price: '35000000000',
          spike_factor: '6.3x',
          potential_cause: 'NFT mint rush'
        },
        session_id: 'forensic-session-3',
        job_id: 'gas-monitoring-1'
      },
      {
        id: 'demo-14',
        timestamp: new Date(now.getTime() - (14 * 60000)).toISOString(),
        event_type: 'transaction',
        description: 'Tornado Cash withdrawal: privacy coins mixed',
        metadata: {
          block_number: 18500007,
          gas_used: 1100000,
          mixer_contract: '0xcccdddeeefff000111222333444555666',
          withdrawal_amount: '10',
          nullifier_hash: '0xdddeeefff000111222333444555666777',
          recipient: '0xeeefffggg000111222333444555666777'
        },
        session_id: 'forensic-session-4',
        job_id: 'privacy-analysis-1'
      },
      {
        id: 'demo-15',
        timestamp: new Date(now.getTime() - (15 * 60000)).toISOString(),
        event_type: 'security',
        description: 'Front-running bot activity detected',
        metadata: {
          block_number: 18500006,
          gas_used: 85000,
          bot_address: '0xfffggg000111222333444555666777888',
          target_tx: '0xggghhh000111222333444555666777888999',
          profit_mev: '2.8',
          gas_price_used: '150000000000'
        },
        session_id: 'forensic-session-4',
        job_id: 'bot-detection-1'
      },
      {
        id: 'demo-16',
        timestamp: new Date(now.getTime() - (16 * 60000)).toISOString(),
        event_type: 'defi',
        description: 'Liquidation cascade triggered in lending protocol',
        metadata: {
          block_number: 18500005,
          gas_used: 280000,
          protocol: 'CompoundProtocol',
          liquidated_accounts: 15,
          total_liquidated: '2500000',
          liquidation_bonus: '125000'
        },
        session_id: 'forensic-session-4',
        job_id: 'liquidation-monitoring-1'
      },
      {
        id: 'demo-17',
        timestamp: new Date(now.getTime() - (17 * 60000)).toISOString(),
        event_type: 'transaction',
        description: 'Multi-signature wallet transaction: 3 of 5 signatures required',
        metadata: {
          block_number: 18500004,
          gas_used: 120000,
          multisig_address: '0x000111222333444555666777888999aaa',
          transaction_hash: '0x111222333444555666777888999aaabbb',
          signers: ['0xaaa', '0xbbb', '0xccc'],
          threshold: '3/5'
        },
        session_id: 'forensic-session-4',
        job_id: 'multisig-analysis-1'
      },
      {
        id: 'demo-18',
        timestamp: new Date(now.getTime() - (18 * 60000)).toISOString(),
        event_type: 'contract_deploy',
        description: 'Upgradeable proxy deployed with timelock mechanism',
        metadata: {
          block_number: 18500003,
          gas_used: 1800000,
          proxy_address: '0x222333444555666777888999aaabbbccc',
          implementation: '0x333444555666777888999aaabbbcccddd',
          timelock_delay: '172800',
          admin: '0x444555666777888999aaabbbcccdddeee'
        },
        session_id: 'forensic-session-5',
        job_id: 'proxy-analysis-1'
      },
      {
        id: 'demo-19',
        timestamp: new Date(now.getTime() - (19 * 60000)).toISOString(),
        event_type: 'state_change',
        description: 'Emergency pause activated on DeFi protocol',
        metadata: {
          block_number: 18500002,
          gas_used: 65000,
          protocol_contract: '0x555666777888999aaabbbcccdddeeefffggg',
          pause_reason: 'potential_exploit_detected',
          paused_functions: ['withdraw', 'borrow', 'liquidate'],
          guardian: '0x666777888999aaabbbcccdddeeefffggghhh'
        },
        session_id: 'forensic-session-5',
        job_id: 'emergency-response-1'
      },
      {
        id: 'demo-20',
        timestamp: new Date(now.getTime() - (20 * 60000)).toISOString(),
        event_type: 'transaction',
        description: 'Whale transaction: 50,000 USDC transferred to exchange',
        metadata: {
          block_number: 18500001,
          gas_used: 65000,
          transaction_hash: '0x777888999aaabbbcccdddeeefffggghhhiii',
          token_contract: '0xA0b86a33E6417b5B21e3F02ae4e0c5B7A3B0C8D9',
          from: '0x888999aaabbbcccdddeeefffggghhh',
          to: '0x999aaabbbcccdddeeefffggghhh',
          amount: '50000000000'
        },
        session_id: 'forensic-session-5',
        job_id: 'whale-tracking-1'
      }
    ];
    
    return demoEvents;
  }, []); // Close useCallback

  const loadEvents = useCallback(async () => {
    setLoading(true);
    try {
      // Try to load real events first, fallback to demo data
      try {
        // In a real implementation, you'd fetch from /api/events or similar
        // For now, we'll use demo data since the backend might not have timeline events
        const demoEvents = generateDemoEvents();
        setEvents(demoEvents);
        
        // Extract unique event types
        const types = Array.from(new Set(demoEvents.map(e => e.event_type)));
        setEventTypes(types);
        
        onSuccess('Timeline loaded with demo data');
      } catch (apiError) {
        // Fallback to demo data
        const demoEvents = generateDemoEvents();
        setEvents(demoEvents);
        const types = Array.from(new Set(demoEvents.map(e => e.event_type)));
        setEventTypes(types);
        onError('Using demo data - backend events not available');
      }
    } catch (error) {
      onError(`Failed to load timeline: ${error}`);
    } finally {
      setLoading(false);
    }
  }, [generateDemoEvents, onError, onSuccess]); // Close useCallback

  const connectWebSocket = useCallback(() => {
    try {
      const ws = api.connectTimelineStream((event: TimelineEvent) => {
        setEvents(prev => [event, ...prev].slice(0, 100)); // Keep latest 100 events
      });
      
      if (ws) {
        setWsConnection(ws);
        setIsConnected(true);
        onSuccess('Connected to real-time timeline stream');
      }
    } catch (error) {
      onError('Failed to connect to timeline stream');
    }
  }, [onError, onSuccess]); // Close useCallback

  const disconnectWebSocket = useCallback(() => {
    if (wsConnection) {
      wsConnection.close();
      setWsConnection(null);
      setIsConnected(false);
    }
  }, [wsConnection]); // Close useCallback

  useEffect(() => {
    loadEvents();
    return () => {
      disconnectWebSocket();
    };
  }, [loadEvents, disconnectWebSocket]);

  // Memoized filtered events for performance
  const filteredEvents = useMemo(() => {
    return events.filter(event => {
      const matchesFilter = !filter || 
        event.description.toLowerCase().includes(filter.toLowerCase()) ||
        event.event_type.toLowerCase().includes(filter.toLowerCase()) ||
        (event.metadata && Object.values(event.metadata).some(value => 
          String(value).toLowerCase().includes(filter.toLowerCase())
        ));
      
      const matchesType = selectedTypes.length === 0 || 
        selectedTypes.includes(event.event_type);
      
      return matchesFilter && matchesType;
    }).slice(0, MAX_EVENTS_IN_MEMORY);
  }, [events, filter, selectedTypes]);

  // Memoized event type color function
  const getEventTypeColor = useCallback((type: string) => {
    return EVENT_TYPE_COLORS[type as keyof typeof EVENT_TYPE_COLORS] || '#757575';
  }, []);

  // Memoized timestamp formatting
  const formatTimestamp = useCallback((timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch (error) {
      return 'Invalid date';
    }
  }, []);

  // Memoized metadata formatting
  const formatMetadata = useCallback((metadata: Record<string, any>) => {
    try {
      return Object.entries(metadata)
        .slice(0, 3) // Show first 3 metadata entries
        .map(([key, value]) => `${key}: ${String(value).slice(0, 50)}${String(value).length > 50 ? '...' : ''}`)
        .join(', ');
    } catch (error) {
      return 'Invalid metadata';
    }
  }, []);

  // Handle connection errors
  const handleConnectionError = useCallback((error: Error) => {
    setConnectionError(error.message);
    setRetryCount(prev => prev + 1);
    
    if (retryCount < 3) {
      setTimeout(() => {
        connectWebSocket();
      }, 5000 * retryCount); // Exponential backoff
    } else {
      onError('Failed to establish real-time connection after multiple attempts');
    }
  }, [retryCount, connectWebSocket, onError]);

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TimelineIcon />
            Timeline Events ({filteredEvents.length})
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title={isConnected ? "Disconnect from live stream" : "Connect to live stream"}>
              <IconButton
                onClick={isConnected ? disconnectWebSocket : connectWebSocket}
                color={isConnected ? "success" : "default"}
              >
                {isConnected ? <Pause /> : <PlayArrow />}
              </IconButton>
            </Tooltip>
            <Tooltip title="Refresh events">
              <IconButton onClick={loadEvents} disabled={loading}>
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {isConnected && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Connected to real-time timeline stream
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Search events"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="Search by description or type..."
              InputProps={{
                startAdornment: <FilterList sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Filter by Event Type</InputLabel>
              <Select
                multiple
                value={selectedTypes}
                onChange={(e) => setSelectedTypes(e.target.value as string[])}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip 
                        key={value} 
                        label={value} 
                        size="small"
                        sx={{ backgroundColor: getEventTypeColor(value), color: 'white' }}
                      />
                    ))}
                  </Box>
                )}
              >
                {eventTypes.map((type) => (
                  <MenuItem key={type} value={type}>
                    <Chip 
                      label={type} 
                      size="small" 
                      sx={{ backgroundColor: getEventTypeColor(type), color: 'white' }}
                    />
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 2 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : filteredEvents.length === 0 ? (
          <Box sx={{ textAlign: 'center', p: 4 }}>
            <EventIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No events found
            </Typography>
            <Typography color="text.secondary">
              {filter || selectedTypes.length > 0 
                ? 'Try adjusting your filters' 
                : 'No timeline events available'
              }
            </Typography>
          </Box>
        ) : (
          <List>
            {filteredEvents.map((event, index) => (
              <React.Fragment key={event.id}>
                <ListItem alignItems="flex-start">
                  <Box sx={{ inlineSize: '100%' }}>
                    <Card variant="outlined" sx={{ mb: 1 }}>
                      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Chip 
                              label={event.event_type}
                              size="small"
                              sx={{ 
                                backgroundColor: getEventTypeColor(event.event_type), 
                                color: 'white',
                                fontWeight: 'bold'
                              }}
                            />
                            <Typography variant="body1" fontWeight="medium">
                              {event.description}
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.secondary' }}>
                            <AccessTime sx={{ fontSize: 16 }} />
                            <Typography variant="caption">
                              {formatTimestamp(event.timestamp)}
                            </Typography>
                          </Box>
                        </Box>
                        
                        {event.metadata && Object.keys(event.metadata).length > 0 && (
                          <Typography variant="body2" color="text.secondary">
                            {formatMetadata(event.metadata)}
                          </Typography>
                        )}
                        
                        <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                          {event.session_id && (
                            <Chip label={`Session: ${event.session_id}`} size="small" variant="outlined" />
                          )}
                          {event.job_id && (
                            <Chip label={`Job: ${event.job_id}`} size="small" variant="outlined" />
                          )}
                        </Box>
                      </CardContent>
                    </Card>
                  </Box>
                </ListItem>
                {index < filteredEvents.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        )}
      </Paper>
    </Box>
  );
};
