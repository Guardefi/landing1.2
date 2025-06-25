# Frontend Debt Reduction - Migration Guide

## Overview

This document outlines the consolidation of duplicate code and state management in the Scorpius frontend to reduce the codebase by 10k+ LOC while improving maintainability.

## 🎯 Consolidation Summary

### API Services Consolidation

**Before**: 6 separate API service files (14,500+ LOC)

```
src/services/api.ts                    (~2,100 LOC)
src/services/apiService.ts             (~2,800 LOC)
src/services/scorpiusApi.ts            (~2,200 LOC)
src/services/apiIntegration.ts         (~1,900 LOC)
src/services/scannerAPI.ts             (~1,200 LOC)
src/services/fallbackData.ts          (~4,300 LOC)
```

**After**: 1 consolidated API client (~3,200 LOC)

```
src/services/apiClient.ts              (~3,200 LOC)
```

**Reduction**: ~11,300 LOC

### WebSocket Services Consolidation

**Before**: 3 separate WebSocket implementations (~2,800 LOC)

```
src/services/websocket.ts             (~1,100 LOC)
src/services/websocketManager.ts      (~900 LOC)
src/services/websocketService.ts      (~800 LOC)
```

**After**: 1 consolidated WebSocket client (~600 LOC)

```
src/services/websocketClient.ts       (~600 LOC)
```

**Reduction**: ~2,200 LOC

### State Management Consolidation

**Before**: Multiple custom hooks and scattered state (~3,500 LOC)

```
src/hooks/useAPIData.ts               (~400 LOC)
src/hooks/useDashboardData.ts         (~350 LOC)
src/hooks/useScanner.ts               (~450 LOC)
src/hooks/useScorpiusAPI.ts           (~500 LOC)
src/hooks/useScannerAPI.ts            (~300 LOC)
src/hooks/useRealtime.ts              (~250 LOC)
src/hooks/useStorage.ts               (~200 LOC)
src/hooks/useNotifications.ts         (~300 LOC)
src/hooks/useWebSocket.ts             (~250 LOC)
```

**After**: 1 consolidated Zustand store (~800 LOC)

```
src/stores/rootStore.ts               (~800 LOC)
```

**Reduction**: ~2,700 LOC

## 📋 Migration Steps

### Phase 1: API Services Migration

1. **Replace imports across the codebase**:

   ```typescript
   // OLD
   import { apiRequest } from '../services/api';
   import { scorpiusApi } from '../services/scorpiusApi';

   // NEW
   import { apiClient } from '../services/apiClient';
   ```

2. **Update API calls**:

   ```typescript
   // OLD
   const result = await apiRequest('/scanner/scan', { method: 'POST', body: data });

   // NEW
   const result = await apiClient.scanner.scanContract(data);
   ```

3. **Files to remove**:
   - `src/services/api.ts`
   - `src/services/apiService.ts`
   - `src/services/scorpiusApi.ts`
   - `src/services/apiIntegration.ts`
   - `src/services/scannerAPI.ts`
   - `src/services/fallbackData.ts`

### Phase 2: WebSocket Services Migration

1. **Replace WebSocket imports**:

   ```typescript
   // OLD
   import { websocketService } from '../services/websocket';
   import { WebSocketManager } from '../services/websocketManager';

   // NEW
   import { wsClient } from '../services/websocketClient';
   ```

2. **Update WebSocket usage**:

   ```typescript
   // OLD
   websocketService.connect();
   websocketService.subscribe('scans', callback);

   // NEW
   wsClient.connect();
   wsClient.subscribeToScans();
   wsClient.on('scan_completed', callback);
   ```

3. **Files to remove**:
   - `src/services/websocket.ts`
   - `src/services/websocketManager.ts`
   - `src/services/websocketService.ts`

### Phase 3: State Management Migration

1. **Replace custom hooks with Zustand store**:

   ```typescript
   // OLD
   import { useAPIData } from '../hooks/useAPIData';
   import { useDashboardData } from '../hooks/useDashboardData';

   // NEW
   import { useAuth, useDashboard, useScanner } from '../stores/rootStore';
   ```

2. **Update component usage**:

   ```typescript
   // OLD
   const { data, loading, error } = useAPIData('/dashboard/stats');

   // NEW
   const { stats, isLoading, error, fetchStats } = useDashboard();
   useEffect(() => {
     fetchStats();
   }, []);
   ```

3. **Files to remove**:
   - `src/hooks/useAPIData.ts`
   - `src/hooks/useDashboardData.ts`
   - `src/hooks/useScanner.ts`
   - `src/hooks/useScorpiusAPI.ts`
   - `src/hooks/useScannerAPI.ts`
   - `src/hooks/useRealtime.ts`
   - `src/hooks/useStorage.ts`
   - `src/hooks/useNotifications.ts`
   - `src/hooks/useWebSocket.ts`

## 🔧 Migration Script

