import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
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
  IconButton,
  Tooltip,
  LinearProgress
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Refresh,
  Add,
  Delete,
  Visibility
} from '@mui/icons-material';
import { api } from '../services/api';
import { ReplayJob } from '../types';

interface JobMonitorProps {
  jobs: ReplayJob[];
  onJobUpdate: (jobs: ReplayJob[]) => void;
  onError: (message: string) => void;
  onSuccess: (message: string) => void;
}

export const JobMonitor: React.FC<JobMonitorProps> = ({
  jobs,
  onJobUpdate,
  onError,
  onSuccess
}) => {
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newJob, setNewJob] = useState({
    start_block: '',
    end_block: '',
    vm_type: 'anvil',
    config: {}
  });

  const handleCreateJob = async () => {
    try {
      const job = await api.createJob({
        start_block: parseInt(newJob.start_block),
        end_block: parseInt(newJob.end_block),
        vm_type: newJob.vm_type,
        config: newJob.config
      });
      
      onJobUpdate([...jobs, job]);
      onSuccess(`Job ${job.id} created successfully`);
      setCreateDialogOpen(false);
      setNewJob({ start_block: '', end_block: '', vm_type: 'anvil', config: {} });
    } catch (err) {
      onError(`Failed to create job: ${err}`);
    }
  };

  const handleCancelJob = async (jobId: string) => {
    try {
      await api.cancelJob(jobId);
      const updatedJobs = jobs.map(job => 
        job.id === jobId ? { ...job, status: 'cancelled' } : job
      );
      onJobUpdate(updatedJobs);
      onSuccess(`Job ${jobId} cancelled`);
    } catch (err) {
      onError(`Failed to cancel job: ${err}`);
    }
  };

  const refreshJobs = async () => {
    try {
      const updatedJobs = await api.getJobs();
      onJobUpdate(updatedJobs);
    } catch (err) {
      onError('Failed to refresh jobs');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'warning';
      case 'failed': return 'error';
      case 'cancelled': return 'default';
      default: return 'info';
    }
  };

  return (
    <Box>
      <Paper sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Replay Jobs ({jobs.length})
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setCreateDialogOpen(true)}
            >
              Create Job
            </Button>
            <Tooltip title="Refresh">
              <IconButton onClick={refreshJobs}>
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Block Range</TableCell>
                <TableCell>VM Type</TableCell>
                <TableCell>Progress</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {jobs.map((job) => (
                <TableRow key={job.id}>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {job.id.slice(0, 8)}...
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={job.status} 
                      color={getStatusColor(job.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {job.start_block} - {job.end_block}
                  </TableCell>
                  <TableCell>{job.vm_type}</TableCell>
                  <TableCell sx={{ width: 120 }}>
                    {job.status === 'running' && (
                      <Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={job.progress || 0} 
                          sx={{ mb: 0.5 }}
                        />
                        <Typography variant="caption">
                          {job.progress || 0}%
                        </Typography>
                      </Box>
                    )}
                  </TableCell>
                  <TableCell>
                    {new Date(job.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Tooltip title="View Details">
                        <IconButton size="small">
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      {(job.status === 'running' || job.status === 'pending') && (
                        <Tooltip title="Cancel">
                          <IconButton 
                            size="small" 
                            onClick={() => handleCancelJob(job.id)}
                          >
                            <Stop />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Replay Job</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Start Block"
              type="number"
              value={newJob.start_block}
              onChange={(e) => setNewJob({ ...newJob, start_block: e.target.value })}
              fullWidth
            />
            <TextField
              label="End Block"
              type="number"
              value={newJob.end_block}
              onChange={(e) => setNewJob({ ...newJob, end_block: e.target.value })}
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>VM Type</InputLabel>
              <Select
                value={newJob.vm_type}
                onChange={(e) => setNewJob({ ...newJob, vm_type: e.target.value })}
              >
                <MenuItem value="anvil">Anvil</MenuItem>
                <MenuItem value="hardhat">Hardhat</MenuItem>
                <MenuItem value="geth">Geth</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateJob} 
            variant="contained"
            disabled={!newJob.start_block || !newJob.end_block}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
