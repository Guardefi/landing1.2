import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Card,
  CardContent,
  CardActions,
  Divider,
  CircularProgress,
  Alert,
  Chip,
  TextField
} from '@mui/material';
import { Compare as DiffIcon, Download, Refresh } from '@mui/icons-material';
import MonacoEditor from '@monaco-editor/react';
import { api } from '../services/api';

interface DiffViewerProps {
  onError: (message: string) => void;
  onSuccess: (message: string) => void;
}

interface DiffData {
  format: string;
  content: string;
  summary?: {
    added: number;
    removed: number;
    modified: number;
  };
}

interface Snapshot {
  id: string;
  job_id: string;
  block_number: number;
  created_at: string;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({ onError, onSuccess }) => {
  const [leftSnapshot, setLeftSnapshot] = useState('');
  const [rightSnapshot, setRightSnapshot] = useState('');
  const [diffData, setDiffData] = useState<DiffData | null>(null);
  const [format, setFormat] = useState('json');
  const [loading, setLoading] = useState(false);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);

  // Generate demo snapshots
  const generateDemoSnapshots = (): Snapshot[] => {
    const demoSnapshots: Snapshot[] = [];
    for (let i = 1; i <= 5; i++) {
      demoSnapshots.push({
        id: `snapshot-${i}`,
        job_id: `job-${Math.floor(i / 2) + 1}`,
        block_number: 18500000 + i * 100,
        created_at: new Date(Date.now() - (5 - i) * 3600000).toISOString()
      });
    }
    return demoSnapshots;
  };

  const loadSnapshots = async () => {
    try {
      // Try to load real snapshots first
      try {
        const snapshotData = await api.getSnapshots();
        setSnapshots(snapshotData);
      } catch (apiError) {
        // Fallback to demo data
        const demoSnapshots = generateDemoSnapshots();
        setSnapshots(demoSnapshots);
        onError('Using demo snapshots - backend snapshots not available');
      }
    } catch (error) {
      onError(`Failed to load snapshots: ${error}`);
    }
  };

  useEffect(() => {
    loadSnapshots();
  }, []);

  const generateDemoDiff = (leftId: string, rightId: string, format: string): DiffData => {
    const leftSnapshot = snapshots.find(s => s.id === leftId);
    const rightSnapshot = snapshots.find(s => s.id === rightId);

    if (format === 'html') {
      return {
        format: 'html',
        content: `
          <div style="font-family: monospace; padding: 20px;">
            <h3>Diff: ${leftSnapshot?.id} → ${rightSnapshot?.id}</h3>
            <div style="background-color: #e8f5e8; padding: 10px; margin: 10px 0;">
              <span style="color: #2d7d32;">+ Added: New contract at 0x1234...abcd</span>
            </div>
            <div style="background-color: #ffebee; padding: 10px; margin: 10px 0;">
              <span style="color: #c62828;">- Removed: Old storage slot 0x5678</span>
            </div>
            <div style="background-color: #fff3e0; padding: 10px; margin: 10px 0;">
              <span style="color: #ef6c00;">~ Modified: Balance changed from 100 ETH to 150 ETH</span>
            </div>
          </div>
        `,
        summary: { added: 12, removed: 5, modified: 8 }
      };
    }

    return {
      format: 'json',
      content: JSON.stringify({
        diff_metadata: {
          left_snapshot: leftSnapshot?.id,
          right_snapshot: rightSnapshot?.id,
          block_range: `${leftSnapshot?.block_number} → ${rightSnapshot?.block_number}`,
          timestamp: new Date().toISOString()
        },
        state_changes: {
          contracts: {
            added: [
              {
                address: '0x1234567890abcdef1234567890abcdef12345678',
                code_hash: '0xabcd1234...',
                deployed_at_block: rightSnapshot?.block_number
              }
            ],
            removed: [
              {
                address: '0xfedcba0987654321fedcba0987654321fedcba09',
                reason: 'selfdestruct'
              }
            ]
          },
          storage: {
            modified: [
              {
                address: '0x9876543210fedcba9876543210fedcba98765432',
                slot: '0x0000000000000000000000000000000000000000000000000000000000000001',
                old_value: '0x0000000000000000000000000000000000000000000000000de0b6b3a7640000',
                new_value: '0x0000000000000000000000000000000000000000000000001bc16d674ec80000'
              }
            ]
          },
          balances: {
            modified: [
              {
                address: '0x5555444433332222111100009999888877776666',
                old_balance: '100000000000000000000',
                new_balance: '150000000000000000000'
              }
            ]
          }
        },
        summary: {
          total_changes: 25,
          contracts_added: 12,
          contracts_removed: 5,
          storage_modified: 8
        }
      }, null, 2),
      summary: { added: 12, removed: 5, modified: 8 }
    };
  };

