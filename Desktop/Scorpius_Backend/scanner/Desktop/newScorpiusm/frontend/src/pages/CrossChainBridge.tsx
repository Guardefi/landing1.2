import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  GitBranch,
  DollarSign,
  Clock,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  Wallet,
  Network,
  TrendingUp,
} from 'lucide-react';

interface BridgeTransfer {
  id: string;
  fromChain: string;
  toChain: string;
  amount: number;
  token: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  timestamp: string;
  txHash: string;
  estimatedTime: number;
  currentStep: number;
  totalSteps: number;
}

interface LiquidityPool {
  id: string;
  chain: string;
  token: string;
  totalLiquidity: number;
  apy: number;
  volume24h: number;
  userShare: number;
}

const supportedChains = [
  { id: 'ethereum', name: 'Ethereum', icon: '⟠' },
  { id: 'polygon', name: 'Polygon', icon: '⬟' },
  { id: 'arbitrum', name: 'Arbitrum', icon: '▲' },
  { id: 'optimism', name: 'Optimism', icon: '○' },
  { id: 'avalanche', name: 'Avalanche', icon: '🔺' },
  { id: 'bsc', name: 'BSC', icon: '🟡' },
];

const mockTransfers: BridgeTransfer[] = [
  {
    id: '1',
    fromChain: 'Ethereum',
    toChain: 'Polygon',
    amount: 1.5,
    token: 'ETH',
    status: 'processing',
    timestamp: '2 minutes ago',
    txHash: '0x1234...5678',
    estimatedTime: 300,
    currentStep: 2,
    totalSteps: 3,
  },
  {
    id: '2',
    fromChain: 'Polygon',
    toChain: 'Arbitrum',
    amount: 1000,
    token: 'USDC',
    status: 'completed',
    timestamp: '15 minutes ago',
    txHash: '0xabcd...efgh',
    estimatedTime: 180,
    currentStep: 3,
    totalSteps: 3,
  },
];

const mockPools: LiquidityPool[] = [
  {
    id: '1',
    chain: 'Ethereum',
    token: 'ETH/USDC',
    totalLiquidity: 12500000,
    apy: 8.5,
    volume24h: 2800000,
    userShare: 0.05,
  },
  {
    id: '2',
    chain: 'Polygon',
    token: 'MATIC/USDC',
    totalLiquidity: 8200000,
    apy: 12.3,
    volume24h: 1900000,
    userShare: 0.12,
  },
];

