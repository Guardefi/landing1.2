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
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Add,
  Delete,
  Merge,
  Visibility,
  AccountTree as BranchIcon,
  Refresh
} from '@mui/icons-material';
import { api } from '../services/api';
import { Branch } from '../types';

interface BranchManagerProps {
  onError: (message: string) => void;
  onSuccess: (message: string) => void;
}

export const BranchManager: React.FC<BranchManagerProps> = ({
  onError,
  onSuccess
}) => {
  const [branches, setBranches] = useState<Branch[]>([]);
  const [loading, setLoading] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newBranch, setNewBranch] = useState({
    name: '',
    description: '',
    base_snapshot_id: ''
  });

  // Generate demo branches if no real data available
  const generateDemoBranches = (): Branch[] => {
    return [
      {
        id: 'main-branch',
        name: 'main',
        description: 'Main development branch',
        created_at: new Date(Date.now() - 86400000).toISOString(),
        base_snapshot_id: 'snapshot-1',
        head_snapshot_id: 'snapshot-5',
        author: 'developer',
        tags: ['stable', 'production'],
        is_active: true
      },
      {
        id: 'feature-branch-1',
        name: 'feature/gas-optimization',
        description: 'Optimizing gas usage for smart contracts',
        created_at: new Date(Date.now() - 43200000).toISOString(),
        base_snapshot_id: 'snapshot-3',
        head_snapshot_id: 'snapshot-6',
        author: 'alice',
        tags: ['feature', 'optimization'],
        is_active: false
      },
      {
        id: 'bugfix-branch-1',
        name: 'bugfix/state-corruption',
        description: 'Fix state corruption issue in replay',
        created_at: new Date(Date.now() - 21600000).toISOString(),
        base_snapshot_id: 'snapshot-4',
        head_snapshot_id: 'snapshot-7',
        author: 'bob',
        tags: ['bugfix', 'critical'],
        is_active: false
      }
    ];
  };

  const loadBranches = async () => {
    setLoading(true);
    try {
      try {
        const branchData = await api.getBranches();
        setBranches(branchData);
        onSuccess('Branches loaded successfully');
      } catch (apiError) {
        // Fallback to demo data
        const demoBranches = generateDemoBranches();
        setBranches(demoBranches);
        onError('Using demo data - backend branches not available');
      }
    } catch (error) {
      onError(`Failed to load branches: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBranches();
  }, []);

  const handleCreateBranch = async () => {
    if (!newBranch.name.trim()) {
      onError('Branch name is required');
      return;
    }

    try {
      const branch = await api.createBranch(newBranch);
      setBranches(prev => [...prev, branch]);
      onSuccess(`Branch ${branch.name} created successfully`);
      setCreateDialogOpen(false);
      setNewBranch({ name: '', description: '', base_snapshot_id: '' });
    } catch (err) {
      // For demo purposes, create a mock branch
      const mockBranch: Branch = {
        id: `branch-${Date.now()}`,
        name: newBranch.name,
        description: newBranch.description,
        created_at: new Date().toISOString(),
        base_snapshot_id: newBranch.base_snapshot_id || 'snapshot-1',
        head_snapshot_id: newBranch.base_snapshot_id || 'snapshot-1',
        author: 'current-user',
        tags: [],
        is_active: false
      };
      setBranches(prev => [...prev, mockBranch]);
      onSuccess(`Demo branch ${mockBranch.name} created`);
      setCreateDialogOpen(false);
      setNewBranch({ name: '', description: '', base_snapshot_id: '' });
    }
  };

  const handleDeleteBranch = async (branchId: string) => {
    const branch = branches.find(b => b.id === branchId);
    if (!branch) return;

    if (branch.is_active) {
      onError('Cannot delete active branch');
      return;
    }

    try {
      await api.deleteBranch(branchId);
      setBranches(prev => prev.filter(b => b.id !== branchId));
      onSuccess('Branch deleted successfully');
    } catch (err) {
      // For demo purposes, remove from local state
      setBranches(prev => prev.filter(b => b.id !== branchId));
      onSuccess(`Demo branch ${branch.name} deleted`);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (isActive: boolean) => {
    return isActive ? 'success' : 'default';
  };

  const getStatusText = (isActive: boolean) => {
    return isActive ? 'Active' : 'Inactive';
  };

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <BranchIcon />
            Branches ({branches.length})
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Refresh branches">
              <IconButton onClick={loadBranches} disabled={loading}>
                <Refresh />
              </IconButton>
            </Tooltip>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setCreateDialogOpen(true)}
            >
              Create Branch
            </Button>
          </Box>
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Author</TableCell>
                  <TableCell>Tags</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {branches.map((branch) => (
                  <TableRow key={branch.id}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {branch.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {branch.description || 'No description'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={branch.author} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {branch.tags.map(tag => (
                          <Chip key={tag} label={tag} size="small" />
                        ))}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={getStatusText(branch.is_active)}
                        color={getStatusColor(branch.is_active) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatDate(branch.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="View branch details">
                          <IconButton size="small">
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Merge branch">
                          <IconButton size="small" disabled={branch.is_active}>
                            <Merge />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete branch">
                          <IconButton 
                            size="small" 
                            color="error"
                            disabled={branch.is_active}
                            onClick={() => handleDeleteBranch(branch.id)}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {branches.length === 0 && !loading && (
          <Box sx={{ textAlign: 'center', p: 4 }}>
            <BranchIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No branches found
            </Typography>
            <Typography color="text.secondary">
              Create your first branch to get started
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Create Branch Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Branch</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Branch Name"
            fullWidth
            variant="outlined"
            value={newBranch.name}
            onChange={(e) => setNewBranch(prev => ({ ...prev, name: e.target.value }))}
            placeholder="e.g., feature/new-analysis"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newBranch.description}
            onChange={(e) => setNewBranch(prev => ({ ...prev, description: e.target.value }))}
            placeholder="Describe what this branch is for..."
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Base Snapshot ID"
            fullWidth
            variant="outlined"
            value={newBranch.base_snapshot_id}
            onChange={(e) => setNewBranch(prev => ({ ...prev, base_snapshot_id: e.target.value }))}
            placeholder="snapshot-1 (leave empty for latest)"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateBranch} variant="contained">
            Create Branch
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
