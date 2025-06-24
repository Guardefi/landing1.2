# API Endpoints & WebSocket Connections TODO List

## Scanner Module (15 endpoints + 3 WebSockets)

### REST Endpoints

- [ ] POST /api/scanner/scan - Start new vulnerability scan
- [ ] GET /api/scanner/scan/{scan_id} - Get scan status and results
- [ ] GET /api/scanner/scans - List all scans with pagination
- [ ] DELETE /api/scanner/scan/{scan_id} - Cancel/delete scan
- [ ] POST /api/scanner/quick-scan - Quick scan with limited plugins
- [ ] GET /api/scanner/plugins - List available scanner plugins
- [ ] POST /api/scanner/plugins/{plugin_name}/enable - Enable specific plugin
- [ ] POST /api/scanner/plugins/{plugin_name}/disable - Disable specific plugin
- [ ] GET /api/scanner/plugins/{plugin_name}/config - Get plugin configuration
- [ ] PUT /api/scanner/plugins/{plugin_name}/config - Update plugin configuration
- [ ] POST /api/scanner/batch-scan - Start batch scan of multiple contracts
- [ ] GET /api/scanner/statistics - Get scanning statistics
- [ ] POST /api/scanner/rescan - Rescan existing contract with new plugins
- [ ] GET /api/scanner/findings/{finding_id} - Get detailed finding information
- [ ] PUT /api/scanner/findings/{finding_id}/status - Update finding status

### WebSocket Connections

- [ ] WS /ws/scanner/scan/{scan_id} - Real-time scan progress updates
- [ ] WS /ws/scanner/live-feed - Live feed of all scanning activity
- [ ] WS /ws/scanner/alerts - Real-time vulnerability alerts

## Mempool Module (12 endpoints + 4 WebSockets)

### REST Endpoints

- [ ] GET /api/mempool/monitor/start - Start mempool monitoring
- [ ] GET /api/mempool/monitor/stop - Stop mempool monitoring
- [ ] GET /api/mempool/monitor/status - Get monitoring status
- [ ] GET /api/mempool/transactions - Get recent mempool transactions
- [ ] GET /api/mempool/transactions/{tx_hash} - Get specific transaction details
- [ ] POST /api/mempool/filter - Set transaction filtering criteria
- [ ] GET /api/mempool/statistics - Get mempool statistics
- [ ] GET /api/mempool/pending-count - Get pending transaction count
- [ ] POST /api/mempool/analyze - Analyze mempool for patterns
- [ ] GET /api/mempool/gas-tracker - Get gas price tracking data
- [ ] POST /api/mempool/alerts/configure - Configure mempool alerts
- [ ] GET /api/mempool/history - Get historical mempool data

### WebSocket Connections

- [ ] WS /ws/mempool/live - Live mempool transaction feed
- [ ] WS /ws/mempool/gas-prices - Real-time gas price updates
- [ ] WS /ws/mempool/alerts - Mempool-based alerts
- [ ] WS /ws/mempool/statistics - Live mempool statistics

## Bytecode Analysis Module (10 endpoints + 2 WebSockets)

### REST Endpoints

- [ ] POST /api/bytecode/analyze - Analyze contract bytecode
- [ ] GET /api/bytecode/analysis/{analysis_id} - Get analysis results
- [ ] POST /api/bytecode/similarity - Compare bytecode similarity
- [ ] GET /api/bytecode/patterns - Get known vulnerability patterns
- [ ] POST /api/bytecode/patterns - Add new vulnerability pattern
- [ ] DELETE /api/bytecode/patterns/{pattern_id} - Delete vulnerability pattern
- [ ] GET /api/bytecode/decompile - Decompile bytecode to pseudo-code
- [ ] POST /api/bytecode/batch-analyze - Batch analyze multiple contracts
- [ ] GET /api/bytecode/statistics - Get bytecode analysis statistics
- [ ] POST /api/bytecode/compare - Compare two bytecode samples

### WebSocket Connections

- [ ] WS /ws/bytecode/analysis/{analysis_id} - Real-time analysis progress
- [ ] WS /ws/bytecode/alerts - Bytecode-based vulnerability alerts

## Time Machine Module (14 endpoints + 5 WebSockets)

### REST Endpoints

- [ ] GET /api/time-machine/exploits - List historical exploits
- [ ] GET /api/time-machine/exploits/{exploit_id} - Get exploit details
- [ ] POST /api/time-machine/replay/{exploit_id} - Start exploit replay
- [ ] GET /api/time-machine/replay/{session_id} - Get replay status
- [ ] DELETE /api/time-machine/replay/{session_id} - Stop replay session
- [ ] GET /api/time-machine/replay/{session_id}/transactions - Get replay transactions
- [ ] POST /api/time-machine/search - Search historical exploits
- [ ] GET /api/time-machine/timeline - Get exploit timeline
- [ ] POST /api/time-machine/bookmark - Bookmark exploit for later
- [ ] GET /api/time-machine/bookmarks - Get user bookmarks
- [ ] DELETE /api/time-machine/bookmarks/{bookmark_id} - Remove bookmark
- [ ] GET /api/time-machine/statistics - Get historical statistics
- [ ] POST /api/time-machine/analyze-period - Analyze specific time period
- [ ] GET /api/time-machine/trends - Get exploit trends analysis