  const handleGenerateDiff = async () => {
    if (!leftSnapshot || !rightSnapshot) {
      onError('Please select both snapshots to compare');
      return;
    }

    if (leftSnapshot === rightSnapshot) {
      onError('Please select different snapshots to compare');
      return;
    }

    setLoading(true);
    try {
      try {
        const response = await api.generateDiff({
          left_snapshot_id: leftSnapshot,
          right_snapshot_id: rightSnapshot,
          format: format,
          include_metadata: true
        });
        setDiffData(response);
        onSuccess('Diff generated successfully');
      } catch (apiError) {
        // Fallback to demo diff
        const demoDiff = generateDemoDiff(leftSnapshot, rightSnapshot, format);
        setDiffData(demoDiff);
        onSuccess('Demo diff generated - backend diff not available');
      }
    } catch (err) {
      onError(`Failed to generate diff: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadDiff = () => {
    if (!diffData) return;

    const blob = new Blob([diffData.content], { 
      type: format === 'html' ? 'text/html' : 'application/json' 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `diff_${leftSnapshot}_${rightSnapshot}.${format === 'html' ? 'html' : 'json'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    onSuccess('Diff downloaded');
  };

  const getEditorLanguage = () => {
    switch (format) {
      case 'html':
        return 'html';
      case 'sarif':
        return 'json';
      default:
        return 'json';
    }
  };

  const formatSnapshotLabel = (snapshot: Snapshot) => {
    return `${snapshot.id} (Block ${snapshot.block_number})`;
  };

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <DiffIcon />
          Snapshot Diff Viewer
        </Typography>

        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Left Snapshot</InputLabel>
              <Select
                value={leftSnapshot}
                onChange={(e) => setLeftSnapshot(e.target.value)}
                label="Left Snapshot"
              >
                {snapshots.map((snapshot) => (
                  <MenuItem key={snapshot.id} value={snapshot.id}>
                    {formatSnapshotLabel(snapshot)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Right Snapshot</InputLabel>
              <Select
                value={rightSnapshot}
                onChange={(e) => setRightSnapshot(e.target.value)}
                label="Right Snapshot"
              >
                {snapshots.map((snapshot) => (
                  <MenuItem key={snapshot.id} value={snapshot.id}>
                    {formatSnapshotLabel(snapshot)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Output Format</InputLabel>
              <Select
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                label="Output Format"
              >
                <MenuItem value="json">JSON</MenuItem>
                <MenuItem value="html">HTML</MenuItem>
                <MenuItem value="sarif">SARIF</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            onClick={handleGenerateDiff}
            disabled={loading || !leftSnapshot || !rightSnapshot}
            startIcon={loading ? <CircularProgress size={20} /> : <DiffIcon />}
          >
            Generate Diff
          </Button>
          
          <Button
            variant="outlined"
            onClick={loadSnapshots}
            startIcon={<Refresh />}
          >
            Refresh Snapshots
          </Button>
          
          {diffData && (
            <Button
              variant="outlined"
              onClick={handleDownloadDiff}
              startIcon={<Download />}
            >
              Download
            </Button>
          )}
        </Box>
      </Paper>

      {diffData && (
        <Paper sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Diff Result
            </Typography>
            {diffData.summary && (
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip label={`+${diffData.summary.added} Added`} color="success" size="small" />
                <Chip label={`-${diffData.summary.removed} Removed`} color="error" size="small" />
                <Chip label={`~${diffData.summary.modified} Modified`} color="warning" size="small" />
              </Box>
            )}
          </Box>

          <Divider sx={{ mb: 2 }} />

          <Card variant="outlined">
            <CardContent sx={{ p: 0 }}>
              <MonacoEditor
                height="500px"
                language={getEditorLanguage()}
                value={diffData.content}
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  wordWrap: 'on',
                  automaticLayout: true
                }}
                theme="vs-dark"
              />
            </CardContent>
          </Card>
        </Paper>
      )}

      {snapshots.length === 0 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <DiffIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            No snapshots available
          </Typography>
          <Typography color="text.secondary">
            Create some replay jobs to generate snapshots for comparison
          </Typography>
        </Paper>
      )}
    </Box>
  );
};
