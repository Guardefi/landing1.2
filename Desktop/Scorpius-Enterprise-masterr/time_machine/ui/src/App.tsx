import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Tabs,
  Tab,
  Box,
  Snackbar,
  Alert,
  CssBaseline,
  createTheme,
  ThemeProvider
} from '@mui/material';
import { Timeline } from './components/Timeline';
import EnhancedJobMonitor from './components/EnhancedJobMonitor';
import { BranchManager } from './components/BranchManager';
import { DiffViewer } from './components/DiffViewer';
import { PluginDashboard } from './components/PluginDashboard';

// Create a dark theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00d4aa',
    },
    secondary: {
      main: '#ff6b35',
    },
    background: {
      default: '#0d1117',
      paper: '#161b22',
    },
  },
});

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleError = (message: string) => {
    setError(message);
    setTimeout(() => setError(null), 5000);
  };

  const handleSuccess = (message: string) => {
    setSuccess(message);
    setTimeout(() => setSuccess(null), 3000);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Time Machine - Blockchain Forensics Dashboard
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth={false} sx={{ mt: 2 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="Timeline" />
            <Tab label="Jobs" />
            <Tab label="Branches" />
            <Tab label="Diff Viewer" />
            <Tab label="Plugins" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <Timeline 
            onError={handleError}
            onSuccess={handleSuccess}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <EnhancedJobMonitor />
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <BranchManager 
            onError={handleError}
            onSuccess={handleSuccess}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <DiffViewer 
            onError={handleError}
            onSuccess={handleSuccess}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={4}>
          <PluginDashboard 
            onError={handleError}
            onSuccess={handleSuccess}
          />
        </TabPanel>
      </Container>

      <Snackbar 
        open={!!error} 
        autoHideDuration={6000} 
        onClose={() => setError(null)}
      >
        <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar 
        open={!!success} 
        autoHideDuration={4000} 
        onClose={() => setSuccess(null)}
      >
        <Alert onClose={() => setSuccess(null)} severity="success" sx={{ width: '100%' }}>
          {success}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App;
