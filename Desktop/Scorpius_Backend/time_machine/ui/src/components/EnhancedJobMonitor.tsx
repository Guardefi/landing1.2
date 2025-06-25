import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { ReplayJob } from '../types';
import { api } from '../services/api';

const EnhancedJobMonitor: React.FC = () => {
  const [jobs, setJobs] = useState<ReplayJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newJob, setNewJob] = useState({
    start_block: 19000000,
    end_block: 19000100,
    vm_type: 'anvil',
    config: { network: 'mainnet' }
  });

  // Load jobs on component mount
  useEffect(() => {
    loadJobs();
    
    // Set up WebSocket for real-time job updates
    const jobWs = api.connectJobStatus((update) => {
      setJobs(prev => prev.map(job =>
        job.id === update.job_id ? { 
          ...job, 
          status: update.status, 
          progress: update.progress,
          error: update.error 
        } : job
      ));
    });

    return () => {
      if (jobWs) jobWs.close();
    };
  }, []);

  const loadJobs = async () => {
    try {
      setLoading(true);
      const jobsData = await api.getJobs();
      setJobs(jobsData);
      setError(null);
    } catch (err) {
      console.error('Failed to load jobs:', err);
      setError('Backend not available. Showing demo data.');
      // Add realistic demo data
      setJobs([
        {
          id: 'job-eth-mainnet-001',
          status: 'running',
          start_block: 19000000,
          end_block: 19000100,
          vm_type: 'anvil',
          created_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
          progress: 73,
          config: { network: 'mainnet', fork_url: 'https://mainnet.infura.io' }
        },
        {
          id: 'job-polygon-defi-002',
          status: 'completed',
          start_block: 51000000,
          end_block: 51000200,
          vm_type: 'foundry',
          created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          completed_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
          progress: 100,
          config: { network: 'polygon', analysis_type: 'defi' }
        },
        {
          id: 'job-arbitrum-nft-003',
          status: 'failed',
          start_block: 150000000,
          end_block: 150000050,
          vm_type: 'hardhat',
          created_at: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
          progress: 45,
          error: 'RPC endpoint unreachable',
          config: { network: 'arbitrum', analysis_type: 'nft' }
        },
        {
          id: 'job-bsc-bridge-004',
          status: 'pending',
          start_block: 34000000,
          end_block: 34000150,
          vm_type: 'anvil',
          created_at: new Date().toISOString(),
          progress: 0,
          config: { network: 'bsc', analysis_type: 'bridge' }
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateJob = async () => {
    try {
      const job = await api.createJob(newJob);
      setJobs(prev => [job, ...prev]);
      setCreateDialogOpen(false);
      setNewJob({ 
        start_block: 19000000, 
        end_block: 19000100, 
        vm_type: 'anvil', 
        config: { network: 'mainnet' } 
      });
      setSuccess('Job created successfully!');
    } catch (err) {
      console.error('Failed to create job:', err);
      // Simulate creating job for demo
      const demoJob: ReplayJob = {
        id: `job-demo-${Date.now()}`,
        status: 'pending',
        start_block: newJob.start_block,
        end_block: newJob.end_block,
        vm_type: newJob.vm_type,
        created_at: new Date().toISOString(),
        progress: 0,
        config: newJob.config
      };
      setJobs(prev => [demoJob, ...prev]);
      setCreateDialogOpen(false);
      setSuccess('Demo job created! (Backend not connected)');
    }
  };

  const handleCancelJob = async (jobId: string) => {
    try {
      await api.cancelJob(jobId);
      setJobs(prev => prev.map(job =>
        job.id === jobId ? { ...job, status: 'cancelled' } : job
      ));
      setSuccess('Job cancelled successfully!');
    } catch (err) {
      console.error('Failed to cancel job:', err);
      // Simulate cancellation for demo
      setJobs(prev => prev.map(job =>
        job.id === jobId ? { ...job, status: 'cancelled' } : job
      ));
      setSuccess('Demo job cancelled! (Backend not connected)');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'primary';
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'cancelled': return 'warning';
      case 'pending': return 'info';
      default: return 'default';
    }
  };

  const formatDuration = (startTime: string, endTime?: string) => {
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const duration = Math.floor((end.getTime() - start.getTime()) / 1000);
    
    if (duration < 60) return `${duration}s`;
    if (duration < 3600) return `${Math.floor(duration / 60)}m ${duration % 60}s`;
    return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`;
  };

  const getNetworkFromConfig = (config: any) => {
    return config?.network || 'Unknown';
  };

  const getAnalysisTypeFromConfig = (config: any) => {
    return config?.analysis_type || 'General';
  };

  if (loading && jobs.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading replay jobs...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header with Actions */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center">
          <TimelineIcon sx={{ mr: 1, fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            Blockchain Replay Jobs
          </Typography>
        </Box>
        <Box>
          <Button
            startIcon={<RefreshIcon />}
            onClick={loadJobs}
            variant="outlined"
            sx={{ mr: 1 }}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Refresh'}
          </Button>
          <Button
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
            variant="contained"
          >
            New Replay Job
          </Button>
        </Box>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="warning" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Jobs Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'background.paper' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Jobs
              </Typography>
              <Typography variant="h3" color="primary">
                {jobs.length}
              </Typography>
              <Typography variant="body2">
                All time
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'primary.dark' }}>
            <CardContent>
              <Typography color="primary.contrastText" gutterBottom>
                Running
              </Typography>
              <Typography variant="h3" color="primary.contrastText">
                {jobs.filter(j => j.status === 'running').length}
              </Typography>
              <Typography variant="body2" color="primary.contrastText">
                Active replays
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'success.dark' }}>
            <CardContent>
              <Typography color="success.contrastText" gutterBottom>
                Completed
              </Typography>
              <Typography variant="h3" color="success.contrastText">
                {jobs.filter(j => j.status === 'completed').length}
              </Typography>
              <Typography variant="body2" color="success.contrastText">
                Successful runs
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'error.dark' }}>
            <CardContent>
              <Typography color="error.contrastText" gutterBottom>
                Failed
              </Typography>
              <Typography variant="h3" color="error.contrastText">
                {jobs.filter(j => j.status === 'failed').length}
              </Typography>
              <Typography variant="body2" color="error.contrastText">
                Need attention
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Jobs Table */}
      <Card>
        <CardHeader 
          title="Replay Job Details" 
          subheader={`${jobs.length} jobs total`}
        />
        <CardContent>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Job ID</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Network</TableCell>
                  <TableCell>Block Range</TableCell>
                  <TableCell>VM Type</TableCell>
                  <TableCell>Progress</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Analysis</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {jobs.map((job) => (
                  <TableRow key={job.id} hover>
                    <TableCell>
                      <Tooltip title={`Full ID: ${job.id}`}>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            fontFamily: 'monospace',
                            backgroundColor: 'action.hover',
                            padding: '2px 6px',
                            borderRadius: 1,
                            display: 'inline-block'
                          }}
                        >
                          {job.id.length > 20 ? `${job.id.substring(0, 20)}...` : job.id}
                        </Typography>
                      </Tooltip>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={job.status.toUpperCase()} 
                        color={getStatusColor(job.status) as any}
                        size="small"
                        variant={job.status === 'running' ? 'filled' : 'outlined'}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={getNetworkFromConfig(job.config)}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {job.start_block.toLocaleString()} - {job.end_block.toLocaleString()}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {(job.end_block - job.start_block).toLocaleString()} blocks
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={job.vm_type} size="small" />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, minWidth: 120 }}>
                        <LinearProgress 
                          variant="determinate" 
                          value={job.progress || 0} 
                          sx={{ 
                            flexGrow: 1, 
                            height: 8, 
                            borderRadius: 4,
                            backgroundColor: 'action.hover'
                          }}
                          color={job.status === 'failed' ? 'error' : 'primary'}
                        />
                        <Typography variant="body2" sx={{ minWidth: 35 }}>
                          {job.progress || 0}%
                        </Typography>
                      </Box>
                      {job.error && (
                        <Typography variant="caption" color="error">
                          {job.error}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatDuration(job.created_at, job.completed_at)}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {job.completed_at ? 'Completed' : 'Running'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={getAnalysisTypeFromConfig(job.config)}
                        size="small"
                        color="secondary"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        {job.status === 'running' && (
                          <Tooltip title="Cancel Job">
                            <IconButton 
                              size="small" 
                              onClick={() => handleCancelJob(job.id)}
                              color="error"
                            >
                              <StopIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="View Details">
                          <IconButton size="small" color="primary">
                            <InfoIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          {jobs.length === 0 && (
            <Box 
              display="flex" 
              flexDirection="column" 
              alignItems="center" 
              justifyContent="center" 
              py={4}
            >
              <TimelineIcon sx={{ fontSize: 64, color: 'action.disabled', mb: 2 }} />
              <Typography variant="h6" color="textSecondary">
                No replay jobs found
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Create your first blockchain replay job to start analysis
              </Typography>
              <Button 
                startIcon={<AddIcon />}
                onClick={() => setCreateDialogOpen(true)}
                variant="contained"
                sx={{ mt: 2 }}
              >
                Create First Job
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Create Job Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Blockchain Replay Job</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
            Replay blockchain transactions to analyze contract behavior, track state changes, and detect patterns.
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <TextField
                label="Start Block"
                type="number"
                value={newJob.start_block}
                onChange={(e) => setNewJob(prev => ({ ...prev, start_block: parseInt(e.target.value) }))}
                fullWidth
                helperText="Starting block number for replay"
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                label="End Block"
                type="number"
                value={newJob.end_block}
                onChange={(e) => setNewJob(prev => ({ ...prev, end_block: parseInt(e.target.value) }))}
                fullWidth
                helperText="Ending block number for replay"
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>VM Type</InputLabel>
                <Select
                  value={newJob.vm_type}
                  onChange={(e) => setNewJob(prev => ({ ...prev, vm_type: e.target.value }))}
                >
                  <MenuItem value="anvil">Anvil (Foundry) - Fast & Accurate</MenuItem>
                  <MenuItem value="hardhat">Hardhat Network - Development</MenuItem>
                  <MenuItem value="ganache">Ganache - Legacy Support</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Network</InputLabel>
                <Select
                  value={newJob.config.network || 'mainnet'}
                  onChange={(e) => setNewJob(prev => ({ 
                    ...prev, 
                    config: { ...prev.config, network: e.target.value }
                  }))}
                >
                  <MenuItem value="mainnet">Ethereum Mainnet</MenuItem>
                  <MenuItem value="polygon">Polygon</MenuItem>
                  <MenuItem value="arbitrum">Arbitrum</MenuItem>
                  <MenuItem value="optimism">Optimism</MenuItem>
                  <MenuItem value="bsc">BSC</MenuItem>
                  <MenuItem value="avalanche">Avalanche</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateJob} 
            variant="contained"
            startIcon={<PlayIcon />}
          >
            Start Replay Job
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Export the component
export default EnhancedJobMonitor;