### WebSocket Connections

- [ ] WS /ws/time-machine/replay/{session_id} - Live replay progress
- [ ] WS /ws/time-machine/live-exploits - Real-time exploit detection
- [ ] WS /ws/time-machine/replay-feed - Live transaction replay feed
- [ ] WS /ws/time-machine/analysis - Real-time analysis updates
- [ ] WS /ws/time-machine/alerts - Historical pattern alerts

## Simulation Module (16 endpoints + 4 WebSockets)

### REST Endpoints

- [ ] POST /api/simulation/create - Create new simulation environment
- [ ] GET /api/simulation/{sim_id} - Get simulation status
- [ ] DELETE /api/simulation/{sim_id} - Destroy simulation environment
- [ ] POST /api/simulation/{sim_id}/deploy - Deploy contract to simulation
- [ ] POST /api/simulation/{sim_id}/execute - Execute transaction in simulation
- [ ] GET /api/simulation/{sim_id}/state - Get current simulation state
- [ ] POST /api/simulation/{sim_id}/fork - Fork blockchain at specific block
- [ ] POST /api/simulation/{sim_id}/exploit - Run exploit simulation
- [ ] GET /api/simulation/{sim_id}/logs - Get simulation logs
- [ ] POST /api/simulation/{sim_id}/snapshot - Create state snapshot
- [ ] POST /api/simulation/{sim_id}/restore - Restore from snapshot
- [ ] GET /api/simulation/templates - Get exploit templates
- [ ] POST /api/simulation/templates - Create new exploit template
- [ ] GET /api/simulation/environments - List active simulations
- [ ] POST /api/simulation/batch-test - Run batch exploit tests
- [ ] GET /api/simulation/results/{test_id} - Get batch test results

### WebSocket Connections

- [ ] WS /ws/simulation/{sim_id}/logs - Live simulation logs
- [ ] WS /ws/simulation/{sim_id}/state - Real-time state changes
- [ ] WS /ws/simulation/alerts - Simulation-based alerts
- [ ] WS /ws/simulation/progress - Batch test progress updates

## Reports Module (18 endpoints + 3 WebSockets)

### REST Endpoints

- [ ] GET /api/reports - List all reports with pagination
- [ ] GET /api/reports/{report_id} - Get specific report
- [ ] POST /api/reports/generate - Generate new report
- [ ] DELETE /api/reports/{report_id} - Delete report
- [ ] GET /api/reports/{report_id}/download - Download report file
- [ ] POST /api/reports/{report_id}/share - Share report with others
- [ ] GET /api/reports/templates - Get report templates
- [ ] POST /api/reports/templates - Create custom report template
- [ ] PUT /api/reports/templates/{template_id} - Update report template
- [ ] DELETE /api/reports/templates/{template_id} - Delete report template
- [ ] POST /api/reports/schedule - Schedule automated reports
- [ ] GET /api/reports/scheduled - Get scheduled reports
- [ ] PUT /api/reports/scheduled/{schedule_id} - Update scheduled report
- [ ] DELETE /api/reports/scheduled/{schedule_id} - Delete scheduled report
- [ ] GET /api/reports/statistics - Get reporting statistics
- [ ] POST /api/reports/export - Export reports in bulk
- [ ] GET /api/reports/audit-trail - Get report audit trail
- [ ] POST /api/reports/poc-generate - Generate proof-of-concept code

### WebSocket Connections

- [ ] WS /ws/reports/generation/{report_id} - Report generation progress
- [ ] WS /ws/reports/notifications - Report-related notifications
- [ ] WS /ws/reports/audit - Real-time audit trail updates

## MEV Operations Module (15 endpoints + 6 WebSockets)

### REST Endpoints

- [ ] GET /api/mev/opportunities - Get current MEV opportunities
- [ ] POST /api/mev/simulate - Simulate MEV transaction
- [ ] GET /api/mev/simulation/{sim_id} - Get MEV simulation results
- [ ] POST /api/mev/strategies - Create MEV strategy
- [ ] GET /api/mev/strategies - List MEV strategies
- [ ] PUT /api/mev/strategies/{strategy_id} - Update MEV strategy
- [ ] DELETE /api/mev/strategies/{strategy_id} - Delete MEV strategy
- [ ] POST /api/mev/backtest - Backtest MEV strategy
- [ ] GET /api/mev/backtest/{test_id} - Get backtest results
- [ ] GET /api/mev/analytics - Get MEV analytics data
- [ ] POST /api/mev/alerts/configure - Configure MEV alerts
- [ ] GET /api/mev/flashloan/providers - Get flashloan providers
- [ ] POST /api/mev/flashloan/simulate - Simulate flashloan attack
- [ ] GET /api/mev/arbitrage/opportunities - Get arbitrage opportunities
- [ ] POST /api/mev/sandwich/detect - Detect sandwich attack opportunities

