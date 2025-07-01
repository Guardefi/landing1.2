import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import {
  AlertTriangle,
  CheckCircle,
  Download,
  Eye,
  Filter,
  RefreshCw,
  Search,
  Shield,
  TrendingUp,
  Users,
  XCircle,
} from 'lucide-react';
import { toast } from 'sonner';

interface AuditEvent {
  event_id: string;
  timestamp: string;
  event_type: string;
  user_id: string;
  org_id: string;
  resource_type: string;
  resource_id: string;
  action: string;
  ip_address?: string;
  user_agent?: string;
  details: Record<string, any>;
  success: boolean;
  risk_score?: number;
  content_hash: string;
  signature: string;
  qldb_document_id?: string;
  postgres_block_hash: string;
  chain_position: number;
}

interface AuditProof {
  event_id: string;
  content_hash: string;
  signature: string;
  qldb_document_id?: string;
  postgres_block_hash: string;
  chain_position: number;
  verified: boolean;
}

interface ChainVerification {
  verified: boolean;
  total_blocks: number;
  verified_blocks: number;
  broken_chains: number[];
  invalid_signatures: number[];
  missing_blocks: number[];
  verification_timestamp: string;
}

interface DashboardStats {
  total_events: number;
  recent_events: AuditEvent[];
  event_type_distribution: Record<string, number>;
  security_metrics: {
    failed_access_attempts: number;
    total_access_attempts: number;
  };
  chain_status: {
    verified: boolean;
    last_verification: string;
  };
}