export function CrossChainBridge() {
  const [transfers, setTransfers] = useState<BridgeTransfer[]>(mockTransfers);
  const [transferAmount, setTransferAmount] = useState('');
  const [fromChain, setFromChain] = useState('');
  const [toChain, setToChain] = useState('');
  const [selectedToken, setSelectedToken] = useState('');

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-500';
      case 'processing':
        return 'text-yellow-500';
      case 'pending':
        return 'text-blue-500';
      case 'failed':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'processing':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const initiateTransfer = () => {
    if (transferAmount && fromChain && toChain && selectedToken) {
      const newTransfer: BridgeTransfer = {
        id: Date.now().toString(),
        fromChain,
        toChain,
        amount: parseFloat(transferAmount),
        token: selectedToken,
        status: 'pending',
        timestamp: 'Just now',
        txHash: '0x' + Math.random().toString(16).substr(2, 8) + '...',
        estimatedTime: 300,
        currentStep: 1,
        totalSteps: 3,
      };
      setTransfers(prev => [newTransfer, ...prev]);
      setTransferAmount('');
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #181a1b 0%, #004242 50%, #181a1b 100%)',
        padding: '24px',
        fontFamily: 'ui-monospace, SFMono-Regular, monospace',
      }}
    >
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '32px' }}>
          <div>
            <h1
              style={{
                fontSize: '32px',
                fontWeight: '700',
                color: '#00ff88',
                letterSpacing: '2px',
                textShadow: '0 0 20px rgba(0, 255, 136, 0.6)',
                marginBottom: '8px',
              }}
            >
              CROSS-CHAIN BRIDGE NETWORK
            </h1>
            <p style={{ color: '#a8a095', letterSpacing: '1px' }}>
              Seamless multi-chain asset transfers and liquidity management
            </p>
          </div>
        </div>

        {/* Bridge Statistics */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '24px',
            marginBottom: '32px',
          }}
        >
          <Card
            style={{
              background:
                'linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(0, 0, 0, 0.2))',
              border: '1px solid rgba(0, 255, 255, 0.3)',
            }}
          >
            <CardHeader
              style={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '8px',
              }}
            >
              <CardTitle
                style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#cccccc',
                }}
              >
                Total Volume
              </CardTitle>
              <DollarSign className="h-4 w-4" style={{ color: '#00ffff' }} />
            </CardHeader>
            <CardContent>
              <div
                style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#00ffff',
                }}
              >
                $47.2M
              </div>
              <p style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                24h volume
              </p>
            </CardContent>
          </Card>

          <Card
            style={{
              background:
                'linear-gradient(135deg, rgba(147, 51, 234, 0.1), rgba(0, 0, 0, 0.2))',
              border: '1px solid rgba(147, 51, 234, 0.3)',
            }}
          >
            <CardHeader
              style={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '8px',
              }}
            >
              <CardTitle
                style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#cccccc',
                }}
              >
                Total Transfers
              </CardTitle>
              <GitBranch className="h-4 w-4" style={{ color: '#9333ea' }} />
            </CardHeader>
            <CardContent>
              <div
                style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#9333ea',
                }}
              >
                2,847
              </div>
              <p style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                Successfully completed
              </p>
            </CardContent>
          </Card>

          <Card
            style={{
              background:
                'linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 0, 0, 0.2))',
              border: '1px solid rgba(0, 255, 136, 0.3)',
            }}
          >
            <CardHeader
              style={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '8px',
              }}
            >
              <CardTitle
                style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#cccccc',
                }}
              >
                Success Rate
              </CardTitle>
              <CheckCircle className="h-4 w-4" style={{ color: '#00ff88' }} />
            </CardHeader>
            <CardContent>
              <div
                style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#00ff88',
                }}
              >
                99.8%
              </div>
              <p style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                Bridge reliability
              </p>
            </CardContent>
          </Card>

          <Card
            style={{
              background:
                'linear-gradient(135deg, rgba(255, 170, 0, 0.1), rgba(0, 0, 0, 0.2))',
              border: '1px solid rgba(255, 170, 0, 0.3)',
            }}
          >
            <CardHeader
              style={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '8px',
              }}
            >
              <CardTitle
                style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#cccccc',
                }}
              >
                Avg. Time
              </CardTitle>
              <Clock className="h-4 w-4" style={{ color: '#ffaa00' }} />
            </CardHeader>
            <CardContent>
              <div
                style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#ffaa00',
                }}
              >
                3.2min
              </div>
              <p style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                Average completion
              </p>
            </CardContent>
          </Card>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '24px',
            marginBottom: '32px',
          }}
        >
          {/* Bridge Transfer Interface */}
          <Card
            style={{
              background: 'rgba(0, 0, 0, 0.6)',
              border: '1px solid rgba(0, 255, 136, 0.3)',
            }}
          >
            <CardHeader>
              <CardTitle
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: '#00ff88',
                }}
              >
                <GitBranch className="h-5 w-5" />
                <span>Bridge Assets</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '16px',
                }}
              >
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '16px',
                  }}
                >
                  <div>
                    <label
                      style={{
                        fontSize: '14px',
                        fontWeight: '500',
                        marginBottom: '8px',
                        display: 'block',
                        color: '#cccccc',
                      }}
                    >
                      From Chain
                    </label>
                    <Select value={fromChain} onValueChange={setFromChain}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select chain" />
                      </SelectTrigger>
                      <SelectContent>
                        {supportedChains.map(chain => (
                          <SelectItem key={chain.id} value={chain.name}>
                            {chain.icon} {chain.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label
                      style={{
                        fontSize: '14px',
                        fontWeight: '500',
                        marginBottom: '8px',
                        display: 'block',
                        color: '#cccccc',
                      }}
                    >
                      To Chain
                    </label>
                    <Select value={toChain} onValueChange={setToChain}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select chain" />
                      </SelectTrigger>
                      <SelectContent>
                        {supportedChains.map(chain => (
                          <SelectItem key={chain.id} value={chain.name}>
                            {chain.icon} {chain.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <label
                    style={{
                      fontSize: '14px',
                      fontWeight: '500',
                      marginBottom: '8px',
                      display: 'block',
                      color: '#cccccc',
                    }}
                  >
                    Token
                  </label>
                  <Select value={selectedToken} onValueChange={setSelectedToken}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select token" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ETH">ETH</SelectItem>
                      <SelectItem value="USDC">USDC</SelectItem>
                      <SelectItem value="USDT">USDT</SelectItem>
                      <SelectItem value="WBTC">WBTC</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label
                    style={{
                      fontSize: '14px',
                      fontWeight: '500',
                      marginBottom: '8px',
                      display: 'block',
                      color: '#cccccc',
                    }}
                  >
                    Amount
                  </label>
                  <Input
                    type="number"
                    placeholder="0.0"
                    value={transferAmount}
                    onChange={e => setTransferAmount(e.target.value)}
                  />
                </div>

                <div
                  style={{
                    padding: '12px',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      fontSize: '14px',
                      marginBottom: '8px',
                    }}
                  >
                    <span style={{ color: '#888' }}>Estimated fee:</span>
                    <span style={{ color: '#ffffff' }}>$2.50</span>
                  </div>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      fontSize: '14px',
                      marginBottom: '8px',
                    }}
                  >
                    <span style={{ color: '#888' }}>Estimated time:</span>
                    <span style={{ color: '#ffffff' }}>~3 minutes</span>
                  </div>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      fontSize: '14px',
                      fontWeight: '500',
                    }}
                  >
                    <span style={{ color: '#888' }}>You'll receive:</span>
                    <span style={{ color: '#00ff88' }}>
                      {transferAmount || '0'} {selectedToken}
                    </span>
                  </div>
                </div>

                <Button
                  style={{
                    width: '100%',
                    background: 'linear-gradient(135deg, #00ff88, #00ffff)',
                    border: 'none',
                    color: '#000',
                  }}
                  onClick={initiateTransfer}
                  disabled={!transferAmount || !fromChain || !toChain || !selectedToken}
                >
                  <ArrowRight className="h-4 w-4 mr-2" />
                  Initiate Bridge Transfer
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Active Transfers */}
          <Card
            style={{
              background: 'rgba(0, 0, 0, 0.6)',
              border: '1px solid rgba(255, 170, 0, 0.3)',
            }}
          >
            <CardHeader>
              <CardTitle
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: '#ffaa00',
                }}
              >
                <Clock className="h-5 w-5" />
                <span>Transfer Status</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '16px',
                }}
              >
                {transfers.map(transfer => (
                  <div
                    key={transfer.id}
                    style={{
                      padding: '16px',
                      borderRadius: '8px',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      background: 'rgba(0, 0, 0, 0.3)',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        marginBottom: '12px',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                        }}
                      >
                        {getStatusIcon(transfer.status)}
                        <span style={{ fontWeight: '500', color: '#ffffff' }}>
                          {transfer.amount} {transfer.token}
                        </span>
                      </div>
                      <Badge
                        style={{
                          borderColor: 'rgba(255, 255, 255, 0.3)',
                          background: 'rgba(255, 255, 255, 0.1)',
                        }}
                        className={getStatusColor(transfer.status)}
                      >
                        {transfer.status.toUpperCase()}
                      </Badge>
                    </div>

                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        fontSize: '14px',
                        color: '#888',
                        marginBottom: '12px',
                      }}
                    >
                      <span>{transfer.fromChain}</span>
                      <ArrowRight className="h-4 w-4" />
                      <span>{transfer.toChain}</span>
                    </div>

                    {transfer.status === 'processing' && (
                      <div style={{ marginBottom: '12px' }}>
                        <div
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            fontSize: '14px',
                            marginBottom: '4px',
                          }}
                        >
                          <span style={{ color: '#888' }}>Progress</span>
                          <span style={{ color: '#888' }}>
                            Step {transfer.currentStep} of {transfer.totalSteps}
                          </span>
                        </div>
                        <Progress
                          value={(transfer.currentStep / transfer.totalSteps) * 100}
                        />
                      </div>
                    )}

                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: '12px',
                        color: '#888',
                      }}
                    >
                      <span>{transfer.timestamp}</span>
                      <span style={{ fontFamily: 'monospace' }}>{transfer.txHash}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Liquidity Pools */}
        <Card
          style={{
            background: 'rgba(0, 0, 0, 0.6)',
            border: '1px solid rgba(0, 255, 136, 0.3)',
            marginBottom: '32px',
          }}
        >
          <CardHeader>
            <CardTitle
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: '#00ff88',
              }}
            >
              <Wallet className="h-5 w-5" />
              <span>Liquidity Pools</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '16px',
              }}
            >
              {mockPools.map(pool => (
                <div
                  key={pool.id}
                  style={{
                    padding: '16px',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    background: 'rgba(0, 0, 0, 0.3)',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '16px',
                    }}
                  >
                    <div>
                      <h3 style={{ fontWeight: '500', color: '#ffffff' }}>
                        {pool.token}
                      </h3>
                      <p style={{ fontSize: '14px', color: '#888' }}>{pool.chain}</p>
                    </div>
                    <Badge
                      style={{
                        color: '#00ff88',
                        borderColor: '#00ff88',
                        background: 'rgba(0, 255, 136, 0.1)',
                      }}
                    >
                      {pool.apy}% APY
                    </Badge>
                  </div>

                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '1fr 1fr',
                      gap: '16px',
                      fontSize: '14px',
                      marginBottom: '16px',
                    }}
                  >
                    <div>
                      <p style={{ color: '#888' }}>Total Liquidity</p>
                      <p style={{ fontWeight: '700', color: '#ffffff' }}>
                        {formatCurrency(pool.totalLiquidity)}
                      </p>
                    </div>
                    <div>
                      <p style={{ color: '#888' }}>24h Volume</p>
                      <p style={{ fontWeight: '700', color: '#ffffff' }}>
                        {formatCurrency(pool.volume24h)}
                      </p>
                    </div>
                    <div>
                      <p style={{ color: '#888' }}>Your Share</p>
                      <p style={{ fontWeight: '700', color: '#ffffff' }}>
                        {pool.userShare}%
                      </p>
                    </div>
                    <div>
                      <p style={{ color: '#888' }}>Earnings</p>
                      <p style={{ fontWeight: '700', color: '#00ff88' }}>
                        +
                        {formatCurrency(
                          (((pool.totalLiquidity * pool.userShare) / 100) * pool.apy) /
                            100 /
                            365,
                        )}
                        /day
                      </p>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <Button
                      size="sm"
                      style={{
                        flex: 1,
                        background: 'linear-gradient(135deg, #00ff88, #00ffff)',
                        border: 'none',
                        color: '#000',
                      }}
                    >
                      Add Liquidity
                    </Button>
                    <Button variant="outline" size="sm" style={{ flex: 1 }}>
                      Remove
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Bridge Network Visualization */}
        <Card
          style={{
            background: 'rgba(0, 0, 0, 0.6)',
            border: '1px solid rgba(147, 51, 234, 0.3)',
          }}
        >
          <CardHeader>
            <CardTitle
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: '#9333ea',
              }}
            >
              <Network className="h-5 w-5" />
              <span>Network Overview</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                gap: '16px',
              }}
            >
              {supportedChains.map(chain => (
                <div
                  key={chain.id}
                  style={{
                    textAlign: 'center',
                    padding: '16px',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    background: 'rgba(0, 0, 0, 0.3)',
                  }}
                >
                  <div style={{ fontSize: '32px', marginBottom: '8px' }}>
                    {chain.icon}
                  </div>
                  <p
                    style={{
                      fontWeight: '500',
                      fontSize: '14px',
                      color: '#ffffff',
                      marginBottom: '4px',
                    }}
                  >
                    {chain.name}
                  </p>
                  <p style={{ fontSize: '12px', color: '#888' }}>Active</p>
                  <div
                    style={{
                      width: '8px',
                      height: '8px',
                      background: '#00ff88',
                      borderRadius: '50%',
                      margin: '8px auto 0',
                    }}
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default CrossChainBridge;