### WebSocket Connections

- [ ] WS /ws/mev/opportunities - Live MEV opportunities feed
- [ ] WS /ws/mev/simulations - Real-time simulation updates
- [ ] WS /ws/mev/alerts - MEV-based alerts
- [ ] WS /ws/mev/analytics - Live MEV analytics
- [ ] WS /ws/mev/arbitrage - Real-time arbitrage opportunities
- [ ] WS /ws/mev/flashloan - Flashloan opportunity alerts

## Honeypot Detection Module (12 endpoints + 3 WebSockets)

### REST Endpoints

- [ ] POST /api/honeypot/analyze - Analyze contract for honeypot patterns
- [ ] GET /api/honeypot/analysis/{analysis_id} - Get honeypot analysis results
- [ ] GET /api/honeypot/patterns - Get known honeypot patterns
- [ ] POST /api/honeypot/patterns - Add new honeypot pattern
- [ ] PUT /api/honeypot/patterns/{pattern_id} - Update honeypot pattern
- [ ] DELETE /api/honeypot/patterns/{pattern_id} - Delete honeypot pattern
- [ ] POST /api/honeypot/batch-analyze - Batch analyze multiple contracts
- [ ] GET /api/honeypot/statistics - Get honeypot detection statistics
- [ ] POST /api/honeypot/test - Test contract with simulated transactions
- [ ] GET /api/honeypot/database - Get honeypot database entries
- [ ] POST /api/honeypot/report - Report suspected honeypot
- [ ] GET /api/honeypot/alerts/configure - Configure honeypot alerts

### WebSocket Connections

- [ ] WS /ws/honeypot/analysis/{analysis_id} - Real-time analysis progress
- [ ] WS /ws/honeypot/alerts - Honeypot detection alerts
- [ ] WS /ws/honeypot/database - Live honeypot database updates

## Settings Module (15 endpoints + 4 WebSockets)

### REST Endpoints

- [ ] GET /api/settings/user - Get user settings
- [ ] PUT /api/settings/user - Update user settings
- [ ] GET /api/settings/system - Get system settings
- [ ] PUT /api/settings/system - Update system settings (admin only)
- [ ] GET /api/settings/api-keys - Get API key management
- [ ] POST /api/settings/api-keys - Create new API key
- [ ] PUT /api/settings/api-keys/{key_id} - Update API key
- [ ] DELETE /api/settings/api-keys/{key_id} - Delete API key
- [ ] GET /api/settings/notifications - Get notification preferences
- [ ] PUT /api/settings/notifications - Update notification preferences
- [ ] GET /api/settings/integrations - Get third-party integrations
- [ ] POST /api/settings/integrations - Add new integration
- [ ] PUT /api/settings/integrations/{integration_id} - Update integration
- [ ] DELETE /api/settings/integrations/{integration_id} - Remove integration
- [ ] POST /api/settings/backup - Create settings backup

### WebSocket Connections

- [ ] WS /ws/settings/notifications - Real-time notification updates
- [ ] WS /ws/settings/system - System setting changes
- [ ] WS /ws/settings/integrations - Integration status updates
- [ ] WS /ws/settings/alerts - Settings-related alerts

## Authentication & Enterprise (20 endpoints + 0 WebSockets)

### REST Endpoints

- [ ] POST /api/auth/login - User login
- [ ] POST /api/auth/logout - User logout
- [ ] POST /api/auth/refresh - Refresh JWT token
- [ ] POST /api/auth/register - User registration
- [ ] POST /api/auth/forgot-password - Forgot password
- [ ] POST /api/auth/reset-password - Reset password
- [ ] GET /api/auth/profile - Get user profile
- [ ] PUT /api/auth/profile - Update user profile
- [ ] GET /api/auth/permissions - Get user permissions
- [ ] GET /api/enterprise/license - Get license information
- [ ] POST /api/enterprise/license/verify - Verify license key
- [ ] GET /api/enterprise/features - Get available features
- [ ] GET /api/enterprise/usage - Get usage statistics
- [ ] GET /api/enterprise/limits - Get tier limits
- [ ] POST /api/enterprise/upgrade - Request tier upgrade
- [ ] GET /api/enterprise/billing - Get billing information
- [ ] GET /api/admin/users - List all users (admin only)
- [ ] POST /api/admin/users - Create new user (admin only)
- [ ] PUT /api/admin/users/{user_id} - Update user (admin only)
- [ ] DELETE /api/admin/users/{user_id} - Delete user (admin only)

## TOTAL SUMMARY

- **REST Endpoints**: 127 endpoints across 9 modules
- **WebSocket Connections**: 34 connections across 8 modules
- **Status**: All endpoints need implementation to connect backend modules to frontend
- **Priority**: Start with Scanner, Mempool, and Reports modules as they are core functionality
