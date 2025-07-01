import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  Shield,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Loader2,
  Search,
  Zap,
  Info,
  ExternalLink,
  RefreshCw,
} from 'lucide-react';
import { useWalletCheck, useWalletRevoke } from '@/hooks';
import { WalletCheckRequest, TokenApproval, RevokeRequest } from '@/lib/api/types';
import { toast } from 'sonner';

interface WalletScannerProps {
  className?: string;
  onScanComplete?: (result: any) => void;
  defaultAddress?: string;
}

export function WalletScanner({ className, onScanComplete, defaultAddress }: WalletScannerProps) {
  const [address, setAddress] = useState(defaultAddress || '');
  const [scanResult, setScanResult] = useState<any>(null);
  const [isValidAddress, setIsValidAddress] = useState(false);

  const walletCheckMutation = useWalletCheck();
  const walletRevokeMutation = useWalletRevoke();

  // Validate Ethereum address format
  const validateAddress = (addr: string) => {
    const isValid = /^0x[a-fA-F0-9]{40}$/.test(addr);
    setIsValidAddress(isValid);
    return isValid;
  };

  const handleAddressChange = (value: string) => {
    setAddress(value);
    validateAddress(value);
  };

  const handleScan = async () => {
    if (!isValidAddress) {
      toast.error('Please enter a valid Ethereum address');
      return;
    }

    const request: WalletCheckRequest = {
      address,
      chain_id: 1, // Ethereum mainnet
      include_nfts: false,
    };

    try {
      const result = await walletCheckMutation.mutateAsync(request);
      setScanResult(result);
      onScanComplete?.(result);
      toast.success('Wallet scan completed successfully');
    } catch (error: any) {
      toast.error(`Scan failed: ${error.message || 'Unknown error'}`);
    }
  };

  const handleRevoke = async (approval: TokenApproval) => {
    const request: RevokeRequest = {
      address,
      token_contract: approval.contract_address,
      spender: approval.spender,
    };

    try {
      const result = await walletRevokeMutation.mutateAsync(request);
      toast.success(result.message || 'Revocation submitted successfully');
      
      // Refresh scan after revocation
      handleScan();
    } catch (error: any) {
      toast.error(`Revocation failed: ${error.message || 'Unknown error'}`);
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical':
        return 'text-red-500';
      case 'high':
        return 'text-orange-500';
      case 'medium':
        return 'text-yellow-500';
      case 'low':
        return 'text-green-500';
      default:
        return 'text-gray-500';
    }
  };

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical':
        return <XCircle className="h-4 w-4" />;
      case 'high':
        return <AlertTriangle className="h-4 w-4" />;
      case 'medium':
        return <AlertTriangle className="h-4 w-4" />;
      case 'low':
        return <CheckCircle2 className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const truncateAddress = (addr: string, chars = 6) => {
    return `${addr.slice(0, chars)}...${addr.slice(-chars)}`;
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Scan Input */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-blue-500" />
            Wallet Security Scanner
          </CardTitle>
          <CardDescription>
            Analyze your wallet for token approvals and security risks
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="wallet-address">Wallet Address</Label>
            <div className="flex gap-2">
              <Input
                id="wallet-address"
                placeholder="0x..."
                value={address}
                onChange={(e) => handleAddressChange(e.target.value)}
                className={`flex-1 ${
                  address && !isValidAddress ? 'border-red-500' : ''
                }`}
              />
              <Button
                onClick={handleScan}
                disabled={!isValidAddress || walletCheckMutation.isPending}
                className="px-6"
              >
                {walletCheckMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
                {walletCheckMutation.isPending ? 'Scanning...' : 'Scan'}
              </Button>
            </div>
            {address && !isValidAddress && (
              <p className="text-sm text-red-500">
                Please enter a valid Ethereum address (0x...)
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      <AnimatePresence>
        {walletCheckMutation.isPending && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Card>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Analyzing wallet security...</span>
                  </div>
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Scan Results */}
      <AnimatePresence>
        {scanResult && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Risk Overview */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Shield className="h-5 w-5" />
                    Security Overview
                  </span>
                  <Badge
                    variant={scanResult.risk_level === 'low' ? 'default' : 'destructive'}
                    className={getRiskColor(scanResult.risk_level)}
                  >
                    {scanResult.risk_level.toUpperCase()}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-muted rounded-lg">
                    <div className="text-2xl font-bold">{scanResult.risk_score}</div>
                    <div className="text-sm text-muted-foreground">Risk Score</div>
                    <Progress value={scanResult.risk_score} className="mt-2" />
                  </div>
                  <div className="text-center p-4 bg-muted rounded-lg">
                    <div className="text-2xl font-bold">{scanResult.total_approvals}</div>
                    <div className="text-sm text-muted-foreground">Total Approvals</div>
                  </div>
                  <div className="text-center p-4 bg-muted rounded-lg">
                    <div className="text-2xl font-bold text-red-500">
                      {scanResult.high_risk_approvals}
                    </div>
                    <div className="text-sm text-muted-foreground">High Risk</div>
                  </div>
                </div>

                {/* Recommendations */}
                {scanResult.recommendations && scanResult.recommendations.length > 0 && (
                  <Alert>
                    <Info className="h-4 w-4" />
                    <AlertDescription>
                      <strong>Recommendations:</strong>
                      <ul className="mt-2 list-disc list-inside space-y-1">
                        {scanResult.recommendations.map((rec: string, index: number) => (
                          <li key={index} className="text-sm">{rec}</li>
                        ))}
                      </ul>
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>

            {/* Token Approvals Table */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Token Approvals</span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleScan}
                    disabled={walletCheckMutation.isPending}
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Token</TableHead>
                      <TableHead>Spender</TableHead>
                      <TableHead>Amount</TableHead>
                      <TableHead>Risk</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {scanResult.approvals.map((approval: TokenApproval, index: number) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            {approval.token}
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger>
                                  <ExternalLink className="h-3 w-3 text-muted-foreground" />
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>{approval.contract_address}</p>
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                          </div>
                        </TableCell>
                        <TableCell>
                          <code className="text-sm">
                            {truncateAddress(approval.spender)}
                          </code>
                        </TableCell>
                        <TableCell>
                          <Badge variant={approval.is_unlimited ? 'destructive' : 'secondary'}>
                            {approval.is_unlimited ? 'Unlimited' : 'Limited'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className={`flex items-center gap-1 ${getRiskColor(approval.risk_level)}`}>
                            {getRiskIcon(approval.risk_level)}
                            <span className="capitalize text-sm">{approval.risk_level}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleRevoke(approval)}
                            disabled={walletRevokeMutation.isPending}
                            className="text-red-600 hover:text-red-700"
                          >
                            {walletRevokeMutation.isPending ? (
                              <Loader2 className="h-3 w-3 animate-spin" />
                            ) : (
                              <Zap className="h-3 w-3" />
                            )}
                            Revoke
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                {scanResult.approvals.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No token approvals found for this wallet.</p>
                    <p className="text-sm">This wallet appears to be secure!</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default WalletScanner;