const AuditTrail: React.FC = () => {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [chainVerification, setChainVerification] = useState<ChainVerification | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<AuditEvent | null>(null);
  const [selectedProof, setSelectedProof] = useState<AuditProof | null>(null);
  const [filters, setFilters] = useState({
    event_type: '',
    resource_type: '',
    user_id: '',
    start_time: '',
    end_time: '',
  });

  useEffect(() => {
    loadDashboardStats();
    loadAuditEvents();
  }, []);

  const loadDashboardStats = async () => {
    try {
      const response = await fetch('/api/audit/dashboard/stats');
      if (response.ok) {
        const stats = await response.json();
        setDashboardStats(stats);
      }
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
      toast.error('Failed to load dashboard statistics');
    }
  };

  const loadAuditEvents = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });

      const response = await fetch(`/api/audit/events?${params}`);
      if (response.ok) {
        const events = await response.json();
        setEvents(events);
      } else {
        toast.error('Failed to load audit events');
      }
    } catch (error) {
      console.error('Failed to load audit events:', error);
      toast.error('Failed to load audit events');
    } finally {
      setLoading(false);
    }
  };

  const verifyChain = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/audit/verify-chain', { method: 'POST' });
      if (response.ok) {
        const verification = await response.json();
        setChainVerification(verification);
        toast.success('Chain verification completed');
      } else {
        toast.error('Failed to verify chain');
      }
    } catch (error) {
      console.error('Failed to verify chain:', error);
      toast.error('Failed to verify chain');
    } finally {
      setLoading(false);
    }
  };

  const exportEvents = async (format: 'csv' | 'json') => {
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      params.append('format', format);

      const response = await fetch(`/api/audit/export?${params}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `audit_export_${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        toast.success(`Audit events exported as ${format.toUpperCase()}`);
      } else {
        toast.error('Failed to export audit events');
      }
    } catch (error) {
      console.error('Failed to export events:', error);
      toast.error('Failed to export audit events');
    }
  };

  const getProof = async (eventId: string) => {
    try {
      const response = await fetch(`/api/audit/events/${eventId}/proof`);
      if (response.ok) {
        const proof = await response.json();
        setSelectedProof(proof);
      } else {
        toast.error('Failed to get audit proof');
      }
    } catch (error) {
      console.error('Failed to get proof:', error);
      toast.error('Failed to get audit proof');
    }
  };

  const getRiskBadgeColor = (riskScore?: number) => {
    if (!riskScore) return 'secondary';
    if (riskScore >= 75) return 'destructive';
    if (riskScore >= 50) return 'destructive';
    if (riskScore >= 25) return 'default';
    return 'secondary';
  };

  const getEventTypeIcon = (eventType: string) => {
    switch (eventType) {
      case 'access_control':
        return <Shield className="h-4 w-4" />;
      case 'user_authentication':
        return <Users className="h-4 w-4" />;
      case 'data_access':
        return <Eye className="h-4 w-4" />;
      default:
        return <AlertTriangle className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Audit Trail</h1>
          <p className="text-muted-foreground">
            Immutable audit logs with cryptographic verification
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={verifyChain} disabled={loading}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Verify Chain
          </Button>
          <Button variant="outline" onClick={() => exportEvents('csv')}>
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
          <Button variant="outline" onClick={() => exportEvents('json')}>
            <Download className="mr-2 h-4 w-4" />
            Export JSON
          </Button>
        </div>
      </div>

      <Tabs defaultValue="dashboard" className="space-y-4">
        <TabsList>
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="events">Events</TabsTrigger>
          <TabsTrigger value="verification">Chain Verification</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-4">
          {dashboardStats && (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Events</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{dashboardStats.total_events}</div>
                  <p className="text-xs text-muted-foreground">Recent activity</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Chain Status</CardTitle>
                  {dashboardStats.chain_status.verified ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-600" />
                  )}
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {dashboardStats.chain_status.verified ? 'Verified' : 'Invalid'}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Last verified: {new Date(dashboardStats.chain_status.last_verification).toLocaleString()}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Access Attempts</CardTitle>
                  <Shield className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{dashboardStats.security_metrics.total_access_attempts}</div>
                  <p className="text-xs text-muted-foreground">
                    {dashboardStats.security_metrics.failed_access_attempts} failed
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {Math.round(
                      ((dashboardStats.security_metrics.total_access_attempts - 
                        dashboardStats.security_metrics.failed_access_attempts) /
                        dashboardStats.security_metrics.total_access_attempts) * 100
                    )}%
                  </div>
                  <p className="text-xs text-muted-foreground">Authentication success</p>
                </CardContent>
              </Card>
            </div>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Recent Events</CardTitle>
              <CardDescription>Latest audit trail entries</CardDescription>
            </CardHeader>
            <CardContent>
              {dashboardStats?.recent_events.map((event) => (
                <div key={event.event_id} className="flex items-center space-x-4 py-2">
                  <div className="flex items-center space-x-2">
                    {getEventTypeIcon(event.event_type)}
                    <Badge variant={event.success ? 'default' : 'destructive'}>
                      {event.event_type}
                    </Badge>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{event.action}</p>
                    <p className="text-xs text-muted-foreground">
                      {event.resource_type}:{event.resource_id}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">
                      {new Date(event.timestamp).toLocaleString()}
                    </p>
                    {event.risk_score && (
                      <Badge variant={getRiskBadgeColor(event.risk_score)} className="text-xs">
                        Risk: {event.risk_score}
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="h-5 w-5" />
                Filters
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
                <div className="space-y-2">
                  <Label htmlFor="event_type">Event Type</Label>
                  <Select
                    value={filters.event_type}
                    onValueChange={(value) => setFilters({ ...filters, event_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All types" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All types</SelectItem>
                      <SelectItem value="access_control">Access Control</SelectItem>
                      <SelectItem value="user_authentication">Authentication</SelectItem>
                      <SelectItem value="data_access">Data Access</SelectItem>
                      <SelectItem value="configuration_change">Configuration</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="resource_type">Resource Type</Label>
                  <Select
                    value={filters.resource_type}
                    onValueChange={(value) => setFilters({ ...filters, resource_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All resources" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All resources</SelectItem>
                      <SelectItem value="scanner">Scanner</SelectItem>
                      <SelectItem value="reports">Reports</SelectItem>
                      <SelectItem value="users">Users</SelectItem>
                      <SelectItem value="settings">Settings</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="user_id">User ID</Label>
                  <Input
                    id="user_id"
                    placeholder="Filter by user"
                    value={filters.user_id}
                    onChange={(e) => setFilters({ ...filters, user_id: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="start_time">Start Time</Label>
                  <Input
                    id="start_time"
                    type="datetime-local"
                    value={filters.start_time}
                    onChange={(e) => setFilters({ ...filters, start_time: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="end_time">End Time</Label>
                  <Input
                    id="end_time"
                    type="datetime-local"
                    value={filters.end_time}
                    onChange={(e) => setFilters({ ...filters, end_time: e.target.value })}
                  />
                </div>
              </div>
              <div className="mt-4">
                <Button onClick={loadAuditEvents} disabled={loading}>
                  <Search className="mr-2 h-4 w-4" />
                  Apply Filters
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Audit Events</CardTitle>
              <CardDescription>Cryptographically signed audit trail</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Event Type</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Resource</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Risk</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {events.map((event) => (
                    <TableRow key={event.event_id}>
                      <TableCell className="text-xs">
                        {new Date(event.timestamp).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          {getEventTypeIcon(event.event_type)}
                          <span className="text-xs">{event.event_type}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-xs">{event.user_id}</TableCell>
                      <TableCell className="text-xs">{event.action}</TableCell>
                      <TableCell className="text-xs">
                        {event.resource_type}:{event.resource_id}
                      </TableCell>
                      <TableCell>
                        <Badge variant={event.success ? 'default' : 'destructive'}>
                          {event.success ? 'Success' : 'Failed'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {event.risk_score && (
                          <Badge variant={getRiskBadgeColor(event.risk_score)}>
                            {event.risk_score}
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setSelectedEvent(event)}
                              >
                                <Eye className="h-3 w-3" />
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="max-w-2xl">
                              <DialogHeader>
                                <DialogTitle>Event Details</DialogTitle>
                                <DialogDescription>
                                  Audit event information and metadata
                                </DialogDescription>
                              </DialogHeader>
                              {selectedEvent && (
                                <div className="space-y-4">
                                  <div className="grid gap-4 md:grid-cols-2">
                                    <div>
                                      <Label>Event ID</Label>
                                      <p className="text-sm font-mono">{selectedEvent.event_id}</p>
                                    </div>
                                    <div>
                                      <Label>Chain Position</Label>
                                      <p className="text-sm">{selectedEvent.chain_position}</p>
                                    </div>
                                    <div>
                                      <Label>Content Hash</Label>
                                      <p className="text-sm font-mono break-all">{selectedEvent.content_hash}</p>
                                    </div>
                                    <div>
                                      <Label>Block Hash</Label>
                                      <p className="text-sm font-mono break-all">{selectedEvent.postgres_block_hash}</p>
                                    </div>
                                  </div>
                                  <div>
                                    <Label>Details</Label>
                                    <pre className="text-xs bg-muted p-2 rounded mt-1 overflow-auto">
                                      {JSON.stringify(selectedEvent.details, null, 2)}
                                    </pre>
                                  </div>
                                </div>
                              )}
                            </DialogContent>
                          </Dialog>

                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => getProof(event.event_id)}
                          >
                            <Shield className="h-3 w-3" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="verification" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Chain Verification</CardTitle>
              <CardDescription>
                Verify the integrity of the audit chain using cryptographic proofs
              </CardDescription>
            </CardHeader>
            <CardContent>
              {chainVerification ? (
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    {chainVerification.verified ? (
                      <CheckCircle className="h-6 w-6 text-green-600" />
                    ) : (
                      <XCircle className="h-6 w-6 text-red-600" />
                    )}
                    <span className="text-lg font-semibold">
                      Chain {chainVerification.verified ? 'Verified' : 'Invalid'}
                    </span>
                  </div>

                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <Label>Total Blocks</Label>
                      <p className="text-2xl font-bold">{chainVerification.total_blocks}</p>
                    </div>
                    <div>
                      <Label>Verified Blocks</Label>
                      <p className="text-2xl font-bold text-green-600">
                        {chainVerification.verified_blocks}
                      </p>
                    </div>
                    <div>
                      <Label>Verification Progress</Label>
                      <Progress
                        value={(chainVerification.verified_blocks / chainVerification.total_blocks) * 100}
                        className="mt-2"
                      />
                    </div>
                  </div>

                  {chainVerification.broken_chains.length > 0 && (
                    <div>
                      <Label>Broken Chain Links</Label>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {chainVerification.broken_chains.map((block) => (
                          <Badge key={block} variant="destructive">
                            Block {block}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {chainVerification.invalid_signatures.length > 0 && (
                    <div>
                      <Label>Invalid Signatures</Label>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {chainVerification.invalid_signatures.map((block) => (
                          <Badge key={block} variant="destructive">
                            Block {block}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {chainVerification.missing_blocks.length > 0 && (
                    <div>
                      <Label>Missing Blocks</Label>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {chainVerification.missing_blocks.map((block) => (
                          <Badge key={block} variant="destructive">
                            Block {block}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  <div>
                    <Label>Verification Timestamp</Label>
                    <p className="text-sm text-muted-foreground">
                      {new Date(chainVerification.verification_timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground mb-4">
                    Click "Verify Chain" to check the integrity of the audit trail
                  </p>
                  <Button onClick={verifyChain} disabled={loading}>
                    <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                    Verify Chain
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Proof Dialog */}
      <Dialog open={!!selectedProof} onOpenChange={() => setSelectedProof(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Cryptographic Proof</DialogTitle>
            <DialogDescription>
              Verification details for audit event
            </DialogDescription>
          </DialogHeader>
          {selectedProof && (
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                {selectedProof.verified ? (
                  <CheckCircle className="h-6 w-6 text-green-600" />
                ) : (
                  <XCircle className="h-6 w-6 text-red-600" />
                )}
                <span className="text-lg font-semibold">
                  Proof {selectedProof.verified ? 'Valid' : 'Invalid'}
                </span>
              </div>

              <div className="grid gap-4">
                <div>
                  <Label>Event ID</Label>
                  <p className="text-sm font-mono break-all">{selectedProof.event_id}</p>
                </div>
                <div>
                  <Label>Content Hash</Label>
                  <p className="text-sm font-mono break-all">{selectedProof.content_hash}</p>
                </div>
                <div>
                  <Label>Digital Signature</Label>
                  <p className="text-xs font-mono break-all bg-muted p-2 rounded">
                    {selectedProof.signature}
                  </p>
                </div>
                <div>
                  <Label>Postgres Block Hash</Label>
                  <p className="text-sm font-mono break-all">{selectedProof.postgres_block_hash}</p>
                </div>
                <div>
                  <Label>Chain Position</Label>
                  <p className="text-sm">{selectedProof.chain_position}</p>
                </div>
                {selectedProof.qldb_document_id && (
                  <div>
                    <Label>QLDB Document ID</Label>
                    <p className="text-sm font-mono">{selectedProof.qldb_document_id}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AuditTrail;