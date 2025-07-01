import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Switch,
  FormControlLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  PlayArrow,
  Settings,
  TrendingUp,
  Security,
  Speed,
  Extension as PluginIcon,
  Refresh,
  Stop,
  Visibility
} from '@mui/icons-material';
import { api } from '../services/api';
import { AnalysisPlugin, AnalysisResult } from '../types';

interface PluginDashboardProps {
  onError: (message: string) => void;
  onSuccess: (message: string) => void;
}

export const PluginDashboard: React.FC<PluginDashboardProps> = ({
  onError,
  onSuccess
}) => {
  const [plugins, setPlugins] = useState<AnalysisPlugin[]>([]);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [runDialogOpen, setRunDialogOpen] = useState(false);
  const [selectedPlugin, setSelectedPlugin] = useState<AnalysisPlugin | null>(null);
  const [analysisConfig, setAnalysisConfig] = useState({
    session_id: '',
    job_id: '',
    config: {}
  });

  // Generate demo plugins if no real data available
  const generateDemoPlugins = (): AnalysisPlugin[] => {
    return [
      {
        id: 'gas-analyzer',
        name: 'Gas Usage Analyzer',
        version: '1.0.0',
        description: 'Analyzes gas consumption patterns in transactions',
        author: 'Time Machine Team',
        plugin_type: 'gas',
        config_schema: {
          max_gas_limit: { type: 'number', default: 30000000 },
          analyze_opcodes: { type: 'boolean', default: true }
        },
        is_enabled: true
      },
      {
        id: 'security-checker',
        name: 'Security Vulnerability Scanner',
        version: '2.1.0',
        description: 'Scans for common smart contract vulnerabilities',
        author: 'Security Team',
        plugin_type: 'security',
        config_schema: {
          check_reentrancy: { type: 'boolean', default: true },
          check_overflow: { type: 'boolean', default: true }
        },
        is_enabled: true
      },
      {
        id: 'defi-analyzer',
        name: 'DeFi Protocol Analyzer',
        version: '0.8.0',
        description: 'Analyzes DeFi protocol interactions and MEV opportunities',
        author: 'DeFi Team',
        plugin_type: 'defi',
        config_schema: {
          protocols: { type: 'array', default: ['uniswap', 'compound'] },
          min_value_usd: { type: 'number', default: 1000 }
        },
        is_enabled: false
      }
    ];
  };

  // Generate demo analysis results
  const generateDemoResults = (): AnalysisResult[] => {
    return [
      {
        id: 'result-1',
        plugin_id: 'gas-analyzer',
        session_id: 'session-1',
        job_id: 'job-1',
        status: 'completed',
        created_at: new Date(Date.now() - 3600000).toISOString(),
        completed_at: new Date(Date.now() - 3500000).toISOString(),
        results: {
          total_gas_used: 2500000,
          average_gas_per_tx: 125000,
          gas_efficiency_score: 85,
          recommendations: [
            'Consider using more efficient opcodes',
            'Batch similar operations to reduce overhead'
          ]
        },
        metadata: {
          blocks_analyzed: 100,
          transactions_count: 20
        }
      },
      {
        id: 'result-2',
        plugin_id: 'security-checker',
        session_id: 'session-1',
        job_id: 'job-2',
        status: 'running',
        created_at: new Date(Date.now() - 1800000).toISOString(),
        results: {},
        metadata: {
          progress: 65,
          contracts_scanned: 13
        }
      }
    ];
  };

  const loadPlugins = async () => {
    setLoading(true);
    try {
      try {
        const pluginData = await api.getPlugins();
        setPlugins(pluginData);
        onSuccess('Plugins loaded successfully');
      } catch (apiError) {
        // Fallback to demo data
        const demoPlugins = generateDemoPlugins();
        setPlugins(demoPlugins);
        onError('Using demo plugins - backend plugins not available');
      }
    } catch (error) {
      onError(`Failed to load plugins: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const loadResults = async () => {
    try {
      try {
        const results = await api.getAnalysisResults();
        setAnalysisResults(results);
      } catch (apiError) {
        // Fallback to demo data
        const demoResults = generateDemoResults();
        setAnalysisResults(demoResults);
      }
    } catch (error) {
      onError(`Failed to load analysis results: ${error}`);
    }
  };

  useEffect(() => {
    loadPlugins();
    loadResults();
  }, []);

  const handleRunAnalysis = async () => {
    if (!selectedPlugin) return;

    try {
      const result = await api.runAnalysis({
        plugin_id: selectedPlugin.id,
        session_id: analysisConfig.session_id || undefined,
        job_id: analysisConfig.job_id || undefined,
        config: analysisConfig.config
      });

      setAnalysisResults(prev => [...prev, result]);
      onSuccess(`Analysis ${result.id} started`);
      setRunDialogOpen(false);
      setSelectedPlugin(null);
      setAnalysisConfig({ session_id: '', job_id: '', config: {} });
    } catch (err) {
      // For demo purposes, create a mock result
      const mockResult: AnalysisResult = {
        id: `result-${Date.now()}`,
        plugin_id: selectedPlugin.id,
        session_id: analysisConfig.session_id || 'demo-session',
        job_id: analysisConfig.job_id || 'demo-job',
        status: 'running',
        created_at: new Date().toISOString(),
        results: {},
        metadata: { progress: 0 }
      };
      setAnalysisResults(prev => [...prev, mockResult]);
      onSuccess(`Demo analysis ${mockResult.id} started`);
      setRunDialogOpen(false);
      setSelectedPlugin(null);
      setAnalysisConfig({ session_id: '', job_id: '', config: {} });
    }
  };

  const getPluginTypeIcon = (type: string) => {
    switch (type) {
      case 'gas': return <Speed />;
      case 'security': return <Security />;
      case 'defi': return <TrendingUp />;
      default: return <PluginIcon />;
    }
  };

  const getPluginTypeColor = (type: string) => {
    switch (type) {
      case 'gas': return '#ff9800';
      case 'security': return '#f44336';
      case 'defi': return '#4caf50';
      default: return '#2196f3';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const formatDuration = (start: string, end?: string) => {
    const startTime = new Date(start);
    const endTime = end ? new Date(end) : new Date();
    const duration = Math.floor((endTime.getTime() - startTime.getTime()) / 1000);
    
    if (duration < 60) return `${duration}s`;
    if (duration < 3600) return `${Math.floor(duration / 60)}m ${duration % 60}s`;
    return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`;
  };

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PluginIcon />
            Analysis Plugins ({plugins.length})
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Refresh plugins">
              <IconButton onClick={loadPlugins} disabled={loading}>
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={2}>
            {plugins.map((plugin) => (
              <Grid item xs={12} md={6} lg={4} key={plugin.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Box sx={{ color: getPluginTypeColor(plugin.plugin_type) }}>
                        {getPluginTypeIcon(plugin.plugin_type)}
                      </Box>
                      <Typography variant="h6" component="div">
                        {plugin.name}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                      <Chip 
                        label={plugin.plugin_type} 
                        size="small"
                        sx={{ backgroundColor: getPluginTypeColor(plugin.plugin_type), color: 'white' }}
                      />
                      <Chip label={`v${plugin.version}`} size="small" variant="outlined" />
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {plugin.description}
                    </Typography>
                    
                    <Typography variant="caption" color="text.secondary">
                      By {plugin.author}
                    </Typography>
                  </CardContent>
                  
                  <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                    <FormControlLabel
                      control={
                        <Switch 
                          checked={plugin.is_enabled} 
                          size="small"
                          onChange={() => {
                            setPlugins(prev => 
                              prev.map(p => 
                                p.id === plugin.id 
                                  ? { ...p, is_enabled: !p.is_enabled }
                                  : p
                              )
                            );
                          }}
                        />
                      }
                      label="Enabled"
                    />
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Tooltip title="Configure">
                        <IconButton size="small">
                          <Settings />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Run Analysis">
                        <IconButton 
                          size="small" 
                          color="primary"
                          disabled={!plugin.is_enabled}
                          onClick={() => {
                            setSelectedPlugin(plugin);
                            setRunDialogOpen(true);
                          }}
                        >
                          <PlayArrow />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {plugins.length === 0 && !loading && (
          <Box sx={{ textAlign: 'center', p: 4 }}>
            <PluginIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No plugins available
            </Typography>
            <Typography color="text.secondary">
              Install analysis plugins to enhance your forensic capabilities
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Analysis Results */}
      <Paper sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Recent Analysis Results ({analysisResults.length})
          </Typography>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadResults}
            size="small"
          >
            Refresh
          </Button>
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Plugin</TableCell>
                <TableCell>Session/Job</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Results</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {analysisResults.map((result) => {
                const plugin = plugins.find(p => p.id === result.plugin_id);
                return (
                  <TableRow key={result.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {plugin && (
                          <Box sx={{ color: getPluginTypeColor(plugin.plugin_type) }}>
                            {getPluginTypeIcon(plugin.plugin_type)}
                          </Box>
                        )}
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {plugin?.name || result.plugin_id}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {result.id}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box>
                        {result.session_id && (
                          <Typography variant="caption" display="block">
                            Session: {result.session_id}
                          </Typography>
                        )}
                        {result.job_id && (
                          <Typography variant="caption" display="block">
                            Job: {result.job_id}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={result.status}
                        color={getStatusColor(result.status) as any}
                        size="small"
                      />
                      {result.metadata?.progress && (
                        <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                          {result.metadata.progress}%
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatDuration(result.created_at, result.completed_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {result.results && Object.keys(result.results).length > 0 ? (
                        <Typography variant="body2" color="success.main">
                          {Object.keys(result.results).length} items
                        </Typography>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          No results yet
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="View Results">
                          <IconButton size="small">
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        {result.status === 'running' && (
                          <Tooltip title="Stop Analysis">
                            <IconButton size="small" color="error">
                              <Stop />
                            </IconButton>
                          </Tooltip>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>

        {analysisResults.length === 0 && (
          <Box sx={{ textAlign: 'center', p: 4 }}>
            <TrendingUp sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No analysis results
            </Typography>
            <Typography color="text.secondary">
              Run a plugin analysis to see results here
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Run Analysis Dialog */}
      <Dialog open={runDialogOpen} onClose={() => setRunDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Run Analysis: {selectedPlugin?.name}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {selectedPlugin?.description}
          </Typography>
          
          <TextField
            margin="dense"
            label="Session ID (optional)"
            fullWidth
            variant="outlined"
            value={analysisConfig.session_id}
            onChange={(e) => setAnalysisConfig(prev => ({ ...prev, session_id: e.target.value }))}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            label="Job ID (optional)"
            fullWidth
            variant="outlined"
            value={analysisConfig.job_id}
            onChange={(e) => setAnalysisConfig(prev => ({ ...prev, job_id: e.target.value }))}
            sx={{ mb: 2 }}
          />
          
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Plugin Configuration
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Advanced configuration options will be available in a future version.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRunDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleRunAnalysis} variant="contained">
            Run Analysis
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