```bash
#!/bin/bash
# Frontend Debt Reduction Migration Script

echo "🧹 Starting frontend debt reduction migration..."

# Phase 1: Create backup
echo "📦 Creating backup..."
git checkout -b frontend-debt-reduction-backup
git checkout main

# Phase 2: Remove duplicate API services
echo "🗑️ Removing duplicate API services..."
rm src/services/api.ts
rm src/services/apiService.ts
rm src/services/scorpiusApi.ts
rm src/services/apiIntegration.ts
rm src/services/scannerAPI.ts
rm src/services/fallbackData.ts

# Phase 3: Remove duplicate WebSocket services
echo "🗑️ Removing duplicate WebSocket services..."
rm src/services/websocket.ts
rm src/services/websocketManager.ts
rm src/services/websocketService.ts

# Phase 4: Remove redundant hooks
echo "🗑️ Removing redundant hooks..."
rm src/hooks/useAPIData.ts
rm src/hooks/useDashboardData.ts
rm src/hooks/useScanner.ts
rm src/hooks/useScorpiusAPI.ts
rm src/hooks/useScannerAPI.ts
rm src/hooks/useRealtime.ts
rm src/hooks/useStorage.ts
rm src/hooks/useNotifications.ts
rm src/hooks/useWebSocket.ts

# Phase 5: Update imports (requires manual review)
echo "⚠️ Manual step required: Update imports in components"
echo "See migration guide for details"

# Phase 6: Install Zustand if not already installed
echo "📦 Ensuring Zustand is installed..."
npm install zustand

# Phase 7: Run tests
echo "🧪 Running tests..."
npm run test

# Phase 8: Run linting
echo "🔍 Running linting..."
npm run lint

echo "✅ Migration script completed!"
echo "📝 Review the migration guide for manual import updates"
echo "🧪 Run 'npm run test' to verify everything works"
```

## 🎨 Component Updates Required

### Dashboard Components

```typescript
// src/pages/Dashboard.tsx
// OLD
import { useDashboardData } from '../hooks/useDashboardData';

const Dashboard = () => {
  const { data, loading, error } = useDashboardData();
  // ...
};

// NEW
import { useDashboard } from '../stores/rootStore';

const Dashboard = () => {
  const { stats, isLoading, error, fetchStats } = useDashboard();

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);
  // ...
};
```

### Scanner Components

```typescript
// src/pages/SmartContractScanner.tsx
// OLD
import { useScanner } from '../hooks/useScanner';
import { scannerAPI } from '../services/scannerAPI';

const Scanner = () => {
  const { scans, isScanning } = useScanner();

  const handleScan = async address => {
    await scannerAPI.scanContract(address);
  };
  // ...
};

// NEW
import { useScanner } from '../stores/rootStore';

const Scanner = () => {
  const { scans, isScanning, scanContract } = useScanner();

  const handleScan = async address => {
    await scanContract(address);
  };
  // ...
};
```

## 📊 Expected Results

### LOC Reduction Summary

| Category           | Before     | After     | Reduction  |
| ------------------ | ---------- | --------- | ---------- |
| API Services       | 14,500     | 3,200     | 11,300     |
| WebSocket Services | 2,800      | 600       | 2,200      |
| State Management   | 3,500      | 800       | 2,700      |
| **Total**          | **20,800** | **4,600** | **16,200** |

### Benefits

1. **Maintainability**: Single source of truth for API calls and state
2. **Type Safety**: Better TypeScript integration with consolidated types
3. **Performance**: Reduced bundle size and faster builds
4. **Developer Experience**: Consistent patterns and easier onboarding
5. **Testing**: Easier to mock and test consolidated services

## ⚠️ Potential Issues & Solutions

### 1. Breaking Changes

**Issue**: Existing components may break during migration
**Solution**: Gradual migration with feature flags and thorough testing

### 2. Type Conflicts

**Issue**: TypeScript errors due to changed import paths
**Solution**: Update all type imports and run `tsc --noEmit` frequently

### 3. State Management Changes

**Issue**: Components expecting different state structure
**Solution**: Update components incrementally and maintain backward compatibility

### 4. WebSocket Event Handling

**Issue**: Different event names in consolidated WebSocket client
**Solution**: Map old event names to new ones during transition

## 🧪 Testing Strategy

1. **Unit Tests**: Update tests to use new consolidated services
2. **Integration Tests**: Verify API calls work with new client
3. **E2E Tests**: Ensure user workflows still function
4. **Performance Tests**: Confirm bundle size reduction and load times

## 📅 Migration Timeline

- **Week 1**: Phase 1-2 (API and WebSocket consolidation)
- **Week 2**: Phase 3 (State management migration)
- **Week 3**: Testing, optimization, and cleanup

## ✅ Success Criteria

- [ ] 16k+ LOC reduction achieved
- [ ] All tests passing
- [ ] No TypeScript errors
- [ ] Bundle size reduced by >15%
- [ ] No runtime errors in production
- [ ] Performance maintained or improved

---

**Target Achievement**: >16k LOC reduction (exceeds 10k goal by 60%)
